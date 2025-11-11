"""
Main Prioritization Service.

This module contains the PrioritizationService class which provides
a clean API for ranking courses by learning priority for individuals
or groups of students.
"""

from typing import List, Optional, Union

from src.database.session_context import get_current_session
from src.models.subject_models import Course
from src.models.student_models import Student
from src.models.associations import CourseStudent
from .scorer import CourseScorer, ScoredCourse
from .aggregation_strategies import AggregationStrategy, BalancedAggregation


class PrioritizationService:
    """
    Main service for course prioritization.
    
    This class provides a clean API for ranking courses by learning priority
    for individuals or groups, using configurable scoring factors and
    aggregation strategies.
    """
    
    def __init__(self, scorer: CourseScorer):
        """Initialize service with a course scorer."""
        self.scorer = scorer
    
    def rank_for_student(
        self,
        student: Student,
        courses: Optional[List[Course]] = None,
        include_scores: bool = False
    ) -> Union[List[Course], List[ScoredCourse]]:
        """Rank courses by priority for a single student."""
        session = get_current_session()
        
        if courses is None:
            course_data = student.get_courses()
            if not course_data:
                return []
            
            course_ids = [c['id'] for c in course_data]
            courses = Course.get_by(id=course_ids)

        scored_courses = []
        for course in courses:
            course_student = CourseStudent.get_by(first=True, student_id=student.id, course_id=course.id)
            
            if course_student:
                scored = self.scorer.score(
                    course, course_student, student,
                    include_breakdown=include_scores
                )
                
                if include_scores:
                    scored_courses.append(scored)
                else:
                    scored_courses.append((course, scored))

        if include_scores:
            scored_courses.sort(key=lambda x: x.score, reverse=True)
            return scored_courses
        else:
            scored_courses.sort(key=lambda x: x[1], reverse=True)
            return [course for course, _ in scored_courses]
    
    def rank_for_group(
        self,
        students: List[Student],
        strategy: Optional[AggregationStrategy] = None,
        include_scores: bool = False
    ) -> Union[List[Course], List[ScoredCourse]]:
        """Rank shared courses by priority for a group of students."""
        session = get_current_session()
        
        if not students:
            return []

        if strategy is None:
            strategy = BalancedAggregation()
        
        student_ids = [s.id for s in students]

        shared_courses = CourseStudent.get_shared_courses(student_ids)
        if not shared_courses:
            return []

        course_ids = [c.id for c in shared_courses]
        course_students = CourseStudent.get_by(student_id=student_ids, course_id=course_ids)

        cs_lookup = {
            (cs.student_id, cs.course_id): cs
            for cs in course_students
        }

        scored_courses = []
        for course in shared_courses:
            individual_scores = []
            
            for student in students:
                cs = cs_lookup[(student.id, course.id)]
                score = self.scorer.score(course, cs, student)
                individual_scores.append(score)

            group_score = strategy.aggregate(individual_scores, students)
            
            if include_scores:
                scored_courses.append(ScoredCourse(
                    course=course,
                    score=group_score,
                    factor_scores={}  # Could extend to show per-student breakdowns
                ))
            else:
                scored_courses.append((course, group_score))

        if include_scores:
            scored_courses.sort(key=lambda x: x.score, reverse=True)
            return scored_courses
        else:
            scored_courses.sort(key=lambda x: x[1], reverse=True)
            return [course for course, _ in scored_courses]
    
    def get_next_course(
        self,
        students: Union[Student, List[Student]],
        strategy: Optional[AggregationStrategy] = None
    ) -> Optional[Course]:
        """Get the single highest-priority course for the next study session."""
        if isinstance(students, Student):
            ranked = self.rank_for_student(students)
        else:
            ranked = self.rank_for_group(students, strategy)
        
        return ranked[0] if ranked else None
