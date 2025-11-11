"""Student-specific routes."""
from flask import Blueprint, render_template, redirect, request, session, current_app
from ..auth import login_required, user_required
from ..utils import flash_message
from src.database import with_db_session
from src.models import Student
from src.enums import UserType, GradeLevel, CourseState

bp = Blueprint('student', __name__)


@bp.route("/my_courses", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def my_courses():
    """Display student's courses & tests progress with filtering option by subject, grade, and state."""
    user = session.get("user")
    student_id = user.get("id")

    subject_filter = request.args.get("subject", None)
    grade_level_filter = request.args.get("grade", None)
    state_filter = request.args.get("state", None)

    try:
        student: Student = Student.get_by(id=student_id, first=True)

        return render_template(
            "my_courses.html",
            user=user,
            courses=student.get_courses(
                subject_filter=subject_filter,
                grade_level_filter=grade_level_filter,
                state_filter=state_filter
            ),
            test_history=student.get_test_history(subject_filter),
            upcoming_tests=student.get_upcoming_tests(subject_filter),
            all_subjects=student.get_subjects(),
            all_grades=list(GradeLevel),
            all_states=list(CourseState),
            selected_subject=subject_filter,
            selected_grade=grade_level_filter,
            selected_state=state_filter
        )

    except Exception as e:
        flash_message("An error occurred while loading your courses.", "error")
        current_app.logger.error(f"My courses error: {e}")
        return redirect("/")
