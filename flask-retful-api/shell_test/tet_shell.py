#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :test_shell.py
# @Time      :2020/9/2 下午4:45

import base64
import zxing
import glob, imageio
import io
import os
import time
import tqdm
from PIL import Image, ImageEnhance
import pandas as pd
import numpy as np
import numpy
import cv2
import uuid
import logging
import requests
import json


def imshow(img, name="picture", winnum=0, savepath=None, save_flag=False):
    cv2.namedWindow(name, winnum)
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if save_flag:
        cv2.imwrite(savepath, img)


def category_re(url, file_path):
    files = {'imagefile': open(file_path, 'rb')}
    print(url)
    data_parame = {
        'qtype': 'ConfirmationLetter',
    }
    res = requests.post(url, files=files, data=data_parame)
    print('result------->', json.loads(res.text))
    res_data = json.loads(res.text)
    return res_data


def deal_col_data(dec_info,qtype='ConfirmationLetter'):
    result_flag = {}
    for q_code in dec_info:
        for k, v in q_code.items():
            if k in ['QRCODE', "QR_CODE"]:
                # let_qrcode let_bar_code 询证函字段
                if len(v) < 30:
                    result_flag['let_qrcode'] = v
                else:
                    result_flag['other_QRCODE'] = v
            elif k in ['CODE128', 'CODE_128']:
                if "-" in v:
                    result_flag['let_bar_code'] = v
                else:
                    result_flag['other_CODE128'] = v
            else:
                result_flag[k] = v

    return result_flag


def main():
    # test_img_dir = r"/home/duanweiye/桌面/询证函_8_21/原始数据/pdf_to_image_dir/img_path"
    # test_img_dir = r"/home/duanweiye/桌面/TZ_总测试数据/100/invoice_choices_img"
    # test_img_dir = "/home/duanweiye/桌面/询证函_8_21/原始数据/识别失败的图片"
    test_img_dir = "/home/duanweiye/桌面/询证函_8_21/原始数据/tielu"
    # test_img_dir = r"/home/duanweiye/桌面/询证函_8_21/原始数据/pdf_to_image_dir/img_path"
    # test_img_dir = r"/home/duanweiye/桌面/询证函_8_21/原始数据/返回多值图片"
    # test_img_dir = r"/home/duanweiye/桌面/TZ_总测试数据/invoice_chose_img_100"
    url = 'http://127.0.0.1:8006/api/v1/qrcode'
    file_paths = glob.glob(f"{test_img_dir}/*")
    file_paths.sort()
    result_list = []

    for qpath in tqdm.tqdm(file_paths, ncols=80):
        result = {}
        func_start_time = time.time()
        tqdm.tqdm(file_paths, ncols=80).set_description(f'{os.path.basename(qpath)}')
        print(qpath.split('/')[-1])
        data = category_re(url=url, file_path=qpath)
        print(f"执行时间: {time.time() - func_start_time}")

        result = deal_col_data(data.get('data'))
        result['filename'] = qpath.split('/')[-1]
        result["time"] = time.time() - func_start_time
        result["time"] = time.time() - func_start_time
        result_list.append(result)

    df = pd.DataFrame(result_list)
    # df.to_csv('./询证函解码数据_增加固定位置切割识别_定位检测_灰度亮度增加判断.csv', encoding='utf_8_sig')
    df.to_csv('./invoice_plt_9_11_bd_包含物流单.csv', encoding='utf_8_sig')
    df.to_csv('./invoice_plt_9_11_bd', encoding='utf_8_sig')
    dic_ = df.to_dict(orient="records")
    sum_count = df.shape[0]
    let_qrcode_na_count = (df['let_qrcode'].isna()).sum()
    let_bar_code_na_count = (df['let_bar_code'].isna()).sum()
    ii = 0
    for q in dic_:
        if q.get('let_qrcode') in ['nan', np.nan] and q.get('let_bar_code') in ['nan', np.nan]:
            ii += 1
        print(
            {'df_shape': df.shape[0],
             'let_qrcode': f"{(sum_count - let_qrcode_na_count) / sum_count}%",
             'let_bar_code': f"{(sum_count - let_bar_code_na_count) / sum_count}%",
             'let_bar__qrcode': f"{(sum_count - ii) / sum_count}%",
             }
        )



def bs64_img():
    # test_img_dir = r"/home/duanweiye/桌面/TZ_总测试数据/100/invoice_choices_img"




if __name__ == "__main__":
    main()
