"""
Scoring Factors for Course Prioritization.

This module contains all the scoring factors used to evaluate course priority.
Each factor is an independent, testable component that calculates a score
between 0 and 1, where higher values indicate higher priority.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from sqlalchemy.orm import Session

from src.models.subject_models import Course
from src.models.student_models import Student
from src.models.associations import CourseStudent
from src.enums import CourseState


# ============================================================================
# BASE CLASS
# ============================================================================


class ScoringFactor(ABC):
    """Abstract base class for course priority scoring factors."""
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize scoring factor.
        
        Args:
            weight: Factor weight (will be normalized by scorer)
        """
        self.weight = weight
    
    @abstractmethod
    def calculate(
        self, 
        course: Course, 
        course_student: CourseStudent, 
        student: Student
    ) -> float:
        """
        Calculate the score for this factor (0-1, higher = higher priority).
        
        Uses the current session from context via get_current_session().

        Returns:
            Score between 0 and 1
        """
        ...
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this factor."""
        ...


# ============================================================================
# CONCRETE IMPLEMENTATIONS
# ============================================================================


class CourseProgressFactor(ScoringFactor):
    """Score based on course progress (inverse: lower progress = higher priority)."""
    
    @property
    def name(self) -> str:
        return "course_progress"
    
    def calculate(
        self, 
        course: Course, 
        course_student: CourseStudent, 
        student: Student
    ) -> float:
        progress = float(course_student.progress or 0.0)
        return 1.0 - progress


class TestUrgencyFactor(ScoringFactor):
    """Score based on upcoming test urgency (closer date = higher priority)."""
    
    @property
    def name(self) -> str:
        return "test_urgency"
    
    def calculate(
        self, 
        course: Course, 
        course_student: CourseStudent, 
        student: Student
    ) -> float:
        upcoming_tests = student.get_upcoming_tests(course_id=course.id)
        
        if not upcoming_tests:
            return 0.0
        
        nearest_test = upcoming_tests[0]
        test_date = nearest_test['date']

        today = date.today()
        if isinstance(test_date, datetime):
            test_date = test_date.date()
        
        days_until_test: int = (test_date - today).days
        
        # Convert to score using exponential decay
        if days_until_test <= 0:
            return 1.0
        elif days_until_test <= 7:
            return 1.0 - (days_until_test / 14)  # 0 days = 1.0, 7 days = 0.5
        elif days_until_test <= 30:
            return 0.5 * (1.0 - (days_until_test - 7) / 46)  # 7 days = 0.5, 30 days = 0.25
        else:
            return 0.1  # Tests far away get low but non-zero priority


class TestPerformanceFactor(ScoringFactor):
    """Score based on historical test performance (lower grades = higher priority)."""
    
    @property
    def name(self) -> str:
        return "test_performance"
    
    def calculate(
        self, 
        course: Course, 
        course_student: CourseStudent, 
        student: Student
    ) -> float:
        avg_grade = student.get_average_grade(course_id=course.id)
        
        if avg_grade is None:
            return 0.5  # Neutral score when no test history
        
        avg_grade = float(avg_grade)
        
        # Convert to priority score (inverse relationship)
        if avg_grade < 60:
            return 1.0
        elif avg_grade < 75:
            return 0.9 - ((avg_grade - 60) / 150)
        elif avg_grade < 85:
            return 0.7 - ((avg_grade - 75) / 50)
        elif avg_grade < 95:
            return 0.5 - ((avg_grade - 85) / 50)
        else:
            return 0.1


class StudentFeedbackFactor(ScoringFactor):
    """Score based on student feedback from recent study sessions."""
    
    def __init__(self, weight: float = 1.0, days: int = 30):
        """
        Initialize feedback factor.
        
        Args:
            weight: Factor weight
            days: Number of days to look back for feedback
        """
        super().__init__(weight)
        self.days = days
    
    @property
    def name(self) -> str:
        return "student_feedback"
    
    def calculate(
        self, 
        course: Course, 
        course_student: CourseStudent, 
        student: Student
    ) -> float:
        feedback = student.get_average_feedback(
            course_id=course.id,
            days=self.days,
            include_home=True,
            include_school=True
        )
        
        if not feedback or feedback['overall'] is None:
            return 0.5
        
        overall_feedback = float(feedback['overall'])
        
        # Convert feedback to priority score (inverse relationship)
        if overall_feedback <= 4:
            return 1.0
        elif overall_feedback <= 6:
            return 0.8
        elif overall_feedback <= 7:
            return 0.6
        elif overall_feedback <= 8:
            return 0.4
        elif overall_feedback <= 9:
            return 0.2
        else:
            return 0.1


class CourseStateFactor(ScoringFactor):
    """Score based on course state (in-progress = higher priority)."""
    
    @property
    def name(self) -> str:
        return "course_state"
    
    def calculate(
        self, 
        course: Course, 
        course_student: CourseStudent, 
        student: Student
    ) -> float:
        state = course_student.state
        
        if state == CourseState.IN_PROGRESS:
            return 1.0
        elif state == CourseState.NOT_STARTED:
            return 0.6
        elif state == CourseState.COMPLETED:
            return 0.2
        else:
            return 0.5
