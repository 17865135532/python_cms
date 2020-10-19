#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :bar_qrcode.py
# @Time      :2020/8/31 下午4:06
import os
import re
import logging
import base64
from PIL import Image, ImageEnhance
import numpy as np
import cv2
from io import BytesIO
from pdf2image import convert_from_path
import datetime

from flask_restx import Resource, Namespace
from flask_restx.reqparse import RequestParser
import werkzeug
from werkzeug.datastructures import FileStorage
from flask import g

from app.utils import check_file_size, check_decode_info, format_decode_info, datetime_toString, \
    pil_tobytes
from app.configs import CONFIG
from app.service.qrcode_by_local import QrcodeInfo
from app.utils import img_to_base64
from app.service import openapi
from app.utils.decorators import login_required

qrcode_api = Namespace('qrcode', description='二维码,条形码 解码相关API')

__all__ = ['qrcode_api']

logger = logging.getLogger(__name__)
bdflag = CONFIG.BDFLAG


@qrcode_api.route('')
class Qrcode(Resource):
    # 识别失败 --> 自动筛选定位框 进行解码 --> 解码失败 --> 第三方接口输出
    logger = logger.getChild('Qrcode')

    creation_parser = RequestParser()
    creation_parser.add_argument('token', location='headers', type=str, required=True, nullable=False, help='用户token')
    creation_parser.add_argument('timestamp', location='headers', type=float, required=True, nullable=False, help='时间戳')
    creation_parser.add_argument(
        'sign', location='headers', type=str, required=True, nullable=False,
        help='校验和，用户token、时间戳、用名字排序后的字符串或整型参数拼接后，计算md5值，再转为大写得到')
    creation_parser.add_argument(
        'imagefile', location='files',
        type=werkzeug.datastructures.FileStorage, help='解码文件'
    )
    creation_parser.add_argument(
        'image_data', location='form',
        type=str, help='', default=''
    )

    creation_parser.add_argument(
        'qtype', location='form', type=str, default=''
    )

    @staticmethod
    def recognition(image_stream, qtype):
        if not image_stream or not isinstance(image_stream, bytes):
            raise ValueError('image_stream is must True and Bytes')

        image = cv2.cvtColor(np.array(Image.open(BytesIO(image_stream))), cv2.COLOR_RGB2BGR)
        # 将bytes结果转化为字节流
        # qtype = args['qtype']
        qrcodeinfo = QrcodeInfo()
        qrcode_result = qrcodeinfo.main_qrcode(image=image, compose=check_file_size(image_stream), qtype=qtype)
        if qtype in ['ConfirmationLetter']:
            if not check_decode_info(qrcode_result, qtype):
                # 固定位置裁剪
                q_result = qrcodeinfo.fixedposition(image, qrcode_result, qtype, bdflag)
                qrcode_result.extend(q_result if q_result else [])

        # 自动检测
        if not check_decode_info(qrcode_result, qtype):
            # 自动检测识别
            q_result, _ = qrcodeinfo.detectimage(image, qrcode_result, qtype)
            qrcode_result.extend(q_result if q_result else [])

        # 避免重复电泳调用第三方接口
        openapi_flag = g.openapi_flag if hasattr(g, 'openapi_flag') else False
        if not openapi_flag:
            # 百度api
            if not check_decode_info(qrcode_result, qtype) and bdflag:
                openapidata = openapi(
                    base64data=img_to_base64(image)
                )
                qrcode_result.extend(openapidata if openapidata else [])
        return format_decode_info(qrcode_result) if qrcode_result else []

    @login_required
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
        imagefile = args['imagefile']
        if imagefile:
            filename = imagefile.filename.split('/')[0]
            file_type = re.match(r"[a-zA-Z]+", os.path.splitext(imagefile.filename)[-1].split('.')[-1].lower()).group()
            if file_type not in CONFIG.FILENAMES:
                return {
                    'return_code': 400,
                    'return_msg': 'Picture format ERROR',
                }
            # 文件转换图片
            if file_type in ['pdf', 'PDF']:
                pdf_file_path = os.path.join(CONFIG.PDF_DIR,
                                             f"{filename}_{datetime_toString(datetime.datetime.now())}.pdf"
                                             )
                imagefile.save(pdf_file_path)
                try:
                    images = convert_from_path(pdf_file_path)
                except Exception as e:
                    self.logger.critical('pdf transformation image faild', exc_info=e)
                    return {
                        'return_code': 200,
                        'return_msg': 'pdf transformation image faild',
                        'data': []
                    }

                qrcode_info = []
                if isinstance(images, list) and images:
                    for index, image in enumerate(images):
                        try:
                            qrcode_info.append(
                                {
                                    'name': f'{filename}_{index}.pdf',
                                    'data': self.recognition(
                                        pil_tobytes(image),
                                        qtype=args['qtype']
                                    )
                                }
                            )
                        except Exception as e:
                            self.logger.critical('pdf file error', exc_info=e)
                return {
                    'return_code': 200,
                    'return_msg': '',
                    'data': qrcode_info
                }
            else:
                image_stream = imagefile.read()  # Bytes 文件
        else:
            if args['image_data']:  # image_data  image base64 字段
                image_stream = base64.b64decode(args['image_data'])
                img_array = np.frombuffer(image_stream, np.uint8)  # 转换np序列
                if img_array is None:
                    return {
                        'return_code': 400,
                        'return_msg': 'Picture format ERROR',
                    }
        return {
            'return_code': 200,
            'return_msg': '',
            'data':
                self.recognition(image_stream, qtype=args['qtype'])
        }
