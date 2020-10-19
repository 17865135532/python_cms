import base64
import glob
import tqdm
import time
import os
import cv2
import requests
import json

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.ocr.v20181119 import ocr_client, models


def imshow(img, name="picture", winnum=0, savepath=None, save_flag=False):
    cv2.namedWindow(name, winnum)
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if save_flag:
        cv2.imwrite(savepath, img)



def get_json(path):
    try:
        cred = credential.Credential("", "")
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
        with open(path, 'rb') as f:
            # base64_data = base64.b64encode(f.read())
            # s = base64_data.decode()
            # ImageBase64_value = 'data:image/jpeg;base64,%s'%s
            # #params是字符串，以下进行拼接
            # params = '{"ImageBase64":"' + ImageBase64_value + '"}' #以图片Base64编码发送请求

            base64data = base64.b64encode(f.read())  # 得到 byte 编码的数据
            base64data = str(base64data, 'utf-8')  # 重新编码数据
            params = '{"ImageBase64":"' + base64data + '"}'
        req.from_json_string(params)
        resp = client.QrcodeOCR(req)
        print(f"腾讯值:{resp.to_json_string()}")

    except TencentCloudSDKException as err:
        print(err)

def get_json_ali(image_path):
    appid = ''
    # 请求头
    headers = {
        'Authorization': f'APPCODE {appid}',  # APPCODE +你的appcod,一定要有空格！！！
        'Content-Type': 'application/json; charset=UTF-8'  # 根据接口的格式来
    }
    host = 'https://qrbarcode.market.alicloudapi.com'
    path = '/api/predict/ocr_qrcode'
    url = host + path
    print(url)
    with open(image_path, 'rb') as f:  # 以二进制读取本地图片
        data = f.read()
        encodestr = str(base64.b64encode(data), 'utf-8')  # base64编码图片
    data = {'image': encodestr}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    ocr_result = {}
    if r.status_code == 200:
        ocr_result = r.json()
    print(f"阿里值:{ocr_result}")
if __name__ == "__main__":
    # test_img_dir = "/home/duanweiye/桌面/询证函_8_21/原始数据/识别失败的图片"
    test_img_dir = "/home/duanweiye/桌面/git/git_pro/qrcode/img_plate_dir"
    file_paths = glob.glob(f"{test_img_dir}/*")
    file_paths.sort()
    result_list = []

    for qpath in tqdm.tqdm(file_paths, ncols=80):
        result = {}
        func_start_time = time.time()
        tqdm.tqdm(file_paths, ncols=80).set_description(f'{os.path.basename(qpath)}')
        print(qpath.split('/')[-1])
        # get_json(qpath)
        get_json_ali(qpath)