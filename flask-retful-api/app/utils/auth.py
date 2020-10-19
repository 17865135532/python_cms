#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :auth.py
import os
import time
import hashlib
import logging
import base64

from gmssl import sm2, func
from app.dao.redis_dao import RedisInstance

logger = logging.getLogger(__name__)

EXPIRE_DEFAULT = float(os.environ.get('TOKEN_EXPIRES_IN', 3600 * 2))
EXPIRE_MAX = 60 * 60 * 24 * 365
# 10w
VISIT_LIMIT_DEFAULT = 100 * 1000
DEFAULT_LIMITS = ["200 per day", "50 per hour"]

private_key = '00B9AB0B828FF68872F21A837FC303668428DEA11DCD1B24429D0C99E24EED83D5'
public_key = 'B9C9A6E04E9C91F7BA880429273747D7EF5DDEB0BB2FF6317EB00BEF331A83081A6994B8993F3F5D6EADDDB81872266C87C018FB4162F5AF347B483E24620207'
sm2_crypt = sm2.CryptSM2(
    public_key=public_key, private_key=private_key
)


def generate_token(key, salt=func.random_hex(16)):
    """
        @Args:
            key: str (用户给定的key，需要用户保存以便之后验证token,每次产生token时的key 都可以是同一个key)
            salt: gmssl func random_hex 生成的随机数
            expire: int(最大有效时间，单位为s)
            visit_limit： int(最大访问次数)
        @Return:
            state: str
    """

    r = RedisInstance()
    visit_limit = r.client.hget("appId:{}".format(key), "visit_limit")
    if visit_limit is not None:
        visit_limit = int(visit_limit)
    else:
        visit_limit = VISIT_LIMIT_DEFAULT
    uri_list = r.client.hget("appid:{}".format(key), "uri_list")
    if uri_list is None:
        uri_list = "*"
    data = "{timestamp}:{key}:{salt}:{expire}:{visit_limit}:{uri_list}".format(
        timestamp=int(time.time()),
        key=key,
        salt=salt,
        expire=EXPIRE_DEFAULT + int(time.time()),
        visit_limit=visit_limit,
        uri_list=uri_list
    )
    enc_data = sm2_crypt.encrypt(data=data.encode('utf-8'))
    b64_token = base64.urlsafe_b64encode(enc_data)
    b64_token_dec = b64_token.decode("utf-8")
    return b64_token_dec

def certify_token(token, uri="*"):
    r"""
        @Args:
            token: str
            uri: str
            visit_count: int
        @Returns:
            dict
    """
    try:
        token = base64.urlsafe_b64decode(token)
        dec_data = sm2_crypt.decrypt(token)
    except Exception as e:
        logger.critical(f"token error: {e.args}", exc_info=True)
        return {
            'return_code': 401,
            'return_msg': 'token is required.'
        }
    except Exception as e:
        return {
            'return_code': 401,
            'return_msg': 'token is required.'
        }
    try:
        data_list = dec_data.decode('utf-8').split(":")
    except UnicodeDecodeError:
        return {
            'return_code': 401,
            'return_msg': 'token is required.'
        }

    except Exception as e:
        logger.critical(f"token error: {e.args}", exc_info=True)
        return {
            'return_code': 401,
            'return_msg': 'token is required.'
        }

    if len(data_list) != 6:
        return {
            'return_code': 506,
            'return_msg': 'token信息长度校验失败'
        }
    timestamp, appid, salt, expire, visit_limit, uri_list = data_list
    expire = int(float(expire))
    # if uri not in uri_list.split(","):
    #     return to_json(507, "无访问权限")
    if int(time.time()) > int(expire):
        local_time = time.localtime(expire)
        expire_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        return {
            'return_code': 503,
            'return_msg': "token已失效，失效时间：%s" % expire_time
        }
    r = RedisInstance()
    visit_count = r.client.hincrby("appid:{}".format(appid), "visit_count")
    if visit_count > int(visit_limit):
        return {
            'return_code': 505,
            'return_msg': "已达到访问次数上限"
        }
    return {
            'return_code': 200,
            'appid': appid
        }


def create_sign(token, timestamp, values):
    _logger = logger.getChild('create_sign')
    data = {}
    for key, val in values.items():
        if key in ['token', 'timestamp', 'sign']:
            continue
        if not isinstance(val, (int, str)):
            continue
        data[key] = str(val)
    content = ''.join([f'{k}{v}' for k, v in sorted(data.items(), key=lambda item: item[0])])
    sign_str = f'{token}.{timestamp}.{content}'
    sign = _md5(sign_str).upper()
    _logger.debug(f'sign : {sign}')
    return sign

def _md5(content):
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.md5(content).hexdigest()


def timestep2strtime(time_stamp):
    time_array = time.localtime(time_stamp)
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time

