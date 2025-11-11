"""Session creation routes - multistep flow."""

from flask import render_template, redirect, request, session, jsonify, current_app

from ...auth import login_required, user_required
from ...utils import flash_message
from src.database import with_db_session
from src.models.student_models import Student
from src.models.subject_models import Course
from src.models.session_models import SchoolHoursStudySession
from src.enums import UserType, HomeHoursStudySessionType, EmotionalState, SessionStatus
from src.services.study_session import (
    create_home_study_session,
    start_session,
    join_school_session,
    StudySessionError,
    ActiveSessionExistsError,
    InvalidSessionStateError
)
from .helpers import (
    _clear_draft_session_data,
    _get_draft_data,
    _get_current_step,
    _check_active_session_redirect
)

from src.app.routes.study import bp


@bp.route("/study/new", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def new_study_session():
    """Redirect to first step of multistep session creation."""
    user = session.get("user")
    student_id = user.get("id")
    
    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response
    
    _clear_draft_session_data()
    
    return redirect("/study/new/session-type")


@bp.route("/study/new/session-type", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def session_type_step():
    """Step 1: Select session type."""
    user = session.get("user")
    student_id = user.get("id")
    
    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response
    
    draft = _get_draft_data()
    
    return render_template(
        "study_new_session_type.html",
        user=user,
        session_types=list(HomeHoursStudySessionType),
        selected_type=draft.get('session_type')
    )


@bp.route("/study/new/session-type", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def session_type_step_submit():
    """Step 1: Store session type and proceed to next step."""
    user = session.get("user")
    student_id = user.get("id")
    
    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response
    
    session_type = request.form.get("session_type")
    
    if not session_type:
        flash_message("Please select a session type.", "error")
        return redirect("/study/new/session-type")
    
    try:
        HomeHoursStudySessionType(session_type)
        
        draft = _get_draft_data()
        draft['session_type'] = session_type
        session.modified = True
        
        return redirect("/study/new/course")
        
    except ValueError:
        flash_message("Invalid session type.", "error")
        return redirect("/study/new/session-type")


@bp.route("/study/new/course", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def course_step():
    """Step 2: Select course and learning units."""
    user = session.get("user")
    student_id = user.get("id")
    
    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response
    
    current_step = _get_current_step()
    if current_step != 'course' and current_step != 'mental-state' and current_step != 'complete':
        return redirect(f"/study/new/{current_step}")
    
    try:
        student = Student.get_by(id=student_id, first=True)
        courses = student.get_courses()
        
        draft = _get_draft_data()
        
        return render_template(
            "study_new_course.html",
            user=user,
            courses=courses,
            selected_course_id=draft.get('course_id'),
            selected_units=draft.get('learning_unit_names', [])
        )
        
    except Exception as e:
        flash_message("An error occurred while loading the course selection.", "error")
        current_app.logger.error(f"Course step error: {e}")
        return redirect("/study")


@bp.route("/study/new/course", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def course_step_submit():
    """Step 2: Store course and learning units, proceed to next step."""
    user = session.get("user")
    student_id = user.get("id")
    
    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response

    if 'back' in request.form:
        return redirect("/study/new/session-type")
    
    course_id = request.form.get("course_id")
    learning_unit_names = request.form.getlist("learning_units")
    
    if not course_id or not learning_unit_names:
        flash_message("Please select a course and at least one learning unit.", "error")
        return redirect("/study/new/course")
    
    try:
        course_id = int(course_id)

        student = Student.get_by(id=student_id, first=True)
        if not student.is_enrolled(course_id):
            flash_message("You are not enrolled in this course.", "error")
            return redirect("/study/new/course")

        draft = _get_draft_data()
        draft['course_id'] = course_id
        draft['learning_unit_names'] = learning_unit_names
        session.modified = True
        
        return redirect("/study/new/mental-state")
        
    except (ValueError, TypeError):
        flash_message("Invalid course selection.", "error")
        return redirect("/study/new/course")
    except Exception as e:
        flash_message("An error occurred.", "error")
        current_app.logger.error(f"Course step submit error: {e}")
        return redirect("/study/new/course")


@bp.route("/study/new/mental-state", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def mental_state_step():
    """Step 3: Log mental state before starting."""
    user = session.get("user")
    student_id = user.get("id")
    
    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response
    
    current_step = _get_current_step()
    if current_step != 'mental-state' and current_step != 'complete':
        return redirect(f"/study/new/{current_step}")
    
    try:
        draft = _get_draft_data()
        
        course = Course.get_by(id=draft.get('course_id'), first=True)
        
        return render_template(
            "study_new_mental_state.html",
            user=user,
            emotional_states=list(EmotionalState),
            selected_state=draft.get('emotional_state_before'),
            session_type=draft.get('session_type'),
            course_name=course.name if course else 'Unknown',
            learning_units=draft.get('learning_unit_names', [])
        )
        
    except Exception as e:
        flash_message("An error occurred.", "error")
        current_app.logger.error(f"Mental state step error: {e}")
        return redirect("/study")


@bp.route("/study/new/mental-state", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def mental_state_step_submit():
    """Step 3: Store mental state and create session."""
    user = session.get("user")
    student_id = user.get("id")

    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response

    if 'back' in request.form:
        return redirect("/study/new/course")
    
    emotional_state_str = request.form.get("emotional_state_before")
    
    if not emotional_state_str:
        flash_message("Please select your current emotional state.", "error")
        return redirect("/study/new/mental-state")
    
    try:
        EmotionalState(emotional_state_str)
        
        draft = _get_draft_data()
        draft['emotional_state_before'] = emotional_state_str
        session.modified = True

        return redirect("/study/create")
        
    except ValueError:
        flash_message("Invalid emotional state.", "error")
        return redirect("/study/new/mental-state")


@bp.route("/study/get_learning_units/<int:course_id>", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def get_learning_units(course_id):
    """Get learning units for a specific course (AJAX endpoint)."""
    user = session.get("user")
    student_id = user.get("id")
    
    try:
        student = Student.get_by(id=student_id, first=True)
        if not student or not student.is_enrolled(course_id):
            return jsonify({"error": "Not enrolled in this course"}), 403

        course = Course.get_by(id=course_id, first=True)
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        learning_units = course.get_ordered_learning_units()
            
        return jsonify({
            "learning_units": [
                {
                    "name": lu.name,
                    "type": lu.type,
                    "description": lu.description,
                    "estimated_duration_minutes": lu.estimated_duration_minutes
                }
                for lu in learning_units
            ]
        })
        
    except Exception as e:
        current_app.logger.error(f"Get learning units error: {e}")
        return jsonify({"error": "An error occurred"}), 500


@bp.route("/study/create", methods=["GET", "POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def create_session():
    """Create a new study session from draft data."""
    user = session.get("user")
    student_id = user.get("id")

    draft = _get_draft_data()
    session_type_str = draft.get("session_type")
    course_id = draft.get("course_id")
    learning_unit_names = draft.get("learning_unit_names")
    emotional_state_str = draft.get("emotional_state_before")

    if not all([session_type_str, course_id, learning_unit_names, emotional_state_str]):
        flash_message("Please complete all steps of the session creation.", "error")
        _clear_draft_session_data()
        return redirect("/study/new")
    
    try:
        session_type = HomeHoursStudySessionType(session_type_str)
        emotional_state = EmotionalState(emotional_state_str)
        course_id = int(course_id)
    except (ValueError, TypeError):
        flash_message("Invalid session data.", "error")
        _clear_draft_session_data()
        return redirect("/study/new")
    
    try:
        study_session = create_home_study_session(
            student_id=student_id,
            session_type=session_type,
            course_id=course_id,
            learning_unit_names=learning_unit_names,
            emotional_state_before=emotional_state
        )

        start_session(study_session.id, session_type='home')

        _clear_draft_session_data()
            
        flash_message("Study session started successfully!", "success")
        return redirect(f"/study/chat/{study_session.id}")
        
    except ActiveSessionExistsError:
        flash_message("You already have an active study session.", "warning")
        _clear_draft_session_data()
        return redirect("/study")
    except StudySessionError as e:
        flash_message(f"Error creating session: {str(e)}", "error")
        current_app.logger.error(f"Create session error: {e}")
        _clear_draft_session_data()
        return redirect("/study")
    except Exception as e:
        flash_message("An unexpected error occurred.", "error")
        current_app.logger.error(f"Unexpected create session error: {e}")
        _clear_draft_session_data()
        return redirect("/study")


@bp.route("/study/join/<int:session_id>", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def join_school_study_session(session_id):
    """Show mental state form for joining a school study session."""
    user = session.get("user")
    student_id = user.get("id")
    
    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response
    
    try:
        study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
        if not study_session:
            flash_message("School session not found or not available for you.", "error")
            return redirect("/study")
        
        if study_session.status != SessionStatus.PENDING:
            flash_message("This session is no longer available to join.", "warning")
            return redirect("/study")

        course_name = 'Unknown'
        learning_units = []
        if study_session.learning_units:
            first_unit = list(study_session.learning_units)[0]
            course = first_unit.course
            course_name = course.name
            learning_units = [lu.name for lu in study_session.learning_units]
        
        return render_template(
            "study_join_mental_state.html",
            user=user,
            session_id=session_id,
            emotional_states=list(EmotionalState),
            course_name=course_name,
            learning_units=learning_units,
            session_type=study_session.type.value.title()
        )
        
    except Exception as e:
        flash_message("An error occurred while loading the session.", "error")
        current_app.logger.error(f"Join session view error: {e}")
        return redirect("/study")


@bp.route("/study/join/<int:session_id>", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def join_school_study_session_submit(session_id):
    """Process mental state and join the school study session."""
    user = session.get("user")
    student_id = user.get("id")
    
    redirect_response = _check_active_session_redirect(student_id)
    if redirect_response:
        return redirect_response
    
    emotional_state_str = request.form.get("emotional_state_before")
    
    if not emotional_state_str:
        flash_message("Please select your current emotional state.", "error")
        return redirect(f"/study/join/{session_id}")
    
    try:
        emotional_state = EmotionalState(emotional_state_str)

        study_session = join_school_session(
            session_id=session_id,
            student_id=student_id,
            emotional_state_before=emotional_state
        )

        try:
            started_session = start_session(session_id, session_type='school')
            current_app.logger.info(f"start_session SUCCESS - Session {session_id} status: {started_session.status}")
        except InvalidSessionStateError as e:
            current_app.logger.warning(f"InvalidSessionStateError for session {session_id}: {e}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error in start_session for {session_id}: {type(e).__name__}: {e}")
            raise

        from src.database.session_context import get_current_session
        db_session = get_current_session()
        db_session.commit()
        
        flash_message("You've successfully joined the school study session!", "success")
        return redirect(f"/study/chat/{session_id}")
        
    except StudySessionError as e:
        flash_message(f"Error joining session: {str(e)}", "error")
        current_app.logger.error(f"Join session error: {e}")
        return redirect("/study")
    except ValueError:
        flash_message("Invalid emotional state.", "error")
        return redirect(f"/study/join/{session_id}")
    except Exception as e:
        flash_message("An unexpected error occurred.", "error")
        current_app.logger.error(f"Unexpected join session error: {e}")
        return redirect("/study")
