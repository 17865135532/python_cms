#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :qcode_by_ali.py
# @Time      :2020/9/8 下午1:45
import json
import time
import requests
import logging

from app.configs import CONFIG

logger = logging.getLogger(__name__)


class OcrAliyun(object):
    '''阿里云通用文字识别'''
    logger = logger.getChild('OcrAliyun')
    header = {
        # "Host": "tysbgpu.market.alicloudapi.com",
        #       "X-Ca-Timestamp":"1546603920846",
        # "gateway_channel": "http",
        # "X-Ca-Request-Mode": "debug",
        # "X-Ca-Key":"25322009",
        "X-Ca-Stage": "RELEASE",
        # "Content-MD5":"XksaIEckrNsEu0NQaDnTDQ==",
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f'APPCODE {CONFIG.APP_CODE}'
    }

    def get_work(self, data):
        """
        获取拼接图ocr识别结果
        :param data:base64编码的图片
        :return:
        """
        url = CONFIG.ALI_HOST
        ocr_result = {}
        try:
            r = requests.post(url, data=json.dumps(data), headers=self.header, timeout=6)
            if r.status_code == 200:
                ocr_result = r.json()
        except Exception as e:
            self.logger.error('', exc_info=e)

        self.logger.info(f"阿里值:{ocr_result}")
        return ocr_result

    def run(self, base64data):
        data = {'image': base64data}

        ali_result = self.get_work(data)
        if not ali_result:
            return

        if ali_result and 'success' in ali_result and ali_result.get('success'):
            return [{code.get('type'): code.get('data') for code in ali_result.get(
                'codes', {}
            )}]

# 阿里值:{'codes': [{'data': '008-6788110290-01-02-02', 'points': [{'x': 74, 'y': 78}, {'x': 7.999996662139893, 'y': 76.99998474121094}, {'x': 9, 'y': 10.999984741210938}, {'x': 75, 'y': 12}], 'type': 'QR-Code'}], 'config_str': '{}', 'request_id': '20200908170518_d41ccb8f74c7450adf0e0351e73efb8c', 'success': True}
