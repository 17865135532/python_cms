from flask import g


def get_role_and_situation():
    user = getattr(g, 'user', None)
    auth_method = getattr(g, 'auth_method', None)
    if auth_method == 'token':
        situation = 'web'
    elif auth_method == 'ak':
        situation = 'api'
    else:
        return {'role': 'administrator', 'situation': 'web'}
    if user and user.role:
        return {'role': user.role.role_name, 'situation': situation}
    raise Exception(
            f'user/role is required: '
            f'user{user}/role{getattr(user, "role", None)}')
