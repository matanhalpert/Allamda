"""Session lifecycle routes - pause, resume, end."""

from flask import render_template, redirect, request, session, jsonify, current_app

from ...auth import login_required, user_required
from ...utils import flash_message
from src.database import with_db_session
from src.models.session_models import HomeHoursStudySession, SchoolHoursStudySession
from src.enums import UserType, EmotionalState
from src.services.study_session import (
    pause_session,
    resume_session,
    end_session,
    get_session_messages,
    StudySessionError,
    InvalidSessionStateError
)

from src.app.routes.study import bp


@bp.route("/study/pause/<int:session_id>", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def pause_study_session(session_id):
    """Pause an active study session (AJAX endpoint)."""
    try:
        user = session.get("user")
        student_id = user.get("id")
        
        session_type = None
        study_session = HomeHoursStudySession.get_by_id_and_student(session_id, student_id)
        if study_session:
            session_type = 'home'
        else:
            study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
            if study_session:
                session_type = 'school'
        
        pause_session(session_id, session_type=session_type)
        return jsonify({"success": True, "message": "Session paused"})
        
    except InvalidSessionStateError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Pause session error: {e}")
        return jsonify({"error": "Failed to pause session"}), 500


@bp.route("/study/resume/<int:session_id>", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def resume_study_session(session_id):
    """Resume a paused study session (AJAX endpoint)."""
    try:
        user = session.get("user")
        student_id = user.get("id")
        
        session_type = None
        study_session = HomeHoursStudySession.get_by_id_and_student(session_id, student_id)
        if study_session:
            session_type = 'home'
        else:
            study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
            if study_session:
                session_type = 'school'
        
        resume_session(session_id, session_type=session_type)
        return jsonify({"success": True, "message": "Session resumed"})
        
    except InvalidSessionStateError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Resume session error: {e}")
        return jsonify({"error": "Failed to resume session"}), 500


@bp.route("/study/end/<int:session_id>", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def end_session_form(session_id):
    """Display end session feedback form. Works for both home and school sessions."""
    user = session.get("user")
    student_id = user.get("id")
    
    try:
        study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
        if not study_session:
            study_session = HomeHoursStudySession.get_by_id_and_student(session_id, student_id)
        
        if not study_session:
            flash_message("Access denied to this session.", "error")
            return redirect("/study")

        messages = get_session_messages(session_id)

        total_minutes = int(study_session.duration.total_seconds() / 60) if study_session.duration else 0
        
        if total_minutes < 1:
            duration_str = "Less than 1 minute"
        elif total_minutes == 1:
            duration_str = "1 minute"
        else:
            duration_str = f"{total_minutes} minutes"
        
        return render_template(
            "study_end.html",
            user=user,
            session_id=session_id,
            message_count=len(messages),
            duration=duration_str,
            emotional_states=list(EmotionalState)
        )
        
    except Exception as e:
        flash_message("An error occurred.", "error")
        current_app.logger.error(f"End session form error: {e}")
        return redirect("/")


@bp.route("/study/end/<int:session_id>", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def complete_session(session_id):
    """Complete a study session with feedback. Works for both home and school sessions."""
    user = session.get("user")
    student_id = user.get("id")

    study_session = HomeHoursStudySession.get_by_id_and_student(session_id, student_id)
    session_type = 'home'
    if not study_session:
        study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
        session_type = 'school'
    
    if not study_session:
        flash_message("Access denied to this session.", "error")
        return redirect("/study")
    
    # Get form data
    emotional_state_str = request.form.get("emotional_state_after")
    difficulty = request.form.get("difficulty_feedback")
    understanding = request.form.get("understanding_feedback")
    textual_feedback = request.form.get("textual_feedback", "").strip()

    if not all([emotional_state_str, difficulty, understanding]):
        flash_message("Please fill in all required fields.", "error")
        return redirect(f"/study/end/{session_id}")
    
    try:
        emotional_state_after = EmotionalState(emotional_state_str)
        difficulty_feedback = int(difficulty)
        understanding_feedback = int(understanding)
        
        if not (1 <= difficulty_feedback <= 10) or not (1 <= understanding_feedback <= 10):
            raise ValueError("Feedback must be between 1 and 10")
            
    except (ValueError, TypeError):
        flash_message("Invalid feedback data.", "error")
        return redirect(f"/study/end/{session_id}")
    
    try:
        end_session(
            session_id=session_id,
            student_id=student_id,
            emotional_state_after=emotional_state_after,
            difficulty_feedback=difficulty_feedback,
            understanding_feedback=understanding_feedback,
            textual_feedback=textual_feedback if textual_feedback else None,
            session_type=session_type
        )
            
        flash_message(
            "Study session completed successfully! Your performance has been evaluated.",
            "success"
        )
        return redirect("/")
        
    except InvalidSessionStateError as e:
        flash_message(f"Cannot end session: {str(e)}", "error")
        return redirect(f"/study/chat/{session_id}")
    except StudySessionError as e:
        flash_message(f"Error ending session: {str(e)}", "error")
        current_app.logger.error(f"End session error: {e}")
        return redirect(f"/study/end/{session_id}")
    except Exception as e:
        flash_message("An unexpected error occurred.", "error")
        current_app.logger.error(f"Unexpected end session error: {e}")
        return redirect(f"/study/end/{session_id}")
