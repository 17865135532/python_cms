import logging
from logging.config import dictConfig
import time

from flask import Flask, request, Blueprint, g, current_app
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
import werkzeug.exceptions

from app.urls import blueprints
from app.dao.mysql import db
from app.exts import migrate, login_manager, babel, nav
from app.configs import CONFIG
from app.utils.routeconverters import RegexConverter
from app.admin import admin
from app.utils import errors


def register_extensions(app):
    app.config.from_object(CONFIG)
    app.config['JSON_AS_ASCII'] = False
    app.url_map.converters['re'] = RegexConverter
    db.init_app(app)
    migrate.init_app(app=app, db=db)
    admin.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    Bootstrap(app)
    CSRFProtect(app)
    nav.init_app(app)


def register_blueprints(app, blueprints):
    """路由封装"""
    for blueprint in blueprints:
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint)
        else:
            raise ValueError(blueprint)


def create_app():
    dictConfig(CONFIG.LOGGING_CONFIG)

    app = Flask(__name__, static_url_path='')

    with app.app_context():
        register_extensions(app)
        register_blueprints(app=app, blueprints=blueprints)

    @app.before_request
    def record_request_from():
        g.request_from = time.time()

    @app.after_request
    def log_access(resp):
        logger = logging.getLogger('access')
        message = {
            'ip': request.remote_addr,
            'method': request.method,
            'path': request.path,
            'request': {
                'args': request.args,
                'form': request.form,
                'json': request.json,
                'files': request.files,
                'cookies': request.cookies,
                'headers': request.headers
            },
            'response': {
                'status_code': resp.status_code
            },
            'cost': time.time() - hasattr(g, 'request_from')
        }
        logger.info(f"{message}")
        return resp

    @app.errorhandler(Exception)
    def on_exception(e):
        logger = logging.getLogger('on_exception')
        if isinstance(e, errors.Error):
            err = e
            logger.log(level=err.log_level, msg=err.log)
        elif (
                isinstance(e, werkzeug.exceptions.NotFound) and
                e.description == 'The requested URL was not found on the server. '
                                 'If you entered the URL manually '
                                 'please check your spelling and try again.'
        ):
            err = errors.ResourceNotFound(errmsg=f'{e.description}:{request.path}')
            logger.log(level=err.log_level, msg=err.log)
        elif (
                isinstance(e, werkzeug.exceptions.MethodNotAllowed) and
                e.description == '405 Method Not Allowed: '
                                 'The method is not allowed for the requested URL.'
        ):
            err = errors.MethodNotAllowed(errmsg=f'{e.description}:[{request.method}]{request.path}')
            logger.log(level=err.log_level, msg=err.log)
        else:
            err = errors.Error(errmsg=str(e))
            logger.log(level=err.log_level, msg=err.log, exc_info=e)
        return err.to_dict_response()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route('/')
    def healthcheck():
        return 'ok'

    @app.route('/favicon.ico')
    def get_fav():
        return current_app.send_static_file('logo.png')
    return app


app = create_app()
