# Study Session Service

This service manages the complete lifecycle of Home Study Sessions in the allamda system, from creation through AI-guided interaction to post-session evaluation.

## Overview

The Study Session Service provides a comprehensive set of functions for managing student study sessions, including:

- Session creation and initialization
- Session state management (pending, active, paused, completed)
- AI-powered chat interaction with Teacher agents
- Post-session feedback collection
- Automatic AI-powered evaluation

## Architecture

### Module Structure

The service is organized using separation of concerns, with each module handling a specific aspect:

```
study_session/
├── __init__.py              # Public API exports (imports from specialized modules)
├── exceptions.py            # Custom exception classes
├── lifecycle.py             # Session creation and completion
├── state_transitions.py     # Start, pause, resume operations + decorator
├── messaging.py             # Chat message handling
├── evaluation.py            # AI-powered evaluation
└── README.md                # This file
```

#### Module Responsibilities

- **__init__.py**: Public API that imports and re-exports all public functions from specialized modules

- **exceptions.py**: Custom exception classes for error handling
  - `StudySessionError` - Base exception
  - `ActiveSessionExistsError` - Duplicate session prevention
  - `SessionNotFoundError` - Missing session errors
  - `InvalidSessionStateError` - Invalid state transitions

- **lifecycle.py**: Session creation and completion
  - `create_home_study_session` - Initialize new sessions
  - `end_session` - Complete sessions with feedback

- **state_transitions.py**: Session state management
  - `session_state_transition` - Decorator that handles validation, state updates, and commits
  - `start_session` - Transition from PENDING to ACTIVE
  - `pause_session` - Pause active sessions
  - `resume_session` - Resume paused sessions

- **messaging.py**: Chat interaction handling
  - `get_session_messages` - Retrieve conversation history
  - `send_message` - Process student messages and get AI responses
  - `send_welcome_message` - Send initial welcome message when session starts

- **evaluation.py**: Post-session evaluation
  - `evaluate_session` - Generate AI-powered proficiency and investment evaluations
  - `extract_score_from_response` - Parse scores from AI responses

### Service Layer Responsibilities

The service layer handles:
- **Business Logic**: Session creation, validation, state transitions
- **Data Persistence**: Creating and updating session records and associations
- **AI Integration**: Coordinating with Teacher and Evaluator agents
- **Error Handling**: Providing meaningful exceptions for different failure scenarios

### Integration Points

- **Models**: Uses SQLAlchemy ORM models for data persistence
- **AI Agents**: Coordinates with Teacher (chat) and Evaluator (assessment) agents
- **Routes**: Called by Flask routes to handle HTTP requests

## Core Functions

### Session Creation

```python
create_home_study_session(
    session: Session,
    student_id: int,
    session_type: HomeHoursStudySessionType,
    course_id: int,
    learning_unit_names: List[str],
    emotional_state_before: EmotionalState
) -> HomeHoursStudySession
```

Creates a new home study session with the following steps:
1. Validates no active session exists for the student
2. Validates student enrollment in the selected course
3. Validates selected learning units exist
4. Automatically assigns Teacher agent based on course subject
5. Creates session with `PENDING` status
6. Associates student with emotional state
7. Links learning units to the session

**Module**: `lifecycle.py`  
**Raises**: `ActiveSessionExistsError`, `StudySessionError`

### Session State Management

#### Start Session
```python
start_session(session: Session, session_id: int) -> HomeHoursStudySession
```
Transitions session from `PENDING` to `ACTIVE` status.

**Module**: `state_transitions.py`  
**Decorator**: Uses `session_state_transition` decorator

#### Pause Session
```python
pause_session(session: Session, session_id: int) -> HomeHoursStudySession
```
Pauses an active session and creates a pause record.

**Module**: `state_transitions.py`  
**Decorator**: Uses `session_state_transition` decorator

#### Resume Session
```python
resume_session(session: Session, session_id: int) -> HomeHoursStudySession
```
Resumes a paused session and closes the active pause record.

**Module**: `state_transitions.py`  
**Decorator**: Uses `session_state_transition` decorator

### Chat Interaction

#### Send Message
```python
send_message(
    session: Session,
    session_id: int,
    student_id: int,
    message_content: str
) -> Dict[str, Any]
```

Handles the complete message flow:
1. Validates session is active
2. Creates student message (prompt) in database
3. Retrieves conversation history
4. Calls Teacher agent to generate response
5. Creates teacher response message in database
6. Links messages together
7. Returns teacher response

**Module**: `messaging.py`

#### Get Session Messages
```python
get_session_messages(
    session: Session,
    session_id: int
) -> List[Dict[str, Any]]
```

Retrieves all messages for a session, ordered chronologically.

**Module**: `messaging.py`

#### Send Welcome Message
```python
send_welcome_message(
    session: Session,
    session_id: int,
    student_id: int
) -> Dict[str, Any]
```

Sends an initial welcome message from the Teacher agent when a session starts. Provides context about the session and learning objectives.

**Module**: `messaging.py`

### Session Completion

#### End Session
```python
end_session(
    session: Session,
    session_id: int,
    student_id: int,
    emotional_state_after: EmotionalState,
    difficulty_feedback: int,
    understanding_feedback: int,
    textual_feedback: Optional[str] = None
) -> HomeHoursStudySession
```

Completes a study session:
1. Closes any open pauses
2. Sets session status to `COMPLETED`
3. Records end time
4. Stores student feedback
5. Triggers automatic evaluation

**Module**: `lifecycle.py`

#### Evaluate Session
```python
evaluate_session(
    session_id: int,
    student_id: int,
    session_type: str = 'home'
) -> tuple[SessionalProficiencyEvaluation, SessionalInvestmentEvaluation]
```

Creates AI-powered evaluations for both home and school sessions:
1. Retrieves complete message transcript
2. Uses Evaluator agent to analyze proficiency
3. Creates SessionalProficiencyEvaluation with score and description
4. Uses Evaluator agent to analyze investment/engagement
5. Creates SessionalInvestmentEvaluation with score and description
6. Links both evaluations to the session (uses appropriate association model based on session_type)

**Module**: `evaluation.py`

## Session Status Flow

```
PENDING → (start) → ACTIVE → (end) → COMPLETED
                       ↓
                    (pause)
                       ↓
                    PAUSED → (resume) → ACTIVE
```

### Status Descriptions

- **PENDING**: Session created but not yet started
- **ACTIVE**: Student is actively studying and can send messages
- **PAUSED**: Session temporarily paused, messages disabled
- **COMPLETED**: Session finished with feedback collected
- **CANCELLED**: Session was cancelled (not currently used)

## Exception Handling

### Custom Exceptions

All exceptions are defined in `exceptions.py`:

- **StudySessionError**: Base exception for all service errors
- **ActiveSessionExistsError**: Student already has an active session
- **SessionNotFoundError**: Requested session doesn't exist
- **InvalidSessionStateError**: Operation invalid for current state

### Usage Example

```python
from src.services.study_session import (
    create_home_study_session,
    send_message,
    end_session,
    ActiveSessionExistsError
)

try:
    # Create session
    session = create_home_study_session(
        session=db_session,
        student_id=1,
        session_type=HomeHoursStudySessionType.TEST_PREPARATION,
        course_id=5,
        learning_unit_names=["Introduction", "Chapter 1"],
        emotional_state_before=EmotionalState.POSITIVE
    )
    
    # Send message
    response = send_message(
        session=db_session,
        session_id=session.id,
        student_id=1,
        message_content="Can you explain photosynthesis?"
    )
    
    # End session
    end_session(
        session=db_session,
        session_id=session.id,
        student_id=1,
        emotional_state_after=EmotionalState.POSITIVE,
        difficulty_feedback=7,
        understanding_feedback=8,
        textual_feedback="Great session!"
    )
    
except ActiveSessionExistsError:
    print("Please complete your current session first")
except StudySessionError as e:
    print(f"Error: {e}")
```

## Database Schema

### Key Models Used

- **HomeHoursStudySession**: Main session entity
- **HomeHoursStudySessionStudent**: Student association with feedback
- **LearningUnitsHomeHoursStudySession**: Learning unit associations
- **Message**: Chat messages (student prompts and teacher responses)
- **SessionalProficiencyEvaluation**: AI proficiency assessment
- **SessionalInvestmentEvaluation**: AI investment assessment

### Relationships

```
HomeHoursStudySession
  ├── students (via HomeHoursStudySessionStudent)
  ├── learning_units (via LearningUnitsHomeHoursStudySession)
  ├── messages (Message)
  ├── teacher (Teacher agent)
  ├── pauses (HomeHoursStudySessionPause)
  ├── sessional_proficiency_evaluations
  └── sessional_investment_evaluations
```

## AI Agent Integration

### Teacher Agent

The Teacher agent:
- Is automatically assigned based on course subject
- Provides personalized responses based on:
  - Student learning profile (learning style, routine, collaboration)
  - Session type (test preparation vs homework)
  - Learning units being studied
  - Student's emotional state
  - Conversation history
- Can use tools to access student progress, Q&A resources, test history

### Evaluator Agent

The Evaluator agent:
- Analyzes the complete session transcript
- Generates proficiency scores (1-10) based on understanding and mastery
- Generates investment scores (1-10) based on engagement and effort
- Provides descriptive evaluations for both dimensions
- Uses AI to extract meaningful insights from student-teacher interaction

## Design Patterns

### State Transition Decorator

The `session_state_transition` decorator (in `state_transitions.py`) implements a reusable pattern for state transitions:

```python
@session_state_transition(
    expected_status=SessionStatus.PENDING,
    new_status=SessionStatus.ACTIVE
)
def start_session(session: Session, session_id: int, study_session: HomeHoursStudySession) -> None:
    # Custom logic here (if any)
    pass
```

This decorator:
1. Validates session exists
2. Checks current status matches expected status
3. Executes the decorated function
4. Updates status to new status
5. Commits changes
6. Handles errors with rollback

### Public API Pattern

The `__init__.py` module provides a single entry point that imports and re-exports all public functions from the specialized modules. This allows:
- Clean imports: `from src.services.study_session import create_home_study_session`
- Internal refactoring without breaking external code
- Clear separation between public API and internal implementation

## Future Enhancements

Potential improvements to consider:

1. **Session Analytics**: Add session duration tracking, message statistics
2. **Adaptive Learning**: Use evaluation scores to adjust difficulty
3. **Progress Tracking**: Link session outcomes to learning unit progress
4. **Multi-Student Support**: Enable school study sessions with multiple students
5. **Advanced Evaluation**: Use more sophisticated prompts or fine-tuned models
6. **Session Templates**: Pre-configured sessions for common study patterns

## Testing

Key test scenarios:

- ✅ Create session with valid data
- ✅ Prevent multiple active sessions
- ✅ Send and receive messages
- ✅ Pause and resume session
- ✅ Complete session with feedback
- ✅ Verify evaluations created automatically
- ✅ Handle invalid session states
- ✅ Resume session after browser close

## Notes

- Only one active session per student is allowed
- Teacher assignment is automatic based on course subject
- Evaluations are created asynchronously after session completion
- All messages are persisted for analysis and review
- Session can be resumed after browser close (as long as not completed)
- The modular structure allows easy extension and maintenance
