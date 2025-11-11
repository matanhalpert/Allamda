"""
Learning Unit Assignment Service.

This module provides intelligent assignment of learning units to study sessions
based on student progress, duration constraints, and unit dependencies.
Supports both individual and group study sessions.
"""

from typing import List, Union, Optional
from dataclasses import dataclass

from src.database.decorators import with_db_session
from src.models.subject_models import Course, LearningUnit
from src.models.student_models import Student
from src.models.associations import LearningUnitStudent


@dataclass
class AssignmentResult:
    """Result of a learning unit assignment operation."""
    assigned_units: List[LearningUnit]
    total_duration: int  # in minutes
    students_affected: List[Student]
    reason: str  # Human-readable explanation


class LearningUnitAssignmentService:
    """
    Service for assigning learning units to study sessions.
    
    This service intelligently selects learning units based on:
    - Student progress (focuses on least advanced in groups)
    - Duration constraints (fits units within available time)
    - Unit dependencies (respects sequential order)
    """
    
    def __init__(self, default_duration_minutes: int = 60):
        """Initialize the service."""
        self.default_duration_minutes = default_duration_minutes
    
    def assign(
        self,
        students: Union[Student, List[Student]],
        course: Course,
        duration_minutes: Optional[int] = None
    ) -> AssignmentResult:
        """
        Assign learning units for a study session.
        
        Handles both individual and group sessions. For group sessions,
        ensures no student is left behind by selecting units aligned with
        the least advanced student in the group.
        """
        student_list = [students] if isinstance(students, Student) else students
        
        if not student_list:
            return AssignmentResult(
                assigned_units=[],
                total_duration=0,
                students_affected=[],
                reason="No students provided for session."
            )
        
        duration = duration_minutes or self.default_duration_minutes
        ordered_units = course.get_ordered_learning_units()
        
        if not ordered_units:
            return AssignmentResult(
                assigned_units=[],
                total_duration=0,
                students_affected=student_list,
                reason="No learning units found for this course."
            )

        student_ids = [s.id for s in student_list]
        first_incomplete_idx = self._find_first_incomplete_unit(
            ordered_units, student_ids
        )
        
        if first_incomplete_idx is None:
            completion_msg = (
                "All learning units are completed for this student."
                if len(student_list) == 1
                else "All learning units are completed for all students in the group."
            )
            return AssignmentResult(
                assigned_units=[],
                total_duration=0,
                students_affected=student_list,
                reason=completion_msg
            )

        assigned_units = self._assign_units_within_duration(
            ordered_units[first_incomplete_idx:], duration
        )
        
        total_duration = sum(unit.estimated_duration_minutes for unit in assigned_units)
        
        # Generate appropriate reason message
        if len(student_list) == 1:
            reason = (
                f"Assigned {len(assigned_units)} unit(s) starting from "
                f"'{assigned_units[0].name}' ({total_duration} minutes)."
            )
        else:
            reason = (
                f"Assigned {len(assigned_units)} unit(s) for {len(student_list)} students, "
                f"starting from '{assigned_units[0].name}' ({total_duration} minutes)."
            )
        
        return AssignmentResult(
            assigned_units=assigned_units,
            total_duration=total_duration,
            students_affected=student_list,
            reason=reason
        )

    @staticmethod
    def _find_first_incomplete_unit(
        ordered_units: List[LearningUnit],
        student_ids: List[int]
    ) -> Optional[int]:
        """
        Find the index of the first learning unit that is incomplete for any student.
        
        For multiple students, returns the earliest incomplete unit across all students
        (ensuring group sessions start at the least advanced point).
        """
        if not ordered_units:
            return None

        course_id = ordered_units[0].course_id

        progress_records = LearningUnitStudent.get_by(
            first=False, course_id=course_id, student_id=student_ids
        )

        progress_lookup = {
            (record.student_id, record.learning_unit_name): record.progress or 0.0
            for record in progress_records
        }
        
        # Find the first unit that any student hasn't completed
        for idx, unit in enumerate(ordered_units):
            for student_id in student_ids:
                progress = progress_lookup.get((student_id, unit.name), 0.0)
                if progress < 1.0:  # Not completed
                    return idx
        
        return None  # All units completed

    @staticmethod
    def _assign_units_within_duration(
        ordered_units: List[LearningUnit],
        duration_minutes: int
    ) -> List[LearningUnit]:
        """Select as many sequential units as possible within the duration constraint."""
        assigned = []
        remaining_time = duration_minutes
        
        for unit in ordered_units:
            if unit.estimated_duration_minutes <= remaining_time:
                assigned.append(unit)
                remaining_time -= unit.estimated_duration_minutes
            else:
                # Can't fit any more units
                break
        
        # Always assign at least one unit if available, even if it exceeds duration
        if not assigned and ordered_units:
            assigned.append(ordered_units[0])
        
        return assigned


@with_db_session
def assign_learning_units(
    students: Union[Student, List[Student]],
    course: Course,
    duration_minutes: Optional[int] = None
) -> AssignmentResult:
    """Quick convenience function to assign learning units."""
    service = LearningUnitAssignmentService()
    return service.assign(students, course, duration_minutes)
