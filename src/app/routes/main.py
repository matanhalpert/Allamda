"""Main routes - home page and error handlers."""
from flask import Blueprint, render_template, redirect, session
from ..auth import login_required
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)


def get_dashboard_data(user):
    """Generate role-based mock dashboard data."""
    user_type = user.get("user_type")
    
    # Get current week dates (Monday to Sunday)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    week_days = [(start_of_week + timedelta(days=i)) for i in range(7)]
    
    # Base data for all users
    dashboard_data = {
        "welcome_message": get_welcome_message(user),
        "highlight": get_user_highlight(user_type),
        "week_days": [
            {
                "date": day,
                "day_name": day.strftime("%a"),
                "day_number": day.day,
                "is_today": day.date() == today.date(),
                "events": get_mock_events(user_type, day)
            }
            for day in week_days
        ],
        "quick_actions": get_quick_actions(user_type)
    }
    
    # Role-specific data
    if user_type == "student":
        dashboard_data.update({
            "active_courses": get_mock_student_courses(),
            "stats": {
                "total_study_hours": 24.5,
                "completion_rate": 78,
                "active_sessions": 3,
                "upcoming_tests": 2
            },
            "recent_achievements": [
                {"title": "Math Excellence", "description": "Scored 95% on Unit 5", "date": "2 days ago"},
                {"title": "Study Streak", "description": "7 days in a row!", "date": "1 week ago"}
            ]
        })
    elif user_type == "class manager":
        dashboard_data.update({
            "class_overview": {
                "total_students": 28,
                "avg_attendance": 92,
                "avg_performance": 85,
                "active_this_week": 25
            },
            "stats": {
                "pending_evaluations": 12,
                "completed_sessions": 15,
                "avg_engagement": 88,
                "upcoming_sessions": 4
            },
            "recent_activities": [
                {"title": "Math Test Grading", "description": "15 tests pending review", "priority": "high"},
                {"title": "Student Evaluations", "description": "Quarterly reviews due", "priority": "medium"}
            ]
        })
    elif user_type == "parent":
        dashboard_data.update({
            "stats": {
                "total_children": 2,
                "avg_performance": 88,
                "study_hours_week": 12,
                "upcoming_events": 3
            }
        })
    elif user_type == "school manager":
        dashboard_data.update({
            "stats": {
                "total_students": 450,
                "total_teachers": 35,
                "avg_school_performance": 84,
                "active_courses": 28
            }
        })
    
    return dashboard_data


def get_welcome_message(user):
    """Generate personalized welcome message based on time of day."""
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    return f"{greeting}, {user.get('first_name')}!"


def get_user_highlight(user_type):
    """Get role-specific highlight message."""
    highlights = {
        "student": "You're making great progress! Keep up the excellent work!",
        "class manager": "Your class is performing well this week!",
        "parent": "Your children are on track with their learning goals.",
        "school manager": "School performance is trending positively this month."
    }
    return highlights.get(user_type, "Welcome to your dashboard!")


def get_mock_events(user_type, day):
    """Generate mock events for a specific day based on user type."""
    events = []
    day_of_week = day.weekday()
    
    if user_type == "student":
        # Add study sessions on weekdays
        if day_of_week < 5:  # Monday to Friday
            if day_of_week in [0, 2, 4]:  # Mon, Wed, Fri
                events.append({"type": "study", "title": "Math Study Session", "time": "15:00"})
            if day_of_week in [1, 3]:  # Tue, Thu
                events.append({"type": "study", "title": "Science Session", "time": "16:00"})
        if day_of_week == 2:  # Wednesday
            events.append({"type": "test", "title": "History Quiz", "time": "14:00"})
        if day_of_week == 4:  # Friday
            events.append({"type": "homework", "title": "Essay Due", "time": "18:00"})
            
    elif user_type == "class manager":
        if day_of_week < 5:  # Weekdays
            events.append({"type": "class", "title": "Morning Class", "time": "09:00"})
            if day_of_week in [1, 3]:  # Tue, Thu
                events.append({"type": "meeting", "title": "Staff Meeting", "time": "15:30"})
        if day_of_week == 2:  # Wednesday
            events.append({"type": "evaluation", "title": "Student Evaluations", "time": "14:00"})
    
    return events


def get_quick_actions(user_type):
    """Get role-specific quick action links."""
    actions = {
        "student": [
            {"title": "Start Studying", "description": "Begin a new study session", "url": "/study", "icon": "book-reader", "color": "primary"},
            {"title": "My Courses", "description": "View all your courses", "url": "/my_courses", "icon": "book-open", "color": "info"},
            {"title": "Take a Test", "description": "Practice with quizzes", "url": "/study/test", "icon": "clipboard-check", "color": "success"}
        ],
        "class manager": [
            {"title": "My Class", "description": "View class overview", "url": "/my_class", "icon": "users", "color": "primary"},
            {"title": "Classroom", "description": "Start a class session", "url": "/classroom", "icon": "chalkboard-teacher", "color": "info"},
            {"title": "Evaluations", "description": "Review student progress", "url": "/my_class", "icon": "chart-line", "color": "success"}
        ],
        "parent": [
            {"title": "My Kids", "description": "View children's progress", "url": "/my_kids", "icon": "user-group", "color": "primary"},
            {"title": "Reports", "description": "Academic reports", "url": "/my_kids", "icon": "file-alt", "color": "info"}
        ],
        "school manager": [
            {"title": "Analytics", "description": "School performance metrics", "url": "/school_analytics", "icon": "chart-line", "color": "primary"},
            {"title": "Reports", "description": "Generate reports", "url": "/school_analytics", "icon": "file-chart-line", "color": "info"}
        ]
    }
    return actions.get(user_type, [])


def get_mock_student_courses():
    """Generate mock course data for students."""
    return [
        {
            "id": 1,
            "name": "Advanced Mathematics",
            "subject": "Mathematics",
            "grade_level": "10th Grade",
            "progress": 75,
            "color": "primary",
            "next_unit": "Trigonometry",
            "icon": "calculator"
        },
        {
            "id": 2,
            "name": "Physics Fundamentals",
            "subject": "Physics",
            "grade_level": "10th Grade",
            "progress": 60,
            "color": "info",
            "next_unit": "Newton's Laws",
            "icon": "atom"
        },
        {
            "id": 3,
            "name": "World History",
            "subject": "History",
            "grade_level": "10th Grade",
            "progress": 85,
            "color": "success",
            "next_unit": "Industrial Revolution",
            "icon": "landmark"
        },
        {
            "id": 4,
            "name": "English Literature",
            "subject": "English",
            "grade_level": "10th Grade",
            "progress": 70,
            "color": "warning",
            "next_unit": "Shakespeare",
            "icon": "book"
        }
    ]


@bp.route("/", methods=["GET", "POST"])
@login_required
def home_page():
    """Home page - dashboard view."""
    user = session.get("user")
    dashboard_data = get_dashboard_data(user)
    return render_template("dashboard.html", user=user, dashboard=dashboard_data)


@bp.app_errorhandler(404)
def page_not_found(_):
    """Handle 404 errors by redirecting to homepage."""
    return redirect("/")
