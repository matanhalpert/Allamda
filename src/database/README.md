# Database Management

Database setup, initialization, and management utilities using SQLAlchemy with MySQL.

## Structure

```
database/
├── __init__.py           # DatabaseManager class export
├── setup.py             # DatabaseManager implementation
├── sample_data.py       # Sample data population script
├── session_context.py   # Context-based session management
└── decorators.py        # Session management decorators
```

## DatabaseManager

Singleton pattern class that manages database connections and operations.

### Key Methods

**Initialization:**
- `initialize()` - Sets up database connection pool
- `validate_environment()` - Checks required environment variables
- `ensure_database_exists()` - Creates database if it doesn't exist
- `create_database_engine()` - Creates SQLAlchemy engine with connection pooling

**Session Management:**
- `get_session()` - Returns SQLAlchemy session (use in context manager)

**Schema Management:**
- `create_tables()` - Creates all tables from models
- `drop_tables(force=False)` - Drops all tables (with confirmation)

**Data Management:**
- `populate_sample_data(clear_existing=False)` - Loads sample data
- `cleanup()` - Disposes of connection pool

## Environment Variables

Required environment variables (set in `.env`):
- `DB_USER` - MySQL username
- `DB_PASSWORD` - MySQL password
- `DB_HOST` - MySQL host (e.g., `localhost` or `127.0.0.1`)
- `DB_NAME` - Database name

## Session Context Management (`session_context.py`)

Modern, context-based session management using Python's `contextvars` module for thread-safe, automatic session access throughout the application.

### Core Functions

**get_current_session()**
```python
from src.database.session_context import get_current_session

# Access current session from anywhere
session = get_current_session()
student = session.query(Student).filter_by(id=1).first()

# Raises RuntimeError if no active session context
```

**set_current_session()**
```python
# Used internally by context managers
set_current_session(session)
```

**has_active_session()**
```python
# Check if session context is active
if has_active_session():
    session = get_current_session()
```

### SessionContext Class

Context manager for establishing session contexts:

```python
from src.database.session_context import SessionContext

session = create_session()
with SessionContext(session, auto_commit=True):
    # Session available via get_current_session()
    # Auto-commits on success, rolls back on exception
    # Closes session on exit
```

**Benefits:**
- Thread-safe via contextvars
- No explicit session passing
- Automatic commit/rollback
- Nested context support
- Automatic cleanup

## Decorators (`decorators.py`)

Decorators for automatic session context management in functions and routes.

### @with_db_session

Decorator that establishes a database session context for a function.

**Usage:**
```python
from src.database import with_db_session

@with_db_session
def my_function():
    # Session automatically available
    session = get_current_session()
    student = Student.get_by(id=1, first=True)
    return student

# No need to pass session as parameter
result = my_function()
```

**In Flask Routes:**
```python
from src.database import with_db_session
from src.app.auth import login_required

@bp.route('/my_courses')
@login_required
@with_db_session
def my_courses():
    # Session context automatically established
    student = Student.get_by(id=student_id, first=True)
    courses = student.get_courses()
    return render_template('my_courses.html', courses=courses)
```

**Features:**
- Reuses existing session if one is active (nested calls)
- Creates new session if none exists
- Automatic commit on success
- Automatic rollback on exception
- Automatic session closure
- No boilerplate needed

**Nested Context Example:**
```python
@with_db_session
def outer_function():
    # Creates session context
    student = Student.get_by(id=1, first=True)
    inner_function()  # Reuses same session
    return student

@with_db_session
def inner_function():
    # Reuses existing session context
    # No new session created
    course = Course.get_by(id=5, first=True)
    return course
```

## Usage

### Basic Setup

```python
from src.database import DatabaseManager

# Initialize and create tables
DatabaseManager.initialize()
DatabaseManager.create_tables()

# Populate with sample data
DatabaseManager.populate_sample_data(clear_existing=True)
```

### Using Context Manager (Low-Level)

```python
from src.database import DatabaseManager

# Context manager for explicit control
with DatabaseManager.get_session() as session:
    # Session available in context
    from src.database.session_context import get_current_session
    session = get_current_session()
    
    student = Student.get_by(id=1, first=True)
    # Changes are automatically committed on successful exit
    # Rolled back on exception
```

### Using Decorator (Recommended)

```python
from src.database import with_db_session
from src.models import Student

@with_db_session
def get_student_courses(student_id):
    # No session parameter needed
    student = Student.get_by(id=student_id, first=True)
    return student.get_courses()

# Clean, simple calls
courses = get_student_courses(student_id=1)
```

### In Models

Models use `get_current_session()` for queries:

```python
from src.models.base import Base
from src.database.session_context import get_current_session

class Student(Base):
    @classmethod
    def get_by(cls, first=False, **filters):
        # Automatically uses current session
        session = get_current_session()
        query = session.query(cls)
        # ... filtering logic ...
        return query.first() if first else query.all()
```

### In Services

Services can assume session context exists:

```python
# services/study_session/lifecycle.py
def create_home_study_session(...):
    # Uses current session via get_current_session()
    session = get_current_session()
    
    # Create session
    study_session = HomeHoursStudySession(...)
    session.add(study_session)
    session.flush()  # Get ID
    
    # Session will be committed by decorator
    return study_session
```

### Standalone Script

```python
# Can be run directly
python src/database/setup.py
```

## Connection Pooling

The engine uses connection pooling with:
- `pool_pre_ping=True` - Validates connections before use
- `pool_recycle=300` - Recycles connections every 5 minutes
- Handles MySQL connection timeouts gracefully

## Sample Data

`sample_data.py` populates the database with:
- Schools, classes, users (students, parents, managers)
- Subjects, courses, learning units
- Test data, Q&A resources
- Enrollments and associations
- AI agents (Teacher, Evaluator)
- Sample study sessions and evaluations

Useful for:
- Development and testing
- Demonstrating system capabilities
- Seeding initial data

## Safety Features

- **Database Creation**: Safely creates database if missing
- **Drop Confirmation**: Requires explicit confirmation before dropping tables
- **Transaction Safety**: Uses SQLAlchemy transactions (automatic rollback on error)
- **Foreign Key Handling**: Properly handles MySQL foreign key constraints during drops

## Notes

- Uses `pymysql` driver for MySQL
- All table creation uses SQLAlchemy metadata from models
- Session factory pattern ensures consistent session handling
- Error handling with proper logging via `src.utils.logger`
