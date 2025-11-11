"""Routes package - contains all Flask blueprints."""
from .auth import bp as auth_bp
from .student import bp as student_bp
from .parent import bp as parent_bp
from .class_manager import bp as class_manager_bp
from .school_manager import bp as school_manager_bp
from .shared import bp as shared_bp
from .main import bp as main_bp
from .study import bp as study_bp

__all__ = [
    'auth_bp',
    'student_bp',
    'parent_bp',
    'class_manager_bp',
    'school_manager_bp',
    'shared_bp',
    'main_bp',
    'study_bp'
]
