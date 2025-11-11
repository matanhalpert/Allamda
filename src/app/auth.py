"""Authentication and authorization decorators."""
from flask import redirect, session, render_template
from functools import wraps
from .utils.flash import flash_message
from src.enums import UserType


def login_required(func):
    """Require authenticated user session to access route."""

    @wraps(func)  # Preserve original function metadata
    def login_check(*args, **kwargs):
        if not session.get("user"):
            return redirect("/login")
        return func(*args, **kwargs)

    return login_check


def logout_required(func):
    """Restrict authenticated users from accessing login route."""

    @wraps(func)
    def logout_check(*args, **kwargs):
        if session.get("user"):
            flash_message("You are already logged in.", "warning")
            return redirect("/")
        return func(*args, **kwargs)

    return logout_check


def user_required(*allowed_user_types):
    """Restrict route access to one or more specific user types."""
    allowed_types = set()
    for user_type in allowed_user_types:
        if isinstance(user_type, UserType) or isinstance(user_type, str):
            allowed_types.add(user_type.lower())
        else:
            raise ValueError(f"Invalid user type: {user_type}. Must be string or UserType enum.")
    
    if not allowed_types:
        raise ValueError("At least one user type must be specified.")

    def decorator(func):
        @wraps(func)
        def user_type_check(*args, **kwargs):
            user = session.get("user")
            user_type = user.get("user_type", "").lower()
            
            if user_type not in allowed_types:
                # Format the list of allowed types for the error message
                if len(allowed_types) == 1:
                    allowed_types_str = list(allowed_types)[0]
                else:
                    allowed_list = sorted(allowed_types)
                    allowed_types_str = ", ".join(allowed_list[:-1]) + f" or {allowed_list[-1]}"
                
                flash_message(
                    f"Access denied. This page is only accessible to {allowed_types_str} users.",
                    "error"
                )
                return render_template("access_denied.html",
                                       required_type=allowed_types_str,
                                       current_type=user_type), 403

            return func(*args, **kwargs)

        return user_type_check

    return decorator

