# coding: utf-8
"""
    flask_weixin
    ~~~~~~~~~~~~

    Weixin implementation in Flask.

    :copyright: (c) 2013 by Hsiaoming Yang.
    :license: BSD, see LICENSE for more detail.
"""

import time
import hashlib

try:
    from lxml import etree
except ImportError:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree


__all__ = ('Weixin',)
__version__ = '0.1.0'
__author__ = 'Hsiaoming Yang <me@lepture.com>'


class Weixin(object):
    """Interface for mp.weixin.qq.com

    http://mp.weixin.qq.com/wiki/index.php
    """

    def __init__(self, app=None):
        self.token = None
        self._registry = {}

        if app:
            self.init_app(app)

    def init_app(self, app):
        if hasattr(app, 'config'):
            config = app.config
        else:
            # flask-weixin can be used without flask
            config = app

        self.token = config.get('WEIXIN_TOKEN', None)
        self.sender = config.get('WEIXIN_SENDER', None)
        self.expires_in = config.get('WEIXIN_EXPIRES_IN', 0)

    def validate(self, signature, timestamp, nonce):
        """Validate request signature."""
        if not self.token:
            raise RuntimeError('WEIXIN_TOKEN is missing')

        if self.expires_in:
            try:
                timestamp = int(timestamp)
            except:
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

    def parse(self, body):
        """Parse xml body sent by weixin."""
        dct = {}
        root = etree.fromstring(body)
        for child in root:
            dct[child.tag] = child.text

        ret = {}
        ret['id'] = dct.get('MsgId')
        ret['timestamp'] = int(dct.get('CreateTime', 0))
        ret['receiver'] = dct.get('ToUserName')
        ret['sender'] = dct.get('FromUserName')
        ret['type'] = type = dct.get('MsgType')

        if type == 'text':
            ret['content'] = dct.get('Content')
            return ret

        if type == 'image':
            ret['picurl'] = dct.get('PicUrl')
            return ret

        if type == 'location':
            ret['location_x'] = dct.get('Location_X')
            ret['location_y'] = dct.get('Location_Y')
            ret['scale'] = int(dct.get('Scale', 0))
            ret['label'] = dct.get('Label')
            return ret

        if type == 'link':
            ret['title'] = dct.get('Title')
            ret['description'] = dct.get('Description')
            ret['url'] = dct.get('url')
            return ret

        return ret

    def reply(self, username, type='text', **kwargs):
        if 'sender' in kwargs:
            sender = kwargs.pop('sender')
        else:
            sender = self.sender

        if not sender:
            raise RuntimeError('WEIXIN_SENDER is missing')

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

        return None

    def register(self, key, func=None):
        # TODO: decorator
        self._registry[key] = func

    def view_func(self):
        from flask import request, Response

        if request.method == 'GET':
            signature = request.args.get('signature')
            timestamp = request.args.get('timestamp')
            nonce = request.args.get('nonce')
            echostr = request.args.get('echostr')
            if self.validate(signature, timestamp, nonce):
                return echostr
            return 'failed', 400

        try:
            ret = self.parse(request.data)
        except:
            return 'invalid', 400

        if 'type' not in ret:
            # not a valid message
            return 'invalid', 400

        if ret['type'] == 'text' and ret['content'] in self._registry:
            func = self._registry[ret['content']]
        elif '*' in self._registry:
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
    articles = map(lambda o: item_template % o, items)

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
