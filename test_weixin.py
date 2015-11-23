# coding: utf-8

from flask import Flask
from flask_weixin import Weixin
from nose.tools import raises


class Base(object):
    def setUp(self):
        app = self.create_app()
        self.client = app.test_client()

        weixin = Weixin(app)
        app.add_url_rule('/', view_func=weixin.view_func)

        self.weixin = weixin
        self.app = app

        self.setup_weixin()

    def create_app(self):
        app = Flask(__name__)
        app.debug = True
        app.secret_key = 'secret'
        app.config['WEIXIN_TOKEN'] = 'B0e8alq5ZmMjcnG5gwwLRPW2'
        return app

    def setup_weixin(self):
        pass


signature_url = (
    '/?signature=16f39f0c528790d3a448a8a7a65cc81ceddd82bb&'
    'echostr=5935258128547730623&'
    'timestamp=1381389497&'
    'nonce=1381909961'
)


class TestNoToken(Base):
    def create_app(self):
        app = Flask(__name__)
        app.debug = True
        app.secret_key = 'secret'
        return app

    @raises(RuntimeError)
    def test_validate(self):
        self.client.get(signature_url)


class TestSimpleWeixin(Base):
    def test_invalid_get(self):
        rv = self.client.get('/')
        assert rv.status_code == 400

    def test_valid_get(self):
        rv = self.client.get(signature_url)
        assert rv.status_code == 200
        assert rv.data == b'5935258128547730623'

    def test_invalid_post(self):
        rv = self.client.post(signature_url)
        assert rv.status_code == 400

    def test_post_text(self):
        '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[this is a test]]></Content>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        text = self.test_post_text.__doc__
        rv = self.client.post(signature_url, data=text)
        assert rv.status_code == 200

    def test_post_image(self):
        '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <PicUrl><![CDATA[this is a url]]></PicUrl>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        text = self.test_post_image.__doc__
        rv = self.client.post(signature_url, data=text)
        assert rv.status_code == 200

    def test_post_location(self):
        '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[location]]></MsgType>
        <Location_X>23.134521</Location_X>
        <Location_Y>113.358803</Location_Y>
        <Scale>20</Scale>
        <Label><![CDATA[location]]></Label>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        text = self.test_post_location.__doc__
        rv = self.client.post(signature_url, data=text)
        assert rv.status_code == 200

    def test_post_link(self):
        '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[link]]></MsgType>
        <Title><![CDATA[title]]></Title>
        <Description><![CDATA[description]]></Description>
        <Url><![CDATA[url]]></Url>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        text = self.test_post_link.__doc__
        rv = self.client.post(signature_url, data=text)
        assert rv.status_code == 200

    def test_post_event(self):
        '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[event]]></MsgType>
        <Event><![CDATA[subscribe]]></Event>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        text = self.test_post_event.__doc__
        rv = self.client.post(signature_url, data=text)
        assert rv.status_code == 200

    def test_post_voice(self):
        '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1357290913</CreateTime>
        <MsgType><![CDATA[voice]]></MsgType>
        <MediaId><![CDATA[media_id]]></MediaId>
        <Format><![CDATA[Format]]></Format>
        <Recognition><![CDATA[腾讯微信团队]]></Recognition>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        text = self.test_post_event.__doc__
        rv = self.client.post(signature_url, data=text)
        assert rv.status_code == 200

    def test_post_no_type(self):
        '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <Title><![CDATA[title]]></Title>
        <Description><![CDATA[description]]></Description>
        <Url><![CDATA[url]]></Url>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        text = self.test_post_no_type.__doc__
        rv = self.client.post(signature_url, data=text)
        assert rv.status_code == 200


class TestExipires(Base):
    def create_app(self):
        app = Base.create_app(self)
        app.config['WEIXIN_EXPIRES_IN'] = 4
        return app

    def test_expires(self):
        rv = self.client.get(signature_url)
        assert rv.status_code == 400

    def test_invalid_timestamp(self):
        signature_url = (
            '/?signature=16f39f0c528790d3a448a8a7a65cc81ceddd82bb&'
            'echostr=5935258128547730623&'
            'timestamp=1381389497s&'
            'nonce=1381909961'
        )
        rv = self.client.get(signature_url)
        assert rv.status_code == 400


class TestReplyWeixin(Base):
    '''
    <xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>1348831860</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    <MsgId>1234567890123456</MsgId>
    </xml>
    '''

    def setup_weixin(self):
        weixin = self.weixin

        def print_all(**kwargs):
            username = kwargs.get('sender')
            sender = kwargs.get('receiver')
            content = kwargs.get('content')
            if not content:
                content = 'text'
            if content == 'music':
                return weixin.reply(
                    username, type='music', sender=sender,
                    title='weixin music',
                    description='weixin description',
                    music_url='link',
                    hq_music_url='hq link',
                )
            elif content == 'news':
                return weixin.reply(
                    username, type='news', sender=sender,
                    articles=[
                        {
                            'title': 'Hello News',
                            'description': 'Hello Description',
                            'picurl': '',
                            'url': 'link',
                        }
                    ]
                )
            elif content == 'customer_service':
                return weixin.reply(
                    username, type='customer_service', sender=sender)

            elif content == 'customer_service_to_foo':
                return weixin.reply(
                    username, type='customer_service', sender=sender,
                    service_account='foo@bar')
            else:
                return weixin.reply(
                    username, sender=sender, content='text reply'
                )

        weixin.register('*', print_all)
        weixin.register('help', 'help me')

        @weixin.register('show')
        def print_show(*args, **kwargs):
            username = kwargs.get('sender')
            sender = kwargs.get('receiver')
            return weixin.reply(
                username, sender=sender, content='show reply'
            )

    def test_help(self):
        text = self.__doc__ % 'help'
        rv = self.client.post(signature_url, data=text)
        assert b'help me' in rv.data

    def test_news(self):
        text = self.__doc__ % 'news'
        rv = self.client.post(signature_url, data=text)
        assert b'Hello News' in rv.data

    def test_music(self):
        text = self.__doc__ % 'music'
        rv = self.client.post(signature_url, data=text)
        assert b'weixin music' in rv.data

    def test_show(self):
        text = self.__doc__ % 'show'
        rv = self.client.post(signature_url, data=text)
        assert b'show reply' in rv.data

    def test_customer_service(self):
        text = self.__doc__ % 'customer_service'
        rv = self.client.post(signature_url, data=text)
        assert b'transfer_customer_service' in rv.data

    def test_customer_service_to_foo(self):
        text = self.__doc__ % 'customer_service_to_foo'
        rv = self.client.post(signature_url, data=text)
        assert b'transfer_customer_service' in rv.data
        assert b'foo@bar' in rv.data

    @raises(RuntimeError)
    def test_no_sender(self):
        @self.weixin.register('send')
        def print_send(*args, **kwargs):
            username = kwargs.get('sender')
            return self.weixin.reply(
                username, sender=None, content='send reply'
            )

        text = self.__doc__ % 'send'
        self.client.post(signature_url, data=text)


class TestKeyMatching(Base):

    def setup_weixin(self):
        @self.weixin.register(type='event', event='subscribe')
        def subscribe_event(sender, receiver, event_key, **kwargs):
            return self.weixin.reply(
                sender, sender=receiver, content='@sub:%s' % event_key)

        @self.weixin.register(type='event')
        def event(sender, receiver, **kwargs):
            return self.weixin.reply(sender, sender=receiver, content='@event')

        @self.weixin.register(type='link')
        def link(sender, receiver, **kwargs):
            return self.weixin.reply(sender, sender=receiver, content='@link')

        @self.weixin.register(type='voice')
        def voice(sender, receiver, **kwargs):
            return self.weixin.reply(sender, sender=receiver, content='@voice')

        @self.weixin.register('*')
        def fallback(sender, receiver, **kwargs):
            return self.weixin.reply(sender, sender=receiver, content='@*')

    def test_subscribe_event(self):
        data = '''
        <xml><ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[FromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[event]]></MsgType>
        <Event><![CDATA[subscribe]]></Event>
        <EventKey><![CDATA[qrscene_123123]]></EventKey>
        <Ticket><![CDATA[TICKET]]></Ticket>
        </xml>
        '''
        rv = self.client.post(signature_url, data=data)
        assert rv.status_code == 200, rv.status_code
        assert b'@sub:qrscene_123123' in rv.data

    def test_other_event(self):
        data = '''
        <xml><ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[FromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[event]]></MsgType>
        <Event><![CDATA[CLICK]]></Event>
        <EventKey><![CDATA[V_1001]]></EventKey>
        <Ticket><![CDATA[TICKET]]></Ticket>
        </xml>
        '''
        rv = self.client.post(signature_url, data=data)
        assert rv.status_code == 200, rv.status_code
        assert b'@event' in rv.data
        assert b'qrscene_123123' not in rv.data

    def test_link(self):
        data = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[link]]></MsgType>
        <Title><![CDATA[title]]></Title>
        <Description><![CDATA[desc]]></Description>
        <Url><![CDATA[url]]></Url>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        rv = self.client.post(signature_url, data=data)
        assert rv.status_code == 200, rv.status_code
        assert b'@link' in rv.data

    def test_voice(self):
        data = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1357290913</CreateTime>
        <MsgType><![CDATA[voice]]></MsgType>
        <MediaId><![CDATA[media_id]]></MediaId>
        <Format><![CDATA[Format]]></Format>
        <Recognition><![CDATA[腾讯微信团队]]></Recognition>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        rv = self.client.post(signature_url, data=data)
        assert rv.status_code == 200, rv.status_code
        assert b'@voice' in rv.data

    def test_fallback(self):
        data = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[location]]></MsgType>
        <Location_X>23.134521</Location_X>
        <Location_Y>113.358803</Location_Y>
        <Scale>20</Scale>
        <Label><![CDATA[city-name]]></Label>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        rv = self.client.post(signature_url, data=data)
        assert rv.status_code == 200, rv.status_code
        assert b'@*' in rv.data
