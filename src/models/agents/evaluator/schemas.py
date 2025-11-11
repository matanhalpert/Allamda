"""
Pydantic schemas for Evaluator agent tools.

This module defines type-safe parameter and response models for all Evaluator tools.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


# ===== Structured Output Schemas =====

class EvaluationResponse(BaseModel):
    """
    Structured response model for AI-generated evaluations.
    
    This model defines the format for evaluation outputs from the Evaluator agent,
    ensuring type-safe and validated responses.
    """
    
    evaluation_score: int = Field(
        ...,
        description="Numeric score from 1-10 representing the evaluation result",
        ge=1,
        le=10
    )
    evaluation_description: str = Field(
        ...,
        description="Detailed explanation and reasoning for the evaluation score",
        min_length=10
    )
    
    @field_validator('evaluation_score')
    @classmethod
    def validate_score_range(cls, v: int) -> int:
        """Ensure score is within valid range."""
        if not 1 <= v <= 10:
            raise ValueError(f"Score must be between 1 and 10, got {v}")
        return v
    
    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """
        Convert to OpenAI structured output schema format.
        
        Returns JSON schema for use with OpenAI's response_format parameter.
        """
        return {
            "name": "evaluation_response",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "evaluation_score": {
                        "type": "integer",
                        "description": "Numeric score from 1-10 representing the evaluation result",
                        "minimum": 1,
                        "maximum": 10
                    },
                    "evaluation_description": {
                        "type": "string",
                        "description": "Detailed explanation and reasoning for the evaluation score"
                    }
                },
                "required": ["evaluation_score", "evaluation_description"],
                "additionalProperties": False
            }
        }


# ===== Tool Parameter Schemas =====

class StudentTestPerformanceParams(BaseModel):
    """Parameters for getting student test performance data."""
    
    student_id: int = Field(..., description="The ID of the student to evaluate")
    subject_name: Optional[str] = Field(
        None,
        description="Optional subject filter (math, science, english, history, art)"
    )
    
    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """Convert to OpenAI tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "integer",
                    "description": "The ID of the student to evaluate"
                },
                "subject_name": {
                    "type": "string",
                    "description": "Optional subject filter (math, science, english, history, art)",
                    "enum": ["math", "science", "english", "history", "art"]
                }
            },
            "required": ["student_id"]
        }


class StudentEvaluationHistoryParams(BaseModel):
    """Parameters for getting student evaluation history."""
    
    student_id: int = Field(..., description="The ID of the student")
    evaluation_type: str = Field(
        ...,
        description="Type of evaluation to retrieve (proficiency, investment, social)"
    )
    limit: int = Field(
        5,
        description="Maximum number of recent evaluations to retrieve"
    )
    
    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """Convert to OpenAI tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "integer",
                    "description": "The ID of the student"
                },
                "evaluation_type": {
                    "type": "string",
                    "description": "Type of evaluation to retrieve (proficiency, investment, social)",
                    "enum": ["proficiency", "investment", "social"]
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of recent evaluations to retrieve (default: 5)",
                    "default": 5
                }
            },
            "required": ["student_id", "evaluation_type"]
        }


class SessionPauseStatisticsParams(BaseModel):
    """Parameters for getting session pause statistics."""
    
    session_id: int = Field(..., description="The ID of the study session to analyze")
    session_type: str = Field(
        ...,
        description="Type of study session (home or school)",
        pattern="^(home|school)$"
    )
    
    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """Convert to OpenAI tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "integer",
                    "description": "The ID of the study session to analyze"
                },
                "session_type": {
                    "type": "string",
                    "description": "Type of study session (home or school)",
                    "enum": ["home", "school"]
                }
            },
            "required": ["session_id", "session_type"]
        }


class SessionContextParams(BaseModel):
    """Parameters for getting study session context (course, learning units)."""
    
    session_id: int = Field(..., description="The ID of the study session")
    session_type: str = Field(
        ...,
        description="Type of study session (home or school)",
        pattern="^(home|school)$"
    )
    
    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """Convert to OpenAI tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "integer",
                    "description": "The ID of the study session"
                },
                "session_type": {
                    "type": "string",
                    "description": "Type of study session (home or school)",
                    "enum": ["home", "school"]
                }
            },
            "required": ["session_id", "session_type"]
        }


class SessionMessageStatisticsParams(BaseModel):
    """Parameters for getting session message statistics."""
    
    session_id: int = Field(..., description="The ID of the study session to analyze")
    session_type: str = Field(
        ...,
        description="Type of study session (home or school)",
        pattern="^(home|school)$"
    )
    
    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """Convert to OpenAI tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "integer",
                    "description": "The ID of the study session to analyze"
                },
                "session_type": {
                    "type": "string",
                    "description": "Type of study session (home or school)",
                    "enum": ["home", "school"]
                }
            },
            "required": ["session_id", "session_type"]
        }
