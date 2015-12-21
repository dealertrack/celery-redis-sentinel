# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import mock
from celery.backends import BACKEND_ALIASES
from kombu.transport import TRANSPORT_ALIASES

from celery_redis_sentinel.register import get_class_path, register


class Foo(object):
    pass


def test_get_class_path():
    assert get_class_path(Foo) == __name__ + '.Foo'


@mock.patch.dict(BACKEND_ALIASES, {})
@mock.patch.dict(TRANSPORT_ALIASES, {})
def test_register():
    assert 'foo' not in BACKEND_ALIASES
    assert 'foo' not in TRANSPORT_ALIASES

    register('foo')

    assert 'foo' in BACKEND_ALIASES
    assert 'foo' in TRANSPORT_ALIASES
    assert BACKEND_ALIASES['foo'] == 'celery_redis_sentinel.backend.RedisSentinelBackend'
    assert TRANSPORT_ALIASES['foo'] == 'celery_redis_sentinel.transport.SentinelTransport'
