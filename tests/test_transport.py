# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import mock
from kombu import Connection
from redis import StrictRedis

from celery_redis_sentinel.redis_sentinel import CelerySentinelConnectionPool
from celery_redis_sentinel.transport import SentinelChannel, SentinelTransport

from test_tasks.celeryconfig import BROKER_TRANSPORT_OPTIONS
from test_tasks.tasks import app


class TestSentinelChannel(object):
    @mock.patch.object(StrictRedis, 'execute_command')  # needed since channel does client.info in __init__
    @mock.patch('celery_redis_sentinel.transport.get_redis_via_sentinel')
    def test_sentinel_pool(self, mock_get_redis_via_sentinel, mock_execute_command):
        connection = Connection()
        connection.transport_options = BROKER_TRANSPORT_OPTIONS
        transport = SentinelTransport(app=app, client=connection)

        mock_get_redis_via_sentinel.return_value.connection_pool.get_master_address.return_value = (
            '192.168.1.128', '6379',
        )

        channel = SentinelChannel(connection=transport)
        channel.sentinels = BROKER_TRANSPORT_OPTIONS['sentinels']
        channel.service_name = BROKER_TRANSPORT_OPTIONS['service_name']
        channel.socket_timeout = BROKER_TRANSPORT_OPTIONS['socket_timeout']

        del channel.sentinel_pool
        mock_get_redis_via_sentinel.reset_mock()

        pool = channel.sentinel_pool

        assert pool == mock_get_redis_via_sentinel.return_value.connection_pool
        mock_get_redis_via_sentinel.assert_called_once_with(
            host=mock.ANY,
            max_connections=mock.ANY,
            password=mock.ANY,
            port=mock.ANY,
            connection_pool_class=CelerySentinelConnectionPool,
            redis_class=channel.Client,
            db=0,
            sentinels=[('192.168.1.1', 26379),
                       ('192.168.1.2', 26379),
                       ('192.168.1.3', 26379)],
            service_name='master',
            socket_timeout=1,
            socket_connect_timeout=mock.ANY,
            socket_keepalive=mock.ANY,
            socket_keepalive_options=mock.ANY,
        )


class TestSentinelTransport(object):
    def test_channel(self):
        assert SentinelTransport.Channel is SentinelChannel
