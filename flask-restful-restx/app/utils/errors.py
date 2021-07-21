import logging
from enum import Enum, unique

import sqlalchemy.exc


@unique
class ErrorCode(Enum):
    ParamError = 400001
    DataParamError = 400002
    DataParamValueDuplicate = 400003

    ApiKeyRequired = 401001
    RobotIdRequired = 401002
    TokenRequired= 401003
    SignRequired = 401004
    SignExpired = 401005
    SignInvalid = 401006
    TimestampRequired = 401007
    NonceRequired = 401008
    TokenInvalid = 401009
    UserNotFound = 401010
    RobotNotFound = 401011
    AuthParamsRequired = 401012
    UserInactive = 401013
    UserApiInactive = 401014
    ResourceAccessForbidden = 403001
    ResourceWriteForbidden = 403002
    ResourceCreateForbidden = 403003

    ResourceNotFound = 404001
    MethodNotAllowed = 405001

    PreconditionRequired = 428001

    InternalError = 500001


class Error(Exception):
    code = ErrorCode.InternalError.value
    errmsg = ErrorCode.InternalError.name
    log_level = logging.ERROR

    def __init__(self, code=None, errmsg=None, *args, **kwargs):
        self.code = code or self.code
        self.errmsg = errmsg or self.errmsg

    @property
    def log(self):
        return self.errmsg

    def to_dict_response(self):
        return {
            'return_code': self.code,
            'return_msg': self.errmsg
        }


class ParamError(Error):
    code = ErrorCode.ParamError.value
    errmsg = ErrorCode.ParamError.name
    log_level = logging.WARNING


class DataParamError(Error):
    code = ErrorCode.DataParamError.value
    errmsg = ErrorCode.DataParamError.name
    log_level = logging.WARNING


class ApiKeyRequired(Error):
    code = ErrorCode.ApiKeyRequired.value
    errmsg = ErrorCode.ApiKeyRequired.name
    log_level = logging.WARNING


class RobotIdRequired(Error):
    code = ErrorCode.RobotIdRequired.value
    errmsg = ErrorCode.RobotIdRequired.name
    log_level = logging.WARNING


class TokenRequired(Error):
    code = ErrorCode.TokenRequired.value
    errmsg = ErrorCode.TokenRequired.name
    log_level = logging.WARNING


class SignRequired(Error):
    code = ErrorCode.SignRequired.value
    errmsg = ErrorCode.SignRequired.name
    log_level = logging.WARNING


class TimestampRequired(Error):
    code = ErrorCode.TimestampRequired.value
    errmsg = ErrorCode.TimestampRequired.name
    log_level = logging.WARNING


class NonceRequired(Error):
    code = ErrorCode.NonceRequired.value
    errmsg = ErrorCode.NonceRequired.name
    log_level = logging.WARNING


class TokenInvalid(Error):
    code = ErrorCode.TokenInvalid.value
    errmsg = ErrorCode.TokenInvalid.name
    log_level = logging.WARNING


class UserNotFound(Error):
    code = ErrorCode.UserNotFound.value
    errmsg = ErrorCode.UserNotFound.name


class UserInactive(Error):
    code = ErrorCode.UserInactive.value
    errmsg = ErrorCode.UserInactive.name
    log_level = logging.WARNING


class UserApiInactive(Error):
    code = ErrorCode.UserApiInactive.value
    errmsg = ErrorCode.UserApiInactive.name
    log_level = logging.WARNING


class RobotNotFound(Error):
    code = ErrorCode.RobotNotFound.value
    errmsg = ErrorCode.RobotNotFound.name
    log_level = logging.WARNING


class AuthParamsRequired(Error):
    code = ErrorCode.AuthParamsRequired.value
    errmsg = ErrorCode.AuthParamsRequired.name
    log_level = logging.WARNING


class ResourceAccessForbidden(Error):
    code = ErrorCode.ResourceAccessForbidden.value
    errmsg = ErrorCode.ResourceAccessForbidden.name
    log_level = logging.WARNING


class SignExpired(Error):
    code = ErrorCode.SignExpired.value
    errmsg = ErrorCode.SignExpired.name
    log_level = logging.WARNING


class SignInvalid(Error):
    code = ErrorCode.SignInvalid.value
    errmsg = ErrorCode.SignInvalid.name
    log_level = logging.WARNING


class PreconditionRequired(Error):
    code = ErrorCode.PreconditionRequired.value
    errmsg = ErrorCode.PreconditionRequired.name
    log_level = logging.WARNING


class ResourceWriteForbidden(Error):
    code = ErrorCode.ResourceWriteForbidden.value
    errmsg = ErrorCode.ResourceWriteForbidden.name
    log_level = logging.WARNING


class ResourceNotFound(Error):
    code = ErrorCode.ResourceNotFound.value
    errmsg = ErrorCode.ResourceNotFound.name
    log_level = logging.WARNING


class MethodNotAllowed(Error):
    code = ErrorCode.MethodNotAllowed.value
    errmsg = ErrorCode.MethodNotAllowed.name
    log_level = logging.WARNING


class DBStatementError(Error):
    def to_dict_response(self):
        if isinstance(self.errmsg, sqlalchemy.exc.StatementError):
            msg = self.errmsg.orig.args[1]
        else:
            msg = str(self.errmsg)
        return {
            'return_code': self.code,
            'return_msg': msg
        }


class DBParamValueDuplicate(DBStatementError):
    code = ErrorCode.DataParamValueDuplicate.value
    errmsg = ErrorCode.DataParamValueDuplicate.name
    log_level = logging.WARNING


def gen_doc():
    err_info = '错误码说明：<br><ul>'
    for item in ErrorCode.__members__.values():
        err_info += f'<li>{item.value} --- {item.name}</li>'
    err_info += '</ul>'
    return err_info
