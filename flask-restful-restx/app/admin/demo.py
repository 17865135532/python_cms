from app.admin.base import BaseModelView
from app.dao.mysql import db
from app.models import Demo as DemoModel


class DemoView(BaseModelView):
    can_edit = True
    column_list = ['create_user', 'created_at', 'update_user', 'updated_at']
    column_filters = column_searchable_list = []
    column_sortable_list = ['created_at', 'updated_at']
    column_default_sort = ('updated_at', True)
    column_details_list = []
    form_columns = []
    form_extra_fields = {}
    inline_models = []
    form_choices = column_choices = {}

    def on_model_change(self, form, obj, is_created=False):
        ...


demo_view = DemoView(DemoModel, db.session)
