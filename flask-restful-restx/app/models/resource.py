from app.dao.mysql import db
from app.models.base_model import BaseModel, CreationMixin, UpdationMixin


class ResourceModel(BaseModel, CreationMixin, UpdationMixin):
    __tablename__ = "sys_resource"
    __table_args__ = ({'comment': "资源表"})

    resource_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='资源id')
    resource_name = db.Column(db.String(30), nullable=False, unique=True, comment='资源名称')
    resource_description = db.Column(db.String(50), comment='资源描述')

    resource_permissions = db.relationship(
        'ResourcePermission', backref='resource',
        primaryjoin='foreign(ResourcePermission.resource_id)==ResourceModel.resource_id')

    def __str__(self):
        return self.resource_name
