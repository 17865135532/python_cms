import logging
from datetime import datetime

from flask import request
from flask_restx.reqparse import RequestParser
import ujson

from app.utils.security import decrypt


logger = logging.getLogger(__name__)


def decrypt_json_body(text):
    try:
        decrypted_data = decrypt(text, request.headers['key'])
    except Exception as e:
        logger.warning(f'Decrypt exception: {text}', exc_info=e)
        raise ValueError('decrypt error')
    try:
        return ujson.loads(decrypted_data)
    except Exception as e:
        logger.warning(f'Load exception: {decrypted_data}', exc_info=e)
        raise ValueError('load error')


base_parser = RequestParser()
base_parser.add_argument('timestamp', location='headers', type=int, required=True, nullable=False, help='时间戳')
base_parser.add_argument('nonce', location='headers', type=str, required=True, nullable=False, help='随机字符串')
base_parser.add_argument('sign', location='headers', type=str, required=True, nullable=False, help='校验和')

json_parser = base_parser.copy()
# 定义基础参数
json_parser.add_argument('key', location='headers', type=str, required=True, nullable=False, help='加密后的密钥')
json_parser.add_argument('data', location='json', type=decrypt_json_body, required=True, nullable=False, help='加密后的json数据')

form_parser = base_parser.copy()
form_parser.add_argument('key', location='headers', type=str, required=True, nullable=False, help='加密后的密钥')
form_parser.add_argument('data', location='form', type=decrypt_json_body, required=True, nullable=False, help='加密后的form数据')

list_parser = base_parser.copy()
list_parser.add_argument(
    'create_date_start', location='args',
    type=lambda x: datetime.strptime(x, '%Y-%m-%d'), help='创建时间不早于, 格式为yyyy-MM-DD')
list_parser.add_argument(
    'create_date_end', location='args',
    type=lambda x: datetime.strptime(x, '%Y-%m-%d'), help='创建时间不晚于, 格式为yyyy-MM-DD')
list_parser.add_argument('page', location='args', type=int, default=1, help='页码')
list_parser.add_argument('per_page', location='args', type=int, help='每页条数,为空时返回全部')

parser_with_auth = base_parser.copy()
parser_with_auth.add_argument('api_key', location='headers', type=str)
parser_with_auth.add_argument('token', location='headers', type=str)

json_parser_with_auth = json_parser.copy()
json_parser_with_auth.add_argument('api_key', location='headers', type=str)
json_parser_with_auth.add_argument('token', location='headers', type=str)

list_parser_with_auth = list_parser.copy()
list_parser_with_auth.add_argument('api_key', location='headers', type=str)
list_parser_with_auth.add_argument('token', location='headers', type=str)


parser_with_ad_auth = base_parser.copy()
parser_with_ad_auth.add_argument('api_key', location='headers', type=str)
parser_with_ad_auth.add_argument('robot_id', location='headers', type=str)
parser_with_ad_auth.add_argument('ip', location='headers', type=str)

json_parser_with_ad_auth = json_parser.copy()
json_parser_with_ad_auth.add_argument('api_key', location='headers', type=str)
json_parser_with_ad_auth.add_argument('robot_id', location='headers', type=str)
json_parser_with_ad_auth.add_argument('ip', location='headers', type=str)

form_parser_with_ad_auth = form_parser.copy()
form_parser_with_ad_auth.add_argument('api_key', location='headers', type=str)
form_parser_with_ad_auth.add_argument('robot_id', location='headers', type=str)
form_parser_with_ad_auth.add_argument('ip', location='headers', type=str)

list_parser_with_ad_auth = list_parser.copy()
list_parser_with_ad_auth.add_argument('api_key', location='headers', type=str)
list_parser_with_ad_auth.add_argument('robot_id', location='headers', type=str)
list_parser_with_ad_auth.add_argument('ip', location='headers', type=str)

