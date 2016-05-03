# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import mock
import pytest
from redis import ConnectionError
from redis.client import StrictRedis
from redis.sentinel import SentinelConnectionPool

from celery_redis_sentinel.redis_sentinel import (
    CelerySentinelConnectionPool,
    EnsuredRedisMixin,
    ShortLivedSentinel,
    ShortLivedStrictRedis,
    ensure_redis_call,
    get_redis_via_sentinel,
)


class Bar(object):
    def execute_command(self, *args, **kwargs):
        return 'foo'


class Foo(EnsuredRedisMixin, Bar):
    pass


def test_get_redis_via_sentinel():
    mock_sentinel = mock.Mock()

    result = get_redis_via_sentinel(
        db=0,
        sentinels=['foo', 'bar'],
        service_name='master',
        sentinel_class=mock_sentinel,
    )

    assert result == mock_sentinel.return_value.master_for.return_value


@mock.patch('time.sleep')
def test_ensure_redis_call(mock_sleep):
    m = mock.Mock()
    m.side_effect = ConnectionError

    with pytest.raises(ConnectionError):
        ensure_redis_call(m, 1, foo='bar', attempts=5)

    mock_sleep.assert_has_calls([
        mock.call(1),
        mock.call(2),
        mock.call(4),
        mock.call(8),
        mock.call(16),
    ])


class TestEnsuredRedisMixin(object):
    @mock.patch('celery_redis_sentinel.redis_sentinel.ensure_redis_call')
    def test_execute_command(self, mock_ensure_redis_call):
        f = Foo()

        actual = f.execute_command('lrange', 0, -1)

        assert actual == mock_ensure_redis_call.return_value
        mock_ensure_redis_call.assert_called_once_with(
            mock.ANY, 'lrange', 0, -1,
        )


class TestCelerySentinelConnectionPool(object):
    @mock.patch.object(SentinelConnectionPool, 'get_master_address')
    def test_get_master_address_no_existing_master(self, mock_super_get_master_address):
        p = CelerySentinelConnectionPool('master', None)

        assert p.get_master_address() == mock_super_get_master_address.return_value

    @mock.patch.object(SentinelConnectionPool, 'get_master_address')
    def test_get_master_address_with_existing_master(self, mock_super_get_master_address):
        p = CelerySentinelConnectionPool('master', None)
        p.master_address = 'foo'

        assert p.get_master_address() == 'foo'
        assert not mock_super_get_master_address.called


class TestShortLivedStrictRedis(object):
    @mock.patch.object(StrictRedis, 'execute_command')
    def test_execute_command(self, mock_execute_command):
        r = ShortLivedStrictRedis()
        r.connection_pool = mock.Mock()

        result = r.execute_command('get', 'foo')

        assert result == mock_execute_command.return_value
        mock_execute_command.assert_called_once_with('get', 'foo')
        r.connection_pool.disconnect.assert_called_once_with()


class TestShortLivedSentinel(object):
    def test_init(self):
        sentinel = ShortLivedSentinel([('localhost', '1'), ('localhost', '2')])

        for s in sentinel.sentinels:
            assert isinstance(s, ShortLivedStrictRedis)
