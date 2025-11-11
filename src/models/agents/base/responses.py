"""
Standardized response types for agent tools.

This module provides Pydantic models for consistent tool responses and error handling.
"""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field


T = TypeVar('T')


class ToolError(BaseModel):
    """Standardized error response for tool failures."""
    
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error (e.g., 'not_found', 'unavailable')")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional error context")


class ToolResponse(BaseModel, Generic[T]):
    """
    Generic standardized response format for agent tools.
    
    Provides consistent structure for success/failure responses with optional data and metadata.
    """
    
    success: bool = Field(..., description="Whether the tool execution succeeded")
    data: Optional[T] = Field(None, description="Tool result data if successful")
    error: Optional[ToolError] = Field(None, description="Error details if failed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @classmethod
    def success_response(cls, data: T, metadata: dict[str, Any] = None) -> 'ToolResponse[T]':
        """Create a successful tool response."""
        return cls(
            success=True,
            data=data,
            error=None,
            metadata=metadata or {}
        )
    
    @classmethod
    def error_response(
        cls,
        error_message: str,
        error_type: str = "error",
        context: dict[str, Any] = None,
        metadata: dict[str, Any] = None
    ) -> 'ToolResponse[T]':
        """Create an error tool response."""
        return cls(
            success=False,
            data=None,
            error=ToolError(
                error=error_message,
                error_type=error_type,
                context=context or {}
            ),
            metadata=metadata or {}
        )
