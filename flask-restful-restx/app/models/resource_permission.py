from app.dao.mysql import db
from app.models.base_model import BaseModel, CreationMixin, UpdationMixin


class ResourcePermission(BaseModel, CreationMixin, UpdationMixin):
    __tablename__ = "dat_resource_permission"
    __table_args__ = ({'comment': '资源权限配置表'})

    resource_permission_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='资源权限配置id')
    resource_id = db.Column(db.Integer, nullable=False, comment='资源id')
    permission_id = db.Column(db.Integer, nullable=False, comment='权限id')

    role_permissions = db.relationship(
        'RolePermission', backref='resource_permission',
        primaryjoin='foreign(RolePermission.resource_permission_id)==ResourcePermission.resource_permission_id')

    def __str__(self):
        return f'< Role {self.resource} - Permission {self.permission} >'
