"""
Study Session Service Exceptions

Custom exceptions for study session operations.
"""


class StudySessionError(Exception):
    """Base exception for study session errors."""
    pass


class ActiveSessionExistsError(StudySessionError):
    """Raised when attempting to create a session while one is already active."""
    pass


class SessionNotFoundError(StudySessionError):
    """Raised when a session cannot be found."""
    pass


class InvalidSessionStateError(StudySessionError):
    """Raised when an operation is invalid for the current session state."""
    pass
