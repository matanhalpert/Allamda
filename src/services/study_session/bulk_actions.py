"""
Bulk session management actions for class managers.

Functions for force pausing, resuming, and stopping all sessions in a class.
"""

from typing import List, Dict, Any
from src.database.session_context import get_current_session
from src.models.session_models import SchoolHoursStudySession
from src.enums import SessionStatus
from .state_transitions import pause_session, resume_session
from src.app.utils.websocket import emit_to_manager, emit_to_student


def force_pause_all_sessions(class_manager_id: int) -> Dict[str, Any]:
    """Force pause all active school sessions for a class manager."""
    session = get_current_session()

    active_sessions = SchoolHoursStudySession.get_by(
        first=False,
        class_manager_id=class_manager_id,
        status=SessionStatus.ACTIVE
    )
    if not active_sessions:
        return {'success': True, 'count': 0, 'message': 'No active sessions to pause'}
    
    paused_count = 0
    errors = []
    
    for study_session in active_sessions:
        try:
            # Store student info before pausing
            student = None
            if study_session.students:
                student_assoc = study_session.students[0]
                student = student_assoc.student

            pause_session(study_session.id, session_type='school')

            session.refresh(study_session)

            if student:
                try:
                    emit_to_student(
                        student_id=student.id,
                        event='force_pause',
                        data={
                            'session_id': study_session.id,
                            'message': 'Your class manager has paused your session'
                        }
                    )
                except Exception as e:
                    print(f"Warning: Failed to emit force_pause to student {student.id}: {e}")
            
            paused_count += 1
            
        except Exception as e:
            errors.append(f"Session {study_session.id}: {str(e)}")
            print(f"Error pausing session {study_session.id}: {e}")

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return {'success': False, 'error': f'Failed to commit changes: {str(e)}', 'count': 0}
    
    result = {
        'success': True,
        'count': paused_count,
        'message': f'Paused {paused_count} session(s)'
    }
    
    if errors:
        result['errors'] = errors
    
    return result


def force_resume_all_sessions(class_manager_id: int) -> Dict[str, Any]:
    """Force resume all paused school sessions for a class manager."""
    session = get_current_session()

    paused_sessions = SchoolHoursStudySession.get_by(
        first=False,
        class_manager_id=class_manager_id,
        status=SessionStatus.PAUSED
    )
    if not paused_sessions:
        return {'success': True, 'count': 0, 'message': 'No paused sessions to resume'}
    
    resumed_count = 0
    errors = []
    
    for study_session in paused_sessions:
        try:
            student = None
            if study_session.students:
                student_assoc = study_session.students[0]
                student = student_assoc.student

            resume_session(study_session.id, session_type='school')

            session.refresh(study_session)

            if student:
                try:
                    emit_to_student(
                        student_id=student.id,
                        event='force_resume',
                        data={
                            'session_id': study_session.id,
                            'message': 'Your class manager has resumed your session'
                        }
                    )
                except Exception as e:
                    print(f"Warning: Failed to emit force_resume to student {student.id}: {e}")
            
            resumed_count += 1
            
        except Exception as e:
            errors.append(f"Session {study_session.id}: {str(e)}")
            print(f"Error resuming session {study_session.id}: {e}")

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return {'success': False, 'error': f'Failed to commit changes: {str(e)}', 'count': 0}
    
    result = {
        'success': True,
        'count': resumed_count,
        'message': f'Resumed {resumed_count} session(s)'
    }
    
    if errors:
        result['errors'] = errors
    
    return result


def force_stop_all_sessions(class_manager_id: int) -> Dict[str, Any]:
    """
    Force stop all active/paused school sessions for a class manager.
    This redirects students to the feedback form but doesn't complete the session.
    """
    session = get_current_session()

    ongoing_sessions = SchoolHoursStudySession.get_by(
        first=False,
        class_manager_id=class_manager_id,
        status=[SessionStatus.ACTIVE, SessionStatus.PAUSED]
    )
    if not ongoing_sessions:
        return {'success': True, 'count': 0, 'message': 'No sessions to stop'}
    
    stopped_count = 0
    errors = []
    
    for study_session in ongoing_sessions:
        try:
            if study_session.students:
                student_assoc = study_session.students[0]
                student = student_assoc.student

                try:
                    emit_to_student(
                        student_id=student.id,
                        event='force_stop',
                        data={
                            'session_id': study_session.id,
                            'message': 'Your class manager has ended your session. Please provide feedback'
                        }
                    )
                    stopped_count += 1
                except Exception as e:
                    errors.append(f"Session {study_session.id}: Failed to notify student - {str(e)}")
                    print(f"Warning: Failed to emit force_stop to student {student.id}: {e}")
            
        except Exception as e:
            errors.append(f"Session {study_session.id}: {str(e)}")
            print(f"Error stopping session {study_session.id}: {e}")
    
    result = {
        'success': True,
        'count': stopped_count,
        'message': f'Stopped {stopped_count} session(s)'
    }
    
    if errors:
        result['errors'] = errors
    
    return result
