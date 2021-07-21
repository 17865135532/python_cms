#!/usr/bin/python
import logging

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import request

from app.dao.mysql import db
from app.models.base_model import (
    BaseModel, CreationMixin, UpdationMixin,
    UserOperationLog, ApiOperationLog, AdminOperationLog, AdminApiOperationLog)
from app import constants
from app.utils.security import create_token, rsa_encrypt, rsa_decrypt
from app.utils.helpers import get_role_and_situation


logger = logging.getLogger(__name__)


class User(BaseModel, CreationMixin, UpdationMixin, UserMixin):
    __tablename__ = "sys_user"
    __table_args__ = {'comment': '用户表'}

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="用户id")
    user_name = db.Column(db.String(20), nullable=False, comment="用户名")
    password = db.Column(db.String(100), nullable=False, comment="用户密码（加密）")
    email = db.Column(db.String(50), unique=True, nullable=False, comment="邮箱地址")
    telephone = db.Column(db.String(20), unique=True, nullable=False, comment="电话号码")
    address = db.Column(db.String(50), nullable=False, comment="联系地址")
    contact_person = db.Column(db.String(20), nullable=False, comment="联系人")
    ip = db.Column(db.String(20), nullable=False, comment="注册时的ip")
    user_state = db.Column(db.String(20), nullable=False, default=constants.UserState.active.value, comment="用户状态")
    api_key = db.Column(db.String(32), nullable=False, index=True, comment="接口id")
    secret_key = db.Column(db.String(256), nullable=False, comment="接口密钥(加密)")
    api_state = db.Column(db.String(10), nullable=False, default=constants.ResourceState.active.value, comment="接口状态")
    role_id = db.Column(db.Integer, nullable=False, comment="用户角色")

    create_user = db.relationship(
        "User", remote_side=[user_id],
        primaryjoin='foreign(User.created_by)==User.user_id', post_update=True)
    update_user = db.relationship(
        "User", remote_side=[user_id],
        primaryjoin='foreign(User.updated_by)==User.user_id', post_update=True)
    created_roles = db.relationship(
        'Role', backref='create_user',
        primaryjoin='foreign(Role.created_by)==User.user_id')
    updated_roles = db.relationship(
        'Role', backref='update_user',
        primaryjoin='foreign(Role.updated_by)==User.user_id')
    created_demos = db.relationship(
        'Demo', backref='create_user',
        primaryjoin='foreign(Demo.created_by)==User.user_id')
    updated_demos = db.relationship(
        'Demo', backref='update_user',
        primaryjoin='foreign(Demo.updated_by)==User.user_id')

    @property
    def pwd(self):
        raise AttributeError('password is not a readable attribute')

    @pwd.setter
    def pwd(self, value):
        self.password = generate_password_hash(value)

    def verify_pwd(self, password):
        role_and_situation = get_role_and_situation()
        tables_mapping = {
            role_and_situation: m
            for m in [UserOperationLog, ApiOperationLog, AdminOperationLog, AdminApiOperationLog]
            for role_and_situation in m.role_and_situations
        }
        try:
            op = constants.Operation.login.value
            role = role_and_situation.get('role')
            situation = role_and_situation.get('situation')
            log_model = tables_mapping[(role, situation)]
            log_model(
                user_name=self.user_name,
                operation=op,
                object_type=self.__table_args__.get("comment") or self.__tablename__,
                object_id=self.user_id,
                user_ip=request.remote_addr,
                created_by=self.user_id
            ).save(user=self)
        except Exception as e:
            logger.error('', exc_info=e)
        return check_password_hash(self.password, password)

    def gen_token(self):
        return create_token({'user_id': self.user_id})

    @property
    def sk(self):
        try:
            return rsa_decrypt(self.secret_key).decode()
        except ValueError as e:
            logger.warning(f'secret_key invalid, {e}: {self.pk_id}:')

    @sk.setter
    def sk(self, value):
        self.secret_key = rsa_encrypt(value)

    @property
    def api_active(self):
        return self.api_state == constants.ResourceState.active.value

    # For Admin
    def get_id(self):
        return self.user_id

    @property
    def is_active(self):
        return self.user_state == constants.ResourceState.active.value

    def has_role(self, role_name):
        return self.role.role_name == role_name

    def __str__(self):
        return self.user_name
