# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals


CELERY_IMPORTS = ("test_tasks.tasks",)

BROKER_URL = 'redis-sentinel://redis-sentinel:26379/0'
BROKER_TRANSPORT_OPTIONS = {
    'sentinels': [('192.168.1.1', 26379),
                  ('192.168.1.2', 26379),
                  ('192.168.1.3', 26379)],
    'service_name': 'master',
    'socket_timeout': 1,
}

CELERY_RESULT_BACKEND = 'redis-sentinel://redis-sentinel:26379/1'
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = BROKER_TRANSPORT_OPTIONS

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_ENABLE_UTC = True

CELERY_REDIRECT_STDOUTS_LEVEL = 'INFO'
