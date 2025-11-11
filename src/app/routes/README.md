# Flask Routes

Flask blueprint-based routing system handling all HTTP endpoints in the Allamda application. Organized by user role and functionality with clear separation of concerns between presentation logic and business services.

## Overview

The routes package implements Flask's blueprint pattern to modularize the application into logical sections. Each blueprint handles routes for specific user types or features, with authentication/authorization enforced through decorators. Routes coordinate between user input, service layer business logic, and template rendering.

## Structure

```
routes/
├── __init__.py          # Blueprint exports
├── main.py             # Home page and dashboard routing
├── auth.py             # Login/logout authentication
├── student.py          # Student dashboard and features
├── parent.py           # Parent monitoring interface
├── class_manager.py    # Class management interface
├── school_manager.py   # School-wide analytics interface
├── shared.py           # Shared cross-role routes
├── websocket.py        # WebSocket event handlers
└── study/              # Study session routes (subpackage)
    ├── __init__.py
    ├── home.py
    ├── session_creation.py
    ├── session_lifecycle.py
    ├── chat.py
    ├── files.py
    └── helpers.py
```

## Blueprints

### Main Blueprint (`main_bp`)

**Module**: `main.py`  
**URL Prefix**: `/`  
**Purpose**: Home page and role-based dashboard routing

**Routes:**
- `GET /` - Role-based dashboard (redirects to appropriate view)

**Features:**
- Automatic role detection from session
- Dynamic dashboard data generation
- Week calendar view with events
- Quick actions by role
- Role-specific statistics

### Auth Blueprint (`auth_bp`)

**Module**: `auth.py`  
**URL Prefix**: `/`  
**Purpose**: User authentication and session management

**Routes:**
- `GET/POST /login` - User login form and authentication
- `GET /logout` - User logout and session clearing

**Features:**
- Email/password authentication
- "Remember me" functionality
- Session persistence
- Flash message feedback
- Logout confirmation

### Student Blueprint (`student_bp`)

**Module**: `student.py`  
**URL Prefix**: `/`  
**Purpose**: Student-specific features and course management

**Routes:**
- `GET /my_courses` - View enrolled courses with progress tracking

**Features:**
- Course enrollment display
- Progress visualization per course
- Learning unit completion tracking
- Upcoming tests display
- Study session history

### Parent Blueprint (`parent_bp`)

**Module**: `parent.py`  
**URL Prefix**: `/`  
**Purpose**: Parent monitoring and child progress tracking

**Routes:**
- `GET /my_kids` - View all children's academic information

**Features:**
- Multi-child overview
- Individual child progress cards
- Course performance by child
- Study session summaries
- Test results display

### Class Manager Blueprint (`class_manager_bp`)

**Module**: `class_manager.py`  
**URL Prefix**: `/`  
**Purpose**: Class management and student oversight

**Routes:**
- `GET /my_class` - Class roster and analytics dashboard

**Features:**
- Class student roster
- Class-wide performance metrics
- Student progress tracking
- Session supervision interface
- Evaluation management

### School Manager Blueprint (`school_manager_bp`)

**Module**: `school_manager.py`  
**URL Prefix**: `/`  
**Purpose**: School-wide analytics and reporting

**Routes:**
- `GET /school_analytics` - Comprehensive school performance dashboard

**Features:**
- School-wide statistics
- Multi-class comparison
- Grade distribution charts
- Attendance trends
- Top performers identification
- Using Analytics Service for visualizations

### Shared Blueprint (`shared_bp`)

**Module**: `shared.py`  
**URL Prefix**: `/`  
**Purpose**: Cross-role shared functionality

**Routes:**
- `GET /student/<student_id>` - Detailed student view (for parents/managers)

**Features:**
- Unified student detail view
- Access control by role
- Course progress display
- Session history
- Evaluation summaries

### Study Blueprint (`study_bp`)

**Module**: `study/` (subpackage)  
**URL Prefix**: `/study`  
**Purpose**: Complete study session lifecycle management

See [Study Routes README](study/README.md) for detailed documentation.

**Key Routes:**
- `GET /study` - Study hub interface
- `POST /study/create` - Create new session
- `POST /study/start/<id>` - Start session
- `POST /study/chat` - Send message
- `POST /study/end/<id>` - Complete session

### WebSocket Handler (`websocket_bp`)

**Module**: `websocket.py`  
**Purpose**: Real-time communication for voice mode and live updates

**Events:**
- `connect` - WebSocket connection established
- `disconnect` - Connection closed
- Voice input/output events
- Live session updates

## Route Organization Strategy

### By User Role

Routes are grouped by the primary user type accessing them:
- **Student routes**: Course management, study features
- **Parent routes**: Child monitoring, progress tracking
- **Class Manager routes**: Class oversight, evaluations
- **School Manager routes**: School-wide analytics

### By Functionality

Complex features get dedicated subpackages:
- **Study routes**: Separate subpackage for session management
- **Shared routes**: Cross-role functionality in one place

### Blueprint Registration

All blueprints registered in `src/app/__init__.py`:

```python
def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(class_manager_bp)
    app.register_blueprint(school_manager_bp)
    app.register_blueprint(shared_bp)
    app.register_blueprint(study_bp)
    
    return app
```

## Authentication & Authorization

### Decorators

Routes use authentication decorators from `src/app/auth.py`:

**@login_required**
```python
@bp.route('/my_courses')
@login_required
def my_courses():
    # User must be logged in
```

**@logout_required**
```python
@bp.route('/login')
@logout_required
def login():
    # User must NOT be logged in (redirects if already authenticated)
```

**@user_required(UserType)**
```python
@bp.route('/my_class')
@login_required
@user_required(UserType.CLASS_MANAGER)
def my_class():
    # User must be logged in AND be a class manager
```

### Session Management

User data stored in Flask session:

```python
session['user'] = {
    'id': user.id,
    'username': user.username,
    'user_type': user.user_type.value,
    'first_name': user.first_name,
    'last_name': user.last_name
}

# Access in routes
user_id = session['user']['id']
user_type = session['user']['user_type']
```

## Database Session Management

Routes use `@with_db_session` decorator for automatic database session handling:

```python
from src.database import with_db_session

@bp.route('/my_courses')
@login_required
@with_db_session
def my_courses():
    # Database session automatically available
    # Uses get_current_session() internally
    student = Student.get_by(id=student_id, first=True)
    # Session automatically committed on success, rolled back on exception
```

## Integration with Services

Routes delegate business logic to service layer:

```python
from src.services.course_prioritization import get_next_course
from src.services.learning_unit_assignment import assign_learning_units
from src.services.study_session import create_home_study_session

@bp.route('/study/create', methods=['POST'])
@login_required
@with_db_session
def create_session():
    # Get form data
    course_id = request.form.get('course_id')
    
    # Use services for business logic
    learning_units = assign_learning_units(student, course)
    session = create_home_study_session(
        student_id=student_id,
        course_id=course_id,
        learning_unit_names=[u.name for u in learning_units]
    )
    
    # Return response
    return redirect(f'/study/chat/{session.id}')
```

## Template Rendering

Routes use Jinja2 templates from `src/app/templates/`:

```python
@bp.route('/my_courses')
@login_required
def my_courses():
    courses = get_student_courses(student_id)
    
    return render_template(
        'my_courses.html',
        courses=courses,
        user=session['user']
    )
```

## Error Handling

### Flash Messages

Routes use flash message utility for user feedback:

```python
from ..utils import flash_message

@bp.route('/login', methods=['POST'])
def login():
    if not valid_credentials:
        flash_message("Invalid email or password.", "error")
        return render_template('login.html')
    
    flash_message(f"Welcome back, {user.first_name}!", "success")
    return redirect('/')
```

**Flash Categories:**
- `success` - Green, positive feedback
- `error` - Red, error messages
- `warning` - Yellow, warnings
- `info` - Blue, informational messages

### Exception Handling

```python
@bp.route('/some_route')
def some_route():
    try:
        # Route logic
        result = some_service_call()
        return render_template('success.html', data=result)
    except CustomException as e:
        flash_message(str(e), "error")
        return redirect('/fallback')
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {e}")
        flash_message("An unexpected error occurred.", "error")
        return render_template('error.html'), 500
```

## Request Handling Patterns

### GET Requests (Display)
```python
@bp.route('/my_courses')
def my_courses():
    # Fetch data
    courses = get_courses(student_id)
    
    # Render template
    return render_template('my_courses.html', courses=courses)
```

### POST Requests (Form Submission)
```python
@bp.route('/create_session', methods=['POST'])
def create_session():
    # Get form data
    course_id = request.form.get('course_id')
    
    # Validate
    if not course_id:
        flash_message("Please select a course.", "error")
        return redirect('/study')
    
    # Process
    session = create_home_study_session(...)
    
    # Redirect
    return redirect(f'/study/chat/{session.id}')
```

### AJAX/JSON Requests
```python
@bp.route('/api/get_data')
def get_data():
    data = fetch_some_data()
    return jsonify({
        'success': True,
        'data': data
    })
```

## URL Patterns

### RESTful Conventions
- `GET /resource` - List/index
- `GET /resource/<id>` - Show specific item
- `POST /resource/create` - Create new item
- `POST /resource/<id>/update` - Update item
- `POST /resource/<id>/delete` - Delete item

### Study Session Patterns
- `GET /study` - Hub/home
- `POST /study/create` - Create session
- `GET /study/chat/<id>` - Session interface
- `POST /study/start/<id>` - Start session
- `POST /study/pause/<id>` - Pause session
- `POST /study/end/<id>` - End session

## Testing Routes

```python
# In tests/test_routes.py
def test_login_route(client):
    response = client.post('/login', data={
        'email': 'student@example.com',
        'password': 'password'
    })
    assert response.status_code == 302  # Redirect
    assert b'Welcome' in response.data

def test_protected_route(client):
    # Without login
    response = client.get('/my_courses')
    assert response.status_code == 302  # Redirect to login
    
    # With login
    client.post('/login', data={...})
    response = client.get('/my_courses')
    assert response.status_code == 200
```

## Dependencies

- **Flask**: Web framework and blueprint system
- **Jinja2**: Template rendering
- **Werkzeug**: Request/response handling
- **Flask-Session**: Server-side session management
- **SQLAlchemy**: Database ORM (via models)
- **Service Layer**: Business logic delegation

## Notes

- All routes use blueprint pattern for modularity
- Authentication required for all routes except login
- Database sessions managed automatically via decorators
- Flash messages provide user feedback
- Services handle business logic, routes handle presentation
- WebSocket support for real-time features
- RESTful URL patterns where applicable

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

