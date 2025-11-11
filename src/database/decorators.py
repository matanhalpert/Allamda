"""
Database Session Decorators.

This module provides decorators for automatic session context management
in functions and methods.
"""

from functools import wraps
from typing import Callable, Any

from .session_context import has_active_session
from .setup import DatabaseManager


def with_db_session(func: Callable) -> Callable:
    """
    Decorator that establishes a database session context for a function.
    
    If a session is already active in the current context, it will be reused.
    Otherwise, a new session is created and automatically managed (commit on
    success, rollback on exception, close when done).
    
    This decorator is ideal for route handlers and top-level service functions.
    
    Usage:
        @with_session
        def my_route():
            student = Student.get_by(id=1, first=True)
            # Session is automatically available
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if has_active_session():
            return func(*args, **kwargs)

        with DatabaseManager.get_session():
            return func(*args, **kwargs)
    
    return wrapper
