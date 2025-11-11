"""
Course Scorer - Computes priority scores using configurable factors.

This module contains the CourseScorer class which combines multiple
scoring factors to produce an overall priority score for courses.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Union
from sqlalchemy.orm import Session

from src.models.subject_models import Course
from src.models.student_models import Student
from src.models.associations import CourseStudent
from .scoring_factors import ScoringFactor


@dataclass
class ScoredCourse:
    """Container for a course with its priority score and factor breakdown."""
    course: Course
    score: float
    factor_scores: Dict[str, float] = field(default_factory=dict)


class CourseScorer:
    """
    Computes priority scores for courses using a configurable set of factors.
    
    This class uses composition - it's built from independent scoring factors
    that can be easily added, removed, or swapped without modifying this class.
    """
    
    def __init__(self, factors: List[ScoringFactor]):
        """Initialize scorer with a list of scoring factors."""
        self.factors = factors
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Normalize factor weights to sum to 1.0."""
        total_weight = sum(f.weight for f in self.factors)
        
        if total_weight == 0:
            raise ValueError("Total weight of factors cannot be zero")
        
        for factor in self.factors:
            factor.weight = factor.weight / total_weight
    
    def score(
        self,
        course: Course,
        course_student: CourseStudent,
        student: Student,
        include_breakdown: bool = False
    ) -> Union[float, ScoredCourse]:
        """Calculate the overall priority score for a course."""
        total_score = 0.0
        factor_scores = {}
        
        for factor in self.factors:
            factor_score = factor.calculate(course, course_student, student)
            weighted_score = factor_score * factor.weight
            total_score += weighted_score
            factor_scores[factor.name] = factor_score
        
        if include_breakdown:
            return ScoredCourse(
                course=course,
                score=total_score,
                factor_scores=factor_scores
            )
        
        return total_score
