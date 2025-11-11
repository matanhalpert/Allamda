"""File serving routes for study sessions."""

import os
from flask import session, current_app, send_from_directory

from ...auth import login_required, user_required
from src.database import with_db_session
from src.models.session_models import HomeHoursStudySession
from src.enums import UserType

from src.app.routes.study import bp


@bp.route("/uploads/study_sessions/<int:session_id>/<filename>")
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def serve_file(session_id, filename):
    """Serve uploaded files with access control."""
    user = session.get("user")
    student_id = user.get("id")

    study_session = HomeHoursStudySession.get_by_id_and_student(
        session_id, student_id
    )
    if not study_session:
        return "Access denied", 403
    
    upload_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        str(session_id)
    )
    
    return send_from_directory(upload_dir, filename)
