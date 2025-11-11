"""
AI Agent Mixin for adding agentic capabilities to AI agent models.

This module provides the core AIAgentMixin class that adds tool management
and LLM interaction capabilities to agent models.
"""

import os
import json
from decimal import Decimal
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional, Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel, ValidationError

from .tool import AIAgentTool
from src.utils.logger import Logger

T = TypeVar('T', bound=BaseModel)


class AgentJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles common database types."""
    
    def default(self, obj):
        """Convert non-serializable objects to JSON-serializable types."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return obj.total_seconds()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__

        return super().default(obj)


class AIAgentMixin:
    """
    Mixin that adds AI agent capabilities with automatic tool discovery.
    
    Subclasses must implement _get_context() to define agent behavior.
    Tools are discovered automatically from @agent_tool decorated methods.
    """
    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1000
    
    def __init_subclass__(cls, **kwargs):
        """Initialize subclass with auto-discovered tools from @agent_tool decorated methods."""
        super().__init_subclass__(**kwargs)

        cls._tools: Dict[str, AIAgentTool] = {}
        
        # Auto-discover and register decorated tool methods
        # Iterate through MRO to find all decorated methods including inherited ones
        for base_cls in cls.__mro__:
            # Skip the mixin itself and any base classes that don't have __dict__
            if base_cls is AIAgentMixin or not hasattr(base_cls, '__dict__'):
                continue
                
            for name, method in base_cls.__dict__.items():
                if callable(method) and hasattr(method, '_is_agent_tool'):
                    if name not in cls._tools:
                        tool = AIAgentTool(
                            name=name,
                            description=method._tool_description,
                            parameters=method._tool_parameters,
                            function=method
                        )
                        cls.register_tool(tool)
    
    @classmethod
    def register_tool(cls, tool: AIAgentTool) -> None:
        """Register a tool for this agent class."""
        cls._tools[tool.name] = tool
    
    @classmethod
    def get_tools(cls) -> List[AIAgentTool]:
        """Get all registered tools for this agent class."""
        return list(cls._tools.values())

    @classmethod
    def _get_tools_description(cls) -> str:
        """Generate comma-separated list of available tool names for system prompt."""
        if cls._tools:
            tool_names = [tool.name for tool in cls._tools.values()]
            return f"Available tools: {', '.join(tool_names)}"
        return ""

    def _get_context(self, **context_kwargs) -> str:
        """Generate agent-specific system prompt context. Must be implemented by subclasses."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _get_context() method"
        )

    def get_system_prompt(self, **context_kwargs) -> str:
        """Generate complete system prompt by combining context and tool descriptions."""
        context: str = self._get_context(**context_kwargs)
        prompt_parts = [context]

        tool_description: str = self._get_tools_description()
        if tool_description:
            prompt_parts.append(f"\n{tool_description}")

        return "\n".join(prompt_parts)

    @staticmethod
    def _get_openai_client() -> OpenAI:
        """Get OpenAI client with API key from environment."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return OpenAI(api_key=api_key)
    
    @property
    def model_config(self) -> Dict[str, Any]:
        """Get model configuration. Override in subclasses for custom settings."""
        return {
            "model": self.DEFAULT_MODEL,
            "temperature": self.DEFAULT_TEMPERATURE,
            "max_tokens": self.DEFAULT_MAX_TOKENS
        }
    
    def _prepare_model_params(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Merge config defaults with optional parameter overrides."""
        config = self.model_config
        return {
            "model": model or config["model"],
            "temperature": temperature if temperature is not None else config["temperature"],
            "max_tokens": max_tokens if max_tokens is not None else config["max_tokens"]
        }
    
    def _build_messages_with_context(
        self,
        messages: List[Dict[str, str]],
        **context_kwargs
    ) -> List[Dict[str, str]]:
        """Prepend system prompt to user messages."""
        full_messages = [{"role": "system", "content": self.get_system_prompt(**context_kwargs)}]
        full_messages.extend(messages)
        return full_messages
    
    def _prepare_api_call(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        additional_params: Optional[Dict[str, Any]] = None,
        **context_kwargs
    ) -> tuple[OpenAI, Dict[str, Any], List[Dict[str, str]]]:
        """Prepare OpenAI API call with client, parameters, and contextualized messages."""
        client = self._get_openai_client()
        params = self._prepare_model_params(model, temperature, max_tokens)
        full_messages = self._build_messages_with_context(messages, **context_kwargs)
        
        api_params = {
            "messages": full_messages,
            **params
        }
        
        if additional_params:
            api_params.update(additional_params)
        
        return client, api_params, full_messages
    
    def _handle_tool_calls(
        self,
        response_message: Any,
        full_messages: List[Dict[str, str]]
    ) -> tuple[List[Dict[str, str]], bool]:
        """
        Handle tool calls from an OpenAI response.
        
        Args:
            response_message: The response message from OpenAI that may contain tool_calls
            full_messages: The current message history
            
        Returns:
            Tuple of (updated_messages, tools_were_called)
        """
        if not response_message.tool_calls:
            return full_messages, False

        full_messages.append(response_message)

        for tool_call in response_message.tool_calls:
            tool_result = self._execute_tool(tool_call)
            
            full_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, cls=AgentJSONEncoder)
            })
        
        return full_messages, True
    
    def _execute_tool(self, tool_call: Any) -> Dict[str, Any]:
        """Execute tool call with error handling.
        
        Tools get the session from the current context automatically using get_current_session().
        """
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        if tool_name not in self._tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self._tools.keys())
            }
        
        try:
            agent_name = self.__class__.__name__
            Logger.info(
                f"{agent_name} is using tool: {tool_name}",
                extra={"tool_args": tool_args}
            )
            
            result = self._tools[tool_name].execute(agent_instance=self, **tool_args)

            if hasattr(result, 'model_dump'):
                return result.model_dump()
            elif hasattr(result, 'dict'):
                return result.dict()
            
            return result
        except Exception as e:
            Logger.error(
                f"{agent_name} (ID: {agent_id}) tool execution failed for {tool_name}: {str(e)}"
            )
            return {
                "error": f"Tool execution failed: {str(e)}",
                "tool_name": tool_name
            }
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **context_kwargs
    ) -> str:
        """Generate text response with automatic tool execution support."""
        additional_params = {}
        if self._tools:
            additional_params["tools"] = [tool.to_openai_format() for tool in self._tools.values()]
            additional_params["tool_choice"] = "auto"

        client, api_params, full_messages = self._prepare_api_call(
            messages, model, temperature, max_tokens, additional_params, **context_kwargs
        )
        
        # Initial API call
        response = client.chat.completions.create(**api_params)
        response_message = response.choices[0].message

        full_messages, tools_were_called = self._handle_tool_calls(response_message, full_messages)
        
        if tools_were_called:
            # Make second API call with tool results
            api_params["messages"] = full_messages
            final_response = client.chat.completions.create(**api_params)
            content = final_response.choices[0].message.content
        else:
            content = response_message.content

        if content is None:
            Logger.error(f"OpenAI API returned None content for {self.__class__.__name__}")
            raise ValueError("AI response content is empty. Please try again.")
        
        return content
    
    def generate_structured_response(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **context_kwargs
    ) -> T:
        """
        Generate validated Pydantic response using OpenAI's structured output.
        
        Requires response_model to implement to_openai_schema() method.
        Supports tool calling - tools will be executed before generating the final structured response.
        """
        if not hasattr(response_model, 'to_openai_schema'):
            raise ValueError(
                f"Response model {response_model.__name__} must implement to_openai_schema() method"
            )

        additional_params = {
            "response_format": {
                "type": "json_schema",
                "json_schema": response_model.to_openai_schema()
            }
        }

        if self._tools:
            additional_params["tools"] = [tool.to_openai_format() for tool in self._tools.values()]
            additional_params["tool_choice"] = "auto"

        client, api_params, full_messages = self._prepare_api_call(
            messages, model, temperature, max_tokens, additional_params, **context_kwargs
        )

        response_content, response_data = None, None

        try:
            response = client.chat.completions.create(**api_params)
            response_message = response.choices[0].message

            full_messages, tools_were_called = self._handle_tool_calls(response_message, full_messages)
            
            if tools_were_called:
                # Make second API call with tool results to get structured response
                # Remove tools from the second call, only keep response_format
                api_params["messages"] = full_messages
                api_params.pop("tools", None)
                api_params.pop("tool_choice", None)
                
                final_response = client.chat.completions.create(**api_params)
                response_content = final_response.choices[0].message.content
            else:
                response_content = response_message.content

            response_data = json.loads(response_content)
            validated_response = response_model(**response_data)
            
            Logger.info(
                f"Successfully generated structured response for {response_model.__name__}"
            )
            return validated_response
            
        except json.JSONDecodeError as e:
            Logger.error(f"Failed to parse JSON response: {e}")
            Logger.error(f"Raw response: {response_content}")
            raise ValueError(f"Model returned invalid JSON: {e}")
            
        except ValidationError as e:
            Logger.error(f"Response validation failed: {e}")
            Logger.error(f"Response data: {response_data}")
            raise
            
        except Exception as e:
            Logger.error(f"Error generating structured response: {e}")
            raise
