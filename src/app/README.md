# Flask Application

Flask web application serving the allamda system with routes, templates, and static assets.

## Structure

```
app/
├── __init__.py           # Application factory (create_app)
├── main.py              # Entry point
├── config.py            # Configuration classes (Development, Production, Testing)
├── routes/              # Flask blueprints (URL routing)
│   ├── main.py         # Home page, error handlers
│   ├── auth.py         # Login/logout
│   ├── student.py      # Student dashboard and courses
│   ├── parent.py       # Parent views (children progress)
│   ├── class_manager.py # Class management and analytics
│   ├── school_manager.py # School-wide analytics
│   ├── study.py        # Study session routes (create, chat, end)
│   └── shared.py       # Shared routes (student detail views)
├── templates/          # Jinja2 HTML templates
├── static/            # Static assets (CSS, JavaScript)
│   ├── *.css          # Stylesheets
│   └── js/            # JavaScript files for study interface
├── auth.py            # Route decorators (auth, user type checks)
└── utils/            # App-specific utilities (flash messages)
```

## Application Factory

The app uses Flask's application factory pattern:

```python
from src.app import create_app
app = create_app()
```

The factory:
- Loads configuration based on `FLASK_ENV` environment variable
- Initializes Flask-Session for server-side sessions
- Registers all blueprints
- Sets up context processors (flash messages)

## Routes (Blueprints)

### Main (`main_bp`)
- `/` - Dashboard/home page (redirects based on user type)

### Auth (`auth_bp`)
- `/login` - User authentication
- `/logout` - Session termination

### Student (`student_bp`)
- `/my_courses` - View enrolled courses and progress

### Parent (`parent_bp`)
- `/my_kids` - View children's courses and progress

### Class Manager (`class_manager_bp`)
- `/my_class` - View class roster and analytics

### School Manager (`school_manager_bp`)
- `/school_analytics` - School-wide performance analytics

### Study (`study_bp`)
- `/study` - Study session setup page
- `/study/create` - Create new study session
- `/study/chat/<session_id>` - Chat interface for active session
- `/study/pause/<session_id>` - Pause session
- `/study/resume/<session_id>` - Resume paused session
- `/study/end/<session_id>` - End session with feedback
- `/study/get_learning_units/<course_id>` - AJAX endpoint for learning units

### Shared (`shared_bp`)
- `/student/<student_id>` - Student detail view (used by parents/managers)

## Authentication & Authorization

### Authentication Decorators
- `@login_required` - Ensures user is logged in
- `@user_required(UserType)` - Ensures user has specific role

### Session Management
- Uses Flask-Session (server-side sessions)
- User data stored in `session['user']` dict with:
  - `id`, `username`, `user_type`, `name`

## Configuration

Three configuration modes:
- **Development**: Debug mode enabled, development settings
- **Production**: Production security settings, requires SECRET_KEY env var
- **Testing**: Testing mode with debug enabled

Key settings:
- `SECRET_KEY` - Flask secret (set via environment variable)
- `UPLOAD_FOLDER` - Directory for study session file uploads
- `ALLOWED_EXTENSIONS` - File types allowed for uploads
- `MAX_CONTENT_LENGTH` - 16MB max file size

## Templates

Templates use Jinja2 and inherit from `base.html`:
- `dashboard.html` - Main dashboard
- `study.html` - Study session setup
- `study_chat.html` - Chat interface
- `study_end.html` - Session completion form
- `my_courses.html` - Course listing
- `student_detail.html` - Student progress view
- `school_analytics.html` - Analytics dashboard

## Static Assets

- `base.css`, `components.css` - Base styling
- `study-session.css` - Study interface styles
- `analytics.css` - Analytics page styles
- `js/study-*.js` - JavaScript for study session interactions

## Integration Points

- **Database**: Uses `DatabaseManager` for session management
- **Services**: Calls study session, prioritization, and assignment services
- **Models**: Uses SQLAlchemy models for data access
- **AI Agents**: Teacher and Evaluator agents via service layer
