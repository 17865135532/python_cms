#!/usr/bin/python
from celery.utils.log import get_task_logger

from app.jobs.celery_app import celery_app
from application import app


app.app_context().push()
logger = get_task_logger(__name__)


@celery_app.task()
def demo():
    pass
