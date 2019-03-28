# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""
import logging
import uuid

from django.template import defaultfilters as filters

from omaha_server.celery import app
from omaha_server.utils import add_extra_to_log_message
from omaha import statistics
from omaha.parser import parse_request
from omaha.limitation import (
    delete_older_than,
    delete_size_is_exceeded,
    delete_duplicate_crashes,
    monitoring_size,
    handle_dangling_files
)
from omaha.models import Version
from sparkle.models import SparkleVersion
from crash.models import Crash, Symbols
from feedback.models import Feedback


@app.task(ignore_result=True)
def collect_statistics(request, ip=None):
    statistics.collect_statistics(parse_request(bytes(bytearray(request, encoding='utf-8'))), ip=ip)


@app.task(name='tasks.auto_delete_older_then', ignore_result=True)
def auto_delete_older_than():
    logger = logging.getLogger('limitation')
    model_list = [
        ('crash', 'Crash'),
        ('feedback', 'Feedback')
    ]
    for model in model_list:
        result = delete_older_than(*model)
        if result.get('count', 0):
            log_id = str(uuid.uuid4())
            extra = dict(
                log_id=log_id,
                meta=True,
                count=result['count'],
                size=filters.filesizeformat(result['size']).replace(u'\xa0', u' '),
                model=model[1],
                reason='old',
            )
            logger.info(add_extra_to_log_message('Automatic cleanup', extra=extra))
            for element in result['elements']:
                element.update({"log_id": log_id, "%s_id" % (model[1]): element.pop('id')})
                logger.info(add_extra_to_log_message('Automatic cleanup element', extra=element))


@app.task(name='tasks.auto_delete_size_is_exceeded', ignore_result=True)
def auto_delete_size_is_exceeded():
    logger = logging.getLogger('limitation')
    model_list = [
        ('crash', 'Crash'),
        ('feedback', 'Feedback')
    ]
    for model in model_list:
        result = delete_size_is_exceeded(*model)
        if result.get('count', 0):
            log_id = str(uuid.uuid4())
            extra = dict(
                log_id=log_id,
                meta=True,
                count=result['count'],
                size=filters.filesizeformat(result['size']).replace(u'\xa0', u' '),
                model=model[1],
                reason='size_is_exceeded'
            )
            logger.info(add_extra_to_log_message('Automatic cleanup', extra=extra))
            for element in result['elements']:
                element.update({"log_id": log_id, "%s_id" % (model[1]): element.pop('id')})
                logger.info(add_extra_to_log_message('Automatic cleanup element', extra=element))


@app.task(name='tasks.auto_delete_duplicate_crashes', ignore_result=True)
def auto_delete_duplicate_crashes():
    logger = logging.getLogger('limitation')
    result = delete_duplicate_crashes()
    if result.get('count', 0):
        log_id = str(uuid.uuid4())
        extra = dict(
            log_id=log_id,
            meta=True,
            count=result['count'],
            size=filters.filesizeformat(result['size']).replace(u'\xa0', u' '),
            reason='duplicated',
            model='Crash',
         )
        logger.info(add_extra_to_log_message('Automatic cleanup', extra=extra))
        for element in result['elements']:
            element.update({"log_id": log_id, "Crash_id": element.pop('id')})
            logger.info(add_extra_to_log_message('Automatic cleanup element', extra=element))


@app.task(name='tasks.deferred_manual_cleanup')
def deferred_manual_cleanup(model, limit_size=None, limit_days=None, limit_duplicated=None):
    logger = logging.getLogger('limitation')
    full_result = dict(count=0, size=0, elements=[])
    if limit_duplicated:
        result = delete_duplicate_crashes(limit=limit_duplicated)
        if result.get('count', 0):
            full_result['count'] += result['count']
            full_result['size'] += result['size']
            full_result['elements'] += result['elements']

    if limit_days:
        result = delete_older_than(*model, limit=limit_days)
        if result.get('count', 0):
            full_result['count'] += result['count']
            full_result['size'] += result['size']
            full_result['elements'] += result['elements']

    if limit_size:
        result = delete_size_is_exceeded(*model, limit=limit_size)
        if result.get('count', 0):
            full_result['count'] += result['count']
            full_result['size'] += result['size']
            full_result['elements'] += result['elements']

    log_id = str(uuid.uuid4())
    extra = dict(
        log_id=log_id,
        meta=True,
        count=full_result['count'],
        size=filters.filesizeformat(full_result['size']).replace(u'\xa0', u' '),
        model=model[1],
        limit_duplicated=limit_duplicated,
        limit_size=limit_size,
        limit_days=limit_days,
        reason='manual'
    )
    logger.info(add_extra_to_log_message('Manual cleanup', extra=extra))
    for element in full_result['elements']:
        element.update({"log_id": log_id, "%s_id" % (model[1]): element.pop('id')})
        logger.info(add_extra_to_log_message('Manual cleanup element', extra=element))


@app.task(name='tasks.auto_monitoring_size', ignore_result=True)
def auto_monitoring_size():
    monitoring_size()


def get_prefix(model_name):
    model_path_prefix = {
        Crash: ('minidump', 'minidump_archive'),
        Feedback: ('blackbox', 'system_logs', 'feedback_attach', 'screenshot'),
        Symbols: ('symbols',),
        Version: ('build',),
        SparkleVersion: ('sparkle',)
    }
    return model_path_prefix[model_name]


@app.task(name='tasks.auto_delete_dangling_files', ignore_result=True)
def auto_delete_dangling_files():
    logger = logging.getLogger('limitation')
    model_kwargs_list = [
        {'model': Crash, 'file_fields': ('upload_file_minidump', 'archive')},
        {'model': Feedback, 'file_fields': ('blackbox', 'system_logs', 'attached_file', 'screenshot')},
        {'model': Symbols, 'file_fields': ('file', )},
        {'model': Version, 'file_fields': ('file', )},
        {'model': SparkleVersion, 'file_fields': ('file', )}
    ]
    for model_kwargs in model_kwargs_list:
        result = handle_dangling_files(
            prefix=get_prefix(model_kwargs['model']),
            **model_kwargs
        )
        if result['mark'] == 'db':
            logger.info('Dangling files detected in db [%d], files path: %s' % (result['count'], result['data']))
        elif result['mark'] == 's3':
            logger.info('Dangling files deleted from s3 [%d], files path: %s' % (result['count'], result['data']))
        else:
            logger.info('Dangling files not detected')
