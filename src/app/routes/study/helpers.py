"""Helper functions for study session management."""

from flask import session, redirect
from ...utils import flash_message
from src.models.session_models import HomeHoursStudySession


def _clear_draft_session_data():
    """Clear temporary draft session data from Flask session."""
    if 'study_draft' in session:
        session.pop('study_draft')


def _get_draft_data():
    """Get draft session data, initializing if needed."""
    if 'study_draft' not in session:
        session['study_draft'] = {}
    return session['study_draft']


def _get_current_step():
    """Determine which step user should be on based on stored data."""
    draft = _get_draft_data()
    
    if not draft.get('session_type'):
        return 'session-type'
    elif not draft.get('course_id') or not draft.get('learning_unit_names'):
        return 'course'
    elif not draft.get('emotional_state_before'):
        return 'mental-state'
    else:
        return 'complete'


def _check_active_session_redirect(student_id):
    """Check if student has active session and return redirect if so."""
    active_session = (
        HomeHoursStudySession
        .cleanup_pending_sessions()
        .get_active_by(student_id)
    )
    if active_session:
        # Handle both dictionary and object responses
        session_id = active_session.get('id') if isinstance(active_session, dict) else active_session.id
        flash_message("You already have an active study session.", "warning")
        return redirect(f"/study/chat/{session_id}")
    return None
