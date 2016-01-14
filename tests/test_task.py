# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import mock

from celery_redis_sentinel.task import EnsuredRedisTask


@mock.patch('celery_redis_sentinel.task.ensure_redis_call')
def test_apply_async(mock_ensure_redis_call):
    task = EnsuredRedisTask()

    actual = task.apply_async('foo', happy='rainbows')

    assert actual == mock_ensure_redis_call.return_value
    mock_ensure_redis_call.assert_called_once_with(mock.ANY, 'foo', happy='rainbows')
