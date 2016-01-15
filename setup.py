#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import os
from itertools import chain

from setuptools import find_packages, setup

from celery_redis_sentinel import __author__, __version__


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), 'rb') as fid:
        return fid.read().decode('utf-8')


def remove_section_from_rst(text, section):
    lines = text.splitlines()

    section_line = lines.index(section)

    separator = lines[section_line + 1]
    assert set(separator) == {separator[0]}

    next_section_line = next(
        i for i, l in enumerate(lines[section_line + 2:])
        if set(l) == {separator[0]}
    )

    return '\n'.join(chain(
        lines[:section_line - 1],
        lines[section_line + next_section_line:]
    ))


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

long_description = remove_section_from_rst(
    '\n\n'.join([readme, history, authors, licence]),
    'Master (not yet on PyPI)'
)

setup(
    name='celery-redis-sentinel',
    version=__version__,
    author=__author__,
    description='Celery broker and results backend implementation for Redis Sentinel',
    long_description=long_description,
    url='https://github.com/dealertrack/celery-redis-sentinel',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*', 'test_tasks', 'test_tasks.*']),
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
