"""Class manager-specific routes."""
from flask import Blueprint, render_template, redirect, session, current_app, request, jsonify
from typing import Optional
from ..auth import login_required, user_required
from ..utils import flash_message
from ..utils.websocket import emit_to_class
from src.database import with_db_session
from src.models import ClassManager, Class
from src.models.session_models import SchoolHoursStudySession, HomeHoursStudySession
from src.enums import UserType, SessionStatus
from src.services.study_session import (
    create_school_study_session, complete_expired_school_sessions, StudySessionError,
    force_pause_all_sessions, force_resume_all_sessions, force_stop_all_sessions
)

bp = Blueprint('class_manager', __name__)


@bp.route("/my_class", methods=["GET"])
@login_required
@user_required(UserType.CLASS_MANAGER)
@with_db_session
def my_class():
    """Display class information and students."""
    user = session.get("user")
    manager_id = user.get("id")

    try:
        manager: ClassManager = ClassManager.get_by(id=manager_id, first=True)
        managed_class: Optional[Class] = manager.get_class()

        if not managed_class:
            flash_message("You are not currently assigned to any class.", "warning")
            return render_template("my_class.html", user=user, has_class=False)

        return render_template(
            "my_class.html",
            user=user,
            has_class=True,
            class_info=managed_class.to_dict(),
            students=managed_class.get_students(),
            average_grade=managed_class.get_class_average_grade(),
            weekly_attendance=managed_class.get_weekly_attendance_rate(days=365)
        )

    except Exception as e:
        flash_message("An error occurred while loading class information.", "error")
        current_app.logger.error(f"My class error: {e}")
        return redirect("/")


@bp.route("/classroom", methods=["GET"])
@login_required
@user_required(UserType.CLASS_MANAGER)
@with_db_session
def classroom():
    """Display classroom session management page."""
    user = session.get("user")
    manager_id = user.get("id")

    try:
        manager: ClassManager = ClassManager.get_by(id=manager_id, first=True)
        managed_class: Optional[Class] = manager.get_class()

        if not managed_class:
            flash_message("You are not currently assigned to any class.", "warning")
            return redirect("/my_class")

        complete_expired_school_sessions(manager_id)

        active_sessions = SchoolHoursStudySession.get_by(
            first=False,
            class_manager_id=manager_id,
            status=[SessionStatus.PENDING, SessionStatus.ACTIVE, SessionStatus.PAUSED]
        )

        session_data = []
        if active_sessions:
            start_times = list(set(s.start_time for s in active_sessions))
            
            if start_times:
                latest_start_time = max(start_times)
                current_session_batch = [s for s in active_sessions if s.start_time == latest_start_time]
                
                for study_session in current_session_batch:
                    if study_session.students:
                        student_assoc = study_session.students[0]
                        student = student_assoc.student

                        course_name = None
                        if study_session.learning_units:
                            first_unit = list(study_session.learning_units)[0]
                            course_name = first_unit.course.name
                        
                        session_data.append({
                            'session_id': study_session.id,
                            'student_name': student.full_name,
                            'student_id': student.id,
                            'status': study_session.status.value,
                            'course_name': course_name,
                            'is_attendant': student_assoc.is_attendant,
                            'start_time': study_session.start_time
                        })

        school_sessions_raw = SchoolHoursStudySession.get_by(
            first=False,
            class_manager_id=manager_id,
            status=SessionStatus.COMPLETED
        )

        students = managed_class.get_students()
        student_ids = [s['id'] for s in students]

        home_sessions_raw = []
        if student_ids:
            all_home_sessions = HomeHoursStudySession.get_by(
                first=False,
                status=SessionStatus.COMPLETED
            )

            if all_home_sessions:
                for home_session in all_home_sessions:
                    if home_session.students:
                        student_assoc = home_session.students[0]
                        if student_assoc.student_id in student_ids:
                            home_sessions_raw.append(home_session)

        all_sessions_raw = (school_sessions_raw or []) + home_sessions_raw
        
        recent_sessions = []
        if all_sessions_raw:
            sorted_sessions = sorted(all_sessions_raw, key=lambda x: x.start_time, reverse=True)[:10]
            
            for study_session in sorted_sessions:
                student_name = 'Unknown'
                
                if study_session.students:
                    student_assoc = study_session.students[0]
                    student_name = student_assoc.student.full_name

                course_name = None
                course_subject = None
                if study_session.learning_units:
                    first_unit = list(study_session.learning_units)[0]
                    course = first_unit.course
                    course_name = course.name
                    course_subject = course.subject.name if course.subject else None

                duration_minutes = None
                if study_session.duration:
                    duration_minutes = int(study_session.duration.total_seconds() / 60)

                session_category = 'School Hours' if isinstance(study_session, SchoolHoursStudySession) else 'Home Hours'
                
                recent_sessions.append({
                    'id': study_session.id,
                    'student_name': student_name,
                    'session_category': session_category,
                    'session_type': study_session.type.value.title() if study_session.type else 'Individual',
                    'course_name': course_name,
                    'course_subject': course_subject,
                    'duration_minutes': duration_minutes,
                    'start_time': study_session.start_time
                })

        return render_template(
            "classroom.html",
            user=user,
            class_info=managed_class.to_dict(),
            students=managed_class.get_students(),
            active_session_data=session_data,
            has_active_session=len(session_data) > 0,
            recent_sessions=recent_sessions
        )

    except Exception as e:
        flash_message("An error occurred while loading classroom information.", "error")
        current_app.logger.error(f"Classroom error: {e}")
        return redirect("/")


@bp.route("/classroom/start_session", methods=["POST"])
@login_required
@user_required(UserType.CLASS_MANAGER)
@with_db_session
def start_classroom_session():
    """Start a new school study session for all students in the class."""
    user = session.get("user")
    manager_id = user.get("id")

    try:
        manager: ClassManager = ClassManager.get_by(id=manager_id, first=True)
        if not manager:
            flash_message("Class Manager not found.", "error")
            return redirect("/classroom")

        managed_class = manager.get_class()
        if not managed_class:
            flash_message("You are not currently assigned to any class.", "warning")
            return redirect("/classroom")

        active_sessions = SchoolHoursStudySession.get_by(
            first=False,
            class_manager_id=manager_id,
            status=[SessionStatus.PENDING, SessionStatus.ACTIVE, SessionStatus.PAUSED]
        )
        if active_sessions:
            flash_message("There is already an active or paused school session. Please wait for it to complete.", "warning")
            return redirect("/classroom")

        created_sessions = create_school_study_session(
            class_manager_id=manager_id,
            duration_minutes=60
        )

        if created_sessions:
            first_session = created_sessions[0]

            emit_to_class(
                school_id=managed_class.school_id,
                year=managed_class.year,
                grade_level=managed_class.grade_level.value,
                event='school_session_created',
                data={
                    'duration_minutes': 60,
                    'start_time': first_session.start_time.isoformat(),
                    'session_count': len(created_sessions)
                }
            )

        flash_message(
            f"School study session started successfully! {len(created_sessions)} students can now join.",
            "success"
        )
        return redirect("/classroom")

    except StudySessionError as e:
        flash_message(f"Error starting session: {str(e)}", "error")
        current_app.logger.error(f"Start classroom session error: {e}")
        return redirect("/classroom")
    except Exception as e:
        flash_message("An unexpected error occurred while starting the session.", "error")
        current_app.logger.error(f"Unexpected classroom session error: {e}")
        return redirect("/classroom")


@bp.route("/classroom/force_pause", methods=["POST"])
@login_required
@user_required(UserType.CLASS_MANAGER)
@with_db_session
def force_pause_sessions():
    """Force pause all active sessions in the class."""
    user = session.get("user")
    manager_id = user.get("id")
    
    try:
        result = force_pause_all_sessions(manager_id)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Force pause error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/classroom/force_resume", methods=["POST"])
@login_required
@user_required(UserType.CLASS_MANAGER)
@with_db_session
def force_resume_sessions():
    """Force resume all paused sessions in the class."""
    user = session.get("user")
    manager_id = user.get("id")
    
    try:
        result = force_resume_all_sessions(manager_id)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Force resume error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/classroom/force_stop", methods=["POST"])
@login_required
@user_required(UserType.CLASS_MANAGER)
@with_db_session
def force_stop_sessions():
    """Force stop all active/paused sessions in the class."""
    user = session.get("user")
    manager_id = user.get("id")
    
    try:
        result = force_stop_all_sessions(manager_id)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Force stop error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
