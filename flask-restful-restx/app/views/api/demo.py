import logging

from flask import g
from flask_restx import Resource, Namespace, fields

from app import marshalling_models, constants
from app.utils import errors
from app.parsers import parser_with_auth, json_parser_with_auth, list_parser_with_auth
from app.utils.decorators import check_request, sign_required, authentication_required
from app.dao.mysql import db
from app.models.demo import Demo as DemoModel


__all__ = ['demo_api']
logger = logging.getLogger(__name__)
demo_api = Namespace('demos', path='/demos', description='demo相关API')
creation_schema = {
    "type": "object",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "demo_creation",
    "description": "添加demo",
    "properties": {
        "demo_name": {"description": "demo名称", "type": "string", "max_bytes_len": 15},
    },
    "required": ["demo_name"],
    "additionalProperties": False
}
update_schema = {
    "type": "object",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "demo_update",
    "description": "更新demo",
    "properties": {
        "demo_name": {"description": "demo名称", "type": "string", "max_bytes_len": 15},
    },
    "additionalProperties": False
}
demo_api.models[marshalling_models.base_resp.name] = marshalling_models.base_resp
demo_api.models[marshalling_models.demo_model.name] = marshalling_models.demo_model
crud_resp = demo_api.clone('demo_resp', marshalling_models.base_resp, {
    'data': fields.Nested(marshalling_models.demo_model, skip_none=True)
})
list_resp = demo_api.clone('demos_resp', marshalling_models.base_resp, {
    'data': fields.Nested(
        demo_api.model(
            'demos_data',
            {'demos': fields.List(fields.Nested(marshalling_models.demo_model, skip_none=True))}
        ), skip_none=True
    )
})


@demo_api.route('')
class Demos(Resource):
    logger = logger.getChild('Demos')

    @demo_api.expect(json_parser_with_auth)
    @demo_api.marshal_with(crud_resp)
    @check_request(json_parser_with_auth, creation_schema)
    @authentication_required(
        resource_name=constants.ResourceEnum.demo.name,
        permission_name=constants.Operation.create.name)
    @sign_required
    def post(self):
        demo = DemoModel(demo_name=g.args['demo_name'])
        try:
            demo.save(user=g.user)
        except errors.Error as e:
            logger.log(level=e.log_level, msg=e.log)
            return e.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': demo
        }

    search_parser = list_parser_with_auth.copy()
    search_parser.add_argument('demo_name', type=str)
    search_parser.add_argument('demo_state', type=str, choices=[v.value for k, v in constants.ResourceState.__members__.items()])

    @demo_api.expect(search_parser)
    @demo_api.marshal_with(list_resp)
    @check_request(search_parser)
    @authentication_required(
        resource_name=constants.ResourceEnum.demo.name,
        permission_name=constants.Operation.query.name)
    @sign_required
    def get(self):
        """批量查询demo"""
        cursor = db.session.query(DemoModel)
        if g.args.get('demo_name') is not None:
            cursor = cursor.filter(DemoModel.demo_name.contains(g.args['demo_name']))
        if g.args.get('demo_state') is not None:
            cursor = cursor.filter(DemoModel.demo_state == g.args['demo_state'])
        cursor = cursor.filter_by_create_date_and_page(
            create_date_start=g.args.get('create_date_start'),
            create_date_end=g.args.get('create_date_end'),
            per_page=g.args.get('per_page'), page=g.args.get('page')
        )
        demos = cursor.record().all()
        if not demos:
            err = errors.ResourceNotFound(errmsg='Demos not found')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': {'demos': demos}
        }


@demo_api.route('/<int:demo_id>')
@demo_api.param('demo_id', description='demo id', _in='path')
class Demo(Resource):
    logger = logger.getChild('Demo')

    @demo_api.expect(json_parser_with_auth)
    @demo_api.marshal_with(crud_resp)
    @check_request(json_parser_with_auth, update_schema)
    @authentication_required(
        resource_name=constants.ResourceEnum.demo.name,
        permission_name=constants.Operation.update.name)
    @sign_required
    def post(self, demo_id):
        """更新demo信息"""
        demo = db.session.query(DemoModel).get(demo_id)
        if not demo:
            err = errors.ResourceNotFound(errmsg='Demo not found.')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        try:
            demo.update(g.args, user=g.user)
        except errors.Error as e:
            logger.log(level=e.log_level, msg=e.log)
            return e.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': demo
        }

    @demo_api.expect(parser_with_auth)
    @demo_api.marshal_with(crud_resp)
    @check_request(parser_with_auth)
    @authentication_required(
        resource_name=constants.ResourceEnum.demo.name,
        permission_name=constants.Operation.query.name)
    @sign_required
    def get(self, demo_id):
        """查询demo信息"""
        demo = db.session.query(DemoModel).get_active(demo_id, record=True)
        if not demo:
            err = errors.ResourceNotFound(errmsg='Demo not found.')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': demo
        }
