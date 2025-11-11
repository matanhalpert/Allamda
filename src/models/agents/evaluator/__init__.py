"""
Evaluator Agent.

This subpackage contains the Evaluator agent implementation:
- Agent class with evaluation context
- Tool implementations for assessment
- Pydantic schemas for type safety
"""

from .agent import Evaluator
from .schemas import EvaluationResponse

__all__ = ['Evaluator', 'EvaluationResponse']
