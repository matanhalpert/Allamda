"""Parent-specific routes."""
from flask import Blueprint, render_template, redirect, session, current_app
from ..auth import login_required, user_required
from ..utils import flash_message
from src.database import with_db_session
from src.models import Parent
from src.enums import UserType

bp = Blueprint('parent', __name__)


@bp.route("/my_kids", methods=["GET"])
@login_required
@user_required(UserType.PARENT)
@with_db_session
def my_kids():
    """Display all children for the logged-in parent."""
    user = session.get("user")
    parent_id = user.get("id")

    try:
        parent: Parent = Parent.get_by(id=parent_id, first=True)
        children = parent.get_children()

        return render_template(
            "my_kids.html",
            user=user,
            children=children
        )

    except Exception as e:
        flash_message("An error occurred while loading your children's information.", "error")
        current_app.logger.error(f"My kids error: {e}")
        return redirect("/")
