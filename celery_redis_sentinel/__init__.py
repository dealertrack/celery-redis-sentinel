# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals


__author__ = 'Miroslav Shubernetskiy'
__version__ = '0.3.0'

try:
    from .backend import RedisSentinelBackend  # noqa
    from .register import register  # noqa
    from .transport import SentinelTransport  # noqa
except ImportError:
    # probably importing in setup.py so make these optional imports
    pass
