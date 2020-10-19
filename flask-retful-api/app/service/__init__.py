#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :__init__.py.py
# @Time      :2020/8/31 下午4:41

from app.service.qrcode_by_ali import OcrAliyun
from app.service.qrcode_by_baidu import OcrBaidu
from app.service.qrcode_by_tencent import OcrTencent

def openapi(base64data):
    # for func in [OcrAliyun]:
    # for func in [OcrBaidu, OcrAliyun, OcrTencent]:
    for func in [OcrBaidu]:
        data = func().run(base64data)
        if data:
            return data

