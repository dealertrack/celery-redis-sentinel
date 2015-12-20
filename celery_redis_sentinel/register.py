# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from celery.backends import BACKEND_ALIASES
from kombu.transport import TRANSPORT_ALIASES

from .backend import RedisSentinelBackend
from .transport import SentinelTransport


def get_class_path(cls):
    """
    Get full Python dot-notation path for the given class

    Parameters
    ----------
    cls : type
        Class object

    Returns
    -------
    str
        Full Python dot-notation path of the class object.
        For example ``'celery_redis_sentinel.transport.SentinelTransport'``
        is returned for :class:`.SentinelTransport`.
    """
    return '{}.{}'.format(cls.__module__, cls.__name__)


def register(alias='redis-sentinel'):
    """
    Function to register sentinel transport and results backend
    into Celery's registry

    .. note::
        This function should be used before configuring celery app
        (e.g. via ``app.config_from_object()`` method)

    Parameters
    ----------
    alias : str, optional
        Alias name to use for the sentinel support.
        This is the host name which will be used in the celery config
        (e.g. ``redis-sentinel://localhost``).
        By default ``'redis-sentinel'`` is used.
    """
    # broker
    TRANSPORT_ALIASES[alias] = get_class_path(SentinelTransport)
    # result backend
    BACKEND_ALIASES[alias] = get_class_path(RedisSentinelBackend)


register()
