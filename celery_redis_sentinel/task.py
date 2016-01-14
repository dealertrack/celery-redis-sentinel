# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from celery import Task

from .redis_sentinel import ensure_redis_call


class EnsuredRedisTask(Task):
    """
    Abstract celery task subclass which provides same functionality as
    :py:class:`ensure_redis_call <celery_redis_sentinel.redis_sentinel.ensure_redis_call>`
    except it is added at task definition time instead of during task schedule call.

    This task subclass can be provided during task definition
    by using ``base`` parameter.

    Examples
    --------

    ::

        @app.task(base=EnsuredRedisTask)
        def add(a, b):
            return a + b
    """
    abstract = True

    def apply_async(self, *args, **kwargs):
        _super = super(EnsuredRedisTask, self).apply_async
        return ensure_redis_call(_super, *args, **kwargs)
