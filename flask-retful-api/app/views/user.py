#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :user.py
# @Time      :2020/9/17 上午10:57
import logging
import time
import os
import datetime

import werkzeug
from flask_restx import Resource, Namespace
from flask_restx.reqparse import RequestParser

from app.utils import auth
from app.dao.redis_dao import RedisInstance
from app.utils.decorators import check_allow_ip

user_api = Namespace('', escription='用户相关 appid')

__all__ = ['user_api']

logger = logging.getLogger(__name__)


@user_api.route('/appid')
class UserAppKey(Resource):
    logger = logger.getChild('UserAppKey')

    creation_parser = RequestParser()
    creation_parser.add_argument(
        'visit_limit', location='form', type=int,
        help='appid 请求次数'
    )
    creation_parser.add_argument(
        'uri_list', location='form', type=int,
        help='appid ip地址绑定'
    )

    @check_allow_ip
    def post(self):
        try:
            args = self.creation_parser.parse_args()
        except werkzeug.exceptions.BadRequest as e:
            self.logger.warning(f'{dir(e), str(e), e.args, e.data, e.name, e.description}')
            return_msg = '\n'.join([f'{v}: {k}.' for k, v in e.data['errors'].items()])
            return {
                'return_code': 400,
                'return_msg': return_msg
            }

        appId = os.popen("openssl rand -base64 24").read().strip()
        secret = os.popen("openssl rand -base64 24").read().strip()
        redis_ins = RedisInstance()
        redis_ins.client.hset("appId:{}".format(appId), "appId", appId)
        redis_ins.client.hset("appId:{}".format(appId), "secret", secret)
        today = datetime.datetime.now()
        next_year = datetime.datetime(today.year + 1, today.month,
                                      today.day, today.hour,
                                      today.minute, today.second)
        expire = int(time.mktime(next_year.timetuple()))
        redis_ins.client.hset("appId:{}".format(appId), "expire", expire)
        expire_at = auth.timestep2strtime(expire)
        if args['visit_limit']:
            redis_ins.client.hset("appId:{}".format(appId), "visit_limit", args['visit_limit'])

        if args['uri_list']:
            redis_ins.client.hset("appId:{}".format(appId), "uri_list", args['uri_list'])

        return {
            'return_code': 200, 'data':
                {"appid": appId,
                 "secret": secret,
                 "expire_at": expire_at
                 }
        }


@user_api.route('/token')
class AccessToken(Resource):
    logger = logger.getChild('Token')

    creation_parser = RequestParser()
    creation_parser.add_argument(
        'appid', location='form', type=str, required=True,
        help='appid is not null'
    )
    creation_parser.add_argument(
        'secret', location='form', type=str, required=True, help='secret is not null'
    )

    def post(self):
        try:
            args = self.creation_parser.parse_args()
        except werkzeug.exceptions.BadRequest as e:
            self.logger.warning(f'{dir(e), str(e), e.args, e.data, e.name, e.description}')
            return_msg = '\n'.join([f'{v}: {k}.' for k, v in e.data['errors'].items()])
            return {
                'return_code': 400,
                'return_msg': return_msg
            }
        key = args['appid']
        secret = args['secret']

        redis_ins = RedisInstance()
        secret_ = redis_ins.client.hget("appId:{}".format(key), "secret")
        if secret_ is None:
            return {
                'return_code': 530,
                'return_msg': '"appid secret无效"'
            }
        if secret_.decode("utf-8") != secret:
            return {
                'return_code': 530,
                'return_msg': '"appid secret无效"'
            }
        expire_ = redis_ins.client.hget("appId:{}".format(key), "expire")
        if not expire_:
            return dict(return_code=531, return_msg="appid expire_ error", data={})
        if time.time() > float(expire_):
            return {
                'return_code': 531,
                'return_msg': "appid 已过期"
            }
        return {
            'return_code': 200,

            "data": {'token': auth.generate_token(key=key)}

        }
