#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :Qcode.py
# @Time      :2020/8/31 下午4:41


# !/usr/bin/python
# -*- coding: UTF-8 -*-
import zxing
import os
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import uuid
import logging
from io import BytesIO

try:
    import pyzbar.pyzbar as pyzbar
except ImportError:
    ...
from app.configs import CONFIG
from app.utils import img_to_base64, check_decode_info
from app.service import openapi

"""
# if (isinstance(img, np.ndarray)):  
#     img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
# img = Image.open(imgpath)
# img = img.convert('L')  # 灰度化
# img = img.convert("1")
# img.show()
# img = ImageEnhance.Sharpness(img).enhance(17.0)  # 锐利化
# img = ImageEnhance.Contrast(img).enhance(4.0)  # 增加对比度
# img = img.convert('L')  # 灰度化
# img = img.convert("1")
# image.show()

"""



logger = logging.getLogger(__name__)


def imshow(img, name="picture", winnum=0, savepath=None, save_flag=False):
    cv2.namedWindow(name, winnum)
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if save_flag:
        cv2.imwrite(savepath, img)


class DetectImage():
    """图片自动检测二维码 条形码"""
    logger = logger.getChild('DetectImage')

    @staticmethod
    def preprocess(gray):
        # 高斯平滑
        # imshow(gray)
        gaussian = cv2.GaussianBlur(gray, (3, 3), 0, 0, cv2.BORDER_DEFAULT)
        # imshow(gaussian)
        # 中值滤波
        median = cv2.medianBlur(gaussian, 5)
        # imshow(median)

        # Sobel算子，X方向求梯度
        sobel = cv2.Sobel(median, cv2.CV_8U, 1, 0, ksize=3)
        # imshow(sobel)

        # 二值化
        ret, binary = cv2.threshold(sobel, 170, 255, cv2.THRESH_BINARY)
        # imshow(binary)

        # 膨胀和腐蚀操作的核函数
        element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
        element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 7))
        # 膨胀一次，让轮廓突出
        dilation = cv2.dilate(binary, element2, iterations=1)
        erosion = cv2.erode(dilation, element1, iterations=1)
        # 再次膨胀，让轮廓明显一些
        dilation2 = cv2.dilate(erosion, element2, iterations=3)
        return dilation2

    @staticmethod
    def findPlateNumberRegion(img):
        region = []
        # 查找轮廓
        contours, hierarchy = cv2.findContours(image=img, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
        # 筛选面积小的
        for i in range(len(contours)):
            cnt = contours[i]
            # 计算该轮廓的面积
            area = cv2.contourArea(cnt)

            # 面积小的都筛选掉
            if (area < 3000):
                continue

            rect = cv2.minAreaRect(cnt)
            # box是四个点的坐标
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            # 计算高和宽
            height = abs(box[0][1] - box[2][1])
            width = abs(box[0][0] - box[2][0])
            # 正常情况下长高比在2.7-5之间
            ratio = float(width) / float(height)

            # ys = [box[0, 1], box[1, 1], box[2, 1], box[3, 1]]
            # xs = [box[0, 0], box[1, 0], box[2, 0], box[3, 0]]
            # ys_sorted_index = np.argsort(ys)
            # xs_sorted_index = np.argsort(xs)
            #
            # x1 = box[xs_sorted_index[0], 0]
            # x2 = box[xs_sorted_index[3], 0]
            #
            # y1 = box[ys_sorted_index[0], 1]
            # y2 = box[ys_sorted_index[3], 1]
            #
            # img_org2 = img.copy()
            # img_plate = img_org2[y1:y2, x1:x2]
            # imshow(img_plate)
            # print(ratio)
            if (ratio > 5 or ratio < 0.5 or height < 50 or height > 300 or width < 40):
                # if (ratio > 5 or ratio < 0.5 or width < 40):
                continue
            if (0.7 < ratio < 1.3 or 4 < ratio < 5):
                region.append(box)
        return region

    @classmethod
    def detect(cls, img):
        if isinstance(img, str):
            img = cv2.imread(img)
        elif isinstance(img, np.ndarray):
            img = img
        # 转化成灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 形态学变换的预处理
        dilation = cls.preprocess(gray)
        # 查找区域
        region = cls.findPlateNumberRegion(dilation)
        # 用绿线画出这些找到的轮廓
        region_list = []
        for index, box in enumerate(region):
            # cv2.drawContours(img, [box], 0, (0, 255, 0), 2)
            # imshow(img)

            ys = [box[0, 1], box[1, 1], box[2, 1], box[3, 1]]
            xs = [box[0, 0], box[1, 0], box[2, 0], box[3, 0]]
            ys_sorted_index = np.argsort(ys)
            xs_sorted_index = np.argsort(xs)

            x1 = box[xs_sorted_index[0], 0]
            x2 = box[xs_sorted_index[3], 0]

            y1 = box[ys_sorted_index[0], 1]
            y2 = box[ys_sorted_index[3], 1]

            img_org2 = img.copy()
            img_plate = img_org2[y1:y2, x1:x2]
            # imshow(img_plate)
            region_list.append(img_plate)

            # 切割图片写本地
            img_plate_dir = CONFIG.IMG_PLATE_DIR
            # if not os.path.exists(img_plate_dir):
            #     os.mkdir(img_plate_dir)
            img_plate_path = os.path.join(img_plate_dir, f'number_{index}_{str(img_plate.size)}_plate.jpg')
            cv2.imwrite(img_plate_path, img_plate)
        return region_list


class CompressImage():
    logger = logger.getChild('CompressImage')

    def get_size(self, file):
        # 获取文件大小:KB
        size = os.path.getsize(file)
        return size / 1024

    def compress_image(self, file, maxmb=1000, fx=1.0, fy=1.0, k=0.1, save_path=None):
        # 图片压缩
        image = cv2.imread(file)
        if self.get_size(file) > maxmb:
            fx -= k
            fy -= k
            h, w = image.shape[: 2]
            img = cv2.resize(image, (int(w * fx), int(h * fy)), interpolation=cv2.INTER_LINEAR)
            image = img
        return image

    def get_shape(self, img):
        """
        return the height and width of an image
        """
        return np.shape(img)[0:2]

    def resize(self, img, fx=0.8, fy=0.8, interpolation=None):
        if interpolation is None:
            interpolation = cv2.INTER_LINEAR

        if all([fx, fy]):
            return cv2.resize(img, None, fx=fx, fy=fy, interpolation=interpolation)


class QrcodeInfo:
    logger = logger.getChild('QrcodeInfo')

    def zabr_parser(self, image, preprocess=True):
        if isinstance(image, str):
            # image path
            image = Image.open(image)

        elif isinstance(image, bytes):
            # 将bytes结果转化为字节流
            # bytes_stream = BytesIO(image)
            # 读取到图片
            image = Image.open(BytesIO(image))

        elif isinstance(image, np.ndarray):
            # opencv array 转 pil
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        img = image
        if preprocess:
            img = ImageEnhance.Brightness(image).enhance(2.0)  # 增加亮度
            img = ImageEnhance.Contrast(img).enhance(4.0)  # 增加对比度
            img = img.convert('L')  # 灰度化

        # img.show('title')
        barcodes = []
        try:
            barcodes = pyzbar.decode(img)
        except Exception as e:
            self.logger.error(e.args)
        return barcodes

    def qrcode_zxing(self, image, temp_flag=False):
        zx = zxing.BarCodeReader()
        zxing_img_temp_dir = os.path.join(os.path.abspath('.'), 'zxing_img_temp_dir')
        os.makedirs(zxing_img_temp_dir, exist_ok=True)
        save_path = os.path.join(zxing_img_temp_dir, f"test_{uuid.uuid1()}.jpg")
        if isinstance(image, np.ndarray):
            cv2.imwrite(save_path, image)
            image = save_path
            temp_flag = True

        elif isinstance(image, bytes):
            # 读取到图片
            image = Image.open(BytesIO(image))
            # image.show('test')
            image.save(save_path)
            image = save_path
            temp_flag = True

        try:
            zxdata = zx.decode(image)  # 图片解码
        except Exception as e:
            logger.error(e.args)
        # 删除临时文件
        if temp_flag and os.path.exists(image):
            os.remove(image)
        return zxdata

    def decode_img_zabr_parser(self, qpath, preprocess=True):
        if self.zabr_parser(image=qpath, preprocess=preprocess):
            return self.zabr_parser(image=qpath, preprocess=preprocess)
        elif self.zabr_parser(image=qpath, preprocess=False):
            return self.zabr_parser(image=qpath, preprocess=False)

    def decode_img_zxing_parser(self, qpath, preprocess=True):
        if self.qrcode_zxing(image=qpath):
            return self.qrcode_zxing(image=qpath)

    def main_decode_img(self, image_path, qtype):
        """
        识别结果处理
        :param image_path:
        :return: decodea_data
        """
        decodea_data = []
        zabrdetail = self.decode_img_zabr_parser(qpath=image_path)
        if zabrdetail is not None:
            for q in zabrdetail:
                decodea_data.append(
                    {q.type : q.data.decode("utf-8")}
                )

            # decodea_data.append(
            #     {q.type: q.data.decode("utf-8")} for q in zabrdetail
            # )
        else:
            zxingdetail = self.decode_img_zxing_parser(qpath=image_path)
            if zxingdetail is not None:
                # zxindata = zxingdetail.parsed
                # format = zxingdetail.format
                try:
                    decodea_data.append(
                        {zxingdetail.format: zxingdetail.parsed}
                    )
                except Exception as e:
                    self.logger.error(f"zxingdetail.parsed error: {e.args}")
        return decodea_data

    # 图片预处理，旋转方正并拉伸到407 * 407分辨率
    def prepare_image(self, cut_image, qr_cnt):
        # 最小外接矩形
        min_area_rect = cv2.minAreaRect(qr_cnt)
        # 取角点
        box_points = cv2.boxPoints(min_area_rect)

        # 生成透视变换矩阵
        source_position = np.float32(
            [[box_points[1][0], box_points[1][1]], [box_points[2][0], box_points[2][1]],
             [box_points[0][0], box_points[0][1]], [box_points[3][0], box_points[3][1]]])
        target_position = np.float32([[0, 0], [407, 0], [0, 407], [407, 407]])

        transform = cv2.getPerspectiveTransform(source_position, target_position)

        # 进行透视变换
        transform_image = cv2.warpPerspective(cut_image, transform, (407, 407))

        if self.trace_image:
            cv2.imwrite(self.trace_path + "101_transform_" + self.image_name, transform_image)

        return transform_image

    def fixedposition(self, image, result, qtype, bdflag):
        h, w = image.shape[: 2]
        img_org2 = image.copy()
        img_plates_list = []
        # 裁剪三次
        for i in [10, 9, 8]:
            codepoints = dict(let_qrcode={
                "y1": 0, "y2": int(h / i),
                "x1": int(w / 1.4), "x2": int(w),
            },
                let_bar_code={
                    "y1": 0,
                    "y2": int(h / i),
                    "x1": 0, "x2": int(w / 2),
                })
            for code, points in codepoints.items():
                # if code in result:continue
                img_plate = img_org2[points['y1']:points['y2'], points['x1']:points['x2']]
                c_h, c_w = img_plate.shape[: 2]
                fx, fy = 1.5, 1.5
                img_plate = cv2.resize(img_plate, (int(c_w * fx), int(c_h * fy)), interpolation=cv2.INTER_LINEAR)
                # imshow(img_plate, 'after')
                # 裁剪原图解码
                decodedata = self.main_decode_img(img_plate, qtype)
                result.extend(decodedata if decodedata else [])
                # result.update({k: v for k, v in decodedata.items() if k not in result if decodedata})
                logger.info(f"Fixed position decode data: {decodedata}")
                # 检测函数识别
                detectdata = {}
                if i != 8: continue
                #
                if not check_decode_info(result, qtype):
                    detectdata, img_plates = self.detectimage(image=img_plate, result=result, qtype=qtype)
                    result = detectdata if decodedata else result
                    # result.update({k: v for k, v in detectdata.items() if k not in result if detectdata})
                    if isinstance(img_plates, list):
                        img_plates_list.extend(img_plates)
                    elif isinstance(img_plates, str):
                        img_plates_list.append(img_plate)

        # 百度 api
        for image in img_plates_list:
            # imshow(image)
            if not check_decode_info(result, qtype) and bdflag:
                openapidata = openapi(img_to_base64(image))
                self.logger.info(f"第三方接口数据: {openapidata}")
                result.extend(openapidata if openapidata else [])

                from flask import g

                g.openapi_flag = True
        return result

    # 图片预处理，旋转方正并拉伸到407 * 407分辨率
    def prepare_image(self, cut_image, qr_cnt):
        # 最小外接矩形
        min_area_rect = cv2.minAreaRect(qr_cnt)
        # 取角点
        box_points = cv2.boxPoints(min_area_rect)

        # 生成透视变换矩阵
        source_position = np.float32(
            [[box_points[1][0], box_points[1][1]], [box_points[2][0], box_points[2][1]],
             [box_points[0][0], box_points[0][1]], [box_points[3][0], box_points[3][1]]])
        target_position = np.float32([[0, 0], [407, 0], [0, 407], [407, 407]])

        transform = cv2.getPerspectiveTransform(source_position, target_position)

        # 进行透视变换
        transform_image = cv2.warpPerspective(cut_image, transform, (407, 407))
        return transform_image

    def detectimage(self, image, result, qtype):
        # 二维码检测遍历识别
        img_plates = DetectImage.detect(image)
        for img_plate in img_plates:
            # if "let_qrcode" in result and "let_bar_code" in result:
            #     continue
            try:
                # imshow(img_plate)
                # 转化成灰度图
                gray = cv2.cvtColor(img_plate, cv2.COLOR_BGR2GRAY)
                c_h, c_w = gray.shape[: 2]
                fx, fy = 2, 2
                img_plate = cv2.resize(gray, (int(c_w * fx), int(c_h * fy)), interpolation=cv2.INTER_LINEAR)
                # imshow(img_plate)
                # print(f"img_plate shape 111: {img_plate.shape[: 2]}")
                # imshow(gray, 'gray')
                # 高斯平滑
                # gaussian = cv2.GaussianBlur(gray, (1, 1), 0, 0, cv2.BORDER_DEFAULT)
                # imshow(gaussian, 'gaussian')
                # 中值滤波
                # median = cv2.medianBlur(gaussian, 5)
                # imshow(median, 'median')
                data = self.main_decode_img(img_plate, qtype)
                logger.info(f"Detect Image data: {data}")
                # if not data:
                #     baidudata = OcrBaidu().baidurun({'image':img_to_base64(img_plate)})
                #     logger.info(f"OcrBaidu Image data: {baidudata}")
                #     if baidudata.get("codes_result_num",'') !=0 and baidudata.get('codes_result',[]):
                #         data = {
                #             "bddata" : baidudata.get('codes_result',[])[0]
                #         }
                # result.update({k: v for k, v in data.items() if k not in result if data})
                result.extend(data if data else [])
            except Exception as e:
                logger.error(f"data decode error: {e.args}")
                continue
        return result, img_plates

    def main_qrcode(self, image, compose=True, qtype='ConfirmationLetter'):
        return self.main_decode_img(image, qtype)

        # q_result = {}
        # # TODO 图片压缩
        # # 整张图片进行识别
        # q_result.update(
        #     self.main_decode_img(image, qtype)
        #     if self.main_decode_img(image, qtype) else {}
        # )
        # ConfirmationLetter 固定位置裁剪
        # if qtype in ['ConfirmationLetter']:
        #     if "let_qrcode" not in q_result or "let_bar_code" not in q_result:
        #         q_result = self.fixedposition(image, q_result, qtype)
        # else:
        #     q_result = self.detectimage(image, q_result)
        # return q_result
