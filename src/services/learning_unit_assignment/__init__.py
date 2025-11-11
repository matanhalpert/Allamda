"""
Learning Unit Assignment Service Module.

This module provides intelligent assignment of learning units to study sessions.
"""

from .service import (
    LearningUnitAssignmentService,
    AssignmentResult,
    assign_learning_units,
)

__all__ = [
    'LearningUnitAssignmentService',
    'AssignmentResult',
    'assign_learning_units',
]
