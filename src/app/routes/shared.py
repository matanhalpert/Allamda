"""Shared routes - accessible by multiple user types."""
from flask import Blueprint, render_template, redirect, request, session, current_app
from ..auth import login_required, user_required
from ..utils import flash_message
from src.database import with_db_session
from src.models import Parent, Student
from src.models.session_models import HomeHoursStudySession, SchoolHoursStudySession
from src.enums import UserType

bp = Blueprint('shared', __name__)


@bp.route("/student/<int:student_id>", methods=["GET"])
@login_required
@user_required(UserType.CLASS_MANAGER, UserType.PARENT)
@with_db_session
def student_detail(student_id):
    """Display detailed information about a specific student.

    Accessible by:
    - CLASS_MANAGER: Can view students in their managed class
    - PARENT: Can view their own children
    """
    user = session.get("user")
    user_id = user.get("id")
    user_type = user.get("user_type", "")

    def custom_redirect():
        """Redirects based on user type."""
        if user_type == UserType.CLASS_MANAGER:
            return redirect("/my_class")
        else:
            return redirect("/my_kids")

    try:
        student = Student.get_by(id=student_id, first=True)

        if not student:
            flash_message("Student not found.", "error")
            return custom_redirect()

        # Verify access permissions
        if user_type == UserType.CLASS_MANAGER:
            from src.models import ClassManager
            class_manager: ClassManager = ClassManager.get_by(id=user_id, first=True)

            if not class_manager.manage(student):
                flash_message("You do not have access to this student's information.", "error")
                return redirect("/my_class")

            back_label = "My Class"

        else:  # Parent
            parent: Parent = Parent.get_by(id=user_id, first=True)

            if not parent.has_child(student):
                flash_message("You do not have access to this student's information.", "error")
                return redirect("/my_kids")

            back_label = "My Kids"

        return render_template(
            "student_detail.html",
            user=user,
            student=student.to_dict(),
            average_grade=student.get_average_grade(),
            attendance=student.get_attendance_behavior(days=365),
            learning_profile=student.get_learning_profile(),
            recent_evaluations=student.get_all_recent_evaluations(),
            courses=student.get_courses(),
            upcoming_tests=student.get_upcoming_tests(),
            test_history=student.get_test_history(),
            back_label=back_label
        )

    except Exception as e:
        flash_message("An error occurred while loading student information.", "error")
        current_app.logger.error(f"Student detail error: {e}")
        return custom_redirect()


@bp.route("/course/<int:course_id>", methods=["GET"])
@login_required
@user_required(UserType.STUDENT, UserType.CLASS_MANAGER, UserType.PARENT)
@with_db_session
def course_detail(course_id):
    """Display detailed information about a specific course.
    
    Accessible by:
    - STUDENT: Can view their own courses
    - CLASS_MANAGER: Can view courses for students in their class
    - PARENT: Can view courses for their children
    """
    user = session.get("user")
    user_type = user.get("user_type", "").lower()

    try:
        student_id = request.args.get("student_id", type=int) or user.get("id")
        student: Student = Student.get_by(id=student_id, first=True)

        course = student.get_courses(
            course_id=course_id,
            include_learning_units=True,
            include_tests=True
        )

        if not course:
            flash_message("Course not found or you are not enrolled in this course.", "error")
            if user_type == UserType.STUDENT:
                return redirect("/my_courses")
            else:
                return redirect(f"/student/{student_id}")

        if user_type == UserType.STUDENT:
            back_label = "My Courses"
        else:
            back_label = "Student Details"

        return render_template(
            "course_detail.html",
            user=user,
            course=course,
            student_id=student_id,
            back_label=back_label
        )

    except Exception as e:
        flash_message("An error occurred while loading course information.", "error")
        current_app.logger.error(f"Course detail error: {e}")
        if user_type == UserType.STUDENT:
            return redirect("/my_courses")
        elif user_type == UserType.CLASS_MANAGER:
            return redirect("/my_class")
        else:
            return redirect("/my_kids")


@bp.route("/study/session/<int:session_id>", methods=["GET"])
@login_required
@user_required(UserType.STUDENT, UserType.CLASS_MANAGER)
@with_db_session
def session_details(session_id: int):
    """Display comprehensive study session details with role-based access."""
    user = session.get("user")
    user_id = user.get("id")
    user_type = user.get("user_type")

    def custom_redirect():
        """Redirects based on user type."""
        if user_type_enum == UserType.STUDENT:
            return redirect("/study")
        elif user_type_enum == UserType.CLASS_MANAGER:
            return redirect("/classroom")
        else:
            return redirect("/")

    try:
        if isinstance(user_type, str):
            user_type_enum = UserType(user_type)
        else:
            user_type_enum = user_type
    except (KeyError, AttributeError, ValueError):
        flash_message("Invalid user type.", "error")
        current_app.logger.error(f"Invalid user type: {user_type}")
        return redirect("/")
    
    try:

        session_data = None

        session_data = HomeHoursStudySession.get_session_details(
            session_id=session_id,
            requesting_user_id=user_id,
            requesting_user_type=user_type_enum
        )
        if not session_data:
            session_data = SchoolHoursStudySession.get_session_details(
                session_id=session_id,
                requesting_user_id=user_id,
                requesting_user_type=user_type_enum
            )

        if not session_data:
            flash_message("Session not found or you don't have permission to view it.", "error")

            custom_redirect()

        return render_template(
            "study_session_detail.html",
            user=user,
            session=session_data
        )
        
    except Exception as e:
        flash_message("An error occurred while loading session details.", "error")
        current_app.logger.error(f"Session details error: {e}")
        
        custom_redirect()
