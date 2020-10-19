#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time      :2020/9/3 下午3:46
import time
import requests
import logging
import json

from app.dao.redis_dao import RedisInstance
from app.configs import CONFIG


logger = logging.getLogger(__name__)


class OcrBaidu(object):
    logger = logger.getChild('OcrBaidu')

    def get_work(self, data):
        """
        :param base64编码的图片
        :return:
        """
        baidudata = {}
        access_token = self.get_token()

        if not access_token:
            raise AttributeError('access_token is None')

        try:
            time_bd_ocr_start = time.time()
            BD_QCODE_URL = CONFIG.BD_QCODE_URL + "?access_token=" + access_token
            resp = requests.post(BD_QCODE_URL, timeout=5, data=data)
            logger.info(f"time_bd_ocr: {(time.time() - time_bd_ocr_start)}")
            if resp.status_code == 200:
                baidudata = json.loads(resp.text)
        except (requests.HTTPError, requests.ConnectionError, Exception) as e:
            logger.error(f"{e.args}", exc_info=True)

        if all([baidudata, baidudata.get("codes_result_num", '') != 0, baidudata.get('codes_result', [])]):
            return [{codes.get('type'): codes.get('text')[0]} for codes in baidudata.get('codes_result', [])]

    def run(self, base64data):
        bddata = self.get_work({'image': base64data})
        return bddata if bddata else []

    def get_token(self):
        """
        获取access_token
        :return: access_token or None
        """
        redis_ins = RedisInstance()
        redis_token = redis_ins.get_apibaidu_access_token()
        if redis_token:
            token = redis_token
            self.logger.info("token from redis")
        else:
            # 更新access_token
            r = requests.get(CONFIG.BDTOKEN_URL, params=CONFIG.BAIDU_OCR_ACCOUNT)
            token = None
            if r.status_code == 200:
                res_json = r.json()
                has_error = res_json.get("error")
                if has_error:
                    self.logger.error(to_json(555, "baidu ocr token error", res_json))
                    return None
                token = res_json.get("access_token")
                expires_in = res_json.get("expires_in")
                redis_ins.set_apibaidu_access_token(token, expires_in)
                self.logger.info("token insert redis success")
        if token:
            if isinstance(token, bytes):
                return token.decode("utf-8")
        return token


if __name__ == "__main__":
    import base64
    bd = OcrBaidu()
    # 识别失败的整张进行 百度识别

    img = "/home/duanweiye/桌面/询证函_8_21/原始数据/pdf_to_image_dir/img_path/3、回函原件-兰州永恒莉商贸有限公司-01-0-1-2.png"
    # img = "3、回函原件-兰州永恒莉商贸有限公司-01-0-1-2.png"
    img_content = open(img, 'rb').read()
    base64_data = base64.b64encode(img_content)
    base64_data = base64_data.decode(encoding='utf-8')
    data = {"image": base64_data}
    qrcode_info = bd.run(base64_data)
    print(qrcode_info)