"""
Study Session State Transitions

Functions for managing study session state transitions (start, pause, resume).
Includes the session_state_transition decorator for handling state transitions.
"""

from datetime import datetime
from typing import Callable, Union
from functools import wraps

from src.database.session_context import get_current_session
from src.models.base import StudySession
from src.models.session_models import (
    HomeHoursStudySession, HomeHoursStudySessionPause,
    SchoolHoursStudySession, SchoolHoursStudySessionPause
)
from src.models.student_models import Student
from src.enums import SessionStatus
from .exceptions import SessionNotFoundError, InvalidSessionStateError, StudySessionError
from src.utils import Logger
from src.app.utils.websocket import emit_to_manager


def _get_session(session_id: int, session_type: str = None) -> Union[HomeHoursStudySession, SchoolHoursStudySession, None]:
    """
    Helper to find a session in either home or school tables.
    
    Args:
        session_id: The session ID to look up
        session_type: Optional type hint - 'home' or 'school'. If provided, only that type is queried.
    
    Returns:
        The session object, or None if not found
    """
    if session_type == 'home':
        return HomeHoursStudySession.get_by(first=True, id=session_id)
    elif session_type == 'school':
        return SchoolHoursStudySession.get_by(first=True, id=session_id)
    
    # If no type specified, check both (legacy behavior)
    home_session = HomeHoursStudySession.get_by(first=True, id=session_id)
    school_session = SchoolHoursStudySession.get_by(first=True, id=session_id)
    
    if home_session and school_session:
        Logger.warning(f"ID COLLISION! Both home and school sessions exist with ID {session_id}")
        Logger.warning(f"  Home session status: {home_session.status}, School session status: {school_session.status}")
        Logger.warning("  Please specify session_type='home' or 'school' to disambiguate")

    return school_session or home_session


def state_transition(
        expected_status: SessionStatus,
        new_status: SessionStatus
):
    """Decorator for session state transition methods. Works with both home and school sessions."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(study_session_id: int, *args, **kwargs) -> StudySession:
            session = get_current_session()
            operation_name = func.__name__.replace('_session', '')
            
            # Extract session_type from kwargs if provided
            session_type = kwargs.get('session_type', None)

            study_session = _get_session(study_session_id, session_type=session_type)
            if not study_session:
                raise SessionNotFoundError(f"Session {study_session_id} not found")

            if study_session.status != expected_status:
                raise InvalidSessionStateError(
                    f"Cannot {operation_name} session in {study_session.status} state"
                )

            try:
                func(study_session_id, *args, **kwargs)

                study_session.status = new_status
                session.flush()  # Flush changes to DB within current transaction
                session.refresh(study_session)  # Refresh to ensure object reflects DB state

                return study_session

            except Exception as e:
                if expected_status == SessionStatus.PENDING:
                    try:
                        study_session.status = SessionStatus.CANCELLED
                        session.flush()
                    except Exception:
                        session.rollback()
                else:
                    session.rollback()
                raise StudySessionError(f"Error during {operation_name}: {str(e)}")

        return wrapper

    return decorator


@state_transition(SessionStatus.PENDING, SessionStatus.ACTIVE)
def start_session(study_session_id: int, session_type: str = None) -> StudySession:
    """
    Start a pending study session (transition to ACTIVE).
    
    Args:
        study_session_id: The session ID to start
        session_type: Optional session type ('home' or 'school') to disambiguate
    """
    study_session = _get_session(study_session_id, session_type=session_type)
    
    if isinstance(study_session, SchoolHoursStudySession) and study_session.class_manager_id:
        try:
            if study_session.students:
                student_assoc = study_session.students[0]
                student = student_assoc.student

                course_name = None
                if study_session.learning_units:
                    first_unit = list(study_session.learning_units)[0]
                    course_name = first_unit.course.name
                
                emit_to_manager(
                    manager_id=study_session.class_manager_id,
                    event='student_started_session',
                    data={
                        'session_id': study_session_id,
                        'student_id': student.id,
                        'student_name': student.full_name,
                        'status': 'ACTIVE',
                        'course_name': course_name
                    }
                )
        except Exception as e:
            print(f"Warning: Failed to emit student_started_session event: {e}")


@state_transition(SessionStatus.ACTIVE, SessionStatus.PAUSED)
def pause_session(study_session_id: int, session_type: str = None) -> StudySession:
    """Pause an active study session. Works for both home and school sessions."""
    session = get_current_session()
    study_session = _get_session(study_session_id, session_type=session_type)

    if isinstance(study_session, HomeHoursStudySession):
        pause = HomeHoursStudySessionPause(
            home_hours_study_session_id=study_session_id,
            start_time=datetime.now()
        )
    else:
        pause = SchoolHoursStudySessionPause(
            school_hours_study_session_id=study_session_id,
            start_time=datetime.now()
        )
    
    session.add(pause)

    if isinstance(study_session, SchoolHoursStudySession) and study_session.class_manager_id:
        try:
            if study_session.students:
                student_assoc = study_session.students[0]
                student = student_assoc.student

                course_name = None
                if study_session.learning_units:
                    first_unit = list(study_session.learning_units)[0]
                    course_name = first_unit.course.name
                
                emit_to_manager(
                    manager_id=study_session.class_manager_id,
                    event='session_paused',
                    data={
                        'session_id': study_session_id,
                        'student_id': student.id,
                        'student_name': student.full_name,
                        'status': 'PAUSED',
                        'course_name': course_name
                    }
                )
        except Exception as e:
            print(f"Warning: Failed to emit session_paused event: {e}")


@state_transition(SessionStatus.PAUSED, SessionStatus.ACTIVE)
def resume_session(study_session_id: int, session_type: str = None) -> StudySession:
    """Resume a paused study session. Works for both home and school sessions."""
    study_session = _get_session(study_session_id, session_type=session_type)

    if isinstance(study_session, HomeHoursStudySession):
        active_pause = HomeHoursStudySessionPause.get_active_pause(study_session_id)
    else:
        active_pause = SchoolHoursStudySessionPause.get_active_pause(study_session_id)

    if active_pause:
        active_pause.end_time = datetime.now()

    if isinstance(study_session, SchoolHoursStudySession) and study_session.class_manager_id:
        try:
            if study_session.students:
                student_assoc = study_session.students[0]
                student = student_assoc.student

                course_name = None
                if study_session.learning_units:
                    first_unit = list(study_session.learning_units)[0]
                    course_name = first_unit.course.name
                
                emit_to_manager(
                    manager_id=study_session.class_manager_id,
                    event='session_resumed',
                    data={
                        'session_id': study_session_id,
                        'student_id': student.id,
                        'student_name': student.full_name,
                        'status': 'ACTIVE',
                        'course_name': course_name
                    }
                )
        except Exception as e:
            print(f"Warning: Failed to emit session_resumed event: {e}")
