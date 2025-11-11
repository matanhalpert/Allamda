import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.utils import Logger
from src.database.session_context import SessionContext

# Load environment variables from .env file
load_dotenv()


class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None

    @classmethod
    def initialize(cls):
        """Initialize database connection if not already initialized."""
        if cls._engine is None:
            cls.validate_environment()
            cls.ensure_database_exists()
            cls._engine = cls.create_database_engine()
            cls._session_factory = sessionmaker(bind=cls._engine)
        return cls._session_factory

    @staticmethod
    def validate_environment() -> None:
        """Validates that all required environment variables are present."""
        required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}\n"
            error_msg += "Please create a .env file in the project root with the following variables:\n"
            error_msg += "DB_USER=your_username\n"
            error_msg += "DB_PASSWORD=your_password\n"
            error_msg += "DB_HOST=your_host\n"
            error_msg += "DB_NAME=your_database_name"
            raise ValueError(error_msg)

    @classmethod
    def ensure_database_exists(cls):
        """Creates the target database if it doesn't already exist."""
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_NAME = os.getenv('DB_NAME')
        ROOT_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}"

        temp_engine = create_engine(ROOT_DATABASE_URL)
        try:
            with temp_engine.connect() as connection:
                connection = connection.execution_options(isolation_level="AUTOCOMMIT")
                connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
                Logger.info(f"Database '{DB_NAME}' ensured to exist")
        except SQLAlchemyError as e:
            Logger.error(f"Error creating database '{DB_NAME}': {e}")
            raise
        finally:
            temp_engine.dispose()

    @classmethod
    def create_database_engine(cls):
        """Creates and tests the main database engine with connection pooling."""
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_NAME = os.getenv('DB_NAME')
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,  # Validates connections before use
            pool_recycle=300,  # Recycle connections every 5 minutes
            echo=False  # Set to True for SQL query debugging
        )

        try:
            # Test the connection
            with engine.connect():
                pass
            Logger.info(f"Successfully connected to database '{DB_NAME}'")
            return engine
        except OperationalError as e:
            Logger.error(f"Error connecting to database '{DB_NAME}': {e}")
            raise

    @classmethod
    def get_session(cls, auto_commit: bool = True):
        """
        Get a database session as a context manager.

        Args:
            auto_commit: Whether to auto-commit on successful completion (default: True)
            
        Returns:
            SessionContext manager
        """
        if cls._session_factory is None:
            cls.initialize()
        
        session = cls._session_factory()
        return SessionContext(session, auto_commit=auto_commit)

    @classmethod
    def create_tables(cls) -> None:
        """Creates all database tables defined in the imported models."""
        from src.models import Base
        
        if cls._engine is None:
            cls.initialize()

        try:
            Base.metadata.create_all(cls._engine)
            Logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            Logger.error(f"Error creating tables: {e}")
            raise

    @classmethod
    def drop_tables(cls, force: bool = False) -> None:
        """Drops all database tables after explicit user confirmation."""
        if cls._engine is None:
            cls.initialize()

        if not force:
            Logger.warning("WARNING: This will permanently delete all data in the database!")
            confirm = input("Are you sure you want to drop all tables? Type 'yes' to confirm: ")
            should_drop = confirm.strip().lower() == "yes"
        else:
            should_drop = True
            Logger.warning("Force dropping all tables to fix schema issues...")

        if should_drop:
            try:
                # For MySQL, disable foreign key checks and then drop all tables
                with cls._engine.connect() as connection:
                    connection = connection.execution_options(isolation_level="AUTOCOMMIT")
                    connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                    
                    # Get all table names first
                    result = connection.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in result]
                    
                    # Drop each table individually
                    for table in tables:
                        connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    
                    connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                Logger.info("All tables dropped successfully")
            except SQLAlchemyError as e:
                Logger.error(f"Error dropping tables: {e}")
        else:
            Logger.info("Drop tables operation cancelled by user")

    @classmethod
    def populate_sample_data(cls, clear_existing: bool = False) -> None:
        """Populate the database with sample data.
        
        Args:
            clear_existing: If True, drops all tables and recreates them before populating
        """
        from src.database.sample_data import populate_sample_data
        
        if cls._engine is None:
            cls.initialize()
        
        if clear_existing:
            Logger.info("Dropping all tables to clear existing data...")
            cls.drop_tables(force=True)
            Logger.info("Recreating tables...")
            cls.create_tables()
        
        with cls.get_session() as session:
            try:
                Logger.info("Populating sample data...")
                populate_sample_data()
            except Exception as e:
                Logger.error(f"Error populating sample data: {e}")
                raise

    @classmethod
    def cleanup(cls):
        """Properly disposes of the database engine and its connection pool."""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            Logger.info("Database engine disposed")


if __name__ == "__main__":
    try:
        # DatabaseManager.create_tables()
        DatabaseManager.populate_sample_data(clear_existing=True)
        # DatabaseManager.drop_tables()     # CAUTION!
    except Exception as e:
        Logger.error(f"Database initialization failed: {e}")
        exit(1)
    finally:
        DatabaseManager.cleanup()
