"""Authentication routes - login and logout."""
from flask import Blueprint, render_template, redirect, request, session, current_app
from ..auth import logout_required
from ..utils import flash_message
from src.database import with_db_session
from src.models import User

bp = Blueprint('auth', __name__)


@bp.route("/login", methods=["GET", "POST"])
@logout_required
@with_db_session
def login():
    """Handle user login."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        if not email or not password:
            flash_message("Please enter both email and password.", "error")
            return render_template("login.html")

        try:
            user: User = User.authenticate_any_user(email, password)

            if user:
                session["user"] = user.to_dict()
                session.permanent = remember

                flash_message(f"Welcome back, {user.first_name}!", "success")
                return redirect("/")
            else:
                flash_message("Invalid email or password. Please try again.", "error")

        except Exception as e:
            flash_message("An error occurred during login. Please try again.", "error")
            current_app.logger.error(f"Login error: {e}")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Handle user logout."""
    user_name = session.get("user", {}).get("first_name", "")
    session.clear()
    if user_name:
        flash_message(f"Goodbye, {user_name}! You have been logged out successfully.", "info")
    return redirect("/login")
