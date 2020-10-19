#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :decorators_self.py
import logging
import datetime
import time
import functools
from flask import request

from app.utils import auth
from app.configs import CONFIG
from app.dao.redis_dao import RedisInstance

logger = logging.getLogger(__name__)

redis = RedisInstance()

# 把字符串转成datetime
def string_toDatetime(string, format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(string, format)

def login_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        token = request.headers.get('token')
        sign = request.headers.get('sign')
        timestamp = request.headers.get('timestamp')
        if 'appid' not in auth.certify_token(token):
            return auth.certify_token(token)
        server_sign = auth.create_sign(token=token, timestamp=timestamp, values=request.values)
        if sign != server_sign:
            return {
                'return_code': 401,
                'return_msg': f'sign is error.'
            }
        try:
            # diff_time = datetime.datetime.now() - datetime.datetime.fromtimestamp(float(timestamp)/1000)
            # if diff_time.seconds > CONFIG.SIGN_TIMEOUT_TIME:
            if time.time() - float(timestamp) > CONFIG.SIGN_TIMEOUT_TIME:
                return {
                    'return_code': 401,
                    'return_msg': f'sign is invalid.'
                }

        except Exception as e:
            logger.error("", exc_info=e.args)
        return func(*args, **kwargs)

    return inner


def check_allow_ip(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            if request.remote_addr not in CONFIG.ALLOW_IP:
                return {
                    'return_code': 401,
                    'return_msg': f'No access rights, contact management'
                }
        except Exception as e:
            logger.error("", exc_info=e.args)
        return func(*args, **kwargs)
    return inner
