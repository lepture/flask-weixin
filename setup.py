#!/usr/bin/env python
# coding: utf-8


try:
    # python setup.py test
    import multiprocessing
except ImportError:
    pass

import os
import re

from setuptools import setup


def fread(fname):
    filepath = os.path.join(os.path.dirname(__file__), fname)
    with open(filepath) as f:
        return f.read()


content = fread('flask_weixin.py')
m = re.findall(r'__version__\s*=\s*\'(.*)\'', content)
version = m[0]


setup(
    name='Flask-Weixin',
    version=version,
    url='https://github.com/lepture/flask-weixin',
    author='Hsiaoming Yang',
    author_email='me@lepture.com',
    description='Weixin for Flask.',
    long_description=fread('README.rst'),
    license='BSD',
    py_modules=['flask_weixin'],
    zip_safe=False,
    platforms='any',
    tests_require=['nose', 'Flask'],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
