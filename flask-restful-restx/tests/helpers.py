import time
import random
import string

import ujson

from app.utils.security import create_token, create_sign, encrypt


def validate_resp(rv, expected_return_code=200, path=None, method=None, data=None):
    assert rv.status_code == 200, (rv.status_code, str(rv.data))
    assert rv.is_json, str(rv.data)
    res = rv.json
    if expected_return_code is not None:
        assert res.get('return_code') == expected_return_code, res
    assert isinstance(res.get('data', {}), dict), res
    assert isinstance(res.get('return_msg', ""), str), res
    return res


def format_headers_and_body(raw_body=None, params=None, auth_method='ak', token=None, ak=None, sk=None):
    if raw_body is not None:
        encrypt_res = encrypt(ujson.dumps(raw_body))
        data = encrypt_res['data']
        key = encrypt_res['key']
        body = {
            'data': data
        }
    else:
        body = {}
        key = None
    timestamp = str(int(time.time()))
    nonce = ''.join(random.sample(string.ascii_letters, 5))
    headers = {
        'timestamp': timestamp,
        'nonce': nonce,
    }
    if key is not None:
        headers['key'] = key
    if auth_method == 'ak':
        ak = ak or '10162afcc69f36ec94bebb560fe2bd5f'
        sk = sk or '978a714c5eac4063b9f9703d2f9ec0e2'
        token_or_secret = sk
        headers['api_key'] = ak
    elif auth_method == 'token':
        token_or_secret = token = token or create_token({"user_id": 1})
        headers['token'] = token
    elif auth_method == 'robot_id':
        robot_id = str(1)
        token_or_secret = secret = "c4076c2f0e6847f09a5d685dc674aad0"
        headers['robot_id'] = robot_id
    elif auth_method is None:
        token_or_secret = None
    else:
        raise ValueError(auth_method)
    values = {}
    if body:
        values.update(body)
    if params:
        values.update(params)
    headers['sign'] = create_sign(values, timestamp, nonce, token_or_secret=token_or_secret)
    return headers, body or None
