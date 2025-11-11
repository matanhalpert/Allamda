"""
Aggregation Strategies for Group Course Prioritization.

This module contains strategies for aggregating individual student scores
(for a given course) into group scores. Each strategy implements a different approach to
balancing the needs of multiple students.
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from sqlalchemy.orm import Session

from src.models.student_models import Student


# ============================================================================
# BASE CLASS
# ============================================================================


class AggregationStrategy(ABC):
    """Abstract base class for group score aggregation strategies."""
    
    @abstractmethod
    def aggregate(
        self, 
        individual_scores: List[float],
        students: List[Student]
    ) -> float:
        """
        Aggregate individual student scores into a group score.

        Args:
            individual_scores: List of individual priority scores
            students: List of students (for context-aware strategies)
            
        Returns:
            Aggregated group score
        """
        ...
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this strategy."""
        ...


# ============================================================================
# CONCRETE IMPLEMENTATIONS
# ============================================================================


class AverageAggregation(AggregationStrategy):
    """Simple average of all students' scores (democratic approach)."""
    
    @property
    def name(self) -> str:
        return "average"
    
    def aggregate(
        self, 
        individual_scores: List[float],
        students: List[Student]
    ) -> float:
        if not individual_scores:
            return 0.0
        return sum(individual_scores) / len(individual_scores)


class WeightedAverageAggregation(AggregationStrategy):
    """Weighted average prioritizing struggling students."""
    
    @property
    def name(self) -> str:
        return "weighted_average"
    
    def aggregate(
        self, 
        individual_scores: List[float],
        students: List[Student]
    ) -> float:
        if not individual_scores:
            return 0.0
        
        weights = self._compute_student_weights(students)
        
        weighted_sum = sum(
            score * weights.get(student.id, 1.0)
            for score, student in zip(individual_scores, students)
        )
        total_weight = sum(weights.get(s.id, 1.0) for s in students)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def _compute_student_weights(
        students: List[Student]
    ) -> Dict[int, float]:
        """Compute performance-based weights (lower performance = higher weight)."""
        weights = {}
        
        for student in students:
            avg_grade = student.get_average_grade()
            
            if avg_grade is None:
                weights[student.id] = 1.0
            else:
                avg_grade = float(avg_grade)
                if avg_grade < 60:
                    weights[student.id] = 2.0
                elif avg_grade < 75:
                    weights[student.id] = 1.5
                elif avg_grade < 85:
                    weights[student.id] = 1.0
                else:
                    weights[student.id] = 0.7
        
        return weights


class HighestNeedAggregation(AggregationStrategy):
    """
    Prioritize based on the highest individual need ("no student left behind").
    
    Focuses on the student with the highest priority score (highest need),
    while considering group dynamics. Uses 70% of the maximum individual score
    plus 30% group-adjusted component to balance individual needs with class cohesion.
    """
    
    @property
    def name(self) -> str:
        return "highest_need"
    
    def aggregate(
        self, 
        individual_scores: List[float],
        students: List[Student]
    ) -> float:
        if not individual_scores:
            return 0.0
        
        max_score = max(individual_scores)
        avg_score = sum(individual_scores) / len(individual_scores)
        group_factor = avg_score / max_score if max_score > 0 else 0.5
        
        return 0.7 * max_score + 0.3 * max_score * group_factor


class MaxBasedAggregation(AggregationStrategy):
    """Prioritize maximum engagement potential."""
    
    @property
    def name(self) -> str:
        return "max_based"
    
    def aggregate(
        self, 
        individual_scores: List[float],
        students: List[Student]
    ) -> float:
        if not individual_scores:
            return 0.0
        return max(individual_scores)


class BalancedAggregation(AggregationStrategy):
    """Balanced: 60% average + 40% highest-need approach."""
    
    def __init__(self):
        self._average_strategy = AverageAggregation()
        self._highest_need_strategy = HighestNeedAggregation()
    
    @property
    def name(self) -> str:
        return "balanced"
    
    def aggregate(
        self, 
        individual_scores: List[float],
        students: List[Student]
    ) -> float:
        if not individual_scores:
            return 0.0
        
        avg_score = self._average_strategy.aggregate(individual_scores, students)
        highest_need_score = self._highest_need_strategy.aggregate(individual_scores, students)
        
        return 0.6 * avg_score + 0.4 * highest_need_score
