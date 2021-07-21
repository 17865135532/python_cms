import logging
from functools import partial

from sqlalchemy import event

from app import constants
from app.models.resource import ResourceModel
from app.models.permission import Permission
from app.models.user import User
from app.models.role import Role
from app.models.resource_permission import ResourcePermission
from app.models.role_permission import RolePermission
from app.models.base_model import UserOperationLog, ApiOperationLog, AdminApiOperationLog, AdminOperationLog, audit_log
from app.models.demo import Demo


logger = logging.getLogger(__name__)
event.listen(User, 'after_insert', partial(audit_log, constants.Operation.create))
event.listen(User, 'after_update', partial(audit_log, constants.Operation.update))
event.listen(User, 'after_delete', partial(audit_log, constants.Operation.delete))
event.listen(Role, 'after_insert', partial(audit_log, constants.Operation.create))
event.listen(Role, 'after_update', partial(audit_log, constants.Operation.update))
event.listen(Role, 'after_delete', partial(audit_log, constants.Operation.delete))
event.listen(Permission, 'after_insert', partial(audit_log, constants.Operation.create))
event.listen(Permission, 'after_update', partial(audit_log, constants.Operation.update))
event.listen(Permission, 'after_delete', partial(audit_log, constants.Operation.delete))
event.listen(RolePermission, 'after_insert', partial(audit_log, constants.Operation.create))
event.listen(RolePermission, 'after_update', partial(audit_log, constants.Operation.update))
event.listen(RolePermission, 'after_delete', partial(audit_log, constants.Operation.delete))
event.listen(Demo, 'after_insert', partial(audit_log, constants.Operation.create))
event.listen(Demo, 'after_update', partial(audit_log, constants.Operation.update))
event.listen(Demo, 'after_delete', partial(audit_log, constants.Operation.delete))
