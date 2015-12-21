# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from celery import Celery

from celery_redis_sentinel import register


# has to be called before creating celery app
register()

app = Celery('tasks')
app.config_from_object('test_tasks.celeryconfig')


@app.task
def add(a, b):
    return a + b
