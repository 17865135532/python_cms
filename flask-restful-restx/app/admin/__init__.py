from flask_admin import Admin

from app.admin.index import index_view
from app.admin.demo import demo_view


admin = Admin(name='后台管理系统Demo', index_view=index_view, template_mode='bootstrap3')
admin.add_view(demo_view)
