"""
Subject-related models.

This module contains models for Subject, Course, LearningUnit, QA, and Test entities.
"""

from sqlalchemy import (
    Column, Enum, ForeignKey, ForeignKeyConstraint, Integer, String,
    Text, Float, CheckConstraint
)
from sqlalchemy.orm import relationship

from .base import Base
from src.database.session_context import get_current_session
from src.enums import (
    SubjectName, Region, GradeLevel, CourseType, 
    LearningUnitType, QAType, TestType
)


class Subject(Base):
    __tablename__ = 'subjects'

    name = Column(Enum(SubjectName), primary_key=True)
    region = Column(Enum(Region), primary_key=True)
    year = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)

    # Relationships
    courses = relationship("Course", back_populates="subject")
    teachers = relationship("Teacher", back_populates="subject")
    regional_supervisors = relationship(
        "RegionalSupervisor", secondary="subjects_regional_supervisors", back_populates="subjects"
    )
    quarter_proficiency_evaluations = relationship("QuarterProficiencyEvaluation", back_populates="subject")
    quarter_investment_evaluations = relationship("QuarterInvestmentEvaluation", back_populates="subject")


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    grade_level = Column(Enum(GradeLevel), nullable=False)
    type = Column(Enum(CourseType), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, CheckConstraint('level >= 1 AND level <= 5'), nullable=True)
    subject_name = Column(Enum(SubjectName), ForeignKey('subjects.name'), nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="courses")
    learning_units = relationship("LearningUnit", back_populates="course")
    tests = relationship("Test", back_populates="course")
    students = relationship("Student", secondary="courses_students", back_populates="courses")
    prerequisites = relationship("CoursePrerequisite", foreign_keys="CoursePrerequisite.course_id",
                                 back_populates="course")
    prerequisite_for = relationship("CoursePrerequisite", foreign_keys="CoursePrerequisite.prerequisite_course_id",
                                    back_populates="prerequisite_course")

    def get_ordered_learning_units(self) -> list['LearningUnit']:
        """Get all learning units for this course in their proper sequential order."""
        units = LearningUnit.get_by(course_id=self.id)
        
        if not units:
            return []

        units_dict = {unit.name: unit for unit in units}

        first_unit = None
        for unit in units:
            if not unit.previous_learning_unit or unit.previous_learning_unit not in units_dict:
                first_unit = unit
                break

        if not first_unit:
            # Fallback to alphabetical if no clear start
            return sorted(units, key=lambda u: u.name)
        
        # Follow the chain
        ordered = []
        current = first_unit
        visited = set()
        
        while current and current.name not in visited:
            ordered.append(current)
            visited.add(current.name)
            
            next_name = current.next_learning_unit
            if next_name and next_name in units_dict:
                current = units_dict[next_name]
            else:
                current = None
        
        # Add any orphaned units
        remaining = [u for u in units if u.name not in visited]
        ordered.extend(sorted(remaining, key=lambda u: u.name))
        
        return ordered


class LearningUnit(Base):
    __tablename__ = 'learning_units'

    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    name = Column(String(100), primary_key=True)
    type = Column(Enum(LearningUnitType), nullable=False)
    weight = Column(Float, CheckConstraint('weight >= 0 AND weight <= 1'), nullable=False)
    description = Column(Text, nullable=True)
    previous_learning_unit = Column(String(100), nullable=True)
    next_learning_unit = Column(String(100), nullable=True)
    estimated_duration_minutes = Column(Integer, CheckConstraint('estimated_duration_minutes > 0'), nullable=False)

    # Relationships
    course = relationship("Course", back_populates="learning_units")
    students = relationship("LearningUnitStudent", back_populates="learning_unit")
    home_study_sessions = relationship("HomeHoursStudySession", secondary="learning_units_home_sessions",
                                       back_populates="learning_units")
    school_study_sessions = relationship("SchoolHoursStudySession", secondary="learning_units_school_sessions",
                                         back_populates="learning_units")
    tests = relationship("Test", secondary="tests_learning_units", back_populates="learning_units")
    qas = relationship("QA", back_populates="learning_unit")


class QA(Base):
    __tablename__ = 'qas'

    course_id = Column(Integer, primary_key=True)
    learning_unit_name = Column(String(100), primary_key=True)
    question = Column(String(500), primary_key=True)
    answer = Column(Text, nullable=False)
    type = Column(Enum(QAType), nullable=False)
    level = Column(Integer, CheckConstraint('level >= 1 AND level <= 4'), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(['course_id', 'learning_unit_name'],
                             ['learning_units.course_id', 'learning_units.name']),
    )

    # Relationships
    learning_unit = relationship("LearningUnit", back_populates="qas")


class Test(Base):
    __tablename__ = 'tests'

    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    name = Column(String(100), primary_key=True)
    type = Column(Enum(TestType), nullable=False)
    link = Column(String(500), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="tests")
    students = relationship("TestStudent", back_populates="test")
    learning_units = relationship("LearningUnit", secondary="tests_learning_units", back_populates="tests")
