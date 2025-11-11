"""
Tool infrastructure for AI agents.

This module provides the AIAgentTool class and agent_tool decorator for registering
and managing tools that agents can use.
"""

from typing import Callable, Dict, Any


class AIAgentTool:
    """Represents a tool that an AI agent can use as an instance method."""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any], function: Callable):
        """Initialize an AI agent tool."""
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def execute(self, agent_instance: Any, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        if agent_instance is None:
            raise ValueError(f"Tool '{self.name}' requires an agent instance to execute")
        return self.function(agent_instance, **kwargs)


def agent_tool(description: str, parameters: Dict[str, Any]):
    """
    Decorator to mark a method as an agent tool.

    Args:
        description: Human-readable description of what the tool does
        parameters: JSON schema describing the tool's parameters (OpenAI format)
    """
    def decorator(func: Callable) -> Callable:
        func._is_agent_tool = True
        func._tool_description = description
        func._tool_parameters = parameters
        return func
    return decorator
