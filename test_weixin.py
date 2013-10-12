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
        rv = self.client.post('/')
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
        rv = self.client.post('/', data=text)
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
        rv = self.client.post('/', data=text)
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
        rv = self.client.post('/', data=text)
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
        rv = self.client.post('/', data=text)
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
        rv = self.client.post('/', data=text)
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
        rv = self.client.post('/', data=text)
        assert b'help me' in rv.data

    def test_news(self):
        text = self.__doc__ % 'news'
        rv = self.client.post('/', data=text)
        assert b'Hello News' in rv.data

    def test_music(self):
        text = self.__doc__ % 'music'
        rv = self.client.post('/', data=text)
        assert b'weixin music' in rv.data

    def test_show(self):
        text = self.__doc__ % 'show'
        rv = self.client.post('/', data=text)
        assert b'show reply' in rv.data

    @raises(RuntimeError)
    def test_no_sender(self):
        @self.weixin.register('send')
        def print_send(*args, **kwargs):
            username = kwargs.get('sender')
            return self.weixin.reply(
                username, sender=None, content='send reply'
            )

        text = self.__doc__ % 'send'
        self.client.post('/', data=text)
