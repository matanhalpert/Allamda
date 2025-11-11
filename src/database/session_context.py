"""
Session Context Management.

This module provides context-based session management using contextvars,
allowing automatic session access throughout the application without
explicit parameter passing.
"""

from contextvars import ContextVar
from typing import Optional
from sqlalchemy.orm import Session

from src.utils import Logger


_current_session: ContextVar[Optional[Session]] = ContextVar('current_session', default=None)


def get_current_session() -> Session:
    """
    Get the current database session from context.
    
    Returns:
        The active Session object
        
    Raises:
        RuntimeError: If no session context is currently active
    """
    session = _current_session.get()
    if session is None:
        raise RuntimeError(
            "No database session is active in the current context. "
            "Make sure you're within a session context (use @with_session decorator "
            "or 'with DatabaseManager.get_session()' context manager)."
        )
    return session


def set_current_session(session: Optional[Session]) -> None:
    """Set the current database session in context."""
    _current_session.set(session)


def has_active_session() -> bool:
    """Check if there's an active session in the current context."""
    return _current_session.get() is not None


class SessionContext:
    """
    Context manager for establishing a database session context.
    
    This is used internally by DatabaseManager and decorators to
    automatically manage session lifecycle and context.
    """
    
    def __init__(self, session: Session, auto_commit: bool = True):
        """
        Initialize session context.
        
        Args:
            session: The SQLAlchemy session to manage
            auto_commit: Whether to auto-commit on successful exit
        """
        self.session = session
        self.auto_commit = auto_commit
        self._previous_session = None
    
    def __enter__(self) -> Session:
        """Enter the session context."""
        self._previous_session = _current_session.get()

        set_current_session(self.session)
        
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the session context.
        
        Automatically commits on success or rolls back on exception,
        then closes the session and restores previous context.
        """
        try:
            if exc_type is not None:
                self.session.rollback()
                Logger.debug(f"Session rolled back due to exception: {exc_type.__name__}")
            elif self.auto_commit:
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            Logger.error(f"Error during session cleanup: {e}")
            raise
        finally:
            self.session.close()

            set_current_session(self._previous_session)
