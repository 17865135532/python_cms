#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :qrcode_by_tencent.py
# @Time      :2020/9/8 下午2:13
# pip install tencentcloud-sdk-python

import logging
import json

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models

from app.configs import CONFIG

logger = logging.getLogger(__name__)


class OcrTencent(object):
    logger = logger.getChild('OcrTencent')

    def __init__(self):
        self.SecretId = CONFIG.SecretId
        self.SecretKey = CONFIG.SecretKey

    def get_work(self, base64data):
        try:
            cred = credential.Credential(self.SecretId, self.SecretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)
            req = models.QrcodeOCRRequest()
            # with open(file=img_path, mode='rb') as file:
            #     base64_data = base64.b64encode(file.read())
            # 对本地图片进行base64转码【本地图片解析需要先转成base64编码】
            # img = cv2.imread(path)
            # imshow(img)
            # with open(path, 'rb') as f:
            #     # base64_data = base64.b64encode(f.read())
            #     # s = base64_data.decode()
            #     # ImageBase64_value = 'data:image/jpeg;base64,%s'%s
            #     # #params是字符串，以下进行拼接
            #     # params = '{"ImageBase64":"' + ImageBase64_value + '"}' #以图片Base64编码发送请求
            #
            #     base64data = base64.b64encode(f.read())  # 得到 byte 编码的数据
            #     base64data = str(base64data, 'utf-8')  # 重新编码数据
            params = '{"ImageBase64":"' + base64data + '"}'
            req.from_json_string(params)
            resp = client.QrcodeOCR(req)
            self.logger.info(f"腾讯解码值:{resp.to_json_string()}")
            return json.loads(resp.to_json_string())
        except TencentCloudSDKException as e:
            self.logger.error('TencentCloudSDKException:', exc_info=e)

        except Exception as e:
            self.logger.error('TencentCloudSDKException:', exc_info=e)

    # 腾讯值: {"CodeResults": [{"TypeName": "QR_CODE", "Url": "008-6897023354-01-02-02",
    #                        "Position": {"LeftTop": {"X": 9, "Y": 12}, "RightTop": {"X": 72, "Y": 12},
    #                                     "RightBottom": {"X": 72, "Y": 76}, "LeftBottom": {"X": 9, "Y": 76}}}],
    #       "ImgSize": {"Wide": 86, "High": 89}, "RequestId": "371b8dfc-b2d8-485e-96b9-ad399044a46f"}

    def run(self, base64data):
        tencent_result = self.get_work(base64data)
        if not tencent_result:
            return

        if tencent_result and 'CodeResults' in tencent_result and tencent_result.get('CodeResults'):
            return [{code.get('TypeName'): code.get('Url') for code in tencent_result.get(
                'CodeResults', {}
            )}]


