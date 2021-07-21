from flask import Blueprint
from flask_restx import Api

from app.views.ad.user import user_api
from app.configs import CONFIG
from app.utils import errors


__all__ = ['ad_v1']
ad_v1 = Blueprint("ad_v1", __name__, url_prefix='/api/v1/ad')
api_ad_v1 = Api(ad_v1, title='管理员/机器人接口', doc=CONFIG.DOC_URL_PATH, description=errors.gen_doc())
api_ad_v1.add_namespace(user_api)
