# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from celery import Task

from .redis_sentinel import ensure_redis_call


class EnsuredRedisTask(Task):
    abstract = True

    def apply_async(self, *args, **kwargs):
        _super = super(EnsuredRedisTask, self).apply_async
        return ensure_redis_call(_super, *args, **kwargs)
