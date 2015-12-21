# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import mock

from celery_redis_sentinel.backend import RedisSentinelBackend

from test_tasks.celeryconfig import BROKER_TRANSPORT_OPTIONS
from test_tasks.tasks import app


class TestRedisSentinelBackend(object):
    def test_init(self):
        backend = RedisSentinelBackend(transport_options=None, app=app)

        assert backend.transport_options == BROKER_TRANSPORT_OPTIONS
        assert backend.sentinels == BROKER_TRANSPORT_OPTIONS['sentinels']
        assert backend.service_name == BROKER_TRANSPORT_OPTIONS['service_name']
        assert backend.socket_timeout == BROKER_TRANSPORT_OPTIONS['socket_timeout']

    @mock.patch('celery_redis_sentinel.backend.get_redis_via_sentinel')
    def test_client(self, mock_get_redis_via_sentinel):
        backend = RedisSentinelBackend(transport_options=None, app=app)

        client = backend.client

        assert client == mock_get_redis_via_sentinel.return_value
        mock_get_redis_via_sentinel.assert_called_once_with(
            db=0,
            redis_class=mock.ANY,
            sentinels=[('192.168.1.1', 26379),
                       ('192.168.1.2', 26379),
                       ('192.168.1.3', 26379)],
            service_name='master',
            socket_timeout=1,
            host=mock.ANY,
            max_connections=mock.ANY,
            password=mock.ANY,
            port=mock.ANY,
        )
