.. :changelog:

History
-------

Master (not yet on PyPI)
~~~~~~~~~~~~~~~~~~~~~~~~

In Progress

0.3 (2016-05-03)
~~~~~~~~~~~~~~~~

* **New**: Addition of ``ShortLivedStrictRedis`` and ``ShortLivedSentinel``.
  Both of them use short-lived connections which disconnect from redis
  as soon as the query to redis is complete.
* **Fixed**: All sentinel connections are now created via ``ShortLivedSentinel``.
  This fixes an issue when sentinel would reach its max connections limit
  since all celery workers would always be connected to sentinel.
  That is not necessary since sentinel is queried very rarely for the current
  master connection details.
  In addition this is useful when Redis Sentinel is used behind a firewall
  since sentinel would not notice when firewall would close the connections
  and so would not release them.

0.2 (2016-01-14)
~~~~~~~~~~~~~~~~

* **New**: Added ``EnsuredRedisTask`` which allows to ensure tasks are scheduled
  via an abstract base task class in task definition rather then explicitly using
  ``ensure_redis_call`` while calling the task::

      @app.task(base=EnsuredRedisTask)
      def foo(): pass

0.1 (2016-01-13)
~~~~~~~~~~~~~~~~

* First release
