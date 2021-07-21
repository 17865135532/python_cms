# coding: utf-8
import gevent.monkey

from app.configs import CONFIG


LOG_PATH = CONFIG.LOG_PATH
gevent.monkey.patch_all()

bind = '0.0.0.0:5000'
workers = 4
backlog = 2048
worker_class = 'gunicorn.workers.ggevent.GeventWorker'
x_forwarded_for_header = 'X-FORWARDED-FOR'
proc_name = 'gunicorn.proc'
pidfile = f'{LOG_PATH}/gunicorn.pid'
