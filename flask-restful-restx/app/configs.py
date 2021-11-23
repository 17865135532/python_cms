import os
import logging


class BaseConfig:
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUESTS_TIMEOUT = 10
    SIGN_TIMEOUT_TIME = 3600 * 24
    RESTX_MASK_SWAGGER = False
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    JSON_AS_ASCII = False


class CONFIG(BaseConfig):
    DEBUG = int(os.environ.get('DEBUG', 1))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hard to guess string')
    TOKEN_SALT = SECRET_KEY
    TOKEN_EXPIRES_IN = float(os.environ.get('TOKEN_EXPIRES_IN', 3600*2))
    SIGN_EXPIRED_IN = float(os.environ.get('SIGN_EXPIRED_IN', 3600))
    TASK_USER_NAME = os.environ.get('TASK_USER_NAME', 'developer')
    DOC_URL_PATH = os.environ.get('DOC_URL_PATH', '/') if DEBUG else False
    FILE_SECRET = os.environ.get('FILE_SECRET', 'XXX').encode()
    if len(FILE_SECRET) != 16:
        raise Exception('Invalid FILE_SECRET')
    FASTDFS_CONF_PATH = os.environ.get(
        'FASTDFS_CONF_PATH',
        os.path.abspath('./app/dao/fastdfs_test_client.conf'))
    RETURNS_TTL = int(os.environ.get('RETURNS_TTL', 3600*24*7))
    TAX_CLEARANCE_CERTIFICATE_TTL = int(os.environ.get('TAX_CLEARANCE_CERTIFICATE_TTL', 3600*24*7))

    MYSQL_HOST = os.environ.get('MYSQL_HOST', '0.0.0.0')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'admin1234')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'xxx')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'

    REDIS_HOST = os.environ.get('REDIS_HOST', '0.0.0.0')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '123456')

    # celery
    CELERY_BANKED_HOST = REDIS_HOST
    CELERY_BANKED_PORT = REDIS_PORT
    CELERY_BANKED_PASSWORD = REDIS_PASSWORD
    CELERY_BANKED_DB = int(os.environ.get('CELERY_BANKEND_DB', 0))
    CELERY_BROKER_DB = int(os.environ.get('CELERY_BROKER_DB', 1))
    CELERY_BACKEND_URL = f'redis://:{CELERY_BANKED_PASSWORD}@{CELERY_BANKED_HOST}' \
        f':{CELERY_BANKED_PORT}/{CELERY_BANKED_DB}'
    CELERY_BROKER_URL = f'redis://:{CELERY_BANKED_PASSWORD}@{CELERY_BANKED_HOST}' \
        f':{CELERY_BANKED_PORT}/{CELERY_BROKER_DB}'

    LOG_PATH = os.environ.get("LOG_PATH", os.path.join(os.getcwd(), "logs"))

    LOGLEVEL = logging.DEBUG if DEBUG else logging.INFO
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'generic': {
                '()': 'app.utils.logformatter.JsonFormatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': 'process,asctime,name,levelname,message,lineno'
            },
            'access': {
                '()': 'app.utils.logformatter.JsonFormatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': 'process,asctime,message'
            },
            'celery_access': {
                '()': 'app.utils.logformatter.JsonFormatter',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'format': 'process,asctime,name,message'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic'
            },
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
            'celery_task': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': f'{LOG_PATH}/celery_task.log',
                'when': 'MIDNIGHT',
                'interval': 1,
                'formatter': 'generic'
            },
            'celery': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': f'{LOG_PATH}/celery.log',
                'when': 'MIDNIGHT',
                'interval': 1,
                'formatter': 'celery_access'
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
            },
            'celery.task': {
                'handlers': ['celery_task'],
                'level': LOGLEVEL,
                'propagate': False
            },
            'celery': {
                'handlers': ['celery'],
                'level': 'INFO',
                'propagate': False,
            },
            'celery.worker': {
                'handlers': ['celery_task'],
                'level': 'INFO',
                'propagate': False,
            },
            'app.jobs': {
                'handlers': ['celery_task'],
                'level': 'INFO',
                'propagate': False,
            },
            'kombu.mixins': {
                'handlers': ['celery'],
                'level': 'INFO',
                'propagate': False,
            },
            'asyncio': {
                'handlers': ['celery'],
                'level': 'INFO',
                'propagate': False,
            },
            'flower': {
                'handlers': ['celery'],
                'level': 'INFO',
                'propagate': False,
            }
        },
        'root': {
            'handlers': ['file', 'console'] if DEBUG else ['file'],
            'level': LOGLEVEL,
            'propagate': True
        }
    }
