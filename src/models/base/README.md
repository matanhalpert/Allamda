# Base Models

Foundation classes for the Allamda ORM layer. Provides SQLAlchemy declarative base with custom utilities and abstract base classes that all concrete models inherit from. Establishes common patterns, relationships, and query methods used throughout the application.

## Overview

The base models package contains the infrastructure for all SQLAlchemy models in the system. It defines the declarative base with enhanced query capabilities, abstract base classes for major entity types (User, Agent, StudySession, Evaluation), and association base classes for many-to-many relationships. All concrete models in the system inherit from these base classes.

## Structure

```
base/
├── __init__.py           # Package exports
├── declarative_base.py   # Custom SQLAlchemy Base class
├── base_models.py        # Abstract base classes
└── README.md             # This file
```

## Core Components

### declarative_base.py - SQLAlchemy Base

**Purpose**: Enhanced declarative base for all models

**Base Class**:
```python
class Base(declarative_base()):
    """Custom base class with utility methods."""
    __abstract__ = True
```

**Custom Methods:**

**get_by() - Flexible Query Method**
```python
# Single result
student = Student.get_by(id=1, first=True)

# Multiple results
students = Student.get_by(grade_level=10, first=False)

# List filter (IN clause)
students = Student.get_by(id=[1, 2, 3], first=False)

# No results
student = Student.get_by(id=999, first=True)  # Returns None
```

**to_dict() - Dictionary Conversion**
```python
student_dict = student.to_dict()
# Returns: {'id': 1, 'first_name': 'John', 'last_name': 'Doe', ...}
```

**Features:**
- Type-safe generic methods with overloads
- Uses context-based session management
- Flexible filtering with keyword arguments
- List support for IN queries
- Automatic None handling for missing results

### base_models.py - Abstract Base Classes

Contains all abstract base classes that concrete models inherit from.

## Abstract Base Classes

### User Base Class

**Purpose**: Common user entity with authentication

**Inherited By:**
- Student
- Parent
- ClassManager
- SchoolManager
- RegionalSupervisor

**Common Fields:**
```python
id: Integer (PK)
first_name: String(50)
last_name: String(50)
birthdate: Date
email: String(100) - Unique
password: String(255)
```

**Relationships:**
- `phones` - One-to-many with Phone
- `addresses` - One-to-many with Address

**Properties:**
```python
@property
def full_name(self) -> str:
    return f"{self.first_name} {self.last_name}"

@property
def user_type(self) -> UserType:
    # Returns enum based on class name
```

**Methods:**
```python
@classmethod
def authenticate(cls, email: str, password: str) -> User | None:
    # Authenticate user by email/password

@classmethod
def authenticate_any_user(cls, email: str, password: str) -> User | None:
    # Try authentication across all user types
```

**Usage Example:**
```python
from src.models import Student

class Student(User):
    __tablename__ = 'students'
    
    # Student-specific fields
    school_id = Column(Integer, ForeignKey('schools.id'))
    learning_style = Column(Enum(LearningStyle))
    
    # Inherits: id, first_name, last_name, email, password, etc.
    # Inherits: full_name property, authenticate() method
```

### Agent Base Class

**Purpose**: AI-powered entities with database persistence

**Inherited By:**
- Teacher
- Evaluator

**Common Fields:**
```python
ai_model_id: Integer (PK, FK to ai_models)
name: String(100) (PK)
```

**Relationships:**
- `ai_model` - Many-to-one with AIModel

**Properties:**
```python
@property
def agent_type(self) -> str:
    # Returns 'teacher' or 'evaluator' based on class
```

**Usage Example:**
```python
from src.models.agents import Teacher
from src.models.base import Agent

class Teacher(Agent, AIAgentMixin):
    __tablename__ = 'teachers'
    
    subject_name = Column(Enum(SubjectName), ForeignKey('subjects.name'))
    
    # Inherits: ai_model_id, name, agent_type property
    # Mixin provides: AI generation capabilities, tool system
```

### StudySession Base Class

**Purpose**: Common session entity for home and school sessions

**Inherited By:**
- HomeHoursStudySession
- SchoolHoursStudySession

**Common Fields:**
```python
id: Integer (PK)
start_time: DateTime
end_time: DateTime (nullable)
status: Enum(SessionStatus) - Default: PENDING
teacher_ai_model_id: Integer (FK)
teacher_name: String(100) (FK)
```

**Composite Foreign Key:**
```python
ForeignKeyConstraint(
    ['teacher_ai_model_id', 'teacher_name'],
    ['teachers.ai_model_id', 'teachers.name']
)
```

**Relationships (Declared in Subclasses):**
- `students` - Many-to-many via StudySessionStudent
- `learning_units` - Many-to-many via LearningUnitsStudySession
- `messages` - One-to-many
- `teacher` - Many-to-one with Teacher
- `pauses` - One-to-many with StudySessionPause

**Properties:**
```python
@property
def duration(self) -> timedelta | None:
    # Calculate session duration (end_time - start_time)

@property
def is_active(self) -> bool:
    # Check if status is ACTIVE

@property
def is_completed(self) -> bool:
    # Check if status is COMPLETED
```

**Methods:**
```python
@classmethod
def get_active_by(cls, student_id: int) -> StudySession | None:
    # Get active session for student (ACTIVE or PAUSED)

@classmethod
def get_by_id_and_student(cls, session_id: int, student_id: int) -> StudySession | None:
    # Get session by ID with student validation
```

**Usage Example:**
```python
from src.models.session_models import HomeHoursStudySession

class HomeHoursStudySession(StudySession):
    __tablename__ = 'home_hours_study_sessions'
    
    type = Column(Enum(HomeHoursStudySessionType))
    
    # Inherits: id, start_time, end_time, status, teacher
    # Inherits: duration, is_active, get_active_by()
```

### StudySessionPause Base Class

**Purpose**: Pause records for sessions

**Inherited By:**
- HomeHoursStudySessionPause
- SchoolHoursStudySessionPause

**Common Fields:**
```python
id: Integer (PK)
session_id: Integer (FK) - Defined in subclass
start_time: DateTime
end_time: DateTime (nullable)
```

**Properties:**
```python
@property
def duration(self) -> timedelta | None:
    # Calculate pause duration
```

### Evaluation Base Class

**Purpose**: Abstract base for all evaluation types

**Inherited By:**
- AIEvaluation (abstract)
  - SessionalProficiencyEvaluation
  - SessionalInvestmentEvaluation
  - QuarterProficiencyEvaluation
  - QuarterInvestmentEvaluation
- HumanEvaluation (abstract)
  - SessionalSocialEvaluation
  - QuarterSocialEvaluation

**Common Fields:**
```python
id: Integer (PK)
student_id: Integer (FK to students)
created_at: DateTime - Default: now
score: Integer - Check: 1-10
description: Text (nullable)
```

**Constraints:**
```python
CheckConstraint('score >= 1 AND score <= 10')
```

**Relationships:**
- `student` - Many-to-one with Student

**AIEvaluation** (extends Evaluation):
```python
evaluator_ai_model_id: Integer (FK)
evaluator_name: String(100) (FK)

# Composite FK to evaluators table
ForeignKeyConstraint(
    ['evaluator_ai_model_id', 'evaluator_name'],
    ['evaluators.ai_model_id', 'evaluators.name']
)
```

**HumanEvaluation** (extends Evaluation):
```python
evaluator_id: Integer (FK to class_managers)
```

**Usage Example:**
```python
from src.models.evaluation_models import SessionalProficiencyEvaluation

class SessionalProficiencyEvaluation(AIEvaluation):
    __tablename__ = 'sessional_proficiency_evaluations'
    
    # Links to either home or school session
    # (defined via association tables)
    
    # Inherits: id, student_id, score (1-10), description
    # Inherits: evaluator_ai_model_id, evaluator_name
```

## Association Base Classes

For many-to-many relationships between sessions and other entities.

### StudySessionStudent

**Purpose**: Links students to sessions with session-specific data

**Used By:**
- HomeHoursStudySessionStudent
- SchoolHoursStudySessionStudent

**Common Fields:**
```python
session_id: Integer (PK, FK) - Defined in subclass
student_id: Integer (PK, FK to students)
emotional_state_before: Enum(EmotionalState)
emotional_state_after: Enum(EmotionalState) (nullable)
difficulty_feedback: Integer (nullable) - Check: 1-10
understanding_feedback: Integer (nullable) - Check: 1-10
textual_feedback: Text (nullable)
```

**Purpose**: Stores student's emotional state and feedback per session

### LearningUnitsStudySession

**Purpose**: Links learning units to sessions

**Used By:**
- LearningUnitsHomeHoursStudySession
- LearningUnitsSchoolHoursStudySession

**Common Fields:**
```python
session_id: Integer (PK, FK) - Defined in subclass
course_id: Integer (PK, FK)
learning_unit_name: String(100) (PK, FK)
```

**Composite FK:**
```python
ForeignKeyConstraint(
    ['course_id', 'learning_unit_name'],
    ['learning_units.course_id', 'learning_units.name']
)
```

### EvaluationStudySession

**Purpose**: Links evaluations to sessions

**Used By:**
- Multiple evaluation-session association tables

**Common Pattern:**
```python
evaluation_id: Integer (PK, FK)
session_id: Integer (PK, FK)
```

## Inheritance Hierarchy

```
Base (declarative_base)
├── User (abstract)
│   ├── Student
│   ├── Parent
│   ├── ClassManager
│   ├── SchoolManager
│   └── RegionalSupervisor
│
├── Agent (abstract)
│   ├── Teacher (+ AIAgentMixin)
│   └── Evaluator (+ AIAgentMixin)
│
├── StudySession (abstract)
│   ├── HomeHoursStudySession
│   └── SchoolHoursStudySession
│
├── StudySessionPause (abstract)
│   ├── HomeHoursStudySessionPause
│   └── SchoolHoursStudySessionPause
│
└── Evaluation (abstract)
    ├── AIEvaluation (abstract)
    │   ├── SessionalProficiencyEvaluation
    │   ├── SessionalInvestmentEvaluation
    │   ├── QuarterProficiencyEvaluation
    │   └── QuarterInvestmentEvaluation
    └── HumanEvaluation (abstract)
        ├── SessionalSocialEvaluation
        └── QuarterSocialEvaluation
```

## Common Patterns

### Composite Foreign Keys

Used for entities with compound primary keys:

```python
# Agent relationships (ai_model_id + name)
ForeignKeyConstraint(
    ['teacher_ai_model_id', 'teacher_name'],
    ['teachers.ai_model_id', 'teachers.name']
)

# Learning unit relationships (course_id + name)
ForeignKeyConstraint(
    ['course_id', 'learning_unit_name'],
    ['learning_units.course_id', 'learning_units.name']
)
```

### Declared Attributes

For dynamic relationship definitions in abstract classes:

```python
@declared_attr
def phones(cls):
    return relationship(
        "Phone",
        primaryjoin=f"{cls.__name__}.id == foreign(Phone.user_id)",
        cascade="all, delete-orphan"
    )
```

Benefits:
- Relationship name incorporates concrete class name
- Works across inheritance hierarchy
- Proper cascade behavior

### Query Helper Methods

Common pattern for model-specific queries:

```python
@classmethod
def get_active_by(cls, student_id: int):
    session = get_current_session()
    return session.query(cls).filter(
        cls.students.any(id=student_id),
        cls.status.in_([SessionStatus.ACTIVE, SessionStatus.PAUSED])
    ).first()
```

## Integration Points

### Session Context
All query methods use `get_current_session()`:
```python
from src.database.session_context import get_current_session

session = get_current_session()
query = session.query(cls)
```

### Enums
Base classes extensively use enums from `src.enums`:
- SessionStatus (PENDING, ACTIVE, PAUSED, COMPLETED, CANCELLED)
- UserType (STUDENT, PARENT, CLASS_MANAGER, etc.)
- EmotionalState (POSITIVE, NEUTRAL, NEGATIVE, etc.)
- AttendanceReason

### Relationships
Base classes define relationship patterns that concrete models inherit and extend.

## Design Rationale

### Why Abstract Base Classes?

1. **DRY Principle**: Common fields defined once
2. **Polymorphism**: Query across all user types or session types
3. **Consistency**: Ensures all similar entities have same structure
4. **Maintainability**: Changes propagate to all subclasses

### Why Composite Primary Keys for Agents?

Agents use (ai_model_id, name) as composite PK to:
- Support multiple versions of same agent name
- Track which AI model version agent uses
- Enable A/B testing with different models

### Why Separate Home/School Session Types?

Though they share a base, separate tables allow:
- Type-specific fields (e.g., planned_duration for school)
- Different relationship patterns
- Clearer access control
- Performance optimization per type

## Usage Examples

### Creating a Concrete Model

```python
from src.models.base import User

class Student(User):
    __tablename__ = 'students'
    
    # Extend with student-specific fields
    school_id = Column(Integer, ForeignKey('schools.id'))
    learning_style = Column(Enum(LearningStyle))
    
    # Add relationships
    school = relationship("School", back_populates="students")
    
    # Student inherits:
    # - id, first_name, last_name, email, password
    # - full_name property
    # - authenticate() method
    # - get_by() method
    # - to_dict() method
```

### Querying with Base Methods

```python
# Single user by email
user = User.authenticate_any_user('student@example.com', 'password')

# Multiple students by grade
students = Student.get_by(grade_level=10, first=False)

# Active session for student
session = HomeHoursStudySession.get_active_by(student_id=1)

# Convert to dict
student_data = student.to_dict()
```

## Dependencies

- **SQLAlchemy 2.x**: ORM framework
- **src.database.session_context**: Context-based session management
- **src.enums**: Enum definitions
- **Python 3.9+**: Type hints and generic methods

## Notes

- All base classes are abstract (`__abstract__ = True`)
- Composite foreign keys require careful cascade configuration
- Declared attributes enable dynamic relationship names
- Query methods use current session from context
- to_dict() only includes column attributes (not relationships)
- Score constraints enforced at database level (1-10 range)

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

