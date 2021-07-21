#!/usr/bin/python
# -*- encoding: utf-8 -*-

import logging

from flask import g
from flask_restx import Resource, Namespace, fields

from app import marshalling_models, constants
from app.parsers import parser_with_auth

logger = logging.getLogger(__name__)

qrcode_api = Namespace('qrcode', description='二维码,条形码 解码相关API')


