# -*- coding: utf-8 -*-

from functools import wraps

from flask_login import current_user
from werkzeug.exceptions import abort


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(func):
    return permission_required('ADMINISTER')(func)
