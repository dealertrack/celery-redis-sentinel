=====================
Celery Redis Sentinel
=====================

.. image:: https://badge.fury.io/py/celery_redis_sentinel.svg
    :target: http://badge.fury.io/py/celery-redis-sentinel

.. image:: https://travis-ci.org/dealertrack/celery_redis_sentinel.svg?branch=master
        :target: https://travis-ci.org/dealertrack/celery-redis-sentinel

Celery broker and results backend implementation for
`Redis Sentinel <http://redis.io/topics/sentinel>`_

* Free software: MIT license
* GitHub: https://github.com/dealertrack/celery-redis-sentinel
* Documentation: https://celery-redis-sentinel.readthedocs.org.

Why?
----

`Redis <http://redis.io/>`_ is a pretty awesome in-memory key-value data-store.
Being in-memory makes it wickedly fast however at a cost of no-persistence.
In business-critical applications (you know, which make company money) that makes
stand-alone redis deployment non-practical. This is where
`Redis Sentinel <http://redis.io/topics/sentinel>`_ comes in.
It provides scalability and high availability to Redis 2.X
(Redis 3.X comes with native-clustering which is different from Sentinel).
As a result, Redis becomes a viable solution for solving some of business needs.
As you can imagine from the project title, one use-case is using Redis Sentinel with
`celery <http://www.celeryproject.org/>`_.
Unfortunately celery does not support Redis Sentinel by default hence this
library which aims to provide non-official Redis Sentinel support as **both**
celery broker and results backend.

Installing
----------

Installation is super easy with ``pip``::

    $ pip install celery-redis-sentinel

Usage
-----

Using this library is pretty simple. All you need to do is configure celery
to use Redis Sentinel for broker and/or results backend. That is done
with a couple of settings::

    # celeryconfig.py
    BROKER_URL = 'redis-sentinel://redis-sentinel:26379/0'
    BROKER_TRANSPORT_OPTIONS = {
        'sentinels': [('192.168.1.1', 26379),
                      ('192.168.1.2', 26379),
                      ('192.168.1.3', 26379)],
        'service_name': 'master',
        'socket_timeout': 0.1,
    }

    CELERY_RESULT_BACKEND = 'redis-sentinel://redis-sentinel:26379/1'
    CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = BROKER_TRANSPORT_OPTIONS

Some notes about the configuration:

* note the use of ``redis-sentinel`` schema within the URL for broker and results
  backend. In order to use that schema, which is not shipped with celery, where you create
  your celery application you **must** first need to register sentinel support::

      # tasks.py
      from celery_redis_sentinel import register

      # has to be called before creating celery app
      register()

      app = Celery('tasks')
* hostname and port are ignored within the actual URL. Sentinel uses transport options
  ``sentinels`` setting to create a ``Sentinel()`` instead of configuration URL.

Scheduling During Failover
--------------------------

Some considerations while using Redis Sentinel as a celery broker. While the failover
is in progress, no tasks can be scheduled. Trying to schedule a task will either
raise ``Timeout`` or ``ConnectionError``. That is because other sentinel nodes
within the cluster, depending on the configuration, have a timeout until they elect
a new master. During that time, trying to schedule a task will attempt to store
it in now-invalid master node hence the exception. If that is unacceptable within
your application, this library comes with a small wrapper which allows to trigger
tasks which will block the scheduling until new master will be elected::

    from celery_redis_sentinel.redis_sentinel import ensure_redis_call
    from tasks import add

    # this will blow up during failover
    add.delay(1, 2)
    # this will keep retrying until it succeeds
    ensure_redis_call(add.delay, 1, 2)
