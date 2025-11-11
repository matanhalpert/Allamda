"""
AIModel database model.

This module contains the AIModel class which represents the underlying AI models
used by agents (e.g., GPT-4, Claude, etc.)
"""

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from ..base import Base
from src.enums import AIModelStatus


class AIModel(Base):
    """
    Represents an AI model that can be used by agents.
    
    This model tracks the name, version, and status of available AI models
    (e.g., gpt-4o-mini, gpt-4, claude-3, etc.)
    """
    
    __tablename__ = 'ai_models'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    status = Column(Enum(AIModelStatus), nullable=False)

    # Relationships
    evaluators = relationship("Evaluator", back_populates="ai_model")
    teachers = relationship("Teacher", back_populates="ai_model")

