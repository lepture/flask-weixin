Flask-Weixin
============

Flask-Weixin is the implementation for http://mp.weixin.qq.com/ with the
flavor of Flask. It can be used without Flask too.

.. image:: https://img.shields.io/pypi/wheel/flask-weixin.svg?style=flat
   :target: https://pypi.python.org/pypi/Flask-Weixin/
   :alt: Wheel Status
.. image:: https://img.shields.io/pypi/v/flask-weixin.svg?style=flat
   :target: https://pypi.python.org/pypi/Flask-Weixin/
   :alt: Latest Version
.. image:: https://travis-ci.org/lepture/flask-weixin.svg?branch=master
   :target: https://travis-ci.org/lepture/flask-weixin
   :alt: Travis CI
.. image:: https://coveralls.io/repos/lepture/flask-weixin/badge.svg?branch=master
   :target: https://coveralls.io/r/lepture/flask-weixin
   :alt: Coverage Status


Installation
------------

You can install Flask-Weixin with pip::

    $ pip install Flask-Weixin

Or, with setuptools easy_install in case you didn't have pip::

    $ easy_install Flask-Weixin


Getting Started
---------------

Eager to get started? It is always the Flask way to create a new instance::

    from flask_weixin import Weixin

    weixin = Weixin(app)

Or pass the ``app`` later::

    weixin = Weixin()
    weixin.init_app(app)

However, you need to configure before using it, here is the configuration
list:

* WEIXIN_TOKEN: this is required
* WEIXIN_SENDER: a default sender, optional
* WEIXIN_EXPIRES_IN: not expires by default

For Flask user, it is suggested that you use the default view function::

    app.add_url_rule('/', view_func=weixin.view_func)

    @weixin.register('*')
    def reply(**kwargs):
        username = kwargs.get('sender')
        sender = kwargs.get('receiver')
        content = kwargs.get('content')
        return weixin.reply(
            username, sender=sender, content=content
        )

The example above will reply anything the user sent.

Or you can register a function to handle a specific keyword::

    @weixin.register('help')
    def reply_help(**kwargs):
        ...

this function will be used to handle text message ``help``.

There are more ways to match messages to handlers::

    @weixin.register(type='event', event='subscribe')
    def send_welcome(**kwargs):
        username = kwargs.get('sender')
        sender = kwargs.get('receiver')
        return weixin.reply(username, sender=sender, content='Thanks for follow!')

this function will send a message to new followers.


Message Types
-------------

Every message from weixin has these information:

* id: message ID
* receiver: which is ``ToUserName`` in the official documentation
* sender: which is ``FromUserName`` in the official documentation
* type: message type
* timestamp: message timestamp

Text Type
~~~~~~~~~

Text type has an extra data: ``content``.


Image Type
~~~~~~~~~~

Image type has an extra data: ``picurl``.


Link Type
~~~~~~~~~

Link type has extra data:

* title: article title
* description: article description
* url: original url of the article


Location Type
~~~~~~~~~~~~~

Location type has extra data:

* location_x
* location_y
* scale
* label


Event Type
~~~~~~~~~~

Event type has extra data:

* event
* event_key
* latitude
* longitude
* precision

Voice Type
~~~~~~~~~~

Event type has extra data:

* media_id
* format
* recognition
