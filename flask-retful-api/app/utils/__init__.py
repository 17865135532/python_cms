#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :__init__.py.py
# @Time      :2020/8/31 下午4:17
import sys
import cv2
import base64
import numpy as np
from io import BytesIO

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def check_file_size(bytes_content):
    file_size = sys.getsizeof(bytes_content)
    max_size = 1 * 1024 * 1024
    # if file_size > max_size or file_size < min_size:
    if file_size > max_size:
        return False
    else:
        return True


def img_to_base64(image):
    if isinstance(image, str):
        image = image

    elif isinstance(image, bytes):
        image = base64.b64encode(image).decode(encoding='utf-8')

    elif isinstance(image, np.ndarray):
        # OpenCV 图像转base64编码
        img_str = cv2.imencode('.jpg', image)[1].tostring()  # 将图片编码成流数据，放到内存缓存中，然后转化成string格式
        image = base64.b64encode(img_str).decode(encoding='utf-8')  # 编码成base64
    return image


def format_decode_info(dec_info):
    temp_dic = {}
    if dec_info:
        for dic in dec_info:
            for k, v in dic.items():
                if "_" in k:
                    k = k.replace('_', '')

                if k not in temp_dic:
                    temp_dic[k] = v

                elif k in temp_dic and v == temp_dic[k]:
                    dec_info.remove(dic)

    return [{k.replace('_', ''): v} for dic in dec_info for k, v in dic.items()]


def check_decode_info(dec_info=[], qtype=''):
    # if not all([dec_info, qtype]):
    # raise

    if not dec_info:
        return False

    dec_info = format_decode_info(dec_info)
    result_flag = {}
    for q_code in dec_info:
        for k, v in q_code.items():
            if k in ['QRCODE', "QR_CODE"]:
                # let_qrcode let_bar_code 询证函字段
                if qtype in ['ConfirmationLetter']:
                    result_flag['let_qrcode'] = True if len(v) < 30 else False
                else:
                    result_flag['QRCODE'] = True if all([k, v]) else False
            elif k in ['CODE128', 'CODE_128']:
                #  CODE128 存在 但 不为 let_bar_code
                if qtype in ['ConfirmationLetter']:
                    result_flag['let_bar_code'] = True if "-" in v else False
                else:
                    result_flag['CODE128'] = True if all([k, v]) else False
            else:
                result_flag[k] = True if all([k, v]) else False

    if qtype in ['ConfirmationLetter']:
        # if result_flag.get('let_qrcode', '') or result_flag.get('let_bar_code', ''):
        # if 'let_qrcode' in result_flag and result_flag.get('let_qrcode') or 'let_bar_code' in result_flag and result_flag.get('let_bar_code'):
        # if 'let_qrcode' in result_flag or result_flag.get(
        #         'let_qrcode') or 'let_bar_code' in result_flag or result_flag.get('let_bar_code'):
        if result_flag.get('let_qrcode', '') or \
                result_flag.get('let_bar_code', '') or \
                result_flag.get('QRCODE', '') or \
                result_flag.get('CODE128', ''):

            return True
        else:
            return False
    else:
        if (result_flag.get('QRCODE', '') or result_flag.get('CODE128', '')):
            return True
        else:
            # 考虑 除了 QRCODE, CODE128 其他字段的情况
            if all(result_flag.values()):
                return True
            return False


def datetime_toString(dt, format="%Y-%m-%d %H:%M:%S"):
    return dt.strftime(format)


def pil_tobytes(image, image_stream=''):
    try:
        bytesIO = BytesIO()
        try:
            image.save(bytesIO, format='JPEG')
        except Exception as e:
            logger.error('IMAGE TO Byte Error', exc_info=e)
            image.save(bytesIO, format='PNG')
        image_stream = bytesIO.getvalue()  # 转二进制
    except Exception as e:
        logger.critical('pdf file error', exc_info=e)
    return image_stream
