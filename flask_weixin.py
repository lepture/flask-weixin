# coding: utf-8
"""
    flask_weixin
    ~~~~~~~~~~~~

    Weixin implementation in Flask.

    :copyright: (c) 2013 - 2015 by Hsiaoming Yang and its contributors.
    :license: BSD, see LICENSE for more detail.
"""

import time
import hashlib
from datetime import datetime
from collections import namedtuple

try:
    from lxml import etree
except ImportError:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

try:
    from flask import current_app, request, Response
except ImportError:
    current_app = None
    request = None
    Response = None


__all__ = ('Weixin',)
__version__ = '0.5.0'
__author__ = 'Hsiaoming Yang <me@lepture.com>'


StandaloneApplication = namedtuple('StandaloneApplication', ['config'])


class Weixin(object):
    """Interface for mp.weixin.qq.com

    http://mp.weixin.qq.com/wiki/index.php
    """

    def __init__(self, app=None):
        self._registry = {}
        self._registry_without_key = []

        if isinstance(app, dict):
            # flask-weixin can be used without flask
            app = StandaloneApplication(config=app)

        if app is None:
            self.app = current_app
        else:
            self.init_app(app)
            self.app = app

    def init_app(self, app):
        app.config.setdefault('WEIXIN_TOKEN', None)
        app.config.setdefault('WEIXIN_SENDER', None)
        app.config.setdefault('WEIXIN_EXPIRES_IN', 0)

    @property
    def token(self):
        return self.app.config['WEIXIN_TOKEN']

    @property
    def sender(self):
        return self.app.config['WEIXIN_SENDER']

    @property
    def expires_in(self):
        return self.app.config['WEIXIN_EXPIRES_IN']

    def validate(self, signature, timestamp, nonce):
        """Validate request signature.

        :param signature: A string signature parameter sent by weixin.
        :param timestamp: A int timestamp parameter sent by weixin.
        :param nonce: A int nonce parameter sent by weixin.
        """
        if not self.token:
            raise RuntimeError('WEIXIN_TOKEN is missing')

        if self.expires_in:
            try:
                timestamp = int(timestamp)
            except (ValueError, TypeError):
                # fake timestamp
                return False

            delta = time.time() - timestamp
            if delta < 0:
                # this is a fake timestamp
                return False

            if delta > self.expires_in:
                # expired timestamp
                return False

        values = [self.token, str(timestamp), str(nonce)]
        s = ''.join(sorted(values))
        hsh = hashlib.sha1(s.encode('utf-8')).hexdigest()
        return signature == hsh

    def parse(self, content):
        """Parse xml body sent by weixin.

        :param content: A text of xml body.
        """
        raw = {}

        try:
            root = etree.fromstring(content)
        except SyntaxError as e:
            raise ValueError(*e.args)

        for child in root:
            raw[child.tag] = child.text

        formatted = self.format(raw)

        msg_type = formatted['type']
        msg_parser = getattr(self, 'parse_%s' % msg_type, None)
        if callable(msg_parser):
            parsed = msg_parser(raw)
        else:
            parsed = self.parse_invalid_type(raw)

        formatted.update(parsed)
        return formatted

    def format(self, kwargs):
        timestamp = int(kwargs.get('CreateTime', 0))
        return {
            'id': kwargs.get('MsgId'),
            'timestamp': timestamp,
            'receiver': kwargs.get('ToUserName'),
            'sender': kwargs.get('FromUserName'),
            'type': kwargs.get('MsgType'),
            'time': datetime.fromtimestamp(timestamp),
        }

    def parse_text(self, raw):
        return {'content': raw.get('Content')}

    def parse_image(self, raw):
        return {'picurl': raw.get('PicUrl')}

    def parse_location(self, raw):
        return {
            'location_x': raw.get('Location_X'),
            'location_y': raw.get('Location_Y'),
            'scale': int(raw.get('Scale', 0)),
            'label': raw.get('Label'),
        }

    def parse_link(self, raw):
        return {
            'title': raw.get('Title'),
            'description': raw.get('Description'),
            'url': raw.get('url'),
        }

    def parse_event(self, raw):
        return {
            'event': raw.get('Event'),
            'event_key': raw.get('EventKey'),
            'ticket': raw.get('Ticket'),
            'latitude': raw.get('Latitude'),
            'longitude': raw.get('Longitude'),
            'precision': raw.get('Precision'),
        }

    def parse_voice(self, raw):
        return {
            'media_id': raw.get('MediaID'),
            'format': raw.get('Format'),
            'recognition': raw.get('Recognition'),
        }

    def parse_invalid_type(self, raw):
        return {}

    def reply(self, username, type='text', sender=None, **kwargs):
        """Create the reply text for weixin.

        The reply varies per reply type. The acceptable types are `text`,
        `music` and `news`. Each type accepts different parameters, but
        they share some common parameters:

            * username: the receiver's username
            * type: the reply type, aka text, music and news
            * sender: sender is optional if you have a default value

        Text reply requires an additional parameter of `content`.

        Music reply requires 4 more parameters:

            * title: A string for music title
            * description: A string for music description
            * music_url: A link of the music
            * hq_music_url: A link of the high quality music

        News reply requires an additional parameter of `articles`, which
        is a list/tuple of articles, each one is a dict:

            * title: A string for article title
            * description: A string for article description
            * picurl: A link for article cover image
            * url: A link for article url
        """
        sender = sender or self.sender
        if not sender:
            raise RuntimeError('WEIXIN_SENDER or sender argument is missing')

        if type == 'text':
            content = kwargs.get('content', '')
            return text_reply(username, sender, content)

        if type == 'music':
            values = {}
            for k in ('title', 'description', 'music_url', 'hq_music_url'):
                values[k] = kwargs.get(k)
            return music_reply(username, sender, **values)

        if type == 'news':
            items = kwargs.get('articles', [])
            return news_reply(username, sender, *items)

        if type == 'customer_service':
            service_account = kwargs.get('service_account', None)
            return transfer_customer_service_reply(username, sender,
                                                   service_account)

    def register(self, key=None, func=None, **kwargs):
        """Register a command helper function.

        You can register the function::

            def print_help(**kwargs):
                username = kwargs.get('sender')
                sender = kwargs.get('receiver')
                return weixin.reply(
                    username, sender=sender, content='text reply'
                )

            weixin.register('help', print_help)

        It is also accessible as a decorator::

            @weixin.register('help')
            def print_help(*args, **kwargs):
                username = kwargs.get('sender')
                sender = kwargs.get('receiver')
                return weixin.reply(
                    username, sender=sender, content='text reply'
                )
        """
        if func:
            if key is None:
                limitation = frozenset(kwargs.items())
                self._registry_without_key.append((func, limitation))
            else:
                self._registry[key] = func
            return func

        return self.__call__(key, **kwargs)

    def __call__(self, key, **kwargs):
        """Register a reply function.

        Only available as a decorator::

            @weixin('help')
            def print_help(*args, **kwargs):
                username = kwargs.get('sender')
                sender = kwargs.get('receiver')
                return weixin.reply(
                    username, sender=sender, content='text reply'
                )
        """
        def wrapper(func):
            self.register(key, func=func, **kwargs)
            return func

        return wrapper

    def view_func(self):
        """Default view function for Flask app.

        This is a simple implementation for view func, you can add it to
        your Flask app::

            weixin = Weixin(app)
            app.add_url_rule('/', view_func=weixin.view_func)
        """
        if request is None:
            raise RuntimeError('view_func need Flask be installed')

        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        if not self.validate(signature, timestamp, nonce):
            return 'signature failed', 400

        if request.method == 'GET':
            echostr = request.args.get('echostr', '')
            return echostr

        try:
            ret = self.parse(request.data)
        except ValueError:
            return 'invalid', 400

        if 'type' not in ret:
            # not a valid message
            return 'invalid', 400

        if ret['type'] == 'text' and ret['content'] in self._registry:
            func = self._registry[ret['content']]
        else:
            ret_set = frozenset(ret.items())
            matched_rules = (
                _func for _func, _limitation in self._registry_without_key
                if _limitation.issubset(ret_set))
            func = next(matched_rules, None)  # first matched rule

        if func is None:
            if '*' in self._registry:
                func = self._registry['*']
            else:
                func = 'failed'

        if callable(func):
            text = func(**ret)
        else:
            # plain text
            text = self.reply(
                username=ret['sender'],
                sender=ret['receiver'],
                content=func,
            )

        return Response(text, content_type='text/xml; charset=utf-8')

    view_func.methods = ['GET', 'POST']


def text_reply(username, sender, content):
    shared = _shared_reply(username, sender, 'text')
    template = '<xml>%s<Content><![CDATA[%s]]></Content></xml>'
    return template % (shared, content)


def music_reply(username, sender, **kwargs):
    kwargs['shared'] = _shared_reply(username, sender, 'music')

    template = (
        '<xml>'
        '%(shared)s'
        '<Music>'
        '<Title><![CDATA[%(title)s]]></Title>'
        '<Description><![CDATA[%(description)s]]></Description>'
        '<MusicUrl><![CDATA[%(music_url)s]]></MusicUrl>'
        '<HQMusicUrl><![CDATA[%(hq_music_url)s]]></HQMusicUrl>'
        '</Music>'
        '</xml>'
    )
    return template % kwargs


def news_reply(username, sender, *items):
    item_template = (
        '<item>'
        '<Title><![CDATA[%(title)s]]></Title>'
        '<Description><![CDATA[%(description)s]]></Description>'
        '<PicUrl><![CDATA[%(picurl)s]]></PicUrl>'
        '<Url><![CDATA[%(url)s]]></Url>'
        '</item>'
    )
    articles = [item_template % o for o in items]

    template = (
        '<xml>'
        '%(shared)s'
        '<ArticleCount>%(count)d</ArticleCount>'
        '<Articles>%(articles)s</Articles>'
        '</xml>'
    )
    dct = {
        'shared': _shared_reply(username, sender, 'news'),
        'count': len(items),
        'articles': ''.join(articles)
    }
    return template % dct


def transfer_customer_service_reply(username, sender, service_account):
    template = (
        '<xml>%(shared)s'
        '%(transfer_info)s</xml>')
    transfer_info = ''
    if service_account:
        transfer_info = (
            '<TransInfo>'
            '<KfAccount>![CDATA[%s]]</KfAccount>'
            '</TransInfo>') % service_account

    dct = {
        'shared': _shared_reply(username, sender,
                                type='transfer_customer_service'),
        'transfer_info': transfer_info
    }
    return template % dct


def _shared_reply(username, sender, type):
    dct = {
        'username': username,
        'sender': sender,
        'type': type,
        'timestamp': int(time.time()),
    }
    template = (
        '<ToUserName><![CDATA[%(username)s]]></ToUserName>'
        '<FromUserName><![CDATA[%(sender)s]]></FromUserName>'
        '<CreateTime>%(timestamp)d</CreateTime>'
        '<MsgType><![CDATA[%(type)s]]></MsgType>'
    )
    return template % dct
