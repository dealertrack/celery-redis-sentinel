.. :changelog:

History
-------

Master (not yet on PyPI)
~~~~~~~~~~~~~~~~~~~~~~~~

In Progress

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
