"""
AI Agents subpackage within models.

This subpackage contains all AI agent-related functionality organized by agent type:
- Base infrastructure: AIAgentMixin, AIAgentTool, agent_tool decorator
- Evaluator agent: Assessment and evaluation capabilities
- Teacher agent: Personalized instruction capabilities
- AIModel: Database model for tracking AI models
"""

from .base import AIAgentMixin, AIAgentTool, agent_tool
from .evaluator import Evaluator
from .teacher import Teacher
from .ai_model import AIModel

__all__ = [
    # Base infrastructure
    'AIAgentMixin',
    'AIAgentTool',
    'agent_tool',
    
    # Agent models
    'AIModel',
    'Evaluator',
    'Teacher',
]
