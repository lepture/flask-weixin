Flask-Weixin
============

.. image:: https://travis-ci.org/lepture/flask-weixin.png?branch=master
        :target: https://travis-ci.org/lepture/flask-weixin
.. image:: https://coveralls.io/repos/lepture/flask-weixin/badge.png?branch=master
        :target: https://coveralls.io/r/lepture/flask-weixin

Flask-Weixin is the implementation for http://mp.weixin.qq.com/ with the
flavor of Flask. It can be used without Flask too.

Installation
------------

You can install Flask-Weixin with pip::

    $ pip install Flask-Weixin

Or, with setuptools easy_install in case you didn't have pip::

    $ easy_install Flask-Weixin


.. module:: flask_weixin

Get Started
-----------

Eager to get started? It is always the Flask way to create a new instance::

    from flask_weixin import Wexin

    weixin = Weixin(app)

Or pass the ``app`` later::

    wexin = Weixin()
    wexin.init_app(app)

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
