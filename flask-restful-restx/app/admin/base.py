import logging

from flask import redirect, url_for, request, abort
from flask_login import current_user
from flask_admin.contrib import sqla
from flask_admin.model.form import InlineFormAdmin


logger = logging.getLogger(__name__)


class BaseModelView(sqla.ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    can_export = True
    page_size = 20
    can_set_page_size = True

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('administrator'))

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('admin.login_view', next=request.url))

    def on_model_change(self, form, obj, is_created=False):
        if is_created:
            if hasattr(obj, 'created_by'):
                obj.created_by = current_user.user_id
        else:
            if hasattr(obj, 'updated_by'):
                obj.updated_by = current_user.user_id


class BaseInlineFormAdmin(InlineFormAdmin):
    def on_model_change(self, form, obj, is_created=False):
        if is_created:
            if hasattr(obj, 'created_by'):
                obj.created_by = current_user.user_id
        else:
            if hasattr(obj, 'updated_by'):
                obj.updated_by = current_user.user_id
