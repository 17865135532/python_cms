import time
import logging
import hashlib
import binascii

import jwt
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_v1_5
from binascii import b2a_hex, a2b_hex
from flask import request

from app.configs import CONFIG


logger = logging.getLogger(__name__)


def _md5(content):
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.md5(content).hexdigest()


def create_sign(values, timestamp, nonce, token_or_secret=None, skip_fields=None):
    _logger = logger.getChild('create_sign')
    if token_or_secret is None:
        token_or_secret = ''
    data = {}
    for key, val in values.items():
        if key in ['token', 'timestamp', 'sign', 'key']:
            continue
        if not isinstance(val, (int, str)):
            continue
        if skip_fields and key in skip_fields:
            continue
        data[key] = str(val)
    content = ''.join([f'{k}{v}' for k, v in sorted(data.items(), key=lambda item: item[0])])
    sign_str = f'{token_or_secret}.{nonce}{timestamp}.{content}'
    _logger.debug(f'sign str: {sign_str[:100]}')
    return _md5(sign_str).upper()


def create_token(info, algorithm='HS256'):
    now = int(time.time())
    exp = int(now + CONFIG.TOKEN_EXPIRES_IN)
    headers = {
        "alg": algorithm,
        "typ": "JWT"
    }
    payload = {
        'iat': now,
        'nbf': now,
        'exp': exp
    }
    for key in payload:
        if key in info:
            raise KeyError(key)
    payload.update(info)
    return jwt.encode(payload=payload, headers=headers, key=CONFIG.TOKEN_SALT, algorithm=algorithm).decode('utf-8')


def load_token(token, algorithm='HS256', verify=True):
    return jwt.decode(token, CONFIG.TOKEN_SALT, verify=verify, algorithms=algorithm)


def add_to_16(text):
    # 如果text不足16位的倍数就用空格补足为16位
    if not isinstance(text, bytes):
        text = text.encode('utf-8')
    if len(text) % 16:
        add = 16 - (len(text) % 16)
    else:
        add = 0
    text = text + (b'\0' * add)
    return text


def create_rsa_key(password="123456"):
    """
    创建RSA密钥
    步骤说明：
    1、从 Crypto.PublicKey 包中导入 RSA，创建一个密码
    2、生成 1024/2048 位的 RSA 密钥
    3、调用 RSA 密钥实例的 exportKey 方法，传入密码、使用的 PKCS 标准以及加密方案这三个参数。
    4、将私钥写入磁盘的文件。
    5、使用方法链调用 publickey 和 exportKey 方法生成公钥，写入磁盘上的文件。
    """
    key = RSA.generate(1024)
    encrypted_key = key.exportKey(
        passphrase=password, pkcs=8, protection="scryptAndAES128-CBC")
    with open("../my_private_rsa_key.bin", "wb") as f:
        f.write(encrypted_key)
    with open("../my_rsa_public.pem", "wb") as f:
        f.write(key.publickey().exportKey())


def rsa_long_encrypt(text, length=100):
    """
    单次加密串的长度最大为 (key_size/8)-11
    1024bit的证书用100， 2048bit的证书用 200
    """
    if isinstance(text, str):
        text = text.encode()
    recipient_key = RSA.import_key(open("app/my_rsa_public.pem").read())
    cipher_rsa = PKCS1_v1_5.new(recipient_key)
    res = []
    for i in range(0, len(text), length):
        res.append(cipher_rsa.encrypt(text[i:i+length]))
    return b"".join(res)


def rsa_long_decrypt(text, length=128, password="123456"):
    """
    1024bit的证书用128，2048bit证书用256位
    """
    recipient_key = RSA.import_key(
        open("app/my_private_rsa_key.bin").read(),
        passphrase=password)
    cipher_rsa = PKCS1_v1_5.new(recipient_key)
    res = []
    for i in range(0, len(text), length):
        res.append(cipher_rsa.decrypt(text[i:i+length], None))
    return b"".join(res)


def rsa_encrypt(text):
    if isinstance(text, str):
        text = text.encode()
    recipient_key = RSA.import_key(open("app/my_rsa_public.pem").read())
    cipher_rsa = PKCS1_v1_5.new(recipient_key)
    enc_text = cipher_rsa.encrypt(text)
    return binascii.hexlify(enc_text).decode()


def rsa_decrypt(enc_text, password="123456"):
    enc_text = binascii.unhexlify(enc_text.encode())
    private_key = RSA.import_key(open("app/my_private_rsa_key.bin").read(),
                                 passphrase=password)
    cipher_rsa = PKCS1_v1_5.new(private_key)
    return cipher_rsa.decrypt(enc_text, None)


def aes_encrypt(text, key):
    cipher_aes = AES.new(key, AES.MODE_ECB)
    return cipher_aes.encrypt(add_to_16(text))


def aes_decrypt(text, key, a2b=True):
    cipher_aes = AES.new(key, AES.MODE_ECB)
    if a2b:
        text = a2b_hex(text)
    data = cipher_aes.decrypt(text)
    return data.rstrip(b'\0')


def encrypt(text, session_key=None):
    if session_key is None:
        session_key = get_random_bytes(16)
    enc_session_key = rsa_encrypt(session_key)
    ciphertext = b2a_hex(aes_encrypt(text, session_key)).decode()
    return {
        'data': ciphertext,
        'key': enc_session_key
    }


def decrypt(data, enc_session_key, password="123456"):
    session_key = rsa_decrypt(enc_session_key, password)
    return aes_decrypt(data, session_key).decode("utf-8")


if __name__ == '__main__':
    pass
