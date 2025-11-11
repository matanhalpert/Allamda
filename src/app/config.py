"""Flask application configuration."""
import os
from pathlib import Path
from src.enums import ConfigName, FileType


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = Path(__file__).parent / 'flask_session'
    
    # File upload settings
    UPLOAD_FOLDER = Path(__file__).parent.parent.parent / 'uploads' / 'study_sessions'
    TTS_AUDIO_FOLDER = Path(__file__).parent.parent.parent / 'uploads' / 'tts_audio'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {
        FileType.IMAGE: {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        FileType.DOCUMENT: {'doc', 'docx'},
        FileType.PDF: {'pdf'},
        FileType.TEXT: {'txt', 'md'},
        FileType.SPREADSHEET: {'xls', 'xlsx', 'csv'},
        FileType.PRESENTATION: {'ppt', 'pptx'}
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def init_app(cls, app):
        """Production-specific initialization."""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


config = {
    ConfigName.DEVELOPMENT: DevelopmentConfig,
    ConfigName.PRODUCTION: ProductionConfig,
    ConfigName.TESTING: TestingConfig,
    ConfigName.DEFAULT: DevelopmentConfig
}
