from flask import Blueprint


frontend_v1 = Blueprint("web_v1", __name__, url_prefix='/web')
from app.views.web.frontend import *
