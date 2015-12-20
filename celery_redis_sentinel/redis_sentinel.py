# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import time

import six
from redis import ConnectionError, StrictRedis, TimeoutError
from redis.sentinel import Sentinel, SentinelConnectionPool


def get_redis_via_sentinel(db,
                           sentinels,
                           service_name,
                           socket_timeout=0.1,
                           redis_class=StrictRedis,
                           connection_pool_class=SentinelConnectionPool,
                           **kwargs):
    sentinel = Sentinel(
        sentinels,
        socket_timeout=socket_timeout,
    )
    return sentinel.master_for(
        service_name,
        socket_timeout=socket_timeout,
        db=db,
        redis_class=redis_class,
        connection_pool_class=connection_pool_class,
    )


def ensure_redis_call(f, *args, **kwargs):
    attempts = kwargs.pop('attempts', 5)

    for i in six.moves.range(attempts + 1):
        try:
            return f(*args, **kwargs)

        except (ConnectionError, TimeoutError) as e:
            if not attempts:
                raise
            else:
                wait = 2 ** i
                msg = (
                    'Will reattempt to execute {} with args={} kwargs={} '
                    'after {} seconds due to exception {}: {}'
                    ''.format(f, args, kwargs, wait, type(e).__name__, e)
                )
                print(msg)
                time.sleep(wait)


class EnsuredRedisMixin(object):
    def execute_command(self, *args, **options):
        return ensure_redis_call(super(EnsuredRedisMixin, self).execute_command, *args, **options)


class CelerySentinelConnectionPool(SentinelConnectionPool):
    def get_master_address(self):
        if self.master_address:
            return self.master_address
        return super(CelerySentinelConnectionPool, self).get_master_address()
