"""
Pydantic schemas for Teacher agent tools.

This module defines type-safe parameter and response models for all Teacher tools.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# ===== Tool Parameter Schemas =====

class LearningUnitMasteryParams(BaseModel):
    """Parameters for getting student mastery of specific learning units."""
    
    student_id: int = Field(..., description="The ID of the student")
    course_id: int = Field(..., description="The ID of the course")
    learning_unit_names: list[str] = Field(
        ...,
        description="List of learning unit names to check mastery for (typically the units in current session)"
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
                "course_id": {
                    "type": "integer",
                    "description": "The ID of the course"
                },
                "learning_unit_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of learning unit names to check mastery for (typically the units in current session)"
                }
            },
            "required": ["student_id", "course_id", "learning_unit_names"]
        }


class QAResourcesParams(BaseModel):
    """Parameters for getting Q&A resources for a learning unit."""
    
    course_id: int = Field(..., description="The ID of the course")
    learning_unit_name: str = Field(..., description="The name of the learning unit")
    qa_type: Optional[str] = Field(
        None,
        description="Optional filter for type of Q&A (for_test, for_study)"
    )
    level: Optional[int] = Field(
        None,
        description="Optional difficulty level filter (1-4)"
    )
    
    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """Convert to OpenAI tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "course_id": {
                    "type": "integer",
                    "description": "The ID of the course"
                },
                "learning_unit_name": {
                    "type": "string",
                    "description": "The name of the learning unit"
                },
                "qa_type": {
                    "type": "string",
                    "description": "Optional filter for type of Q&A (for_test, for_study)",
                    "enum": ["for_test", "for_study"]
                },
                "level": {
                    "type": "integer",
                    "description": "Optional difficulty level filter (1-4)",
                    "minimum": 1,
                    "maximum": 4
                }
            },
            "required": ["course_id", "learning_unit_name"]
        }


class StudentTestHistoryParams(BaseModel):
    """Parameters for getting student test history."""
    
    student_id: int = Field(..., description="The ID of the student")
    course_id: Optional[int] = Field(
        None,
        description="Optional course ID to filter tests"
    )
    learning_unit_names: Optional[list[str]] = Field(
        None,
        description="Optional list of learning unit names to filter tests covering these specific units"
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
                "course_id": {
                    "type": "integer",
                    "description": "Optional course ID to filter tests"
                },
                "learning_unit_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of learning unit names to filter tests covering these specific units"
                }
            },
            "required": ["student_id"]
        }


class RecentStudentEvaluationsParams(BaseModel):
    """Parameters for getting recent student evaluations."""
    
    student_id: int = Field(..., description="The ID of the student")
    limit: int = Field(
        5,
        description="Maximum number of recent evaluations to retrieve (default: 5)"
    )
    evaluation_type: str = Field(
        "proficiency",
        description="Type of evaluation to retrieve (proficiency, investment)"
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
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of recent evaluations to retrieve (default: 5)",
                    "default": 5
                },
                "evaluation_type": {
                    "type": "string",
                    "description": "Type of evaluation to retrieve",
                    "enum": ["proficiency", "investment"],
                    "default": "proficiency"
                }
            },
            "required": ["student_id"]
        }


class PrerequisiteUnitsStatusParams(BaseModel):
    """Parameters for checking prerequisite learning unit status."""
    
    student_id: int = Field(..., description="The ID of the student")
    course_id: int = Field(..., description="The ID of the course")
    learning_unit_names: list[str] = Field(
        ...,
        description="List of learning unit names to check prerequisites for"
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
                "course_id": {
                    "type": "integer",
                    "description": "The ID of the course"
                },
                "learning_unit_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of learning unit names to check prerequisites for"
                }
            },
            "required": ["student_id", "course_id", "learning_unit_names"]
        }
