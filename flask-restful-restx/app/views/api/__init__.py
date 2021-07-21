from flask import Blueprint
from flask_restx import Api

from app.views.api.user import user_api
from app.configs import CONFIG
from app.utils import errors
from app.views.api.demo import demo_api


v1 = Blueprint("v1", __name__, url_prefix='/api/v1')
api_v1 = Api(v1, title='普通用户接口', doc=CONFIG.DOC_URL_PATH, description=errors.gen_doc())
api_v1.add_namespace(user_api)
api_v1.add_namespace(demo_api)
