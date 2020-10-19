import os
import logging
from datetime import timedelta


class BaseConfig:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUESTS_TIMEOUT = 10
    # SIGN_TIMEOUT_TIME = 3600 * 24
    SIGN_TIMEOUT_TIME = 5 * 60
    RESTX_MASK_SWAGGER = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    FILENAMES = ['png', 'jpeg', 'jpg', 'bmp', 'pdf', 'PDF']
    PDF_FILE = ['pdf', 'PDF']


class CONFIG(BaseConfig):
    ALLOW_IP = ['172.16.5.123', '172.16.207.175']
    DATABASE = {
        # local
        "host": os.environ.get('REDIS_HOST', "127.0.0.1"),
        "port": int(os.environ.get("REDIS_PORT", "6379")),
        'password': os.environ.get("REDIS_PASSWORD", "123456")
    }
    BDFLAG = os.environ.get('BDFLAG', True)
    # 百度
    BDTOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    # 替换 自己的 appid
    BDCLIENT_ID = os.environ.get('BDCLIENT_ID', "")
    BDCLIENT_SECRET = os.environ.get('BDCLIENT_SECRET', "")
    BAIDU_OCR_ACCOUNT = {
        "grant_type": "client_credentials",
        "client_id": BDCLIENT_ID,
        "client_secret": BDCLIENT_SECRET
    }
    BD_QCODE_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/qrcode"

    # Tencent
    SecretId = os.environ.get('SecretId', "")
    SecretKey = os.environ.get('SecretKey', "")

    # ALIYUN
    APP_CODE = ''
    host = 'https://qrbarcode.market.alicloudapi.com'
    path = '/api/predict/ocr_qrcode'
    # url = host + path
    ALI_HOST = host + path

    # 临时文件存储
    TempFileFOLDER = os.environ.get("TempFileFOLDER", os.path.join(os.getcwd(), "temp_data"))
    if not os.path.exists(TempFileFOLDER):
        # os.mkdir(TempFileFOLDER, mode=777)
        os.makedirs(TempFileFOLDER, exist_ok=True)

    PDF_DIR = os.path.join(TempFileFOLDER, 'pdf_file') # pdf文件
    if not os.path.exists(PDF_DIR):
        # os.mkdir(PDF_DIR, mode=777)
        os.makedirs(PDF_DIR, exist_ok=True)

    IMG_PLATE_DIR = os.path.join(TempFileFOLDER, 'img_plate_dir') # 裁剪文件
    if not os.path.exists(IMG_PLATE_DIR):
        # os.mkdir(IMG_PLATE_DIR, mode=777)
        os.makedirs(IMG_PLATE_DIR, exist_ok=True)
    STATIC_FOLDER = os.environ.get('STATIC_FOLDER', 'static')
    STATIC_URL_PATH = os.environ.get('STATIC_URL_PATH', '')
    LOG_PATH = os.environ.get("LOG_PATH", os.path.join(os.getcwd(), "logs"))
    if not os.path.exists(LOG_PATH):
        # os.mkdir(LOG_PATH, mode=777)
        os.makedirs(LOG_PATH, exist_ok=True)
    DEBUG = os.environ.get('DEBUG', 1)
    LOGLEVEL = logging.DEBUG if DEBUG else logging.INFO
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'generic': {
                '()': 'app.utils.logformatter.JsonFormatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': 'process,asctime,name,levelname,message'
            },
            'access': {
                '()': 'app.utils.logformatter.JsonFormatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': 'process,asctime,message'
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': f'{LOG_PATH}/framework.log',
                'when': 'MIDNIGHT',
                'interval': 1,
                'formatter': 'generic'
            },
            'access': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'when': 'MIDNIGHT',
                'interval': 1,
                'filename': f'{LOG_PATH}/access.log',
                'formatter': 'access'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic'
            }
        },
        'loggers': {
            'gunicorn.error': {
                'handlers': ['access'],
                'level': LOGLEVEL,
                'propagate': False
            },
            'access': {
                'handlers': ['access'],
                'level': LOGLEVEL,
                'propagate': False
            },
            'werkzeug': {
                'handlers': ['access'],
                'level': LOGLEVEL,
                'propagate': False
            }
        },
        'root': {
            'handlers': ['file', 'console'] if DEBUG else ['file'],
            'level': LOGLEVEL,
            'propagate': True
        }
    }
