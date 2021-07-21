from app.dao.mysql import db
from app.models.base_model import BaseModel, CreationMixin, UpdationMixin


class Permission(BaseModel, CreationMixin, UpdationMixin):
    __tablename__ = "sys_permission"
    __table_args__ = ({'comment': "权限表"})

    permission_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='权限id')
    permission_name = db.Column(db.String(20), nullable=False, unique=True, comment='权限名称')
    permission_description = db.Column(db.String(50), comment='权限描述')

    resource_permissions = db.relationship(
        'ResourcePermission', backref='permission',
        primaryjoin='foreign(ResourcePermission.permission_id)==Permission.permission_id')

    def __str__(self):
        return self.permission_name
