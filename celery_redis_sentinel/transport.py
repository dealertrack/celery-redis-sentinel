# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from kombu.transport.redis import Channel, Transport
from kombu.utils import cached_property

from .redis_sentinel import CelerySentinelConnectionPool, get_redis_via_sentinel


class SentinelChannel(Channel):
    """
    Redis Channel for interacting with Redis Sentinel

    .. note::
        In order to correctly configure the sentinel,
        this channel expects specific broker transport options to be
        provided via ``BROKER_TRANSPORT_OPTIONS``.
        Here is are sample transport options::

            BROKER_TRANSPORT_OPTIONS = {
                'sentinels': [('192.168.1.1', 26379),
                              ('192.168.1.2', 26379),
                              ('192.168.1.3', 26379)],
                'service_name': 'master',
                'socket_timeout': 0.1,
            }
    """
    from_transport_options = Channel.from_transport_options + (
        'sentinels',
        'service_name',
        'socket_timeout',
    )

    @cached_property
    def sentinel_pool(self):
        """
        Cached property for getting connection pool to redis sentinel.

        In addition to returning connection pool, this property
        changes the ``Transport`` connection details to match the
        connected master so that celery can correctly log to which
        node it is actually connected.

        Returns
        -------
        CelerySentinelConnectionPool
            Connection pool instance connected to redis sentinel
        """
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
    """
    Redis transport with support for Redis Sentinel.
    """
    Channel = SentinelChannel
