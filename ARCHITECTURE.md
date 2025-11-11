# λllamda Architecture Documentation

This document provides a comprehensive overview of the λllamda educational platform architecture, including system design, data models, user roles, and AI agent integration.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Study Session Lifecycle](#study-session-lifecycle)
3. [Database Schema](#database-schema)
4. [User Role Hierarchy](#user-role-hierarchy)
5. [AI Agent Integration](#ai-agent-integration)

---

## System Architecture

The λllamda platform follows a layered architecture pattern, separating concerns across presentation, business logic, data access, and external integrations.

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        WebSocket[WebSocket Client]
    end
    
    subgraph "Presentation Layer - Flask App"
        direction TB
        AuthRoutes[Auth Routes]
        StudentRoutes[Student Routes]
        ParentRoutes[Parent Routes]
        ManagerRoutes[Manager Routes]
        StudyRoutes[Study Routes]
        WSHandler[WebSocket Handler]
        
        Templates[Jinja2 Templates]
        Static[Static Files - CSS/JS]
    end
    
    subgraph "Service Layer - Business Logic"
        direction TB
        StudySessionService[Study Session Service]
        PrioritizationService[Course Prioritization]
        LearningUnitService[Learning Unit Assignment]
        AnalyticsService[Analytics Service]
        VoiceService[Voice Mode Service]
    end
    
    subgraph "Model Layer"
        direction TB
        
        subgraph "AI Agents"
            TeacherAgent[Teacher Agent]
            EvaluatorAgent[Evaluator Agent]
            ToolSystem[Agent Tool System]
        end
        
        subgraph "Database Models"
            UserModels[User Models]
            SchoolModels[School Models]
            SubjectModels[Subject Models]
            SessionModels[Session Models]
            EvalModels[Evaluation Models]
            MessageModels[Message Models]
        end
    end
    
    subgraph "Data Access Layer"
        SessionContext[Session Context Manager]
        Decorators[Transaction Decorators]
        DatabaseManager[Database Manager]
    end
    
    subgraph "Infrastructure"
        MySQL[(MySQL Database)]
        FlaskSession[(Flask Session Store)]
        FileStorage[File Storage - Uploads]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API - GPT Models]
    end
    
    Browser --> AuthRoutes
    Browser --> StudentRoutes
    Browser --> ParentRoutes
    Browser --> ManagerRoutes
    Browser --> StudyRoutes
    WebSocket --> WSHandler
    
    AuthRoutes --> Templates
    StudentRoutes --> Templates
    ParentRoutes --> Templates
    ManagerRoutes --> Templates
    StudyRoutes --> Templates
    
    StudyRoutes --> StudySessionService
    StudyRoutes --> PrioritizationService
    StudyRoutes --> LearningUnitService
    StudentRoutes --> AnalyticsService
    WSHandler --> VoiceService
    
    StudySessionService --> TeacherAgent
    StudySessionService --> EvaluatorAgent
    StudySessionService --> SessionModels
    StudySessionService --> MessageModels
    
    PrioritizationService --> UserModels
    PrioritizationService --> SubjectModels
    
    LearningUnitService --> SubjectModels
    LearningUnitService --> SessionModels
    
    AnalyticsService --> EvalModels
    
    TeacherAgent --> ToolSystem
    TeacherAgent --> OpenAI
    EvaluatorAgent --> OpenAI
    
    UserModels --> SessionContext
    SchoolModels --> SessionContext
    SubjectModels --> SessionContext
    SessionModels --> SessionContext
    EvalModels --> SessionContext
    MessageModels --> SessionContext
    
    SessionContext --> DatabaseManager
    DatabaseManager --> MySQL
    
    Templates --> Static
    Templates --> Browser
    
    AuthRoutes -.-> FlaskSession
    StudyRoutes -.-> FileStorage
```

### Layer Responsibilities

#### Client Layer
- **Web Browser**: Primary interface for all user interactions
- **WebSocket Client**: Real-time communication for voice mode and live updates

#### Presentation Layer
- **Routes**: Handle HTTP requests, authentication, and route to appropriate services
  - `auth.py`: Login, logout, session management
  - `student.py`: Student dashboard, courses, progress
  - `parent.py`: Parent dashboard, children's progress
  - `class_manager.py`, `school_manager.py`: Management interfaces
  - `study/`: Study session creation, chat, lifecycle management
- **Templates**: Jinja2 templates for server-side rendering
- **Static Files**: CSS stylesheets and JavaScript for client-side interactivity

#### Service Layer
- **Study Session Service**: Complete study session lifecycle management
- **Course Prioritization**: Intelligent course ranking based on multiple factors
- **Learning Unit Assignment**: Automatic learning unit selection for sessions
- **Analytics Service**: Performance metrics and progress tracking
- **Voice Mode Service**: Speech-to-text and text-to-speech capabilities

#### Model Layer
- **AI Agents**: OpenAI-powered agents with tool usage capabilities
- **Database Models**: SQLAlchemy ORM models representing domain entities

#### Data Access Layer
- **Session Context Manager**: Thread-safe database session management
- **Transaction Decorators**: Automatic transaction handling and rollback
- **Database Manager**: Database initialization and schema management

---

## Study Session Lifecycle

The study session system uses a state machine pattern to manage the complete lifecycle from creation through completion, including AI interaction and evaluation.

```mermaid
stateDiagram-v2
    [*] --> PENDING: create_home_study_session()
    
    PENDING --> ACTIVE: start_session()
    PENDING --> CANCELLED: cancel_session()
    
    ACTIVE --> PAUSED: pause_session()
    ACTIVE --> COMPLETED: end_session()
    
    PAUSED --> ACTIVE: resume_session()
    PAUSED --> COMPLETED: end_session()
    
    COMPLETED --> Evaluation: Automatic
    Evaluation --> [*]
    
    CANCELLED --> [*]
    
    note right of PENDING
        Actions:
        - Validate no active session exists
        - Assign Teacher agent based on subject
        - Link learning units to session
        - Record emotional state (before)
        
        Status: Ready to start
    end note
    
    note right of ACTIVE
        Actions:
        - send_welcome_message()
        - send_message() - Student input
        - Teacher agent generates responses
        - All messages persisted to database
        
        Status: Student actively studying
    end note
    
    note right of PAUSED
        Actions:
        - Create pause record with timestamp
        - Disable message sending
        
        Status: Temporarily suspended
        Note: Can resume or end
    end note
    
    note right of COMPLETED
        Actions:
        - Record emotional state (after)
        - Collect feedback (difficulty, understanding)
        - Close any open pauses
        - Record end time
        
        Status: Session finished
    end note
    
    note right of Evaluation
        Actions:
        - evaluate_session()
        - Evaluator agent analyzes transcript
        - Generate proficiency evaluation (1-10)
        - Generate investment evaluation (1-10)
        - Link evaluations to session
        
        Output: AI-powered assessments
    end note
```

### State Transition Functions

| Function | Current State | New State | Description |
|----------|--------------|-----------|-------------|
| `create_home_study_session()` | N/A | PENDING | Initialize new session with learning units |
| `start_session()` | PENDING | ACTIVE | Begin active study session |
| `pause_session()` | ACTIVE | PAUSED | Temporarily pause the session |
| `resume_session()` | PAUSED | ACTIVE | Resume paused session |
| `end_session()` | ACTIVE/PAUSED | COMPLETED | Complete session with feedback |
| `evaluate_session()` | COMPLETED | N/A | Generate AI evaluations (automatic) |

### Message Flow During Active Session

```mermaid
sequenceDiagram
    participant Student
    participant Route as Study Route
    participant Service as Study Session Service
    participant DB as Database
    participant Teacher as Teacher Agent
    participant OpenAI as OpenAI API
    
    Student->>Route: POST /study/chat (message)
    Route->>Service: send_message(session_id, student_id, content)
    
    Service->>DB: Create student message (PROMPT)
    Service->>DB: Get conversation history
    DB-->>Service: Previous messages
    
    Service->>Teacher: generate_response(student_profile, history, learning_units)
    Teacher->>Teacher: Build system prompt with context
    Teacher->>Teacher: Execute available tools if needed
    Teacher->>OpenAI: Chat completion request
    OpenAI-->>Teacher: AI response
    Teacher-->>Service: Response content
    
    Service->>DB: Create teacher message (RESPONSE)
    Service->>DB: Link messages together
    DB-->>Service: Saved successfully
    
    Service-->>Route: Response data
    Route-->>Student: JSON response with teacher message
```

---

## Database Schema

The database follows a normalized relational design with clear entity relationships and inheritance hierarchies for users and sessions.

```mermaid
erDiagram
    User ||--o{ Student : "is a"
    User ||--o{ Parent : "is a"
    User ||--o{ ClassManager : "is a"
    User ||--o{ SchoolManager : "is a"
    User ||--o{ RegionalSupervisor : "is a"
    
    Parent }o--o{ Student : "parents_students"
    
    School ||--o{ Student : "enrolled in"
    School ||--o{ Class : "contains"
    School ||--|| SchoolManager : "managed by"
    School ||--o{ ClassManager : "employs"
    
    Class }o--o{ Student : "classes_students"
    Class }o--o{ ClassManager : "classess_class_managers"
    
    Subject ||--o{ Course : "contains"
    Subject ||--o{ Teacher : "assigned to"
    Subject }o--o{ RegionalSupervisor : "subjects_regional_supervisors"
    
    Course ||--o{ LearningUnit : "consists of"
    Course ||--o{ Test : "evaluates"
    Course }o--o{ Student : "courses_students"
    
    LearningUnit ||--o{ QA : "contains"
    LearningUnit }o--o{ Test : "tests_learning_units"
    
    Student ||--o{ TestStudent : "takes"
    Test ||--o{ TestStudent : "taken by"
    
    Student ||--o{ LearningUnitStudent : "progresses through"
    LearningUnit ||--o{ LearningUnitStudent : "progress"
    
    Student ||--o{ HomeHoursStudySession : "participates"
    Student ||--o{ SchoolHoursStudySession : "participates"
    
    HomeHoursStudySession ||--o{ Message : "contains"
    SchoolHoursStudySession ||--o{ Message : "contains"
    
    Student ||--o{ Message : "sends"
    Teacher ||--o{ Message : "responds"
    
    HomeHoursStudySession }o--o{ LearningUnit : "learning_units_home_sessions"
    SchoolHoursStudySession }o--o{ LearningUnit : "learning_units_school_sessions"
    
    Teacher ||--o{ HomeHoursStudySession : "teaches"
    Teacher ||--o{ SchoolHoursStudySession : "teaches"
    
    ClassManager ||--o{ SchoolHoursStudySession : "supervises"
    
    HomeHoursStudySession ||--o{ HomeHoursStudySessionPause : "pauses"
    SchoolHoursStudySession ||--o{ SchoolHoursStudySessionPause : "pauses"
    
    Student ||--o{ SessionalProficiencyEvaluation : "evaluated"
    Student ||--o{ SessionalInvestmentEvaluation : "evaluated"
    Student ||--o{ SessionalSocialEvaluation : "evaluated"
    
    Student ||--o{ QuarterProficiencyEvaluation : "evaluated"
    Student ||--o{ QuarterInvestmentEvaluation : "evaluated"
    Student ||--o{ QuarterSocialEvaluation : "evaluated"
    
    HomeHoursStudySession ||--o{ SessionalProficiencyEvaluation : "generates"
    HomeHoursStudySession ||--o{ SessionalInvestmentEvaluation : "generates"
    
    SchoolHoursStudySession }o--o{ SessionalSocialEvaluation : "generates"
    
    User {
        int id PK
        string username UK
        string email UK
        string password_hash
        string first_name
        string last_name
        date date_of_birth
        datetime created_at
    }
    
    Student {
        int id PK,FK
        int school_id FK
        enum learning_style
        enum routine_style
        enum collaboration_style
    }
    
    Course {
        int id PK
        string name
        enum grade_level
        enum type
        int level
        enum subject_name FK
    }
    
    LearningUnit {
        int course_id PK,FK
        string name PK
        enum type
        float weight
        int estimated_duration_minutes
        string previous_learning_unit
        string next_learning_unit
    }
    
    HomeHoursStudySession {
        int id PK
        enum type
        enum status
        datetime start_time
        datetime end_time
        int teacher_id FK
    }
    
    Message {
        int id PK
        int student_id FK
        int teacher_id FK
        int home_session_id FK
        int school_session_id FK
        enum message_type
        enum message_modality
        text content
        datetime timestamp
    }
    
    SessionalProficiencyEvaluation {
        int id PK
        int student_id FK
        int home_session_id FK
        int school_session_id FK
        int score
        text description
        datetime created_at
    }
    
    SessionalInvestmentEvaluation {
        int id PK
        int student_id FK
        int home_session_id FK
        int school_session_id FK
        int score
        text description
        datetime created_at
    }
```

### Key Entity Groups

#### User Entities
- **User**: Base user table with common attributes
- **Student**: Enrolled in courses, participates in sessions
- **Parent**: Views children's progress
- **ClassManager**: Manages class and supervises school sessions
- **SchoolManager**: Oversees entire school
- **RegionalSupervisor**: Subject-level oversight

#### Academic Entities
- **Subject**: Academic subject (Math, Science, etc.)
- **Course**: Specific course within a subject
- **LearningUnit**: Modular content unit within a course
- **QA**: Question-answer pairs for learning units
- **Test**: Assessments for courses

#### Session Entities
- **HomeHoursStudySession**: Student-initiated study sessions
- **SchoolHoursStudySession**: Class-based study sessions
- **Message**: Chat messages between students and AI teachers
- **StudySessionPause**: Pause records for sessions

#### Evaluation Entities
- **SessionalProficiencyEvaluation**: Per-session knowledge assessment
- **SessionalInvestmentEvaluation**: Per-session engagement assessment
- **SessionalSocialEvaluation**: Per-session social behavior (school only)
- **QuarterProficiencyEvaluation**: Quarterly knowledge assessment
- **QuarterInvestmentEvaluation**: Quarterly engagement assessment
- **QuarterSocialEvaluation**: Quarterly social behavior assessment

#### AI Agent Entities
- **Teacher**: AI teaching agents (GPT-based)
- **Evaluator**: AI evaluation models

---

## User Role Hierarchy

The platform supports multiple user types with different access levels and capabilities.

```mermaid
graph TD
    System[λllamda System]
    
    System --> Students[Students]
    System --> Parents[Parents]
    System --> Managers[School Staff]
    System --> Supervisors[Regional Supervisors]
    
    Students --> StudentCapabilities["
        - Create/join study sessions
        - Send messages to AI teachers
        - View own courses and progress
        - Track learning units
        - View test results
        - Provide session feedback
    "]
    
    Parents --> ParentCapabilities["
        - View children's information
        - Monitor study session history
        - Track academic progress
        - View test performance
        - Access analytics dashboard
    "]
    
    Managers --> ClassManager[Class Managers]
    Managers --> SchoolManager[School Managers]
    
    ClassManager --> ClassCapabilities["
        - Supervise class study sessions
        - View class-wide analytics
        - Monitor student attendance
        - Provide investment evaluations
        - Provide social evaluations
        - Track class performance
    "]
    
    SchoolManager --> SchoolCapabilities["
        - Access school-wide analytics
        - View all classes
        - Monitor overall performance
        - Generate reports
        - Track school metrics
    "]
    
    Supervisors --> SupervisorCapabilities["
        - Subject-level oversight
        - Cross-school analytics
        - Curriculum guidance
        - Regional reporting
    "]
    
    style Students fill:#e1f5ff
    style Parents fill:#fff4e1
    style ClassManager fill:#ffe1f5
    style SchoolManager fill:#f5e1ff
    style Supervisors fill:#e1ffe1
```

### User Relationships

```mermaid
graph LR
    Parent[Parent User] -.has children.-> Student1[Student]
    Parent -.has children.-> Student2[Student]
    Parent -.has children.-> Student3[Student]
    
    Student1 -->|enrolled in| School[School]
    Student2 -->|enrolled in| School
    Student3 -->|enrolled in| School
    
    School -->|managed by| SchoolMgr[School Manager]
    School -->|employs| ClassMgr1[Class Manager]
    School -->|employs| ClassMgr2[Class Manager]
    
    School -->|contains| Class1[Class A]
    School -->|contains| Class2[Class B]
    
    Class1 -->|managed by| ClassMgr1
    Class2 -->|managed by| ClassMgr2
    
    Student1 -->|attends| Class1
    Student2 -->|attends| Class1
    Student3 -->|attends| Class2
    
    Subject[Subject - Math] -.supervised by.-> RegSuper[Regional Supervisor]
    
    style Parent fill:#fff4e1
    style Student1 fill:#e1f5ff
    style Student2 fill:#e1f5ff
    style Student3 fill:#e1f5ff
    style ClassMgr1 fill:#ffe1f5
    style ClassMgr2 fill:#ffe1f5
    style SchoolMgr fill:#f5e1ff
    style RegSuper fill:#e1ffe1
```

### Permission Matrix

| Action | Student | Parent | Class Manager | School Manager | Regional Supervisor |
|--------|---------|--------|---------------|----------------|---------------------|
| Create study session | ✓ | ✗ | ✓ (school hours) | ✗ | ✗ |
| Chat with AI teacher | ✓ | ✗ | ✗ | ✗ | ✗ |
| View own progress | ✓ | ✗ | ✗ | ✗ | ✗ |
| View child progress | ✗ | ✓ | ✗ | ✗ | ✗ |
| View class analytics | ✗ | ✗ | ✓ | ✗ | ✗ |
| View school analytics | ✗ | ✗ | ✗ | ✓ | ✗ |
| View subject analytics | ✗ | ✗ | ✗ | ✗ | ✓ |
| Provide investment evaluation | ✗ | ✗ | ✓ | ✗ | ✗ |
| Provide social evaluation | ✗ | ✗ | ✓ | ✗ | ✗ |

---

## AI Agent Integration

The platform uses OpenAI's GPT models through specialized agent classes that provide educational support and assessment.

### Teacher Agent Architecture

```mermaid
graph TB
    subgraph "Teacher Agent System"
        Agent[Teacher Agent Instance]
        
        subgraph "Context Building"
            StudentProfile[Student Profile]
            LearningStyle[Learning Style Context]
            SessionType[Session Type Context]
            ConversationHistory[Conversation History]
            LearningUnits[Learning Units Context]
        end
        
        subgraph "Tool System"
            GetProgress[get_student_progress]
            GetQA[get_qa_for_learning_unit]
            GetTests[get_upcoming_tests]
            SearchQA[search_qa_by_question]
        end
        
        subgraph "AI Processing"
            SystemPrompt[System Prompt Builder]
            OpenAIAPI[OpenAI API - GPT-4]
            ResponseParser[Response Parser]
        end
    end
    
    Student[Student Message] --> Agent
    
    Agent --> StudentProfile
    Agent --> LearningStyle
    Agent --> SessionType
    Agent --> ConversationHistory
    Agent --> LearningUnits
    
    StudentProfile --> SystemPrompt
    LearningStyle --> SystemPrompt
    SessionType --> SystemPrompt
    ConversationHistory --> SystemPrompt
    LearningUnits --> SystemPrompt
    
    SystemPrompt --> OpenAIAPI
    
    OpenAIAPI --> ToolCall{Tool Call Requested?}
    
    ToolCall -->|Yes| GetProgress
    ToolCall -->|Yes| GetQA
    ToolCall -->|Yes| GetTests
    ToolCall -->|Yes| SearchQA
    
    GetProgress --> OpenAIAPI
    GetQA --> OpenAIAPI
    GetTests --> OpenAIAPI
    SearchQA --> OpenAIAPI
    
    ToolCall -->|No| ResponseParser
    
    ResponseParser --> TeacherResponse[Teacher Response]
    TeacherResponse --> Student
```

### Agent Interaction Flow

```mermaid
sequenceDiagram
    participant Student
    participant Service as Study Session Service
    participant Teacher as Teacher Agent
    participant Tools as Agent Tools
    participant DB as Database
    participant OpenAI as OpenAI API
    
    Student->>Service: Send message: "Explain photosynthesis"
    Service->>DB: Save student message
    Service->>DB: Fetch conversation history
    DB-->>Service: Previous messages
    
    Service->>Teacher: generate_response(context)
    
    Teacher->>Teacher: Build system prompt with:<br/>- Student profile<br/>- Learning style<br/>- Session context<br/>- Learning units
    
    Teacher->>OpenAI: Chat completion request
    
    OpenAI-->>Teacher: Tool call: get_qa_for_learning_unit("Photosynthesis")
    
    Teacher->>Tools: Execute get_qa_for_learning_unit
    Tools->>DB: Query QA table
    DB-->>Tools: QA data
    Tools-->>Teacher: Formatted QA content
    
    Teacher->>OpenAI: Continue with tool results
    
    OpenAI-->>Teacher: Final response text
    
    Teacher-->>Service: Response content
    Service->>DB: Save teacher message
    Service-->>Student: Display response
```

### Evaluator Agent Flow

```mermaid
sequenceDiagram
    participant Service as Study Session Service
    participant Evaluator as Evaluator Agent
    participant DB as Database
    participant OpenAI as OpenAI API
    
    Note over Service: Session completed,<br/>trigger evaluation
    
    Service->>DB: Fetch complete transcript
    DB-->>Service: All messages from session
    
    Service->>Evaluator: evaluate_proficiency(transcript)
    
    Evaluator->>Evaluator: Build evaluation prompt:<br/>- Complete conversation<br/>- Learning objectives<br/>- Scoring criteria (1-10)
    
    Evaluator->>OpenAI: Proficiency evaluation request
    OpenAI-->>Evaluator: Score + Description
    
    Evaluator->>Evaluator: Parse score from response
    Evaluator-->>Service: Proficiency score (1-10) + description
    
    Service->>DB: Save SessionalProficiencyEvaluation
    
    Service->>Evaluator: evaluate_investment(transcript)
    
    Evaluator->>Evaluator: Build engagement prompt:<br/>- Conversation quality<br/>- Student participation<br/>- Effort indicators
    
    Evaluator->>OpenAI: Investment evaluation request
    OpenAI-->>Evaluator: Score + Description
    
    Evaluator->>Evaluator: Parse score from response
    Evaluator-->>Service: Investment score (1-10) + description
    
    Service->>DB: Save SessionalInvestmentEvaluation
    
    Service->>Service: Link evaluations to session
    DB-->>Service: Evaluation complete
```

### Teacher Agent Tools

The Teacher agent has access to several tools to provide accurate, context-aware responses:

| Tool Name | Purpose | Database Query |
|-----------|---------|----------------|
| `get_student_progress` | Retrieve student's progress in current course | LearningUnitStudent table |
| `get_qa_for_learning_unit` | Get Q&A content for specific learning unit | QA table filtered by learning unit |
| `get_upcoming_tests` | Fetch upcoming tests for the course | Test, TestStudent tables |
| `search_qa_by_question` | Search Q&A by question text | QA table with text search |

### Agent Configuration

Both Teacher and Evaluator agents are configured with:

- **Model**: GPT-4 or GPT-3.5-turbo (configurable per subject)
- **Temperature**: 0.7 for Teacher (creative), 0.3 for Evaluator (consistent)
- **Max Tokens**: 1000 for responses
- **Subject Specialization**: Each teacher is assigned to a specific subject
- **Status**: Operational, Disabled, Deprecated, Development, or Testing

---

## Integration Patterns

### Service-to-Service Communication

Services communicate through well-defined interfaces and shared database models:

```mermaid
graph LR
    StudyRoute[Study Route] --> SessionService[Study Session Service]
    StudyRoute --> PrioService[Course Prioritization]
    StudyRoute --> UnitService[Learning Unit Assignment]
    
    SessionService --> TeacherAgent[Teacher Agent]
    SessionService --> EvalAgent[Evaluator Agent]
    
    PrioService -.shared models.-> Database[(Database)]
    UnitService -.shared models.-> Database
    SessionService -.shared models.-> Database
    
    style Database fill:#f0f0f0
```

### Error Handling Strategy

The platform uses custom exceptions for domain-specific errors:

```python
# Study Session Service Exceptions
StudySessionError                  # Base exception
├── ActiveSessionExistsError       # Student has active session
├── SessionNotFoundError           # Session doesn't exist
└── InvalidSessionStateError       # Invalid state transition

# All exceptions propagate to routes for user-friendly error messages
```

### Transaction Management

Database transactions are managed using decorators and context managers:

```python
# Automatic transaction handling
@session_state_transition(expected_status, new_status)
def start_session(session, session_id, study_session):
    # Validation, state update, and commit handled by decorator
    pass

# Manual session context
from src.database.session_context import get_current_session
session = get_current_session()
# Session automatically committed or rolled back
```

---

## Technology Stack Details

### Backend Technologies
- **Flask 2.x**: Web framework
- **SQLAlchemy 2.x**: ORM for database access
- **Flask-Session**: Server-side session management
- **Python 3.9+**: Primary language

### Database
- **MySQL 8.x**: Primary data store
- **Alembic**: Database migrations (optional)

### AI/ML
- **OpenAI API**: GPT-4 and GPT-3.5-turbo
- **LangChain** (optional): Agent framework enhancements

### Frontend
- **Jinja2**: Server-side templating
- **Vanilla JavaScript**: Client-side interactivity
- **CSS3**: Styling
- **WebSocket**: Real-time communication (voice mode)

### Development Tools
- **Python Virtual Environment**: Dependency isolation
- **pip**: Package management
- **Git**: Version control

---

## Deployment Considerations

### Environment Variables
```bash
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_NAME=allamda
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key
```

### Database Initialization
```python
from src.database import DatabaseManager
DatabaseManager.create_tables()
DatabaseManager.populate_sample_data(clear_existing=True)
```

### Production Recommendations
- Use WSGI server (Gunicorn, uWSGI)
- Enable SSL/TLS for all connections
- Configure database connection pooling
- Set up proper logging and monitoring
- Implement rate limiting for OpenAI API calls
- Use environment-specific configuration
- Regular database backups
- Monitor API costs and usage

---

## Future Architecture Enhancements

### Planned Improvements
1. **Microservices Migration**: Split services into independent microservices
2. **Caching Layer**: Redis for session and frequently accessed data
3. **Message Queue**: RabbitMQ/Celery for async task processing
4. **GraphQL API**: Alternative to REST for flexible client queries
5. **Real-time Analytics**: WebSocket-based live dashboards
6. **Multi-tenant Support**: Separate databases per school/district
7. **Mobile Apps**: Native iOS/Android applications
8. **Advanced AI**: Fine-tuned models, embeddings for semantic search

### Scalability Considerations
- Horizontal scaling of Flask application servers
- Database read replicas for analytics queries
- CDN for static assets
- Load balancing across multiple instances
- Session store scaling (Redis Cluster)

---

## Contributing

When contributing to the architecture:
1. Follow the existing layered pattern
2. Keep business logic in service layer
3. Use decorators for cross-cutting concerns
4. Write unit tests for new services
5. Document API changes
6. Update this document for architectural changes

## Additional Resources

- [Study Session Service Documentation](src/services/study_session/README.md)
- [Course Prioritization Documentation](src/services/course_prioritization/README.md)
- [Learning Unit Assignment Documentation](src/services/learning_unit_assignment/README.md)
- [Main README](README.md)

---

**Last Updated**: November 2025  
**Version**: 1.0  
**Maintainers**: λllamda Development Team

