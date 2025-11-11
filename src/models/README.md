# Database Models

SQLAlchemy ORM models organized by domain. All models inherit from `Base` and follow a consistent pattern.

## Structure

```
models/
├── base/              # Base classes and mixins
│   ├── declarative_base.py  # SQLAlchemy Base
│   └── base_models.py       # Abstract base models (User, Agent, StudySession, etc.)
├── user_models.py    # User entities (Student, Parent, ClassManager, etc.)
├── student_models.py # Student-specific models
├── school_models.py  # School, Class, Tablet models
├── subject_models.py # Subject, Course, LearningUnit, Test, QA models
├── session_models.py # Study session models (HomeHours, SchoolHours)
├── evaluation_models.py # Evaluation models (Proficiency, Investment, Social)
├── message_models.py # Message and Attachment models
├── agents/           # AI agent models
│   ├── ai_model.py  # AIModel (tracks AI model versions)
│   ├── teacher/     # Teacher agent implementation
│   ├── evaluator/   # Evaluator agent implementation
│   └── base/        # AI agent base classes and tools
└── associations.py   # Association tables (many-to-many relationships)
```

## Base Models

### Abstract Base Classes (`base/base_models.py`)
- **User**: Base for all user types (has username, password, name)
- **Agent**: Base for AI agents (Teacher, Evaluator)
- **StudySession**: Base for study sessions (abstract)
- **Evaluation**: Base for evaluations (abstract)
- **StudySessionStudent**: Association between session and student
- **LearningUnitsStudySession**: Association between session and learning units

### Inheritance Hierarchy

```
User
├── Student
├── Parent
├── ClassManager
├── SchoolManager
└── RegionalSupervisor

Agent (mixes with AIAgentMixin)
├── Teacher
└── Evaluator

StudySession
├── HomeHoursStudySession
└── SchoolHoursStudySession

Evaluation
├── AIEvaluation
│   ├── SessionalProficiencyEvaluation
│   ├── QuarterProficiencyEvaluation
│   ├── SessionalInvestmentEvaluation
│   ├── QuarterInvestmentEvaluation
│   ├── SessionalSocialEvaluation
│   └── QuarterSocialEvaluation
└── HumanEvaluation
```

## Domain Models

### User Models (`user_models.py`, `student_models.py`)
- **Student**: Learning profile (style, routine, collaboration), enrollment tracking
- **Parent**: Can have multiple children
- **ClassManager**: Manages classes
- **SchoolManager**: School administration
- **RegionalSupervisor**: Subject-level oversight
- **Phone**, **Address**: Contact information

### School Models (`school_models.py`)
- **School**: Educational institution
- **Class**: Class within a school
- **Tablet**: Device tracking

### Subject Models (`subject_models.py`)
- **Subject**: Academic subject (Math, Science, etc.)
- **Course**: Course within a subject (e.g., "Algebra 1")
- **LearningUnit**: Units within a course (with dependencies, duration)
- **Test**: Examinations linked to courses and learning units
- **QA**: Q&A resources for learning units

### Session Models (`session_models.py`)
- **HomeHoursStudySession**: Individual student study sessions
- **SchoolHoursStudySession**: Group study sessions at school
- **HomeHoursStudySessionPause**: Pause tracking for home sessions
- **SchoolHoursStudySessionPause**: Pause tracking for school sessions

### Evaluation Models (`evaluation_models.py`)
- **SessionalProficiencyEvaluation**: AI assessment of understanding per session
- **QuarterProficiencyEvaluation**: Quarterly proficiency summary
- **SessionalInvestmentEvaluation**: AI assessment of engagement per session
- **QuarterInvestmentEvaluation**: Quarterly investment summary
- **SessionalSocialEvaluation**: Social interaction assessment (school sessions)

### Message Models (`message_models.py`)
- **Message**: Chat messages in study sessions (prompts, responses, attachments)
- **Attachment**: File attachments to messages

## Association Tables (`associations.py`)

Many-to-many relationships:
- `ParentStudent` - Parent-child relationships
- `ClassStudent` - Class enrollment
- `ClassClassManager` - Class management
- `TabletStudent` - Device assignment
- `SubjectRegionalSupervisor` - Subject oversight
- `CourseStudent` - Course enrollment
- `CoursePrerequisite` - Course dependencies
- `LearningUnitStudent` - Learning unit progress tracking
- `TestStudent` - Test assignments and results
- `TestLearningUnit` - Tests covering learning units
- `LearningUnitsHomeHoursStudySession` - Units studied in session
- Evaluation associations (linking evaluations to sessions)

## AI Agents (`agents/`)

The system includes AI-powered agents with database persistence and OpenAI integration. All agents inherit from both `Agent` (database model) and `AIAgentMixin` (AI capabilities).

### Teacher Agent (`agents/teacher/`)

**Purpose**: Provides personalized, adaptive instruction to students during study sessions

**Database Model:**
- Table: `teachers`
- Composite PK: (ai_model_id, name)
- Subject-specific (Math, Science, etc.)

**Tools:**
- `get_learning_unit_mastery` - Check student progress in learning units
- `get_qa_resources` - Access Q&A content for explanations
- `get_student_test_history` - Review test performance
- `get_recent_student_evaluations` - Check proficiency/investment trends
- `get_prerequisite_units_status` - Verify prerequisite completion

**Adaptive Features:**
- Learning style adaptation (Visual, Auditory, Kinesthetic, Reading/Writing)
- Session type adaptation (Test Prep, Homework, Revision, Exploration)
- Emotional state awareness
- Group session support with multiple student profiles

**Documentation**: See [Teacher Agent README](agents/teacher/README.md)

### Evaluator Agent (`agents/evaluator/`)

**Purpose**: Assesses student performance through transcript analysis and quantitative metrics

**Database Model:**
- Table: `evaluators`
- Composite PK: (ai_model_id, name)
- Generates sessional and quarterly evaluations

**Tools:**
- `get_session_context` - Get course and learning unit info (MANDATORY for proficiency)
- `get_session_pause_statistics` - Analyze engagement via pause data (MANDATORY for investment)
- `get_session_message_statistics` - Quantify conversational participation
- `get_student_test_performance` - Compare with test scores
- `get_student_evaluation_history` - Review evaluation trends

**Evaluation Dimensions:**
- **Proficiency**: Academic understanding, mastery (1-10 scale)
- **Investment**: Engagement, focus, dedication (1-10 scale)

**Documentation**: See [Evaluator Agent README](agents/evaluator/README.md)

### Base Infrastructure (`agents/base/`)

**Purpose**: Core AI agent capabilities shared by all agents

**Components:**
- **AIAgentMixin**: Adds AI functionality via multiple inheritance
  - Automatic tool discovery from decorated methods
  - OpenAI API integration with function calling
  - System prompt generation
  - Response parsing and error handling
- **AIAgentTool**: Tool definition and execution wrapper
- **agent_tool**: Decorator for marking methods as agent tools
- **ToolResponse**: Standardized return format for tools
- **AgentJSONEncoder**: Custom JSON encoder for database types

**Key Features:**
- Automatic tool registration via `@agent_tool` decorator
- Support for multiple tool calls per conversation turn
- Pydantic schema validation for tool parameters
- Thread-safe operation via database session context

**Documentation**: See [Base Agent Infrastructure README](agents/base/README.md)

## Model Patterns

### Query Methods

All models inherit from `Base` which provides flexible query capabilities:

**get_by() - Universal Query Method**
```python
# Single result
student = Student.get_by(id=1, first=True)

# Multiple results
students = Student.get_by(grade_level="10th Grade", first=False)

# List filter (IN clause)
students = Student.get_by(id=[1, 2, 3], first=False)

# Complex filters
courses = Course.get_by(
    subject_name="MATH",
    grade_level="10th Grade",
    first=False
)

# Returns None if not found (with first=True)
student = Student.get_by(id=999, first=True)  # None
```

**Model-Specific Query Methods**

Many models provide specialized query methods:

```python
# Session queries
HomeHoursStudySession.get_active_by(student_id=1)
HomeHoursStudySession.get_by_id_and_student(session_id=5, student_id=1)

# Student queries
student.get_courses()
student.get_learning_profile()
student.get_recent_evaluations(evaluation_type, limit=5)

# Course queries
course.get_ordered_learning_units()
course.get_enrolled_students()

# User authentication
User.authenticate(email, password)
User.authenticate_any_user(email, password)  # Tries all user types
```

### Relationships

SQLAlchemy relationships enable easy navigation:

```python
# One-to-many
student = Student.get_by(id=1, first=True)
school = student.school  # Access related school
courses = student.courses  # Access enrolled courses

# Many-to-many
course = Course.get_by(id=5, first=True)
students = course.students  # All enrolled students
learning_units = course.learning_units  # All units in course

# One-to-one
session = HomeHoursStudySession.get_by(id=10, first=True)
teacher = session.teacher  # AI teacher agent
```

**Relationship Configuration:**
- `back_populates` - Bidirectional relationships
- `lazy` loading - Query on access (default)
- `cascade` - Automatic deletion/updates
- Foreign key constraints enforced at database level

### to_dict() Method

Convert model instances to dictionaries:

```python
student = Student.get_by(id=1, first=True)
student_dict = student.to_dict()

# Returns:
{
    'id': 1,
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
    'school_id': 5,
    'learning_style': 'VISUAL',
    # ... all column attributes
}

# User subclasses include extra properties
user_dict = student.to_dict()
# Includes: 'full_name', 'user_type'
```

**Note**: `to_dict()` only includes column attributes, not relationships. For relationships, access them explicitly or implement custom serialization.

### Enums

Enums from `src.enums.py` provide type-safe categorical data:

**User-Related:**
- `UserType`: STUDENT, PARENT, CLASS_MANAGER, SCHOOL_MANAGER, REGIONAL_SUPERVISOR
- `LearningStyle`: VISUAL, AUDITORY, KINESTHETIC, READING_WRITING
- `RoutineStyle`: STRUCTURED, FLEXIBLE, MIXED
- `CollaborationStyle`: INDEPENDENT, COLLABORATIVE, MIXED

**Session-Related:**
- `SessionStatus`: PENDING, ACTIVE, PAUSED, COMPLETED, CANCELLED
- `HomeHoursStudySessionType`: TEST_PREPARATION, HOMEWORK, REVISION, EXPLORATION
- `SchoolHoursStudySessionType`: LECTURE, DISCUSSION, PRACTICE, REVIEW

**Evaluation-Related:**
- `EmotionalState`: POSITIVE, NEUTRAL, NEGATIVE, STRESSED, EXCITED
- `EvaluationType`: PROFICIENCY, INVESTMENT, SOCIAL

**Academic-Related:**
- `SubjectName`: MATH, SCIENCE, HISTORY, ENGLISH, etc.
- `CourseState`: IN_PROGRESS, NOT_STARTED, COMPLETED
- `MessageType`: PROMPT, RESPONSE

**Usage:**
```python
from src.enums import SessionStatus, LearningStyle

# Set enum value
session.status = SessionStatus.ACTIVE

# Query by enum
students = Student.get_by(
    learning_style=LearningStyle.VISUAL,
    first=False
)

# Compare enum values
if session.status == SessionStatus.COMPLETED:
    evaluate_session(session)
```

## Usage

```python
from src.models import Student, Course, HomeHoursStudySession
from src.database import DatabaseManager

with DatabaseManager.get_session() as session:
    student = Student.get_by(session, id=1, first=True)
    courses = student.get_courses(session)
    active_session = HomeHoursStudySession.get_active_by(session, student.id)
```

## Notes

- All models use declarative base from `base.declarative_base`
- Models expose relationships for easy navigation
- Association tables handle many-to-many relationships
- AI agents inherit from both `Agent` and `AIAgentMixin` for dual functionality
