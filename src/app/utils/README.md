# App Utilities

Flask application-specific utility functions for flash messaging and WebSocket event handling. These utilities are tightly coupled with the Flask app context and provide reusable patterns for user feedback and real-time communication.

## Overview

The app utils package contains Flask-specific helper functions distinct from general utilities in `src/utils/`. These functions require Flask application context and integrate with Flask-Session for messaging and Flask-SocketIO for real-time events. The utilities provide consistent patterns for displaying user feedback and broadcasting events to specific users or groups.

## Structure

```
app/utils/
├── __init__.py       # Package exports
├── flash.py         # Flash message system
├── websocket.py     # WebSocket event utilities
└── README.md        # This file
```

## Flash Message System (`flash.py`)

### Purpose

Provides temporary user feedback messages that persist across redirects and display once to users. Alternative to Flask's built-in flash() that uses Flask session storage directly.

### Functions

#### flash_message()

**Purpose**: Add a flash message to session storage

**Signature:**
```python
def flash_message(message: str, category: str = "info") -> None
```

**Parameters:**
- `message` (str): Message text to display
- `category` (str): Message type/styling
  - `"info"` - Blue, informational (default)
  - `"success"` - Green, success confirmation
  - `"warning"` - Yellow, warnings
  - `"error"` - Red, error messages

**Usage:**
```python
from src.app.utils import flash_message

# Success message
flash_message("Session started successfully!", "success")

# Error message
flash_message("Failed to load course data.", "error")

# Info message (default)
flash_message("Session will end in 5 minutes.")

# Warning message
flash_message("This action cannot be undone.", "warning")
```

#### get_flash_messages()

**Purpose**: Retrieve and clear all pending flash messages

**Signature:**
```python
def get_flash_messages() -> List[Dict[str, str]]
```

**Returns:**
```python
[
    {"text": "Message 1", "category": "success"},
    {"text": "Message 2", "category": "info"}
]
```

**Usage in Routes:**
```python
@bp.route('/some_route')
def some_route():
    flash_message("Operation completed", "success")
    return redirect('/dashboard')
    # Message will display on dashboard page
```

### Template Integration

Flash messages typically rendered in base template:

```html
<!-- base.html -->
{% for message in get_flash_messages() %}
<div class="alert alert-{{ message.category }}">
    {{ message.text }}
</div>
{% endfor %}
```

### Context Processor

Messages made available via context processor in `src/app/__init__.py`:

```python
@app.context_processor
def inject_flash_messages():
    from src.app.utils import get_flash_messages
    return {'get_flash_messages': get_flash_messages}
```

### Message Categories and Styling

| Category | Color | Bootstrap Class | Use Case |
|----------|-------|----------------|----------|
| **success** | Green | `alert-success` | Successful operations |
| **error** | Red | `alert-danger` | Errors, failures |
| **warning** | Yellow | `alert-warning` | Warnings, cautions |
| **info** | Blue | `alert-info` | General information |

### Message Lifecycle

```
1. Route calls flash_message()
   ↓
2. Message stored in session['messages']
   ↓
3. Route redirects to another page
   ↓
4. New page renders
   ↓
5. Template calls get_flash_messages()
   ↓
6. Messages returned and cleared from session
   ↓
7. Messages displayed to user (one-time)
```

## WebSocket Utilities (`websocket.py`)

### Purpose

Helper functions for emitting WebSocket events to specific users, classes, or managers. Provides consistent room naming and event broadcasting patterns.

### Functions

#### emit_to_class()

**Purpose**: Broadcast event to all users in a specific class

**Signature:**
```python
def emit_to_class(
    school_id: int,
    year: int,
    grade_level: str,
    event: str,
    data: Dict[str, Any]
) -> None
```

**Parameters:**
- `school_id`: School identifier
- `year`: Academic year
- `grade_level`: Grade level (e.g., "10th Grade")
- `event`: Event name
- `data`: Event payload

**Room Format:** `class_{school_id}_{year}_{grade_level}`

**Usage:**
```python
from src.app.utils import emit_to_class

# Notify entire class of new school session
emit_to_class(
    school_id=1,
    year=2024,
    grade_level="10th Grade",
    event='session_started',
    data={
        'session_id': 123,
        'course': 'Mathematics',
        'message': 'Class session has started'
    }
)
```

#### emit_to_manager()

**Purpose**: Send event to specific class manager

**Signature:**
```python
def emit_to_manager(
    manager_id: int,
    event: str,
    data: Dict[str, Any]
) -> None
```

**Room Format:** `manager_{manager_id}`

**Usage:**
```python
from src.app.utils import emit_to_manager

# Notify manager of student joining session
emit_to_manager(
    manager_id=5,
    event='student_joined',
    data={
        'student_name': 'John Doe',
        'session_id': 123
    }
)
```

#### emit_to_student()

**Purpose**: Send event to specific student

**Signature:**
```python
def emit_to_student(
    student_id: int,
    event: str,
    data: Dict[str, Any]
) -> None
```

**Room Format:** `student_{student_id}`

**Usage:**
```python
from src.app.utils import emit_to_student

# Send evaluation results to student
emit_to_student(
    student_id=10,
    event='evaluation_complete',
    data={
        'session_id': 123,
        'proficiency_score': 8,
        'investment_score': 9
    }
)
```

#### get_student_class_room()

**Purpose**: Retrieve class room identifier for a student

**Signature:**
```python
def get_student_class_room(student_id: int) -> Optional[str]
```

**Returns:** Room identifier string or None if student not in class

**Usage:**
```python
from src.app.utils import get_student_class_room

# Get student's class room for broadcasting
room = get_student_class_room(student_id=10)
if room:
    socketio.emit('announcement', data, room=room)
```

### Room Naming Conventions

| User Type | Room Format | Example |
|-----------|-------------|---------|
| **Class** | `class_{school_id}_{year}_{grade_level}` | `class_1_2024_10th Grade` |
| **Manager** | `manager_{manager_id}` | `manager_5` |
| **Student** | `student_{student_id}` | `student_10` |

### Event Types

Common event names used in the application:

| Event | Recipient | Purpose |
|-------|-----------|---------|
| `session_started` | Class | School session began |
| `session_ended` | Class | School session completed |
| `student_joined` | Manager | Student joined session |
| `evaluation_complete` | Student | Evaluation results ready |
| `message_received` | Student | New chat message |
| `voice_response` | Student | TTS audio ready |

### WebSocket Integration

These utilities integrate with Flask-SocketIO:

```python
# In routes/websocket.py
from flask_socketio import join_room, leave_room
from src.app.utils import emit_to_student

@socketio.on('connect')
def handle_connect():
    user_id = session.get('user', {}).get('id')
    room = f"student_{user_id}"
    join_room(room)
    
    # Now emit_to_student() will reach this user
```

## Difference from `src/utils/`

### App Utils (Flask-Specific)
- **flash.py**: Flask session-based messaging
- **websocket.py**: Flask-SocketIO event broadcasting
- Requires Flask application context
- Tightly coupled with Flask ecosystem

### General Utils (Application-Wide)
- **logger.py**: Application logging
- **file_handler.py**: File upload management
- Works outside Flask context
- Can be used in services, models, etc.

## Usage Patterns

### Route with Flash Messages

```python
from flask import redirect
from src.app.utils import flash_message

@bp.route('/delete_session/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    try:
        # Delete logic
        delete_study_session(session_id)
        flash_message("Session deleted successfully", "success")
    except Exception as e:
        flash_message(f"Error deleting session: {str(e)}", "error")
    
    return redirect('/study')
```

### WebSocket Event Broadcasting

```python
from src.app.utils import emit_to_class, emit_to_manager

# When school session starts
def start_school_session(session):
    # ... start logic ...
    
    # Notify class
    emit_to_class(
        school_id=session.school_id,
        year=session.year,
        grade_level=session.grade_level,
        event='session_started',
        data={
            'session_id': session.id,
            'course': session.course.name
        }
    )
    
    # Notify manager
    emit_to_manager(
        manager_id=session.manager_id,
        event='session_started',
        data={'session_id': session.id}
    )
```

### Combined Flash and WebSocket

```python
@bp.route('/end_session/<int:session_id>', methods=['POST'])
def end_session(session_id):
    session = end_study_session(session_id)
    
    # Flash message for page reload
    flash_message("Session ended successfully", "success")
    
    # WebSocket event for real-time update
    emit_to_student(
        student_id=session.student_id,
        event='session_ended',
        data={'session_id': session_id}
    )
    
    return redirect('/study')
```

## Testing

### Testing Flash Messages

```python
def test_flash_message(client):
    with client.session_transaction() as sess:
        # No messages initially
        assert 'messages' not in sess
    
    # Add message
    flash_message("Test message", "success")
    
    with client.session_transaction() as sess:
        messages = sess.get('messages', [])
        assert len(messages) == 1
        assert messages[0]['text'] == "Test message"
        assert messages[0]['category'] == "success"
    
    # Get and clear
    messages = get_flash_messages()
    assert len(messages) == 1
    
    # Now cleared
    messages = get_flash_messages()
    assert len(messages) == 0
```

### Testing WebSocket Events

```python
def test_emit_to_student(socketio_client):
    # Join room
    socketio_client.emit('join', {'room': 'student_1'})
    
    # Emit event
    emit_to_student(
        student_id=1,
        event='test_event',
        data={'message': 'Hello'}
    )
    
    # Verify received
    received = socketio_client.get_received()
    assert len(received) == 1
    assert received[0]['name'] == 'test_event'
    assert received[0]['args'][0]['message'] == 'Hello'
```

## Dependencies

- **Flask**: Session management, application context
- **Flask-SocketIO**: WebSocket support
- **Python 3.7+**: Type hints

## Notes

- Flash messages stored in Flask session (server-side)
- Messages cleared after retrieval (display once)
- WebSocket rooms must be joined before events received
- Room naming is consistent across application
- Multiple messages can be queued before display
- WebSocket utilities require Flask-SocketIO initialization
- get_student_class_room() returns first class if multiple

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

