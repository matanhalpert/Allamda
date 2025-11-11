"""
Builder for Creating Configured CourseScorer Instances.

This module provides a builder pattern for easy construction of
CourseScorer objects with custom or default configurations.
"""

from typing import List

from .scorer import CourseScorer
from .scoring_factors import (
    ScoringFactor,
    CourseProgressFactor,
    TestUrgencyFactor,
    TestPerformanceFactor,
    StudentFeedbackFactor,
    CourseStateFactor,
)


class ScorerBuilder:
    """Builder for creating configured CourseScorer instances."""
    
    def __init__(self):
        self.factors: List[ScoringFactor] = []
    
    def with_default_factors(self) -> 'ScorerBuilder':
        """Add all default scoring factors with standard weights."""
        self.factors = [
            CourseProgressFactor(weight=0.30),
            TestUrgencyFactor(weight=0.25),
            TestPerformanceFactor(weight=0.20),
            StudentFeedbackFactor(weight=0.15),
            CourseStateFactor(weight=0.10),
        ]
        return self
    
    def add_factor(self, factor: ScoringFactor) -> 'ScorerBuilder':
        """Add a custom scoring factor."""
        self.factors.append(factor)
        return self
    
    def build(self) -> CourseScorer:
        """Build the CourseScorer."""
        if not self.factors:
            raise ValueError("Cannot build scorer without any factors")
        return CourseScorer(self.factors)
