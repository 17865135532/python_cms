from app.dao.mysql import db
from app.models.base_model import BaseModel, CreationMixin, UpdationMixin


class RolePermission(BaseModel, CreationMixin, UpdationMixin):
    __tablename__ = "dat_role_permission"
    __table_args__ = ({'comment': '角色权限配置表'})

    role_permission_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='角色权限配置id')
    role_id = db.Column(db.Integer, nullable=False, comment='角色id')
    resource_permission_id = db.Column(db.Integer, nullable=False, comment='权限id')
    role_permission_state = db.Column(db.Boolean, nullable=False, default=True, comment='是否允许')

    def __str__(self):
        return f'< Role {self.role} - Resource Permission {self.resource_permission} - {self.role_permission_state}>'
