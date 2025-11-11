"""School manager-specific routes."""
from flask import Blueprint, render_template, redirect, session, current_app, request
from ..auth import login_required, user_required
from ..utils import flash_message
from src.database import with_db_session
from src.models import SchoolManager, School
from src.enums import UserType
from src.services.analytics import GraphingService

bp = Blueprint('school_manager', __name__)


@bp.route("/school_analytics", methods=["GET"])
@login_required
@user_required(UserType.SCHOOL_MANAGER)
@with_db_session
def school_analytics():
    """Display school analytics dashboard for the logged-in school manager."""
    user = session.get("user")
    manager_id = user.get("id")

    try:
        school_manager: SchoolManager = SchoolManager.get_by(id=manager_id, first=True)

        if not school_manager.assigned_to_school:
            flash_message("You are not currently assigned to any school.", "warning")
            return render_template("school_analytics.html", user=user, has_school=False)

        school: School = school_manager.get_school()

        period = request.args.get('period', '365')
        period_map = {
            '30': 30,
            '90': 90,
            '365': 365,
            'all': None
        }
        days = period_map.get(period, 30)

        analytics_data = {
            'total_students': school.get_total_students_count(),
            'active_courses': school.get_active_courses_count(),
            'average_grade': school.get_school_average_grade(days=days),
            'attendance_rate': school.get_school_attendance_rate(days=days if days else 30),
            'top_students': school.get_top_students(limit=10),
            'class_performance': school.get_average_grades_by_class(),
            'grade_trends': school.get_grade_trends_over_time(days=days if days else 90),
            'attendance_trends': school.get_attendance_trends_over_time(days=days if days else 90)
        }

        charts = {
            'class_performance': GraphingService.create_class_performance_chart(
                analytics_data['class_performance']
            ),
            'top_students': GraphingService.create_top_students_chart(
                analytics_data['top_students'], 
                limit=10
            ),
            'grade_trends': GraphingService.create_grade_trends_chart(
                analytics_data['grade_trends']
            ),
            'attendance_trends': GraphingService.create_attendance_trends_chart(
                analytics_data['attendance_trends']
            )
        }

        return render_template(
            "school_analytics.html",
            user=user,
            has_school=True,
            school=school.to_dict(),
            analytics=analytics_data,
            charts=charts,
            selected_period=period
        )

    except Exception as e:
        flash_message("An error occurred while loading analytics.", "error")
        current_app.logger.error(f"School analytics error: {e}")
        return redirect("/")
