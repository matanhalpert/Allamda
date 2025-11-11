"""Study routes package - contains all study session related routes."""

from flask import Blueprint

bp = Blueprint('study', __name__)

from . import home, session_creation, chat, session_lifecycle, files

__all__ = ['bp']
