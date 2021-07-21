from enum import Enum, unique


@unique
class ResourceState(Enum):
    active = 'active'
    inactive = 'inactive'


@unique
class UserState(Enum):
    unconfirmed = 'unconfirmed'
    active = 'active'
    inactive = 'inactive'


@unique
class DeclarationState(Enum):
    undeclared = 'undeclared'
    pending = 'pending'
    running = 'running'
    successful = 'successful'
    failed = 'failed'


@unique
class PaymentState(Enum):
    failed = 'failed'
    unpaid = 'unpaid'
    paid = 'paid'
    unnecessary = 'unnecessary'


@unique
class LoginWayCode(Enum):
    CA = 1
    user_password = 2
    real_name = 3
    id_card = 4
    telephone_verification_code = 5
    telephone_password = 6


@unique
class LoginWayDescription(Enum):
    CA = 'CA证书登录'
    user_password = '用户名密码登录'
    real_name = '实名制登录'
    id_card = '证件登录'
    telephone_verification_code = '手机号验证码登录'
    telephone_password = '手机号密码登录'


@unique
class DeclarationPeriod(Enum):
    month = 'month'
    quarter = 'quarter'
    half_year = 'half_year'
    year = 'year'
    count = 'count'


@unique
class Operation(Enum):
    create = 'create'
    delete = 'delete'
    update = 'update'
    query = 'query'
    login = 'login'


@unique
class ResourceEnum(Enum):
    demo = 'demo'
    user = 'user'
