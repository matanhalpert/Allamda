# AI Agent Base Infrastructure

Core infrastructure for AI agents with automatic tool discovery, OpenAI API integration, and response handling. Provides the foundation that Teacher and Evaluator agents build upon.

## Overview

The base agent infrastructure implements the core capabilities shared by all AI agents in the system. It provides a mixin pattern for adding AI functionality to database models, automatic tool discovery via decorators, OpenAI API integration with function calling, and standardized response handling. This architecture allows agents to have both database persistence (via Agent base class) and AI capabilities (via AIAgentMixin).

## Structure

```
base/
├── __init__.py      # Package exports
├── mixin.py        # AIAgentMixin - core agent capabilities
├── tool.py         # AIAgentTool class and agent_tool decorator
├── responses.py    # ToolResponse for standardized tool returns
└── README.md       # This file
```

## Core Components

### AIAgentMixin (`mixin.py`)

**Purpose**: Adds AI capabilities to agent models via multiple inheritance

**Key Features:**
- Automatic tool discovery from decorated methods
- System prompt generation with context
- OpenAI API integration (GPT-4/3.5)
- Tool execution with parameter validation
- Response parsing and error handling
- Custom JSON encoder for database types

**Configuration:**
```python
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1000
```

**Auto-Discovery Pattern:**
```python
class Teacher(Agent, AIAgentMixin):
    # Tools automatically discovered from @agent_tool decorators
    @agent_tool(
        description="Get student progress",
        parameters=ProgressSchema.to_openai_schema()
    )
    def get_student_progress(self, ...):
        pass
```

**Core Methods:**

**register_tool()**
```python
@classmethod
def register_tool(cls, tool: AIAgentTool) -> None:
    # Register tool for agent class
```

**get_tools()**
```python
@classmethod
def get_tools(cls) -> List[AIAgentTool]:
    # Get all registered tools
```

**generate_response()**
```python
def generate_response(
    self,
    messages: List[Dict[str, Any]],
    **context_kwargs
) -> str:
    # Generate AI response with tool support
    # Handles:
    # - System prompt generation
    # - Tool function calling
    # - Multiple tool call rounds
    # - Error handling
```

**_get_context()**
```python
def _get_context(self, **context_kwargs) -> str:
    # MUST be implemented by subclasses
    # Defines agent-specific behavior and personality
```

### AIAgentTool (`tool.py`)

**Purpose**: Tool definition and execution wrapper

**Structure:**
```python
class AIAgentTool:
    name: str
    description: str
    parameters: Dict[str, Any]  # OpenAI function schema
    function: callable
```

**Methods:**
```python
def to_openai_format(self) -> Dict[str, Any]:
    # Convert to OpenAI function calling format
    
def execute(
    self,
    agent_instance,
    validated_params: BaseModel
) -> ToolResponse:
    # Execute tool with validated parameters
```

### agent_tool Decorator

**Purpose**: Mark methods as agent tools with auto-registration

**Usage:**
```python
from ..base import agent_tool, ToolResponse
from .schemas import MyToolParams

@agent_tool(
    description="Description of what this tool does",
    parameters=MyToolParams.to_openai_schema()
)
def my_tool(self, param1: str, param2: int) -> ToolResponse:
    # Tool implementation
    result = do_something(param1, param2)
    return ToolResponse.success(data=result)
```

**Decorator Attributes:**
- Adds `_is_agent_tool = True` to method
- Stores `_tool_description`
- Stores `_tool_parameters`
- Enables automatic discovery by AIAgentMixin

### ToolResponse (`responses.py`)

**Purpose**: Standardized return format for tool execution

**Structure:**
```python
@dataclass
class ToolResponse:
    success: bool
    data: Optional[Any]
    error_message: Optional[str]
    error_type: Optional[str]
    context: Optional[Dict[str, Any]]
```

**Factory Methods:**
```python
# Success response
return ToolResponse.success(
    data={"student_id": 1, "progress": 85.5}
)

# Error response
return ToolResponse.error_response(
    error_message="Student not found",
    error_type="not_found",
    context={"student_id": 999}
)
```

**Benefits:**
- Consistent error handling
- Type-safe returns
- Context preservation for debugging
- Easy serialization for AI

## Tool System Architecture

### Tool Discovery Flow

```
1. Define tool method with @agent_tool decorator
   ↓
2. AIAgentMixin.__init_subclass__() called
   ↓
3. Scan MRO for methods with _is_agent_tool attribute
   ↓
4. Create AIAgentTool instances
   ↓
5. Register tools in cls._tools dict
   ↓
6. Tools available for OpenAI function calling
```

### Tool Execution Flow

```
1. Agent receives user message
   ↓
2. generate_response() called with context
   ↓
3. System prompt generated (_get_context())
   ↓
4. Tools converted to OpenAI format
   ↓
5. OpenAI API call with tools
   ↓
6. AI decides to call tool(s)
   ↓
7. Tool parameters validated (Pydantic)
   ↓
8. Tool executed with validated params
   ↓
9. ToolResponse returned
   ↓
10. Results fed back to AI
   ↓
11. AI generates final response
   ↓
12. Return response to caller
```

### Multiple Tool Calls

The system supports sequential tool calling:

```python
# AI can call multiple tools in one conversation turn
1. Call get_session_context()
2. Use context to determine next step
3. Call get_student_progress()
4. Analyze data
5. Generate response incorporating all tool results
```

## Pydantic Schema Pattern

Tools use Pydantic models for parameter validation:

```python
# schemas.py
from pydantic import BaseModel, Field

class MyToolParams(BaseModel):
    student_id: int = Field(..., description="ID of the student")
    course_id: int = Field(..., description="ID of the course")
    include_history: bool = Field(
        default=False,
        description="Include historical data"
    )
    
    @staticmethod
    def to_openai_schema() -> Dict[str, Any]:
        """Convert to OpenAI function parameters format."""
        return {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "integer",
                    "description": "ID of the student"
                },
                "course_id": {
                    "type": "integer",
                    "description": "ID of the course"
                },
                "include_history": {
                    "type": "boolean",
                    "description": "Include historical data"
                }
            },
            "required": ["student_id", "course_id"]
        }
```

**Benefits:**
- Type checking
- Automatic validation
- Clear parameter documentation
- OpenAI schema generation

## Custom JSON Encoder

**AgentJSONEncoder** handles database types:

```python
class AgentJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return obj.total_seconds()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        # ... etc
```

**Supported Types:**
- Decimal → float
- datetime/date → ISO string
- timedelta → seconds (float)
- Models with to_dict() → dict
- Objects with __dict__ → dict

## Usage Examples

### Creating an Agent with Tools

```python
from src.models.base import Agent
from src.models.agents.base import AIAgentMixin, agent_tool, ToolResponse
from .schemas import StudentProgressParams

class MyAgent(Agent, AIAgentMixin):
    __tablename__ = 'my_agents'
    
    def _get_context(self, **context_kwargs) -> str:
        """Define agent personality and behavior."""
        return """
        You are a helpful educational assistant.
        You provide clear, accurate information.
        You use available tools to access student data.
        """
    
    @agent_tool(
        description="Get student progress in a course",
        parameters=StudentProgressParams.to_openai_schema()
    )
    def get_student_progress(
        self,
        student_id: int,
        course_id: int
    ) -> ToolResponse:
        # Implementation
        progress_data = fetch_progress(student_id, course_id)
        return ToolResponse.success(data=progress_data)
```

### Using the Agent

```python
# Fetch agent from database
agent = Teacher.get_by(name="Math Teacher", first=True)

# Generate response with context
messages = [
    {"role": "user", "content": "How is student 123 doing in course 45?"}
]

response = agent.generate_response(
    messages=messages,
    student_id=123,
    course_id=45
)

# Agent automatically:
# 1. Generates system prompt
# 2. Calls OpenAI with available tools
# 3. Executes tools if AI requests them
# 4. Returns final response
```

## OpenAI Integration

### Function Calling Format

Tools converted to OpenAI function format:

```python
{
    "type": "function",
    "function": {
        "name": "get_student_progress",
        "description": "Get student progress in a course",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer", "description": "..."},
                "course_id": {"type": "integer", "description": "..."}
            },
            "required": ["student_id", "course_id"]
        }
    }
}
```

### API Call Structure

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000,
    messages=messages,
    tools=tools,  # Converted from AIAgentTool list
    tool_choice="auto"
)
```

## Error Handling

### Tool Execution Errors

```python
try:
    result = tool.execute(agent, validated_params)
    if not result.success:
        # Tool returned error
        error_msg = result.error_message
except ValidationError as e:
    # Pydantic validation failed
    handle_validation_error(e)
except Exception as e:
    # Unexpected error
    handle_unexpected_error(e)
```

### Response Generation Errors

```python
try:
    response = agent.generate_response(messages, **context)
except Exception as e:
    Logger.error(f"Response generation failed: {e}")
    # Return fallback response
```

## Design Patterns

### Mixin Pattern

Why use mixin instead of inheritance?
- Separates AI capabilities from database model
- Allows Agent to inherit from Base (SQLAlchemy)
- Enables AIAgentMixin reuse across different model types
- Clear separation of concerns

### Decorator Pattern

Why use @agent_tool decorator?
- Declarative tool definition
- Automatic registration
- Metadata attachment without boilerplate
- Clean, readable code

### Factory Pattern

ToolResponse uses factory methods:
- `success()` - Create success response
- `error_response()` - Create error response
- Ensures consistent structure
- Improves readability

## Integration Points

### Database Models
AIAgentMixin adds functionality to Agent models:
```python
class Teacher(Agent, AIAgentMixin):
    # Inherits database persistence from Agent
    # Gains AI capabilities from AIAgentMixin
```

### Session Context
Tools use current session for queries:
```python
from src.database.session_context import get_current_session

session = get_current_session()
student = session.query(Student).filter(...).first()
```

### OpenAI API
All agents use OpenAI's function calling:
- GPT-4 or GPT-3.5-turbo models
- Streaming not currently supported
- Temperature and token limits configurable

## Dependencies

- **OpenAI Python SDK**: API integration
- **Pydantic**: Parameter validation
- **SQLAlchemy**: Database models
- **Python 3.9+**: Type hints and decorators

## Security Considerations

1. **API Key**: Store in environment variables
2. **Parameter Validation**: All tool params validated
3. **Error Messages**: Don't expose sensitive data
4. **Session Access**: Use context-based session management
5. **Tool Permissions**: Tools have full database access

## Performance Considerations

- Tool calls add latency (sequential execution)
- OpenAI API calls are network-bound
- Consider caching for repeated queries
- Limit number of tools per agent (<10 recommended)
- Use efficient database queries in tools

## Future Enhancements

Potential improvements:
- Streaming responses
- Parallel tool execution
- Tool result caching
- Async/await support
- Tool permission system
- Rate limiting
- Response retry logic

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

