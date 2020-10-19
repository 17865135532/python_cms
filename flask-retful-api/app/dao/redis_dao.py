#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :erdos.py
# @Time      :2020/9/3 下午4:01
import logging
import redis
from redis import Redis
from app.configs import CONFIG


REDISDATABASE = CONFIG.DATABASE

logger = logging.getLogger(__name__)
APIBAIDU_ACCESS_TOKEN = "apibaidu_access_token"
ONE_MONTH = 60 * 60 * 24 * 30


class RedisInstance(object):
    APIBAIDU_ACCESS_TOKEN = "apibaidu_access_token"

    def __init__(self):
        self.client = redis.Redis(connection_pool=redis.ConnectionPool(host=REDISDATABASE['host'], port=REDISDATABASE['port'], password=REDISDATABASE['password']))

    def get_apibaidu_access_token(self):
        return self.client.get(self.APIBAIDU_ACCESS_TOKEN)

    def set_apibaidu_access_token(self, value, expires_in=ONE_MONTH):
        self.client.set(self.APIBAIDU_ACCESS_TOKEN, value, ex=expires_in)

    def hset(self, name, key, value):
        return self.client.hset(name, key, value)

    def hget(self, name, key):
        return self.client.hget(name, key)

    def hdel(self, name, key):
        return self.client.hdel(name, key)




if __name__ == "__main__":
    ...
    r = RedisInstance()
    hash_code = "094b1b9b266841f1e22e2103964a1806"
    hash_code_name = "check_hash:" + hash_code
    # res = r.hset(hash_code_name, "imgs_name", 111111)
    print(r.hget(hash_code_name, "imgs_name"))
    # res = r.hget(hash_code_name, "imgs_name")
    #
