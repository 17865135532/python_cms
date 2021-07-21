#!/usr/bin/python
# -*- coding:utf-8 -*-

from app.dao.mysql import db
from app.models.base_model import BaseModel, CreationMixin, UpdationMixin
from app.constants import ResourceState


class Role(BaseModel, CreationMixin, UpdationMixin):
    __tablename__ = "sys_role"
    __table_args__ = ({'comment': "角色表"})

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='角色id')
    role_name = db.Column(db.String(20), nullable=False, unique=True, comment='角色名称')
    role_description = db.Column(db.String(50), comment='角色描述')
    role_state = db.Column(db.String(10), nullable=False, default=ResourceState.active.value, comment='角色状态')

    users = db.relationship(
        'User', backref='role',
        primaryjoin='foreign(User.role_id)==Role.role_id')
    role_permissions = db.relationship(
        'RolePermission', backref='role',
        primaryjoin='foreign(RolePermission.role_id)==Role.role_id')

    def __str__(self):
        return self.role_name
