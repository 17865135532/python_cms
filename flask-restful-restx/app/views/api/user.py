import logging

from flask import g
from flask_restx import Resource, Namespace, fields

from app.parsers import parser_with_auth, json_parser, json_parser_with_auth
from app import marshalling_models, constants
from app.utils import errors
from app.utils.decorators import check_request, sign_required, authentication_required
from app.dao.mysql import db
from app.models import User as UserModel


logger = logging.getLogger(__name__)
user_api = Namespace('users', path='/users', description='用户相关API')
login_schema = {
    "type": "object",
    "title": "user_login",
    "description": "用户登录",
    "properties": {
        "user_id": {"description": "用户ID", "type": "integer"},
        "email": {"description": "联系人邮箱", "type": "string", "format": "email"},
        "telephone": {"description": "联系电话", "type": "string"},
        "password": {"description": "密码", "type": "string"},
    },
    "required": ["password"],
    "additionalProperties": False
}
update_schema = {
    "type": "object",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "user_update",
    "description": "更新用户信息",
    "properties": {
        "user_name": {"description": "用户名", "type": "string", "max_bytes_len": 20},
        "password": {"description": "密码", "type": "string"},
        "contact_person": {"description": "联系人", "type": "string", "max_bytes_len": 20},
        "address": {"description": "联系地址", "type": "string", "max_bytes_len": 50},
        "email": {"description": "联系人邮箱", "type": "string", "format": "email", "max_bytes_len": 50},
        "telephone": {"description": "联系电话", "type": "string", "max_bytes_len": 20}
    },
    "additionalProperties": False
}
login_resp = user_api.clone('login_resp', marshalling_models.base_resp, {
    'data': fields.Nested(
        user_api.model(
            'login_data', {
                'check_result': fields.Boolean(title='验证结果', required=True),
                'token': fields.String(title='调用接口所需token')
            }
        ), skip_none=True
    )
})
user_api.models[marshalling_models.base_resp.name] = marshalling_models.base_resp
user_api.models[marshalling_models.user_model.name] = marshalling_models.user_model
crud_resp = user_api.clone('user_resp', marshalling_models.base_resp, {
    'data': fields.Nested(marshalling_models.user_model, skip_none=True)
})


@user_api.route('/<int:uid>')
@user_api.param('uid', description='用户id', _in='path')
class User(Resource):
    logger = logger.getChild('User')

    @user_api.expect(parser_with_auth)
    @user_api.marshal_with(crud_resp)
    @check_request(parser_with_auth)
    @authentication_required(
        resource_name=constants.ResourceEnum.user.name,
        permission_name=constants.Operation.query.name)
    @sign_required
    def get(self, uid):
        """查询用户信息"""
        if uid != g.user.user_id:
            err = errors.ResourceAccessForbidden()
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        user = db.session.query(UserModel).get_active(uid, record=True)
        return {
            'return_code': 200,
            'return_msg': '',
            'data': user
        }

    @user_api.expect(json_parser_with_auth)
    @user_api.marshal_with(crud_resp)
    @check_request(json_parser_with_auth, update_schema)
    @authentication_required(
        resource_name=constants.ResourceEnum.user.name,
        permission_name=constants.Operation.update.name)
    @sign_required
    def post(self, uid):
        """更新用户信息"""
        args = g.args.copy()
        if uid != g.user.user_id:
            e = errors.ResourceAccessForbidden()
            logger.log(level=e.log_level, msg=e.log)
            return e.to_dict_response()
        if g.args.get("password") is not None:
            g.user.pwd = args.pop("password")
        try:
            g.user.update(args, user=g.user)
        except errors.Error as e:
            logger.log(level=e.log_level, msg=e.log)
            return e.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': g.user
        }


@user_api.route('/login')
class UserLogin(Resource):
    logger = logger.getChild('UserLogin')

    @user_api.expect(json_parser)
    @user_api.marshal_with(login_resp)
    @check_request(json_parser, login_schema)
    @sign_required
    def post(self):
        """用户登录"""
        kwargs = g.args
        if kwargs.get('user_id') is not None:
            query = UserModel.user_id == kwargs['user_id']
        elif kwargs.get('telephone') is not None:
            query = UserModel.telephone == kwargs['telephone']
        elif kwargs.get('email') is not None:
            query = UserModel.email == kwargs['email']
        else:
            err = errors.DataParamError(errmsg='user_id/telephone/email is required')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        user = db.session.query(UserModel).active.filter(query).first()
        if not user:
            err = errors.PreconditionRequired(errmsg='User not found')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        check_result = user.verify_pwd(kwargs['password'])
        return {
            'return_code': 200,
            'return_msg': '',
            'data': {
                'check_result': check_result,
                'token': user.gen_token() if check_result else None
            }
        }


@user_api.route('/confirmation/<secret>')
@user_api.param('secret', description='', _in='path')
class UserConfirmation(Resource):
    logger = logger.getChild('UserConfirmation')
