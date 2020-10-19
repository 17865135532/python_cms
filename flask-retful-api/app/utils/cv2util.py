#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :cvutil.py
import cv2
import os


def mkdir_(dirname='img_plate_dir'):
    img_plate_dir = os.path.join(os.path.abspath('.'), dirname)
    if not os.path.exists(img_plate_dir):
        os.mkdir(img_plate_dir)

def imshow(img, name="picture", winnum=0, savepath=None, save_flag=False):
    cv2.namedWindow(name, winnum)
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if save_flag:
        cv2.imwrite(savepath, img)