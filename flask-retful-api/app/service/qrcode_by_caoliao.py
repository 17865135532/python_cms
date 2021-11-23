#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :qcodeopenapi.py
# @Time      :2020/9/3 上午10:53
import requests
import grequests
import json
import logging

logger = logging.getLogger(__name__)


class CaoLiao(object):
    # 草料
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3719.400 QQBrowser/10.5.3715.400',
            'origin': 'https://cli.im',
            'accept-language': 'zh-CN,zh;q=0.9',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'referer': 'https://cli.im/deqr'
        }

        self.cookies = {'appver': '1.5.2', 'os': 'linux'}
        self.session = requests.Session()
        self.timeout = 2

    def req_image_url(self, image):
        task = []
        files = {'Filedata': open(image, 'rb')}
        url = 'https://upload.api.cli.im/upload.php?kid=cliim'
        try:
            req = grequests.request(
                "POST", url=url, headers=self.headers, files=files, timeout=self.timeout
                                   )
            task.append(req)
            resp = grequests.map(task)
            if all([resp, resp[0]]):
                res_data = json.loads(resp[0].text)
                if res_data.get('status', '') in ['1', 1]:
                    self.headers = self.headers.update(resp[0].headers)
                    self.cookies = self.cookies.update(resp[0].cookies)
                path = res_data.get('data', {}).get('path', '')
                return path
        except Exception as e:
            print(e.args)

    def parse_img(self, image):
        # parseurl = "https://cli.im/apis/up/deqrimg"
        print(image)
        parseurl = "https://cli.im/apis/up/deqrimg"
        image_url = self.req_image_url(image)
        print(f"image_url: {image_url}")

        task = []
        req = grequests.request(
            "POST", url=parseurl, headers=self.headers, timeout=self.timeout, data={'img': image_url}
        )
        task.append(req)
        resp = grequests.map(task)
        for ii in resp:
            # print(json.loads(ii.status_code))
            print(ii.status_code)

if __name__ == "__main__":
    import glob
    import os
    import time

    cl = CaoLiao()

    dir = "/home/XXX/桌面/询证函_8_21/原始数据/识别失败的图片"
    for parh in glob.glob(f"{dir}/*"):
        time.sleep(1)
        data = cl.parse_img(parh)
