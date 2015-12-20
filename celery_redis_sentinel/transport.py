# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from kombu.transport.redis import Channel, Transport
from kombu.utils import cached_property

from .redis_sentinel import CelerySentinelConnectionPool, get_redis_via_sentinel


class SentinelChannel(Channel):
    from_transport_options = Channel.from_transport_options + (
        'sentinels',
        'service_name',
        'socket_timeout',
    )

    @cached_property
    def sentinel_pool(self):
        params = self._connparams()
        params.update({
            'sentinels': self.sentinels,
            'service_name': self.service_name,
            'socket_timeout': self.socket_timeout,
        })
        sentinel = get_redis_via_sentinel(
            redis_class=self.Client,
            connection_pool_class=CelerySentinelConnectionPool,
            **params
        )
        pool = sentinel.connection_pool
        hostname, port = pool.get_master_address()

        # update connection details so that celery correctly logs
        # where it connects
        self.connection.client.hostname = hostname
        self.connection.client.port = port

        return pool

    def _get_pool(self, *args, **kwargs):
        return self.sentinel_pool


class SentinelTransport(Transport):
    Channel = SentinelChannel
