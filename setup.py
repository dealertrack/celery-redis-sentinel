#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import os

from setuptools import find_packages, setup

from celery_redis_sentinel import __author__, __version__


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), 'rb') as fid:
        return fid.read().decode('utf-8')


authors = read('AUTHORS.rst')
history = read('HISTORY.rst').replace('.. :changelog:', '')
licence = read('LICENSE.rst')
readme = read('README.rst')

requirements = read('requirements.txt').splitlines() + [
    'setuptools',
]

test_requirements = (
    read('requirements.txt').splitlines() +
    read('requirements-dev.txt').splitlines()[1:]
)

setup(
    name='celery-redis-sentinel',
    version=__version__,
    author=__author__,
    description='Celery broker and results backend implementation for Redis Sentinel',
    long_description='\n\n'.join([readme, history, authors, licence]),
    url='https://github.com/dealertrack/celery-redis-sentinel',
    license='MIT',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements,
    keywords=' '.join([
        'celery',
        'redis',
        'sentinel',
        'broker',
        'results',
    ]),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 2 - Pre-Alpha',
    ],
)
