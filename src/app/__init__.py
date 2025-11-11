"""Flask application factory."""
import os
from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO

from src.enums import ConfigName

socketio = SocketIO()

__all__ = ['create_app', 'socketio']


def create_app(config_name: ConfigName = None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', ConfigName.DEVELOPMENT)
    
    # Load configuration
    from src.app.config import config
    app.config.from_object(config[config_name])
    
    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TTS_AUDIO_FOLDER'], exist_ok=True)
    
    # Initialize Flask-Session
    Session(app)
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register context processors
    from .utils import get_flash_messages
    
    @app.context_processor
    def inject_flash_messages():
        """Make flash_messages available to all templates."""
        return dict(get_messages=get_flash_messages)
    
    # Register blueprints
    from .routes import (
        main_bp,
        auth_bp,
        student_bp,
        parent_bp,
        class_manager_bp,
        school_manager_bp,
        shared_bp,
        study_bp
    )
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(class_manager_bp)
    app.register_blueprint(school_manager_bp)
    app.register_blueprint(shared_bp)
    app.register_blueprint(study_bp)
    
    # Import and register WebSocket handlers after blueprints
    from .routes import websocket
    
    return app, socketio
