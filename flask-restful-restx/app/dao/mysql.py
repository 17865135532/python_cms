import logging
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy
from flask_sqlalchemy import BaseQuery
from flask import g, request
from flask_login import current_user

from app import constants
from app.utils import helpers


logger = logging.getLogger(__name__)


class SQLAlchemy(BaseSQLAlchemy):

    # 利用contextmanager管理器,对try/except语句封装，使用的时候必须和with结合！！！
    @contextmanager
    def auto_commit_db(self):
        try:
            yield
            self.session.commit()
        except Exception:
            # 加入数据库commit提交失败，必须回滚！！！
            self.session.rollback()
            self.session.remove()
            raise


class Query(BaseQuery):
    @property
    def columns(self):
        mapper = self._mapper_zero()
        return mapper.column_attrs._data.keys()

    def record(self, object_id='list'):
        try:
            role_and_situation = helpers.get_role_and_situation()
            role = role_and_situation.get('role')
            situation = role_and_situation.get('situation')
            user = getattr(g, 'user', None)
            model_class = self._mapper_zero().class_
            op = constants.Operation.query.value
            if role == 'user' and situation == 'web':
                sql = f'insert into u_operation_log ' \
                      f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
                      f'values ("{user.user_name}","{op}",' \
                      f'"{model_class.__table_args__.get("comment") or model_class.__tablename__}",' \
                      f'"{object_id}","{request.remote_addr}",{g.user.user_id});'
            elif role == 'user' and situation == 'api':
                sql = f'insert into u_api_operation_log ' \
                      f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
                      f'values ("{user.user_name}","{op}",' \
                      f'"{model_class.__table_args__.get("comment") or model_class.__tablename__}",' \
                      f'"{object_id}","{request.remote_addr}",{g.user.user_id});'
            elif role == 'admin' and situation == 'api':
                sql = f'insert into admin_api_operation_log ' \
                      f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
                      f'values ("{user.user_name}","{op}",' \
                      f'"{model_class.__table_args__.get("comment") or model_class.__tablename__}",' \
                      f'"{object_id}","{request.remote_addr}",{g.user.user_id});'
            elif role == 'admin' and situation == 'web':
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
                sql = f'insert into admin_operation_log ' \
                      f'(user_name, operation, object_type, object_id, user_ip, created_by)' \
                      f'values ("{user_name}","{op}",' \
                      f'"{model_class.__table_args__.get("comment") or model_class.__tablename__}",' \
                      f'"{object_id}","{ip}",{user_id});'
            elif role == 'robot':
                robot = g.robot
                sql = f'insert into robot_api_operation_log ' \
                      f'(user_name, operation, object_type, object_id, user_ip, create_robot)' \
                      f'values ("{robot.robot_name}","{op}",' \
                      f'"{model_class.__table_args__.get("comment") or model_class.__tablename__}",' \
                      f'"{object_id}","{request.remote_addr}",{g.robot.robot_id});'
            else:
                raise Exception(f'user is {user}, robot is {getattr(g, "robot", None)}, '
                                f'auth_method is {getattr(g, "auth_method", None)}')
            self.session.execute(sql)
        except Exception as e:
            logger.critical(f'object is {self}, operation is {op.value}', exc_info=e)
        return self

    @property
    def active(self):
        model_class = self._mapper_zero().class_
        for col in self.columns:
            if col == 'api_state':
                continue
            if col.endswith('_state') or col == 'state':
                column = getattr(model_class, col)
                return self.filter(column == constants.ResourceState.active.value)
        return self

    def get_active(self, ident, user_id=None, record=False):
        if record is True:
            self.record(object_id=ident)
        ret = super().get(ident)
        if not ret:
            return ret
        for col in self.columns:
            if col == 'api_state':
                continue
            if col.endswith('_state') or col == 'state':
                if getattr(ret, col) != constants.ResourceState.active.value:
                    return None
        if user_id is not None and 'create_user' in self.columns and ret.create_user != user_id:
            return None
        return ret

    def get(self, ident, record=False):
        if record is True:
            self.record(object_id=ident)
        return super().get(ident)

    def filter_by_create_date_and_page(self, create_date_start, create_date_end, per_page, page):
        model_class = self._mapper_zero().class_
        create_date_column = getattr(model_class, 'created_at')
        ret = self
        if create_date_start is not None:
            ret = ret.filter(create_date_column >= create_date_start)
        if create_date_end is not None:
            ret = ret.filter(create_date_column <= create_date_end)
        if per_page is not None:
            ret = ret.limit(per_page).offset(per_page * (page - 1))
        return ret


db = SQLAlchemy(query_class=Query, engine_options={'pool_pre_ping': True, 'pool_recycle': 3600})
