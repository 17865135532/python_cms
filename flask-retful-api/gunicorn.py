# coding: utf-8
import gevent.monkey


gevent.monkey.patch_all()

bind = '0.0.0.0:8006'
workers = 4
backlog = 2048
worker_class = 'gunicorn.workers.ggevent.GeventWorker'
x_forwarded_for_header = 'X-FORWARDED-FOR'
proc_name = 'gunicorn.proc'
pidfile = 'logs/gunicorn.pid'
