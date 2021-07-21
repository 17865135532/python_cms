from flask_restx import fields, Model


base_resp = Model('Body', {
    'return_code': fields.Integer(title='返回码', description='200为成功', example=200, required=True),
    'return_msg': fields.String(title='返回信息', description='成功时可为空字符串', example='Success', required=True)
})
resource_model = Model('ResourceModel', {
    'created_by': fields.Integer(title='创建者ID', example=1, required=True),
    'created_at': fields.String(title='创建时间', example='2020-01-01 08:00:00', required=True),
    'updated_by': fields.Integer(title='更新者ID', example=1),
    'updated_at': fields.String(title='更新时间', example='2020-01-01 08:00:01')
})
user_model = resource_model.clone('user', {
    "user_id": fields.Integer(title="用户ID"),
    'user_name': fields.String(title="用户名"),
    'contact_person': fields.String(title="联系人"),
    'address': fields.String(title="联系地址"),
    'email': fields.String(title="联系人邮箱"),
    'telephone': fields.String(title="联系电话"),
    'api_key': fields.String(title="接口id"),
    'secret_key': fields.String(
        title="接口密钥",
        attribute=lambda x: x.sk if x and x.sk else None)
})
demo_model = resource_model.clone('demo', {
    "demo_id": fields.Integer(title="demo id"),
    'demo_name': fields.String(title="demo名称"),
    'demo_state': fields.String(title="demo状态")
})
