import logging

from flask import g, request
from flask_restx import Resource, Namespace, fields

from app.parsers import parser_with_ad_auth, json_parser_with_ad_auth, list_parser_with_ad_auth
from app import marshalling_models, constants
from app.utils.decorators import check_request, sign_required, ad_authentication_required
from app.utils.code import gen_api_key, gen_secret_key
from app.utils import errors
from app.models import User as UserModel, Role as RoleModel
from app.dao.mysql import db


logger = logging.getLogger(__name__)
user_api = Namespace('users', path='/users', description='用户相关API')
creation_schema = {
    "title": "user_creation",
    "description": "创建用户",
    "type": "object",
    "properties": {
        "user_name": {"description": "用户名", "type": "string", "max_bytes_len": 20},
        "password": {"description": "密码", "type": "string"},
        "contact_person": {"description": "联系人", "type": "string", "max_bytes_len": 20},
        "address": {"description": "联系地址", "type": "string", "max_bytes_len": 50},
        "email": {"description": "联系人邮箱", "type": "string", "format": "email", "max_bytes_len": 50},
        "telephone": {"description": "联系电话", "type": "string", "max_bytes_len": 20}
    },
    "required": ["user_name", "password", "contact_person", "address", "email", "telephone"],
    "additionalProperties": False
}
update_schema = {
    "title": "user_update",
    "description": "更新用户信息",
    "type": "object",
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
# 响应体model
user_api.models[marshalling_models.base_resp.name] = marshalling_models.base_resp
user_api.models[marshalling_models.user_model.name] = marshalling_models.user_model
crud_resp = user_api.clone('user_resp', marshalling_models.base_resp, {
    'data': fields.Nested(marshalling_models.user_model, skip_none=True)
})
list_resp = user_api.clone('user_list_resp', marshalling_models.base_resp, {
    'data': fields.Nested(
        user_api.model('user_list_data', {
            'users': fields.List(
                fields.Nested(marshalling_models.user_model, skip_none=True))
        }), skip_none=True
    )
})


@user_api.route('')
class Users(Resource):
    logger = logger.getChild('Users')

    @user_api.expect(json_parser_with_ad_auth)
    @user_api.marshal_with(crud_resp)
    @check_request(json_parser_with_ad_auth, creation_schema)
    @ad_authentication_required(
        resource_name=constants.ResourceEnum.user.name,
        permission_name=constants.Operation.create.name)
    @sign_required
    def post(self):
        """创建用户"""
        role = db.session.query(RoleModel).active.filter(
            RoleModel.role_name == 'customer').first()
        user = UserModel(
            user_name=g.args['user_name'],
            contact_person=g.args['contact_person'],
            address=g.args['address'],
            email=g.args['email'],
            telephone=g.args['telephone'],
            role_id=role.role_id,
            ip=request.remote_addr,
            api_key=gen_api_key(g.args['email'])
        )
        user.pwd = g.args['password']
        user.sk = gen_secret_key()
        try:
            user.save()
        except errors.Error as err:
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': user
        }

    search_parser = list_parser_with_ad_auth.copy()
    search_parser.add_argument(
        'user_state', type=str, choices=[v.name for k, v in constants.ResourceState.__members__.items()])

    @user_api.expect(search_parser)
    @user_api.marshal_with(list_resp)
    @check_request(search_parser)
    @ad_authentication_required(
        resource_name=constants.ResourceEnum.user.name,
        permission_name=constants.Operation.query.name)
    @sign_required
    def get(self):
        """批量查询用户"""
        kwargs = g.args
        cursor = db.session.query(UserModel)
        if kwargs.get('user_state') is not None:
            cursor = cursor.filter(UserModel.user_state==kwargs['user_state'])
        cursor = cursor.filter_by_create_date_and_page(
            create_date_start=kwargs.get('create_date_start'),
            create_date_end=kwargs.get('create_date_end'),
            per_page=kwargs.get('per_page'), page=kwargs.get('page')
        )
        users = cursor.record().all()
        if not users:
            err = errors.ResourceNotFound(errmsg='users not found')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': {'users': users}
        }


@user_api.route('/<int:uid>')
@user_api.param('uid', _in='path', description='用户id')
class User(Resource):
    logger = logger.getChild('User')

    @user_api.expect(json_parser_with_ad_auth)
    @user_api.marshal_with(crud_resp)
    @check_request(json_parser_with_ad_auth, update_schema)
    @ad_authentication_required(
        resource_name=constants.ResourceEnum.user.name,
        permission_name=constants.Operation.update.name)
    @sign_required
    def post(self, uid):
        """修改用户信息"""
        args = g.args.copy()
        user = db.session.query(UserModel).get(uid)
        if not user:
            e = errors.ResourceNotFound(errmsg='User not found')
            logger.log(level=e.log_level, msg=e.log)
            return e.to_dict_response()
        if g.args.get('password'):
            user.pwd = args.pop('password')
        try:
            user.update(args)
        except errors.Error as err:
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': user
        }

    @user_api.expect(parser_with_ad_auth)
    @user_api.marshal_with(crud_resp)
    @check_request(parser_with_ad_auth)
    @ad_authentication_required(
        resource_name=constants.ResourceEnum.user.name,
        permission_name=constants.Operation.query.name)
    @sign_required
    def get(self, uid):
        """查询用户信息"""
        user = db.session.query(UserModel).get_active(uid, record=True)
        if not user:
            err = errors.ResourceNotFound(errmsg='User not found.')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': user
        }
