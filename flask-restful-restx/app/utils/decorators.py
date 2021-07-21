import logging
import functools
import time

from flask import g, request
import werkzeug.exceptions
import jwt
import jsonschema

from app.utils.security import load_token, create_sign
from app.utils.types import ensure_int
from app.utils.doc import gen_document_from_jsonschema
from app.utils import errors
from app.utils.validators import MyValidator
from app.configs import CONFIG
from app.models import User
from app.dao.mysql import db


logger = logging.getLogger(__name__)


def authenticate_by_token(token, permission_name=None, resource_name=None):
    try:
        info = load_token(token)
    except jwt.exceptions.PyJWTError as e:
        raise errors.TokenInvalid(errmsg=f'token is invalid: {e}')
    user_id = info.get('user_id')
    if not user_id:
        raise errors.TokenInvalid(errmsg='token payload is incomplete.')
    user = db.session.query(User).get_active(user_id)
    if not user:
        raise errors.TokenInvalid(errmsg='token payload is incorrect.')
    if permission_name and resource_name:
        for role_permission in user.role.role_permissions:
            if all([
                role_permission.role_permission_state is False,
                role_permission.permission.permission_name == permission_name,
                role_permission.resource.resource_name == resource_name]
            ):
                raise errors.ResourceAccessForbidden(errmsg='Role in forbidden')
    return user


def get_user_by_ak(api_key, permission_name=None, resource_name=None):
    user = db.session.query(User).active.filter(User.api_key == api_key).first()
    if not user:
        raise errors.UserNotFound()
    if not user.api_active:
        raise errors.UserApiInactive()
    if permission_name and resource_name:
        for role_permission in user.role.role_permissions:
            resource_permission = role_permission.resource_permission
            if all([
                role_permission.role_permission_state is False,
                resource_permission.permission.permission_name == permission_name,
                resource_permission.resource.resource_name == resource_name]
            ):
                raise errors.ResourceAccessForbidden(errmsg='Role in forbidden')
    return user


def check_request(parser, schema=None):
    def parser_check(func):
        if schema is not None:
            func.__doc__ = gen_document_from_jsonschema(schema)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                g.args = parser.parse_args()
            except werkzeug.exceptions.BadRequest as e:
                return_msg = '\n'.join([f'{v}: {k}.' for k, v in e.data['errors'].items()])
                for field, error in [
                    ('api_key', errors.ApiKeyRequired),
                    ('robot_id', errors.RobotIdRequired),
                    ('token', errors.TokenRequired),
                    ('sign', errors.SignRequired),
                    ('timestamp', errors.TimestampRequired),
                    ('nonce', errors.NonceRequired)
                ]:
                    if field in e.data['errors']:
                        err = error(errmsg=return_msg)
                        logger.log(level=err.log_level, msg=err.log)
                        return err.to_dict_response()
                err = errors.DataParamError(errmsg=return_msg)
                logger.log(level=err.log_level, msg=err.log)
                return err.to_dict_response()
            if schema is not None:
                try:
                    MyValidator(schema=schema).validate(g.args['data'])
                except jsonschema.exceptions.ValidationError as e:
                    err = errors.DataParamError(
                        errmsg=f'{e.message}: data{jsonschema._utils.format_as_index(e.relative_path)}')
                    logger.log(level=err.log_level, msg=err.log)
                    return err.to_dict_response()
                g.args.update(g.args['data'])
            return func(*args, **kwargs)
        return inner
    return parser_check


def authentication_required(resource_name=None, permission_name=None):
    def inner2(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            token = request.headers.get('token')
            api_key = request.headers.get('api_key')
            if token is not None:
                try:
                    user = authenticate_by_token(token, resource_name=resource_name, permission_name=permission_name)
                except errors.Error as e:
                    logger.log(level=e.log_level, msg=e.log)
                    return e.to_dict_response()
                g.auth_method = 'token'
            elif api_key is not None:
                try:
                    user = get_user_by_ak(api_key, resource_name=resource_name, permission_name=permission_name)
                except errors.Error as e:
                    logger.log(level=e.log_level, msg=e.log)
                    return e.to_dict_response()
                g.auth_method = 'ak'
            else:
                err = errors.AuthParamsRequired()
                logger.log(level=err.log_level, msg=err.log)
                return err.to_dict_response()
            g.user = user
            return func(*args, **kwargs)
        return inner
    return inner2


def ad_authentication_required(robot_required=False, resource_name=None, permission_name=None):
    def inner2(func):
        required_roles = ['administrator']

        @functools.wraps(func)
        def inner(*args, **kwargs):
            token = request.headers.get('token')
            api_key = request.headers.get('api_key')
            robot_id = request.headers.get('robot_id')
            if robot_required and robot_id is None:
                err = errors.RobotIdRequired()
                logger.log(level=err.log_level, msg=err.log)
                return err.to_dict_response()
            if token is not None:
                try:
                    g.user = authenticate_by_token(token, resource_name=resource_name, permission_name=permission_name)
                    g.auth_method = 'token'
                except errors.Error as e:
                    logger.log(level=e.log_level, msg=e.log)
                    return e.to_dict_response()
                if not g.user.role:
                    err = errors.Error(errmsg='user`s role missing')
                    logger.log(level=err.log_level, msg=err.log)
                    return err.to_dict_response()

                if g.user.role.role_name not in required_roles:
                    err = errors.ResourceAccessForbidden(errmsg='role forbidden')
                    logger.log(level=err.log_level, msg=err.log)
                    return err.to_dict_response()
            elif api_key is not None:
                try:
                    g.user = get_user_by_ak(api_key, resource_name=resource_name, permission_name=permission_name)
                    g.auth_method = 'ak'
                except errors.Error as e:
                    logger.log(level=e.log_level, msg=e.log)
                    return e.to_dict_response()

                if not g.user.role:
                    err = errors.Error(errmsg='user`s role missing')
                    logger.log(level=err.log_level, msg=err.log)
                    return err.to_dict_response()

                if g.user.role.role_name not in required_roles:
                    err = errors.ResourceAccessForbidden(errmsg='role forbidden')
                    logger.log(level=err.log_level, msg=err.log)
                    return err.to_dict_response()
            elif robot_id is not None:
                try:
                    # g.robot = get_robot(robot_id)
                    g.user = None
                    if 'ip' not in request.headers:
                        err = errors.AuthParamsRequired(errmsg='ip is required.')
                        logger.log(level=err.log_level, msg=err.log)
                        return err.to_dict_response()
                    if request.headers['ip'] != g.robot.ip:
                        err = errors.RobotInvalid(errmsg='Robot ip invalid')
                        logger.log(level=err.log_level, msg=err.log)
                        return err.to_dict_response()
                    g.auth_method = 'robot_id'
                except errors.RobotNotFound as e:
                    logger.log(level=e.log_level, msg=e.log)
                    return e.to_dict_response()
            else:
                err = errors.AuthParamsRequired()
                logger.log(level=err.log_level, msg=err.log)
                return err.to_dict_response()
            return func(*args, **kwargs)
        return inner
    return inner2


def sign_required(func):
    # NOTE:需身份认证接口，必须在执行此装饰器前执行身份认证装饰器
    @functools.wraps(func)
    def inner(*args, **kwargs):
        timestamp = request.headers.get('timestamp')
        if not timestamp:
            err = errors.TimestampRequired()
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        try:
            timestamp = ensure_int(timestamp)
        except (TypeError, ValueError) as e:
            err = errors.ParamError(errmsg='timestamp is required to be integer.')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        if time.time() - timestamp > CONFIG.SIGN_EXPIRED_IN:
            err = errors.SignExpired(
                errmsg=f"Expired {time.time() - timestamp - CONFIG.SIGN_EXPIRED_IN} seconds.")
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()

        nonce = request.headers.get('nonce')
        if not nonce:
            err = errors.NonceRequired()
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()

        sign = request.headers.get('sign')
        if not sign:
            err = errors.SignRequired()
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()

        token = request.headers.get('token')
        api_key = request.headers.get('api_key')
        robot_id = request.headers.get("robot_id")
        if api_key:
            token_or_secret = g.user.sk
        elif robot_id:
            token_or_secret = g.robot.sk
        else:
            token_or_secret = token
        values = request.values.copy()
        if request.json:
            values.update(request.json)
        expected_sign = create_sign(
            values, timestamp=timestamp, nonce=nonce,
            token_or_secret=token_or_secret, skip_fields=request.files.keys())
        if expected_sign != sign:
            err = errors.SignInvalid()
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return func(*args, **kwargs)
    return inner
