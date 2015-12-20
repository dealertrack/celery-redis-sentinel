# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from celery.backends.redis import RedisBackend
from kombu.utils import cached_property
from redis import Redis

from .redis_sentinel import EnsuredRedisMixin, get_redis_via_sentinel


class RedisSentinelBackend(RedisBackend):

    def __init__(self, transport_options=None, *args, **kwargs):
        super(RedisSentinelBackend, self).__init__(*args, **kwargs)

        _get = self.app.conf.get
        self.transport_options = transport_options or _get('CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS') or {}
        self.sentinels = self.transport_options['sentinels']
        self.service_name = self.transport_options['service_name']
        self.socket_timeout = self.transport_options.get('socket_timeout', 0.1)

    @cached_property
    def client(self):
        """
        Custom implementation for getting redis client.

        This property uses our dtplatform's ```get_central_redis_session`` to get
        the redis sentinel session.
        """
        params = self.connparams
        params.update({
            'sentinels': self.sentinels,
            'service_name': self.service_name,
            'socket_timeout': self.socket_timeout,
        })
        return get_redis_via_sentinel(
            redis_class=type(str('Redis'), (EnsuredRedisMixin, Redis), {}),
            **params
        )
