import functools
from typing import Any, Callable
from flask import request
from employee_survey_analyzer.config import ADMIN_KEY
from employee_survey_analyzer.representations import InvalidAuthorizationError

"""
    For any operation that requires admin permissions
        e.g. creating, editing, or deleting a survey; deleting a response
"""
def requires_admin(func: Callable[..., Any]):
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        authorization = request.headers.get("Authorization")

        if authorization is None or authorization != ADMIN_KEY:
            raise InvalidAuthorizationError(code="FORBIDDEN", status=403, detail=f"Not authorized")

        return func(*args, **kwargs)
    
    return wrapper