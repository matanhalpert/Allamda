# Teacher Agent

AI-powered teaching agent providing personalized, adaptive instruction to students during study sessions. Leverages GPT-4 with specialized tools to access student progress, learning resources, and historical performance data.

## Overview

The Teacher agent acts as a virtual instructor, adapting teaching style to individual student profiles, session types, and learning objectives. It provides real-time explanations, answers questions, guides problem-solving, and adjusts difficulty based on student mastery levels. The agent has multimodal vision capabilities for analyzing images students share and uses specialized tools to access relevant educational data.

## Structure

```
teacher/
├── __init__.py    # Package exports
├── agent.py       # Teacher class implementation
├── tools.py       # Tool method implementations
├── schemas.py     # Pydantic parameter schemas
└── README.md      # This file
```

## Teacher Agent Class

### Inheritance
```python
class Teacher(Agent, AIAgentMixin):
    # Database persistence from Agent
    # AI capabilities from AIAgentMixin
```

### Database Fields

```python
ai_model_id: Integer (PK, FK)
name: String(100) (PK)
subject_name: Enum(SubjectName) (FK)
```

### Relationships

- `subject` - Many-to-one with Subject
- `home_study_sessions` - One-to-many with HomeHoursStudySession
- `school_study_sessions` - One-to-many with SchoolHoursStudySession
- `sent_messages` - One-to-many with Message
- `test_students` - One-to-many with TestStudent

## Adaptive Teaching Capabilities

### Student Profile Adaptation

**Learning Styles Supported:**
- **Visual**: Emphasizes diagrams, charts, visual examples
- **Auditory**: Uses verbal explanations, discussions
- **Kinesthetic**: Encourages hands-on practice, experiments
- **Reading/Writing**: Focuses on text, notes, written exercises

**Routine Preferences:**
- **Structured**: Organized approach with clear steps
- **Flexible**: Adaptive pacing, exploratory learning
- **Mixed**: Balanced structure and flexibility

**Collaboration Styles:**
- **Independent**: Self-directed approach
- **Collaborative**: Group-oriented strategies
- **Mixed**: Adapts based on context

### Session Type Adaptation

**Home Session Types:**
- **TEST_PREPARATION**: Focused review, practice problems, exam strategies
- **HOMEWORK**: Assignment help, concept clarification
- **REVISION**: Reinforcing previous material
- **EXPLORATION**: Discovery-based learning, new concepts

**School Session Types:**
- **LECTURE**: Structured content delivery
- **DISCUSSION**: Interactive conversation, peer learning
- **PRACTICE**: Hands-on exercises, problem-solving
- **REVIEW**: Recap and reinforcement

### Emotional State Awareness

Adapts approach based on student's emotional state:
- **POSITIVE**: Maintains energy, encourages challenges
- **NEUTRAL**: Standard supportive approach
- **NEGATIVE/STRESSED**: Extra patience, encouragement, simplified explanations

## Available Tools

### 1. get_learning_unit_mastery

**Purpose**: Retrieve student's mastery level for specific learning units

**Parameters:**
```python
{
    "student_id": int,
    "course_id": int,
    "learning_unit_names": list[str]
}
```

**Returns:**
```python
{
    "student_id": int,
    "course_id": int,
    "mastery_data": [
        {
            "learning_unit_name": str,
            "description": str,
            "type": str,
            "state": str,  # "not_started", "in_progress", "completed"
            "progress": float,  # 0-100%
            "recent_proficiency_scores": [int],  # Last 3 scores
            "is_first_time": bool
        }
    ]
}
```

**Use Cases:**
- Assess if student is seeing content for first time
- Adapt difficulty based on progress percentage
- Reference previous proficiency scores
- Skip concepts already mastered

### 2. get_qa_resources

**Purpose**: Access Q&A resources for learning units

**Parameters:**
```python
{
    "course_id": int,
    "learning_unit_names": list[str],
    "qa_types": list[str],  # Optional filter
    "limit": int  # Optional, default 10
}
```

**Returns:**
```python
{
    "course_id": int,
    "total_resources": int,
    "resources": [
        {
            "learning_unit_name": str,
            "qa_type": str,  # "definition", "example", "practice", etc.
            "question": str,
            "answer": str,
            "difficulty": str,
            "tags": [str]
        }
    ]
}
```

**Use Cases:**
- Find relevant examples for concept explanation
- Access practice problems
- Retrieve definitions and formulas
- Get real-world applications

### 3. get_student_test_history

**Purpose**: Retrieve student's past test performance

**Parameters:**
```python
{
    "student_id": int,
    "course_id": int,
    "limit": int  # Optional, default 5
}
```

**Returns:**
```python
{
    "student_id": int,
    "course_id": int,
    "tests": [
        {
            "test_name": str,
            "test_date": str,
            "grade": float,
            "max_grade": float,
            "percentage": float,
            "learning_units_covered": [str]
        }
    ],
    "average_grade": float,
    "trend": str  # "improving", "declining", "stable"
}
```

**Use Cases:**
- Identify weak areas from test performance
- Adjust teaching based on test results
- Reference past struggles or successes
- Motivate with improvement trends

### 4. get_recent_student_evaluations

**Purpose**: Access recent proficiency/investment evaluations

**Parameters:**
```python
{
    "student_id": int,
    "evaluation_type": str,  # "proficiency" or "investment"
    "limit": int  # Optional, default 5
}
```

**Returns:**
```python
{
    "student_id": int,
    "evaluation_type": str,
    "evaluations": [
        {
            "date": str,
            "score": int,  # 1-10
            "description": str,
            "session_type": str
        }
    ],
    "average_score": float,
    "trend": str
}
```

**Use Cases:**
- Understand student's typical engagement level
- Identify patterns in proficiency
- Adjust approach based on historical engagement
- Provide personalized encouragement

### 5. get_prerequisite_units_status

**Purpose**: Check if prerequisite units are completed

**Parameters:**
```python
{
    "student_id": int,
    "course_id": int,
    "learning_unit_name": str
}
```

**Returns:**
```python
{
    "learning_unit_name": str,
    "prerequisites": [
        {
            "unit_name": str,
            "is_completed": bool,
            "progress": float,
            "proficiency_score": int
        }
    ],
    "all_prerequisites_met": bool
}
```

**Use Cases:**
- Verify student has required background knowledge
- Suggest reviewing prerequisites if needed
- Skip foundational review if prerequisites solid

## Context Generation

### System Prompt Structure

The Teacher agent builds comprehensive context prompts including:

1. **Role and Expertise**
   - Agent name and subject specialization
   - Teaching philosophy
   - Multimodal capabilities

2. **Student Profile(s)**
   - Learning style, routine, collaboration preferences
   - How to adapt to each preference

3. **Session Context**
   - Session type and objectives
   - Learning units being studied
   - Emotional state(s) of student(s)

4. **Learning Content**
   - Course and subject information
   - Learning unit descriptions and objectives

5. **Available Tools**
   - List of tools and when to use them

6. **Teaching Guidelines**
   - How to structure responses
   - When to use tools vs direct knowledge
   - Encouragement and support strategies

### Group Session Support

For school sessions with multiple students:
- Lists all student profiles
- Adapts to diverse learning styles simultaneously
- Encourages peer learning and collaboration
- Balances attention across students

## Usage Example

```python
from src.models.agents import Teacher
from src.database import with_db_session

@with_db_session
def handle_student_message(session_id, student_id, message_content):
    # Get session and teacher
    session = HomeHoursStudySession.get_by(id=session_id, first=True)
    teacher = session.teacher
    
    # Get student
    student = Student.get_by(id=student_id, first=True)
    
    # Build message history
    messages = [
        {"role": "user", "content": message_content}
    ]
    
    # Generate response with context
    response = teacher.generate_response(
        messages=messages,
        students=[student],
        session=session,
        learning_units=session.learning_units
    )
    
    return response
```

## Teaching Strategies

### Adaptive Difficulty

```python
# Teacher checks mastery before explaining
if is_first_time:
    # Start with basics
    explanation = simple_introduction()
elif progress < 30:
    # Student struggling, simplify
    explanation = foundational_concepts()
elif progress > 70:
    # Student advanced, challenge them
    explanation = advanced_applications()
```

### Multimodal Teaching

**Text**: Standard explanations and examples

**Images**: Analyzes student-shared images:
- Diagrams: Explains components and relationships
- Handwriting: Checks work, identifies errors
- Photos: Provides context-aware feedback
- Equations: Validates solutions, suggests corrections

**Files**: References uploaded documents and resources

### Socratic Method

- Asks guiding questions
- Encourages critical thinking
- Leads student to discover answers
- Validates understanding through dialogue

## Best Practices

### When to Use Tools

**Use get_learning_unit_mastery when:**
- Student asks about a concept
- Need to gauge starting difficulty level
- Deciding whether to review vs introduce new material

**Use get_qa_resources when:**
- Student needs examples
- Practice problems requested
- Definition or formula needed
- Real-world application desired

**Use get_student_test_history when:**
- Student mentions struggling
- Need to identify knowledge gaps
- Motivation through progress tracking
- Contextualizing current learning

### Communication Style

- **Clear and Concise**: Avoid overwhelming with information
- **Encouraging**: Positive reinforcement and support
- **Patient**: Allow time for understanding
- **Adaptive**: Adjust based on feedback and response quality
- **Engaging**: Use examples relevant to student interests
- **Precise**: Technically accurate explanations

## Integration Points

### Study Session Service
Used by `src/services/study_session/messaging.py`:
- `send_message()` calls teacher's `generate_response()`
- Conversation history maintained
- Context includes session details

### Message Models
Messages link to teacher:
- Teacher sends RESPONSE type messages
- Message modality tracked (TEXT, VOICE, MULTIMODAL)
- Attachments associated with messages

### Session Models
Teachers assigned to sessions:
- Automatic assignment based on course subject
- One teacher per session
- Teacher context includes session type

## Performance Considerations

- **Tool Calls**: Each tool adds 1-3 seconds latency
- **Caching**: Consider caching frequently accessed data
- **Selective Tool Use**: Only call tools when necessary
- **Batch Queries**: Tools fetch multiple units at once
- **Token Limits**: Keep context concise to fit in context window

## Dependencies

- **OpenAI API**: GPT-4 or GPT-3.5-turbo
- **Base Agent Infrastructure**: AIAgentMixin, tool system
- **Database Models**: Student, LearningUnit, QA, Test
- **Pydantic**: Parameter validation

## Notes

- Teachers are subject-specific (Math, Science, etc.)
- Each teacher can handle multiple session types
- Multimodal vision requires GPT-4 Vision model
- Tools use current database session from context
- Response quality depends on prompt engineering
- Tool descriptions guide AI on when/how to use tools

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

