#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import time
from logging.config import dictConfig

from flask import Flask, Blueprint, request

from app.urls import blueprints
from app.configs import CONFIG


def register_blueprints(app, blueprints):
    """路由封装"""
    for blueprint in blueprints:
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint)
        else:
            raise ValueError(blueprint)


def create_app():
    dictConfig(CONFIG.LOGGING_CONFIG)
    app = Flask(__name__, static_folder=CONFIG.STATIC_FOLDER, static_url_path=CONFIG.STATIC_URL_PATH)
    app.config.from_object(CONFIG)
    with app.app_context():
        # register_extensions(app)
        register_blueprints(app=app, blueprints=blueprints)

    # 中间件
    @app.before_request
    def log_access():
        logger = logging.getLogger('access')
        request.request_start = time.time()
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
        }
        #
        # if request.method not in ['/api/v1/qrcode']:
        #     message['request'] = {
        #         'args': request.args,
        #         'form': request.form,
        #         'json': request.json,
        #         'files': request.files,
        #         'cookies': request.cookies,
        #         'headers': request.headers
        #     }
        logger.info(f"{message}")

    @app.after_request
    def log_access(response):
        """验证token"""
        logger = logging.getLogger('access_log')
        message = {
            'ip': request.remote_addr,
            'method': request.method,
            'path': request.path,
            'response': {
                'status_code': response.status_code
            }
        }
        if hasattr(request, 'request_start'):
            message['elapsed'] = time.time() - request.request_start
        if response.status_code == 200 and response.json and isinstance(response.json, dict):
            message['response']['return_code'] = return_code = response.json.get('return_code')
            if return_code != 200:
                message['response']['return_msg'] = response.json.get('return_msg')
        logger.info(message)
        return response

    @app.errorhandler(Exception)
    def on_exception(e):
        logger = logging.getLogger('on_exception')
        logger.critical('Unknown error:', exc_info=e)
        return {
            'return_code': 500,
            'return_msg': str(e)
        }

    # healthcheck
    @app.route('/')
    def healthcheck():
        return 'I am ok'

    return app


app = create_app()
