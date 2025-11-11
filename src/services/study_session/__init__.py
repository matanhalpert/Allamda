"""
Study Session Service

Public API for managing home and school study sessions.

This service provides a comprehensive set of functions for:
- Creating and managing study sessions (both home and school)
- Handling chat interactions with AI Teacher agents
- Collecting feedback and evaluating session outcomes

For detailed documentation, see README.md
"""
from .exceptions import (
    StudySessionError,
    ActiveSessionExistsError,
    SessionNotFoundError,
    InvalidSessionStateError,
)
from .lifecycle import (
    create_home_study_session, create_school_study_session, join_school_session,
    end_session, complete_expired_school_sessions
)
from .state_transitions import start_session, pause_session, resume_session
from .messaging import get_session_messages, send_message, send_welcome_message
from .evaluation import evaluate_session
from .bulk_actions import (
    force_pause_all_sessions, force_resume_all_sessions, force_stop_all_sessions
)

__all__ = [
    # Exceptions
    'StudySessionError',
    'ActiveSessionExistsError',
    'SessionNotFoundError',
    'InvalidSessionStateError',
    
    # Lifecycle functions
    'create_home_study_session',
    'create_school_study_session',
    'join_school_session',
    'end_session',
    'complete_expired_school_sessions',
    
    # State transition functions
    'start_session',
    'pause_session',
    'resume_session',
    
    # Messaging functions
    'get_session_messages',
    'send_message',
    'send_welcome_message',
    
    # Evaluation functions
    'evaluate_session',
    
    # Bulk action functions
    'force_pause_all_sessions',
    'force_resume_all_sessions',
    'force_stop_all_sessions',
]
