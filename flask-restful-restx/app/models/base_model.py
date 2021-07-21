#!/usr/bin/python
import logging

from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import func
import sqlalchemy.exc
from flask import g, request
from flask_login import current_user

from app import constants
from app.dao.mysql import db
from app.utils import errors, helpers


logger = logging.getLogger(__name__)


class BaseModel(db.Model):
    __table_args__ = {}
    __abstract__ = True
    logger = logger.getChild('BaseModel')

    @classmethod
    def pk_field(cls):
        return inspect(cls).primary_key[0].name

    @property
    def pk_id(self):
        return getattr(self, self.pk_field())

    def save(self, user=None, *args, **kwargs):
        user = user or getattr(g, 'user', None)
        if user is None:
            raise errors.Error(errmsg='User is required')
        if 'created_by' in [c.name for c in self.__table__.columns]:
            self.created_by = user.user_id
        try:
            with db.auto_commit_db():
                db.session.add(self)
        except sqlalchemy.exc.IntegrityError as e:
            if e.orig.args[0] == 1062:
                raise errors.DBParamValueDuplicate(errmsg=e)
            raise errors.DBStatementError(errmsg=e)
        except sqlalchemy.exc.StatementError as e:
            raise errors.DBStatementError(errmsg=e)

    def delete(self, *args, **kwargs):
        with db.auto_commit_db():
            db.session.delete(self)

    def update(self, data, user=None, *args, **kwargs):
        user = user or getattr(g, 'user', None)
        if user is None:
            raise errors.Error(errmsg='User is required')
        if 'updated_by' in [c.name for c in self.__table__.columns]:
            self.updated_by = user.user_id
        try:
            with db.auto_commit_db():
                for key, val in data.items():
                    if val is not None and hasattr(self, key):
                        setattr(self, key, val)
        except sqlalchemy.exc.IntegrityError as e:
            if e.orig.args[0] == 1062:
                raise errors.DBParamValueDuplicate(errmsg=e)
            raise errors.DBStatementError(errmsg=e)
        except sqlalchemy.exc.StatementError as e:
            raise errors.DBStatementError(errmsg=e)
    
    def to_dict(self):
        return {
            c.name: getattr(self, c.name, None)
            for c in self.__table__.columns
        }

    def __str__(self):
        return f'<{self.__class__.__name__} {self.pk_id}>'

    def __repr__(self):
        return self.__str__()


class CreationMixin:
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), index=True, comment='创建日期')

    @declared_attr
    def created_by(cls):
        return db.Column(db.Integer, index=True, comment='创建人')


class UpdationMixin:
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now(), index=True, comment='更新日期')

    @declared_attr
    def updated_by(cls):
        return db.Column(db.Integer, index=True, comment='更新人')


class OperationLogMixin(CreationMixin):
    log_id = db.Column(db.Integer, autoincrement=True, primary_key=True, comment='日志流水号')
    role_and_situations = []

    @declared_attr
    def user_name(cls):
        return db.Column(db.String(20), comment='用户名称')

    @declared_attr
    def operation(cls):
        return db.Column(db.String(10), nullable=False, default=constants.Operation.create.value, comment='操作')

    @declared_attr
    def object_type(cls):
        return db.Column(db.String(20), comment='操作对象类型')

    @declared_attr
    def object_id(cls):
        return db.Column(db.String(20), comment='操作对象id')

    @declared_attr
    def info(cls):
        return db.Column(db.String(50), comment='信息')

    @declared_attr
    def user_ip(cls):
        return db.Column(db.String(20), comment='用户ip')

    def __str__(self):
        s = f'{self.user_name} {self.operation} {self.object_type}({self.object_id})'
        if self.info:
            s += f':{self.info}'
        return s


class UserOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'u_operation_log'
    __table_args__ = ({'comment': '用户操作日志表'},)
    role_and_situations = [('customer', 'web')]


class ApiOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'u_api_operation_log'
    __table_args__ = ({'comment': 'api操作日志表'},)
    role_and_situations = [('customer', 'api')]


class AdminOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'admin_operation_log'
    __table_args__ = ({'comment': '后台用户操作日志表'},)
    role_and_situations = [('administrator', 'web')]


class AdminApiOperationLog(BaseModel, OperationLogMixin):
    __tablename__ = 'admin_api_operation_log'
    __table_args__ = ({'comment': '后台api操作日志表'},)
    role_and_situations = [('administrator', 'api')]


def audit_log(op, mapper, connect, self):
    _logger = logger.getChild('audit_log')
    tables_mapping = {
        role_and_situation: m.__tablename__
        for m in [UserOperationLog, ApiOperationLog, AdminOperationLog, AdminApiOperationLog]
        for role_and_situation in m.role_and_situations
    }
    try:
        role_and_situation = helpers.get_role_and_situation()
        role = role_and_situation.get('role')
        situation = role_and_situation.get('situation')
        table_name = tables_mapping[(role, situation)]
        user = getattr(g, 'user', None)
        if not user:
            user = current_user
        if user:
            user_name = user.user_name
            user_id = user.user_id
            ip = request.remote_addr
        else:
            user_name = None
            user_id = getattr(self, 'created_by')
            ip = ''
        sql = f'insert into {table_name} ' \
              f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
              f'values ("{user_name}","{op.value}",' \
              f'"{self.__table_args__.get("comment") or self.__tablename__}",' \
              f'{self.pk_id},"{ip}",{user_id});'
        connect.execute(sql)
    except Exception as e:
        _logger.critical(f'object is {self}, operation is {op.value}', exc_info=e)
