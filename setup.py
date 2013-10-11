#!/usr/bin/env python
# coding: utf-8


try:
    # python setup.py test
    import multiprocessing
except ImportError:
    pass

import re

with open('flask_weixin.py') as f:
    m = re.findall(r'__version__\s*=\s*\'(.*)\'', f.read())
    version = m[0]

from setuptools import setup

setup(
    name='Flask-Weixin',
    version=version,
    url='https://github.com/lepture/flask-weixin',
    author='Hsiaoming Yang',
    author_email='me@lepture.com',
    description='Weixin for Flask.',
    long_description=open('README.rst').read(),
    license='BSD',
    py_modules=['flask_weixin'],
    zip_safe=False,
    platforms='any',
    tests_require=['nose', 'Flask'],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
