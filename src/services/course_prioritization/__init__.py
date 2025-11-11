"""
Course Prioritization Service.

A plugin-based, extensible course prioritization system that uses independent
scoring factors and flexible aggregation strategies to rank courses by
learning priority for individuals and groups.

Architecture:
    - Scoring Factors: Independent components that evaluate specific aspects
      (progress, test urgency, performance, feedback, state)
    - Course Scorer: Combines factors with configurable weights
    - Aggregation Strategies: Different approaches for group prioritization
    - Prioritization Service: Main API for ranking courses

Usage:
    from src.services.course_prioritization import (
        ScorerBuilder, PrioritizationService, CourseProgressFactor
    )
    
    # Build scorer and service
    scorer = ScorerBuilder().with_default_factors().build()
    service = PrioritizationService(scorer)
    
    # Rank courses for a student
    ranked = service.rank_for_student(student, session, include_scores=True)
"""

# Core components
from .scoring_factors import (
    ScoringFactor,
    CourseProgressFactor,
    TestUrgencyFactor,
    TestPerformanceFactor,
    StudentFeedbackFactor,
    CourseStateFactor,
)
from .aggregation_strategies import (
    AggregationStrategy,
    AverageAggregation,
    WeightedAverageAggregation,
    HighestNeedAggregation,
    MaxBasedAggregation,
    BalancedAggregation,
)
from .scorer import CourseScorer, ScoredCourse
from .service import PrioritizationService
from .builder import ScorerBuilder


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Core classes
    'PrioritizationService',
    'CourseScorer',
    'ScoredCourse',
    'ScorerBuilder',
    
    # Scoring factors
    'ScoringFactor',
    'CourseProgressFactor',
    'TestUrgencyFactor',
    'TestPerformanceFactor',
    'StudentFeedbackFactor',
    'CourseStateFactor',
    
    # Aggregation strategies
    'AggregationStrategy',
    'AverageAggregation',
    'WeightedAverageAggregation',
    'HighestNeedAggregation',
    'MaxBasedAggregation',
    'BalancedAggregation',
]
