#!/usr/bin/python
# -*- coding:utf-8 -*-
from logging.config import dictConfig

from celery import Celery

from app.configs import CONFIG


dictConfig(CONFIG.LOGGING_CONFIG)
celery_app = Celery(
    'task',
    include=['app.jobs.tasks']
)
celery_app.config_from_object('app.jobs.celery_config')
