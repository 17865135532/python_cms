#!/usr/bin/python
# -*- coding:utf-8 -*-

from app.configs import CONFIG
from celery.schedules import crontab


broker_url = BROKER_URL = CONFIG.CELERY_BROKER_URL
result_backend = CELERY_RESULT_BACKEND = CONFIG.CELERY_BACKEND_URL

result_serializer = CELERY_RESULT_SERIALIZER = 'json'
timezone = CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True

beat_schedule = CELERYBEAT_SCHEDULE = {
    'demo': {
        'task': 'app.jobs.tasks.demo',
        'schedule': crontab(0, 0, day_of_month='1')
    },
}
