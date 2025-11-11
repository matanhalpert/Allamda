"""
User-related models.

This module contains all user types except Student (Parent, SchoolManager, etc.)
and related entities like Phone and Address.

Note: Student model has been moved to student_models.py due to its size and complexity.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session
from typing import Optional, List, Dict, TYPE_CHECKING

from .base import Base, User

if TYPE_CHECKING:
    from .school_models import School, Class
    from .student_models import Student


class Parent(User):
    __tablename__ = 'parents'

    # Relationships
    students = relationship("Student", secondary="parents_students", back_populates="parents")

    def has_child(self, student: 'Student') -> bool:
        return student in self.students

    def get_children(self) -> List[Dict]:
        """Get all children (students) for this parent with their basic information and metrics."""
        children_data = []
        for student in self.students:
            avg_grade = student.get_average_grade()
            attendance = student.get_attendance_behavior(days=365)
            school_attendance = attendance['school_hours']['attendance_rate']
            courses = student.get_courses()
            total_courses = len(courses)

            if courses:
                overall_progress = sum(course['progress'] for course in courses) / total_courses
            else:
                overall_progress = 0

            student_dict = student.to_dict()
            student_dict.update({
                'average_grade': avg_grade,
                'school_attendance': school_attendance,
                'total_courses': total_courses,
                'overall_progress': round(overall_progress, 1),
                'school_id': student.school_id
            })
            children_data.append(student_dict)

        return children_data


class SchoolManager(User):
    __tablename__ = 'school_managers'

    employment_year = Column(Integer, nullable=False)

    # Relationships
    schools = relationship("School", back_populates="school_manager")

    @property
    def assigned_to_school(self) -> bool:
        return len(self.schools) > 0

    def get_school(self) -> Optional['School']:
        return self.schools[0] if self.assigned_to_school else None


class ClassManager(User):
    __tablename__ = 'class_managers'

    employment_year = Column(Integer, nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)

    # Relationships
    school = relationship("School", back_populates="class_managers")
    classes = relationship("Class", secondary="classess_class_managers", back_populates="class_managers")
    school_study_sessions = relationship("SchoolHoursStudySession", back_populates="class_manager")
    sessional_investment_evaluations = relationship("SessionalInvestmentEvaluation", back_populates="class_manager")
    quarter_investment_evaluations = relationship("QuarterInvestmentEvaluation", back_populates="class_manager")
    sessional_social_evaluations = relationship("SessionalSocialEvaluation", back_populates="class_manager")
    quarter_social_evaluations = relationship("QuarterSocialEvaluation", back_populates="class_manager")

    @property
    def assigned_to_class(self) -> bool:
        return len(self.classes) > 0

    def get_class(self) -> Optional['Class']:
        return self.classes[0] if self.assigned_to_class else None

    def manage(self, instance) -> bool:
        """Checks whether the class manager manage the given student or class."""
        from .school_models import Class
        from .student_models import Student

        if not self.assigned_to_class:
            return False

        if isinstance(instance, Class):
            return instance == self.get_class()
        elif isinstance(instance, Student):
            return instance in self.get_class().students
        else:
            raise ValueError("Class Manager can manage only classes or students.")


class RegionalSupervisor(User):
    __tablename__ = 'regional_supervisors'

    employment_year = Column(Integer, nullable=False)

    # Relationships
    subjects = relationship("Subject", secondary="subjects_regional_supervisors", back_populates="regional_supervisors")


class Phone(Base):
    __tablename__ = 'phones'

    user_id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), primary_key=True)


class Address(Base):
    __tablename__ = 'addresses'

    user_id = Column(Integer, primary_key=True)
    country = Column(String(50), primary_key=True)
    city = Column(String(50), primary_key=True)
    street = Column(String(100), primary_key=True)
    num = Column(String(10), primary_key=True)
