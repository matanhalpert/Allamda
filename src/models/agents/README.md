# AI Agents

AI agent models that provide personalized instruction and evaluation capabilities using OpenAI's API.

## Structure

```
agents/
├── __init__.py          # Package exports
├── ai_model.py         # AIModel database model (tracks model versions)
├── base/               # Base infrastructure
│   ├── mixin.py       # AIAgentMixin - core agent capabilities
│   ├── tool.py        # AIAgentTool - tool definition and execution
│   ├── responses.py   # Response handling utilities
│   └── __init__.py    # Base exports
├── teacher/           # Teacher agent
│   ├── agent.py      # Teacher model and implementation
│   ├── schemas.py    # Pydantic schemas for tool parameters
│   └── tools.py      # Teacher agent tools
└── evaluator/        # Evaluator agent
    ├── agent.py      # Evaluator model and implementation
    ├── schemas.py    # Pydantic schemas for tool parameters
    └── tools.py      # Evaluator agent tools
```

## Architecture

### Base Infrastructure

**AIAgentMixin** (`base/mixin.py`):
- Adds AI capabilities to agent models
- Automatic tool discovery from `@agent_tool` decorated methods
- System prompt generation (context + tool descriptions)
- OpenAI API integration
- Response parsing and validation

**AIAgentTool** (`base/tool.py`):
- Tool definition class (name, description, parameters)
- Tool execution with parameter validation
- Pydantic schema integration

**agent_tool Decorator**:
- Marks methods as agent tools
- Auto-registers tools with agent class
- Extracts tool metadata (description, parameters)

### Agent Models

Both agents inherit from:
- `Agent` (SQLAlchemy model) - Database persistence
- `AIAgentMixin` - AI capabilities

This dual inheritance provides:
- Database records for agents
- Runtime AI functionality

## Teacher Agent

Provides personalized instruction to students during study sessions.

### Capabilities
- Adaptive teaching based on:
  - Student learning profile (learning style, routine, collaboration)
  - Session type (test preparation, homework)
  - Emotional state
  - Learning units being studied
- Personalized explanations and pacing
- Uses conversation history for context

### Tools
- `get_student_course_progress` - Retrieve student's progress in a course
- `get_qa_resources` - Access Q&A resources for learning units
- `get_student_test_history` - View student's test performance history

### Usage
```python
from src.models.agents import Teacher
from src.services.study_session.messaging import send_message

# Teacher is automatically assigned based on course subject
# Used internally by study session service
response = teacher.send_message(
    student=student,
    message_content="Can you explain photosynthesis?",
    session_context={...}
)
```

### Context
The Teacher agent receives:
- Student learning profile
- Session type and learning units
- Emotional state
- Conversation history
- Course progress information

## Evaluator Agent

Assesses student performance and engagement.

### Capabilities
- Analyzes performance across dimensions:
  - **Proficiency**: Understanding, mastery, academic skills
  - **Investment**: Engagement, attendance, dedication
- Generates scores (1-10) with detailed descriptions
- Provides objective, data-driven assessments

### Tools
- `get_student_test_performance` - Analyze test performance
- `get_student_attendance_data` - Get attendance records
- `get_student_evaluation_history` - Review past evaluations

### Usage
```python
from src.models.agents import Evaluator
from src.services.study_session.evaluation import evaluate_session

# Used internally by study session service
proficiency, investment = evaluator.evaluate_session(
    student=student,
    session_transcript=messages,
    context={...}
)
```

### Evaluation Types
- **Sessional Evaluations**: Per-session assessments
- **Quarter Evaluations**: Quarterly summaries

## Tool System

### Creating Tools

Tools are Python methods decorated with `@agent_tool`:

```python
from src.models.agents.base import agent_tool
from src.models.agents.base.responses import ToolResponse

@agent_tool(
    description="Gets student course progress",
    parameters=CourseProgressSchema
)
def get_student_course_progress(self, schema: CourseProgressSchema) -> ToolResponse:
    # Tool implementation
    progress = ...
    return ToolResponse.success(data=progress)
```

### Tool Execution Flow

1. Agent receives message/request
2. Generates system prompt (context + available tools)
3. Calls OpenAI API with tool definitions
4. AI decides which tools to use (function calling)
5. Tools are executed with validated parameters
6. Results fed back to AI for final response
7. Response returned to caller

### Tool Schemas

Each tool has a Pydantic schema defining:
- Required/optional parameters
- Parameter types and validation
- Description for AI understanding

Schemas defined in `teacher/schemas.py` and `evaluator/schemas.py`.

## Configuration

### Model Settings

Default configuration (can be overridden):
- **Model**: `gpt-4o-mini`
- **Temperature**: `0.7`
- **Max Tokens**: `1000`

Set via `model_config` property on agent instances.

### Environment Variables

- `OPENAI_API_KEY` - Required for AI agent functionality

## Database Model

**AIModel** (`ai_model.py`):
- Tracks AI model versions and configurations
- Links to agents using specific models
- Enables model versioning and tracking

## Integration Points

### Study Session Service
- Teacher agent used in `messaging.py` for chat responses
- Evaluator agent used in `evaluation.py` for assessments

### Models
- Agents are database models (can be queried, filtered)
- Relationships to sessions, messages, evaluations

### Services
- Services call agents through their AI methods
- Agents use database session for tool execution

## Design Patterns

1. **Mixin Pattern**: `AIAgentMixin` adds functionality without inheritance hierarchy
2. **Tool Pattern**: Decorator-based tool registration
3. **Strategy Pattern**: Different agents for different purposes
4. **Template Method**: `_get_context()` defines agent-specific behavior

## Notes

- Tools automatically discover methods decorated with `@agent_tool`
- Tool parameters validated using Pydantic schemas
- All AI calls use OpenAI function calling API
- Responses parsed and validated before returning
- Error handling built into tool execution framework
