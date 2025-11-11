"""
Association/Junction tables for many-to-many relationships.

This module contains all association tables that link entities together.
"""

from sqlalchemy import (
    Column, Date, Enum, ForeignKey, ForeignKeyConstraint,
    Integer, String, Float, CheckConstraint
)
from sqlalchemy.orm import relationship

from .base import Base, StudySessionStudent, LearningUnitsStudySession, EvaluationStudySession
from src.database.session_context import get_current_session
from src.enums import GradeLevel, SubjectName, Region, CourseState, TestStatus


# User-related associations
class ParentStudent(Base):
    __tablename__ = 'parents_students'

    parent_id = Column(Integer, ForeignKey('parents.id'), primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)


class ClassStudent(Base):
    __tablename__ = 'classes_students'

    school_id = Column(Integer, primary_key=True)
    class_year = Column(Integer, primary_key=True)
    class_grade_level = Column(Enum(GradeLevel), primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['school_id', 'class_year', 'class_grade_level'],
                             ['classes.school_id', 'classes.year', 'classes.grade_level']),
    )


class ClassClassManager(Base):
    __tablename__ = 'classess_class_managers'

    school_id = Column(Integer, primary_key=True)
    class_year = Column(Integer, primary_key=True)
    class_grade_level = Column(Enum(GradeLevel), primary_key=True)
    class_manager_id = Column(Integer, ForeignKey('class_managers.id'), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['school_id', 'class_year', 'class_grade_level'],
                             ['classes.school_id', 'classes.year', 'classes.grade_level']),
    )


class TabletStudent(Base):
    __tablename__ = 'tablets_students'

    serial_number = Column(String(50), ForeignKey('tablets.serial_number'), primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    # Relationships
    tablet = relationship("Tablet", back_populates="students")
    student = relationship("Student", back_populates="tablets")


# Subject-related associations
class SubjectRegionalSupervisor(Base):
    __tablename__ = 'subjects_regional_supervisors'

    subject_name = Column(Enum(SubjectName), primary_key=True)
    subject_year = Column(Integer, primary_key=True)
    subject_region = Column(Enum(Region), primary_key=True)
    regional_supervisor_id = Column(Integer, ForeignKey('regional_supervisors.id'), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['subject_name', 'subject_region', 'subject_year'],
                             ['subjects.name', 'subjects.region', 'subjects.year']),
    )


# Course-related associations
class CourseStudent(Base):
    __tablename__ = 'courses_students'

    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    state = Column(Enum(CourseState), nullable=False)
    progress = Column(Float, nullable=True)
    
    @classmethod
    def get_shared_courses(cls, student_ids: list[int]):
        """Get courses where ALL students are enrolled."""
        from sqlalchemy import func
        from .subject_models import Course
        
        session = get_current_session()
        num_students = len(student_ids)
        
        shared_course_ids = (
            session.query(cls.course_id)
            .filter(cls.student_id.in_(student_ids))
            .group_by(cls.course_id)
            .having(func.count(func.distinct(cls.student_id)) == num_students)
            .all()
        )
        
        if not shared_course_ids:
            return []
        
        shared_course_ids = [course_id for (course_id,) in shared_course_ids]

        return (
            session.query(Course)
            .filter(Course.id.in_(shared_course_ids))
            .all()
        )


class CoursePrerequisite(Base):
    __tablename__ = 'courses_prerequisites'

    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    prerequisite_course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)

    # Relationships
    course = relationship("Course", foreign_keys=[course_id], back_populates="prerequisites")
    prerequisite_course = relationship("Course", foreign_keys=[prerequisite_course_id],
                                       back_populates="prerequisite_for")


class LearningUnitStudent(Base):
    __tablename__ = 'learning_units_students'

    course_id = Column(Integer, primary_key=True)
    learning_unit_name = Column(String(100), primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    state = Column(Enum(CourseState), nullable=False)
    progress = Column(Float, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(['course_id', 'learning_unit_name'],
                             ['learning_units.course_id', 'learning_units.name']),
    )

    # Relationships
    learning_unit = relationship("LearningUnit", back_populates="students")
    student = relationship("Student", back_populates="learning_units")


class TestStudent(Base):
    __tablename__ = 'tests_students'

    course_id = Column(Integer, primary_key=True)
    test_name = Column(String(100), primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    teacher_ai_model_id = Column(Integer)  # Part of composite FK to Teacher
    teacher_name = Column(String(100))  # Part of composite FK to Teacher
    status = Column(Enum(TestStatus), nullable=False)
    date = Column(Date, nullable=True)
    final_grade = Column(Integer, CheckConstraint('final_grade >= 0 AND final_grade <= 100'), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(['course_id', 'test_name'],
                             ['tests.course_id', 'tests.name']),
        ForeignKeyConstraint(['teacher_ai_model_id', 'teacher_name'],
                             ['teachers.ai_model_id', 'teachers.name']),
    )

    # Relationships
    test = relationship("Test", back_populates="students")
    student = relationship("Student", back_populates="tests")
    teacher = relationship("Teacher", foreign_keys=[teacher_ai_model_id, teacher_name], back_populates="test_students")


class TestLearningUnit(Base):
    __tablename__ = 'tests_learning_units'

    course_id = Column(Integer, primary_key=True)
    test_name = Column(String(100), primary_key=True)
    learning_unit_name = Column(String(100), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['course_id', 'test_name'],
                             ['tests.course_id', 'tests.name']),
        ForeignKeyConstraint(['course_id', 'learning_unit_name'],
                             ['learning_units.course_id', 'learning_units.name']),
    )


# Study session-student associations
class HomeHoursStudySessionStudent(StudySessionStudent):
    __tablename__ = 'home_sessions_students'

    home_hours_study_session_id = Column(Integer, ForeignKey('home_hours_study_sessions.id'), primary_key=True)


class SchoolHoursStudySessionStudent(StudySessionStudent):
    __tablename__ = 'school_sessions_students'

    school_hours_study_session_id = Column(Integer, ForeignKey('school_hours_study_sessions.id'), primary_key=True)


# Learning unit-study session associations
class LearningUnitsHomeHoursStudySession(LearningUnitsStudySession):
    __tablename__ = 'learning_units_home_sessions'

    home_hours_study_session_id = Column(Integer, ForeignKey('home_hours_study_sessions.id'), primary_key=True)


class LearningUnitsSchoolHoursStudySession(LearningUnitsStudySession):
    __tablename__ = 'learning_units_school_sessions'

    school_hours_study_session_id = Column(Integer, ForeignKey('school_hours_study_sessions.id'), primary_key=True)


# Evaluation-study session associations
class SessionalProficiencyEvaluationHomeHoursStudySession(EvaluationStudySession):
    __tablename__ = 'sessional_prof_eval_home_sessions'

    sessional_proficiency_evaluation_id = Column(Integer, ForeignKey('sessional_proficiency_evaluations.id'),
                                                 primary_key=True)
    home_hours_study_session_id = Column(Integer, ForeignKey('home_hours_study_sessions.id'), primary_key=True)


class SessionalInvestmentEvaluationHomeHoursStudySession(EvaluationStudySession):
    __tablename__ = 'sessional_inv_eval_home_sessions'

    sessional_investment_evaluation_id = Column(Integer, ForeignKey('sessional_invesment_evaluations.id'),
                                                primary_key=True)
    home_hours_study_session_id = Column(Integer, ForeignKey('home_hours_study_sessions.id'), primary_key=True)


class SessionalProficiencyEvaluationSchoolHoursStudySession(EvaluationStudySession):
    __tablename__ = 'sessional_prof_eval_school_sessions'

    sessional_proficiency_evaluation_id = Column(Integer, ForeignKey('sessional_proficiency_evaluations.id'),
                                                 primary_key=True)
    school_hours_study_session_id = Column(Integer, ForeignKey('school_hours_study_sessions.id'), primary_key=True)


class SessionalInvestmentEvaluationSchoolHoursStudySession(EvaluationStudySession):
    __tablename__ = 'sessional_inv_eval_school_sessions'

    sessional_investment_evaluation_id = Column(Integer, ForeignKey('sessional_invesment_evaluations.id'),
                                                primary_key=True)
    school_hours_study_session_id = Column(Integer, ForeignKey('school_hours_study_sessions.id'), primary_key=True)


class SessionalSocialEvaluationSchoolHoursStudySession(EvaluationStudySession):
    __tablename__ = 'sessional_soc_eval_school_sessions'

    sessional_social_evaluation_id = Column(Integer, ForeignKey('sessional_social_evaluations.id'), primary_key=True)
    school_hours_study_session_id = Column(Integer, ForeignKey('school_hours_study_sessions.id'), primary_key=True)
