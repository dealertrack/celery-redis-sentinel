# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import time

import six
from redis import ConnectionError, StrictRedis, TimeoutError
from redis.sentinel import Sentinel, SentinelConnectionPool


def ensure_redis_call(f, *args, **kwargs):
    """
    Helper for executing any callable with retry-logic for when
    redis is timing out or is experiencing connection errors
    while redis sentinel failover is in progress.

    The retries are attempted in exponential ease-off (1, 2, 4, ... sec).

    .. note::
        This helper is a blocking function. It waits between retries
        in a blocking fashion.

    .. note::
        In between reties this function prints a helpful error message.
        The reason why ``print`` is used rather then lets say a logger
        is because celery has a configuration at what level ``stdout``
        should be logged as - ``CELERY_REDIRECT_STDOUTS_LEVEL``

    Parameters
    ----------
    f : callable
        The callable to be executed
    attempts : int, optional
        Number of attempts to make with exponential ease-off.
        By default ``5`` is used which means the the wait time
        before last retry will be 16 seconds. Also in that case
        total wait time is 31 seconds.
    args : tuple
        Any arguments to be passed to ``f`` when calling it
    kwargs : dict
        Any keyword arguments to be passed to ``f`` when calling it
    """
    attempts = kwargs.pop('attempts', 5)

    for i in six.moves.range(attempts + 1):
        try:
            return f(*args, **kwargs)

        except (ConnectionError, TimeoutError) as e:
            if i == attempts:
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
    """
    Mixin to be used for ``Redis`` or its subclasses which uses
    :func:`.ensure_redis_call` that each command is executed with
    retry logic.
    """

    def execute_command(self, *args, **options):
        """
        Same as super implementation except its wrapped with :meth:`ensure_redis_call`
        """
        return ensure_redis_call(super(EnsuredRedisMixin, self).execute_command, *args, **options)


class CelerySentinelConnectionPool(SentinelConnectionPool):
    """
    Redis Sentinel connection pool to be exclusively used with celery broker.

    **Why?**

    The reason we need this is because celery broker needs to completely loose
    connection with redis node in order to detect the connection failure
    hence release the sockets which it polls for redis responses.
    If the connection failure is not detected, celery will continue polling
    those sockets even though it will never receive any responses.
    That is precisely what happens when trying to use regular ``SentinelConnectionPool``
    with celery. That pool does a too-good of a job of failing over.
    What happens is that it would fail in celery callback trying to read
    the socket response (e.g. in ``Channel._brpop_read()``) which will
    disconnect the connection. Then on the next iteration of the celery
    event-loop (e.g. in ``Channel._brpop_start()``), the connection pool will
    find a new master and connect to it instead. That sounds like expected behavior
    except celery will not be aware of the change and hence continue polling on the
    previous socket which at that point will never receive any responses.
    The solution for this is to cripple the connection pool by not allowing
    it to switch masters. This will force it to keep trying to connect
    to the same master during failover which will obviously raise
    ``ConnectionError``. That is good because in that case celery
    will fail at the start of the event-loop iteration
    (e.g. in ``Channel._brpop_start()``) which celery picks up and will cause
    it to start reconnection logic to establish connection with broker again.
    When it does that a new ``Transport`` is instantiated with new ``Channel``
    which will create a new connection pool hence this crippled connection pool
    will not have any further impact on celery. It is just merely crippled
    in order for celery to notice connection errors with redis sentinel master node.
    """

    def get_master_address(self):
        """
        Crippled implementation of getting master address which only
        finds master address once after which point it returns same
        master address.

        Please refer to :class:`.CelerySentinelConnectionPool` for explanation
        why this is necessary.
        """
        if self.master_address:
            return self.master_address
        return super(CelerySentinelConnectionPool, self).get_master_address()


class ShortLivedStrictRedis(StrictRedis):
    """
    Custom ``StrictRedis`` which disconnects from redis after sending any command to redis.

    This is really useful in 2 scenarios:

    1. Connections made to redis server via firewall. When firewall closes the connection
       redis will not always notice that and so will not release the connection.
       As a result connections maxlimit eventually will be reached as more clients
       will be connecting.
    2. When the connection is used to make only very few queries. In sentinel case,
       sentinel is only used once to query the master address. There is no need
       to maintain the connection after master address is found and so the
       connection can be closed.
    """

    def execute_command(self, *args, **options):
        """
        In addition to executing redis command, this method closes the redis connection
        """
        try:
            return super(ShortLivedStrictRedis, self).execute_command(*args, **options)
        finally:
            self.connection_pool.disconnect()


class ShortLivedSentinel(Sentinel):
    """
    Custom ``Sentinel`` implementation which uses :py:class:`.ShortLivedStrictRedis`
    to query sentinel for information.

    That assures that sentinel connection is being opened when sentinel is being
    queried. After the query is successful, sentinel connection is closed.
    """

    def __init__(self, sentinels, *args, **kwargs):
        super(ShortLivedSentinel, self).__init__(sentinels, *args, **kwargs)
        self.sentinels = [
            ShortLivedStrictRedis(hostname, port, **self.sentinel_kwargs)
            for hostname, port in sentinels
        ]


def get_redis_via_sentinel(db,
                           sentinels,
                           service_name,
                           socket_timeout=0.1,
                           redis_class=StrictRedis,
                           sentinel_class=ShortLivedSentinel,
                           connection_pool_class=SentinelConnectionPool,
                           **kwargs):
    """
    Helper function for getting ``Redis`` instance via sentinel
    with sentinel connection pool

    Parameters
    ----------
    db : int, str
        Redis DB to which connection should be established to.
        In most cases this should be ``0`` DB.
    sentinels : list
        List of tuples of all sentinel nodes within the sentinel cluster.
        Each tuple should be of format ``(ip, port)``.
    service_name : str
        Name of the sentinel service_name.
    socket_timeout : float, optional
        Socket timeout value. By default ``0.1`` is used.
    redis_class : type, optional
        Class to be used for the ``Redis`` being returned.
        By default ``StrictRedis`` is used.
        This is useful since sometimes ``Redis`` needs to be used
        instead of ``StrictRedis``. For example ``Channel`` implementation
        in ``kombu`` uses ``Redis`` instead of ``StrictRedis``.
    sentinel_class : type, optional
        Class to be used for the ``Sentinel`` being used to return
        redis client. By default :py:class:`.ShortLivedSentinel` is used.
    connection_pool_class : type, optional
        Class to be used for the connection pool.
        By default ``SentinelConnectionPool`` is used.

    Returns
    -------
    Redis
        Connected ``Redis`` instance with sentinel connection pool
    """
    sentinel = sentinel_class(
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
