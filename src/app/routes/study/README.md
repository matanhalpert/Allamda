# Study Routes

Flask routes handling the complete study session lifecycle from creation through completion. Implements a multi-step session creation wizard, real-time chat interface, voice interaction, file uploads, and session state management.

## Overview

The Study Routes subpackage provides all HTTP endpoints for student study sessions. It coordinates between user interactions, the study session service layer, and AI teacher agents. Routes handle both home study sessions (student-initiated) and school sessions (class-based), with support for text chat, voice input, file attachments, and session pause/resume.

## Structure

```
study/
├── __init__.py             # Blueprint definition and imports
├── home.py                # Study hub home page
├── session_creation.py     # Multi-step session wizard
├── session_lifecycle.py    # Start, pause, resume, end operations
├── chat.py                # Chat interface and messaging
├── files.py               # File upload handling
├── helpers.py             # Shared utility functions
└── README.md              # This file
```

## Modules

### home.py - Study Hub Interface

**Purpose**: Entry point for study features, displays active sessions and recent history

**Routes:**
- `GET /study` - Study hub home page

**Features:**
- Active session detection (home and school)
- Recent session history display
- Quick action links (create session, join school session)
- Pending session cleanup (removes stale PENDING sessions)
- Session status badges and navigation

### session_creation.py - Multi-Step Session Wizard

**Purpose**: Guided session creation with validation at each step

**Routes:**
- `GET /study/new` - Start new session wizard
- `GET /study/new/session-type` - Step 1: Select session type
- `POST /study/new/session-type` - Submit session type
- `GET /study/new/course` - Step 2: Select course
- `POST /study/new/course` - Submit course selection
- `GET /study/new/mental-state` - Step 3: Record emotional state
- `POST /study/new/mental-state` - Submit mental state
- `POST /study/create` - Finalize and create session
- `GET /study/join/<session_id>` - Join pending school session
- `POST /study/join/<session_id>` - Join school session with mental state

**Session Creation Flow:**
```
1. /study/new/session-type
   ↓ (select: TEST_PREPARATION, HOMEWORK, REVISION, EXPLORATION)
2. /study/new/course
   ↓ (select course from enrolled courses)
3. /study/new/mental-state
   ↓ (record emotional state before session)
4. POST /study/create
   ↓ (creates session, assigns learning units, assigns teacher)
5. Redirect to /study/chat/<session_id>
```

**Features:**
- Multi-step form with draft data stored in Flask session
- Navigation between steps
- Validation at each step
- Active session checking (prevents duplicate sessions)
- Automatic learning unit assignment
- Teacher agent assignment based on course subject
- Draft data persistence across page refreshes
- Clear draft data on completion or cancellation

### session_lifecycle.py - Session State Management

**Purpose**: State transition operations for sessions

**Routes:**
- `POST /study/start/<session_id>` - Start PENDING session (→ ACTIVE)
- `POST /study/pause/<session_id>` - Pause ACTIVE session (→ PAUSED)
- `POST /study/resume/<session_id>` - Resume PAUSED session (→ ACTIVE)
- `GET /study/end/<session_id>` - Display session end form
- `POST /study/end/<session_id>` - Complete session with feedback (→ COMPLETED)

**State Transitions:**
```
PENDING → (start) → ACTIVE → (end) → COMPLETED
                      ↓
                   (pause)
                      ↓
                   PAUSED → (resume) → ACTIVE
```

**Features:**
- Validates current session state before transitions
- Creates pause records with timestamps
- Collects end-of-session feedback:
  - Emotional state after
  - Difficulty rating (1-10)
  - Understanding rating (1-10)
  - Optional textual feedback
- Triggers automatic AI evaluation on completion
- Error handling for invalid state transitions
- Flash message feedback for all operations

### chat.py - Chat Interface and Messaging

**Purpose**: Real-time messaging interface with AI teacher

**Routes:**
- `GET /study/chat/<session_id>` - Display chat interface
- `POST /study/chat/<session_id>/welcome` - Send welcome message
- `POST /study/chat/<session_id>/message` - Send student message
- `POST /study/chat/<session_id>/transcribe` - Transcribe voice input
- `GET /study/chat/<session_id>/tts/<message_id>` - Get text-to-speech audio
- `GET /study/chat/<session_id>/messages` - Fetch all messages (AJAX)

**Chat Features:**
- Real-time message display
- Support for text and voice input
- File attachments (images, documents)
- Message history with timestamps
- AI teacher response generation
- Welcome message on session start
- Message modality tracking (TEXT, VOICE, MULTIMODAL)
- Learning units sidebar
- Session timer and status display

**Voice Features:**
- Audio recording in browser
- Speech-to-text transcription (Whisper API)
- Text-to-speech for teacher responses (OpenAI TTS)
- Audio file validation (format, size)
- TTS caching by message ID
- Voice input button in UI

**File Features:**
- Image uploads (PNG, JPG, JPEG, GIF, WEBP)
- Document uploads (PDF, DOC, DOCX, TXT, MD)
- Spreadsheet uploads (XLS, XLSX, CSV)
- File preview in chat
- Attachment storage per session

### files.py - File Upload Handling

**Purpose**: File attachment processing for messages

**Routes:**
- `POST /study/chat/<session_id>/upload` - Upload file attachment

**Features:**
- File validation (type and size)
- Storage in session-specific directories
- File type detection
- Error handling for invalid files
- Returns file URL for message association

**Supported File Types:**
- Images: png, jpg, jpeg, gif, webp
- Documents: pdf, doc, docx, txt, md
- Spreadsheets: xls, xlsx, csv
- Presentations: ppt, pptx

### helpers.py - Shared Utilities

**Purpose**: Common helper functions used across study routes

**Functions:**
- `_get_draft_data()` - Retrieve draft session data from Flask session
- `_clear_draft_session_data()` - Clear draft data
- `_get_current_step()` - Determine current wizard step
- `_check_active_session_redirect()` - Check for active sessions and redirect if found
- `_validate_session_access()` - Verify student has access to session
- Session type formatting utilities
- Error message standardization

## Route-to-Service Mapping

Routes delegate business logic to services:

| Route Operation | Service Function |
|----------------|------------------|
| Create session | `create_home_study_session()` |
| Join school session | `join_school_session()` |
| Start session | `start_session()` |
| Pause session | `pause_session()` |
| Resume session | `resume_session()` |
| End session | `end_session()` |
| Send message | `send_message()` |
| Get messages | `get_session_messages()` |
| Welcome message | `send_welcome_message()` |
| Evaluate session | `evaluate_session()` (automatic) |

## Session State Management in Routes

### Flask Session Data

**Draft Session Data** (temporary during creation):
```python
session['draft_session'] = {
    'session_type': 'TEST_PREPARATION',
    'course_id': 5,
    'current_step': 'mental-state'
}
```

**User Session Data** (persistent):
```python
session['user'] = {
    'id': 123,
    'user_type': 'student',
    'first_name': 'John'
}
```

### Database Session State

Study sessions have status tracked in database:
- PENDING - Created but not started
- ACTIVE - Currently in progress
- PAUSED - Temporarily paused
- COMPLETED - Finished with feedback
- CANCELLED - Cancelled (not currently used)

## Error Handling

### Custom Exceptions

Routes catch service-layer exceptions:

```python
from src.services.study_session import (
    StudySessionError,
    ActiveSessionExistsError,
    InvalidSessionStateError,
    SessionNotFoundError
)

try:
    session = create_home_study_session(...)
except ActiveSessionExistsError:
    flash_message("You already have an active session.", "error")
    return redirect('/study')
except StudySessionError as e:
    flash_message(str(e), "error")
    return redirect('/study')
```

### Flash Message Patterns

```python
# Success messages
flash_message("Session started successfully!", "success")

# Error messages
flash_message("Failed to start session.", "error")

# Info messages
flash_message("This session has already been completed.", "info")

# Warning messages
flash_message("Session will end in 5 minutes.", "warning")
```

## Integration Points

### Study Session Service
Primary service for all session operations:
- Session creation and lifecycle management
- Message handling and AI interaction
- Evaluation generation

### Voice Mode Service
Handles voice interactions:
- SpeechToTextService for transcription
- TextToSpeechService for audio generation

### Learning Unit Assignment Service
Automatically selects appropriate learning units:
- Called during session creation
- Considers student progress and session duration

### AI Teacher Agents
Integrated via service layer:
- Teacher agent generates responses
- Context includes student profile and learning style
- Tools provide access to progress data and Q&A resources

### File Handler Utility
Manages file uploads:
- File validation and storage
- Image encoding for AI processing
- URL generation for attachments

## Templates

Study routes render these templates:

| Template | Purpose |
|----------|---------|
| `study_hub.html` | Study home page |
| `study_new_session_type.html` | Session type selection |
| `study_new_course.html` | Course selection |
| `study_new_mental_state.html` | Mental state recording |
| `study_join_mental_state.html` | Join school session |
| `study_chat.html` | Chat interface |
| `study_end.html` | Session end form |
| `study_session_detail.html` | Session details/history |

## JavaScript Integration

Chat interface uses JavaScript for:
- Real-time message updates
- Voice recording
- Audio playback
- File uploads
- Auto-scrolling
- Timer display
- Status updates

**Key JS Files:**
- `study-chat.js` - Main chat functionality
- `study-voice.js` - Voice recording and playback
- `study-files.js` - File upload handling
- `study-timer.js` - Session timer

## Access Control

All study routes require:
1. User must be logged in (`@login_required`)
2. User must be a STUDENT (`@user_required(UserType.STUDENT)`)
3. Database session available (`@with_db_session`)

**Example:**
```python
@bp.route('/study/chat/<int:session_id>')
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def chat_interface(session_id):
    # Only students who are logged in can access
```

Additional validation:
- Student must be associated with the session
- Session must be in appropriate state for operation
- School sessions require class membership

## AJAX Endpoints

Several routes support AJAX for dynamic updates:

```python
# Fetch messages without page reload
GET /study/chat/<session_id>/messages
→ Returns: JSON array of messages

# Send message via AJAX
POST /study/chat/<session_id>/message
→ Returns: JSON response with teacher reply

# Transcribe audio
POST /study/chat/<session_id>/transcribe
→ Returns: JSON with transcript text
```

## URL Patterns

```
/study                              # Hub home
/study/new                          # Start creation wizard
/study/new/session-type             # Step 1: Type
/study/new/course                   # Step 2: Course
/study/new/mental-state             # Step 3: Mental state
/study/create                       # Finalize creation
/study/join/<id>                    # Join school session
/study/chat/<id>                    # Chat interface
/study/chat/<id>/welcome            # Welcome message
/study/chat/<id>/message            # Send message
/study/chat/<id>/transcribe         # Voice transcription
/study/chat/<id>/tts/<msg_id>       # TTS audio
/study/chat/<id>/upload             # File upload
/study/start/<id>                   # Start session
/study/pause/<id>                   # Pause session
/study/resume/<id>                  # Resume session
/study/end/<id>                     # End session
/study/session/<id>                 # Session details
```

## Testing

Key test scenarios:
- Session creation wizard flow
- Active session detection
- Message sending and receiving
- Voice transcription
- File uploads
- State transitions
- Error handling
- Access control
- Draft data persistence

## Dependencies

- Flask blueprint system
- Study session service layer
- Voice mode services (Whisper, TTS)
- File handler utility
- Message models
- Session models
- Authentication decorators
- Flash message utility

## Notes

- Sessions are student-specific (one active session per student)
- Draft data stored in Flask session during creation
- All operations redirect on success/error with flash messages
- Voice features require OpenAI API key
- File uploads require proper directory permissions
- TTS audio cached by message ID to save API costs
- School sessions have automatic end time based on planned duration
- Welcome message sent automatically when session starts

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

