from app.dao.mysql import db
from app.models.base_model import BaseModel, CreationMixin, UpdationMixin
from app.constants import ResourceState


class Demo(BaseModel, CreationMixin, UpdationMixin):
    __tablename__ = "dat_demo"
    __table_args__ = {'comment': 'demo表'}

    demo_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='demo id')
    demo_name = db.Column(db.String(15), nullable=False, unique=True, index=True, comment="demo名称")
    demo_state = db.Column(db.String(10), nullable=False, default=ResourceState.active.name, comment='demo状态')

    def __str__(self):
        return self.demo_name
