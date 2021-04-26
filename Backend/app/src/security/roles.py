from functools import wraps
from ...setup import login_manager
from flask_login import current_user
from enum import Enum
from flask import jsonify


class URole (Enum):
    ADMIN = 0
    INSTRUCTOR = 1
    NONE = 2


class CRole (Enum):
    ROOT = 0
    ADMIN = 1
    INSTRUCTOR = 2
    GRADER = 3
    STUDENT = 4


def role_required(role=URole.NONE.value):
    """
    Wrapper to be used for API calls that require the user's role
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            urole = (current_user._get_current_object()).get_urole(
                     current_user._get_current_object())
            if ((urole != role)):
                return jsonify({'reason': 'Unauthorized'}), 401
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
