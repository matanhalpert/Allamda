"""Study hub home page routes."""

from datetime import datetime, timedelta
from flask import render_template, redirect, session, current_app

from ...auth import login_required, user_required
from ...utils import flash_message
from src.database import with_db_session
from src.models.session_models import HomeHoursStudySession, SchoolHoursStudySession
from src.enums import UserType, SessionStatus

from src.app.routes.study import bp


@bp.route("/study", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def study_home():
    """Display study session hub with recent sessions."""
    user = session.get("user")
    student_id = user.get("id")
    
    try:
        active_home_session = (
            HomeHoursStudySession
            .cleanup_pending_sessions()
            .get_active_by(student_id)
        )

        school_session_candidate = SchoolHoursStudySession.get_active_by(student_id)

        pending_school_session = None
        active_school_session = None
        
        if school_session_candidate:
            # Debug logging to identify the type
            current_app.logger.debug(f"school_session_candidate type: {type(school_session_candidate)}")
            
            # Handle both dictionary and object responses
            if isinstance(school_session_candidate, dict):
                candidate_status = school_session_candidate.get('status')
                candidate_start_time = school_session_candidate.get('start_time')
            else:
                candidate_status = school_session_candidate.status
                candidate_start_time = school_session_candidate.start_time
            
            if candidate_status == SessionStatus.PENDING:
                cutoff_time = datetime.now() - timedelta(minutes=60)
                if candidate_start_time >= cutoff_time:
                    pending_school_session = school_session_candidate
            else:  # ACTIVE or PAUSED
                active_school_session = school_session_candidate

        home_sessions = HomeHoursStudySession.get_recent_sessions_for_student(
            student_id=student_id,
            limit=10
        )
        
        school_sessions = SchoolHoursStudySession.get_recent_sessions_for_student(
            student_id=student_id,
            limit=10
        )
        
        all_sessions = home_sessions + school_sessions
        all_sessions.sort(key=lambda s: s['start_time'], reverse=True)
        recent_sessions = all_sessions[:5]

        active_session = active_school_session or active_home_session
        
        # Convert to dict if needed (handle both dict and object types)
        active_session_dict = None
        if active_session:
            active_session_dict = active_session if isinstance(active_session, dict) else active_session.to_dict()
        
        pending_school_session_dict = None
        if pending_school_session:
            pending_school_session_dict = pending_school_session if isinstance(pending_school_session, dict) else pending_school_session.to_dict()
        
        return render_template(
            "study_hub.html",
            user=user,
            active_session=active_session_dict,
            pending_school_session=pending_school_session_dict,
            recent_sessions=recent_sessions
        )
        
    except Exception as e:
        import traceback
        flash_message("An error occurred while loading the study page.", "error")
        current_app.logger.error(f"Study home error: {e}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return redirect("/")
