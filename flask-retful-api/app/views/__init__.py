from flask import Blueprint
from flask_restx import Api

from app.views.qrcode_decode import qrcode_api
from app.views.user import user_api

v1 = Blueprint("v1", __name__, url_prefix='/api/v1')
api_v1 = Api(v1)


api_v1.add_namespace(qrcode_api)
api_v1.add_namespace(user_api)
