"""
Student model.

This module contains the Student model which was separated from user_models.py
due to its size and complexity.
"""

from sqlalchemy import Column, Enum, ForeignKey, Integer, func, desc, cast
from sqlalchemy.orm import relationship, Query
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from .base import User
from src.database.session_context import get_current_session

from src.enums import (
    LearningStyle, RoutineStyle, CollaborationStyle,
    SubjectName, GradeLevel, CourseState, TestStatus, EvaluationType
)


class Student(User):
    __tablename__ = 'students'

    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    learning_style = Column(Enum(LearningStyle), nullable=True)
    routine_style = Column(Enum(RoutineStyle), nullable=True)
    collaboration_style = Column(Enum(CollaborationStyle), nullable=True)

    # Relationships
    school = relationship("School", back_populates="students")
    parents = relationship("Parent", secondary="parents_students", back_populates="students")
    classes = relationship("Class", secondary="classes_students", back_populates="students")
    tablets = relationship("TabletStudent", back_populates="student")
    courses = relationship("Course", secondary="courses_students", back_populates="students")
    learning_units = relationship("LearningUnitStudent", back_populates="student")
    tests = relationship("TestStudent", back_populates="student")
    home_study_sessions = relationship("HomeHoursStudySessionStudent", back_populates="student")
    school_study_sessions = relationship("SchoolHoursStudySessionStudent", back_populates="student")
    sessional_proficiency_evaluations = relationship("SessionalProficiencyEvaluation", back_populates="student")
    quarter_proficiency_evaluations = relationship("QuarterProficiencyEvaluation", back_populates="student")
    sessional_investment_evaluations = relationship("SessionalInvestmentEvaluation", back_populates="student")
    quarter_investment_evaluations = relationship("QuarterInvestmentEvaluation", back_populates="student")
    sessional_social_evaluations = relationship("SessionalSocialEvaluation", back_populates="student")
    quarter_social_evaluations = relationship("QuarterSocialEvaluation", back_populates="student")
    sent_messages = relationship("Message", back_populates="student")

    def get_learning_profile(self) -> Dict[str, str]:
        """Get student's learning style profile."""
        return {
            'learning_style': self.learning_style,
            'routine_style': self.routine_style,
            'collaboration_style': self.collaboration_style
        }

    def to_dict(self) -> dict:
        student_dict: dict = super().to_dict()
        student_dict.update(self.get_learning_profile())
        return student_dict

    def is_enrolled(self, course_id: int) -> bool:
        """Check if student is enrolled in a specific course."""
        from .associations import CourseStudent
        enrollment = CourseStudent.get_by(first=True, student_id=self.id, course_id=course_id)
        return enrollment is not None

    def get_courses(self, course_id: int = None, subject_filter: SubjectName = None,
                    grade_level_filter: GradeLevel = None, state_filter: CourseState = None,
                    include_learning_units: bool = False, include_tests: bool = False
                    ) -> Optional[list[dict]]:
        """
        Get course(s) for this student with progress and optional detailed information.
        
        This unified method handles both listing multiple courses and fetching detailed 
        information for a single course.
        """
        from .subject_models import Course
        from .associations import CourseStudent

        session = get_current_session()
        query: Query = session.query(Course).add_entity(CourseStudent)

        # Apply Course filters
        if course_id:
            query = query.filter(Course.id == course_id)
        if subject_filter:
            query = query.filter(Course.subject_name == subject_filter)
        if grade_level_filter:
            query = query.filter(Course.grade_level == grade_level_filter)

        # Join with CourseStudent and filter by student
        query = query.join(CourseStudent, Course.id == CourseStudent.course_id).filter(
            CourseStudent.student_id == self.id)

        if state_filter:
            query = query.filter(CourseStudent.state == state_filter)

        if course_id:
            result = query.first()
            if not result:
                return None
            results = [result]
        else:
            results = query.all()

        # Process results
        courses_data = []
        for course, course_student in results:
            progress_percentage = (course_student.progress * 100) if course_student.progress else 0

            course_dict = course.to_dict()
            course_dict.update({
                'state': course_student.state,
                'progress': round(progress_percentage, 1)  # Round to 1 decimal place
            })

            if course_id:
                if include_learning_units:
                    course_dict['learning_units'] = self.get_learning_units_progress(course_id=course.id)

                if include_tests:
                    course_dict['upcoming_tests'] = self.get_upcoming_tests(course_id=course.id)
                    course_dict['test_history'] = self.get_test_history(course_id=course.id)

            courses_data.append(course_dict)

        # Return single course dict or list based on query type
        if course_id:
            return courses_data[0] if courses_data else None
        return courses_data

    def _get_tests(self, status_filters: List[TestStatus], subject_filter: SubjectName = None,
                   course_id: int = None, include_final_grade: bool = False
                   ) -> List[Dict[str, str]]:
        """Internal method to get tests for this student with flexible status filtering."""
        from .subject_models import Test, Course
        from .associations import TestStudent

        session = get_current_session()
        query: Query = session.query(Test).add_entity(TestStudent).add_entity(Course)

        if course_id:
            query = query.filter(Test.course_id == course_id)

        query = query.join(
            TestStudent,
            (Test.course_id == TestStudent.course_id) & (Test.name == TestStudent.test_name)
        )

        query = query.join(Course, Test.course_id == Course.id)
        if subject_filter:
            query = query.filter(Course.subject_name == subject_filter)

        query = query.filter(
            TestStudent.student_id == self.id,
            TestStudent.status.in_(status_filters)
        )

        results = query.all()

        tests = []
        for test, test_student, course in results:
            test_dict = test.to_dict()
            test_dict.update({
                'course_name': course.name,
                'subject_name': course.subject_name,
                'status': test_student.status,
                'date': test_student.date
            })

            if include_final_grade:
                test_dict['final_grade'] = test_student.final_grade

            tests.append(test_dict)

        return tests

    def get_test_history(self, subject_filter: SubjectName = None,
                         course_id: int = None) -> List[Dict[str, str]]:
        """Get all completed/failed tests for this student."""
        return self._get_tests(
            status_filters=[TestStatus.PASSED, TestStatus.FAILED],
            subject_filter=subject_filter,
            course_id=course_id,
            include_final_grade=True
        )

    def get_upcoming_tests(self, subject_filter: SubjectName = None,
                           course_id: int = None) -> List[Dict[str, str]]:
        """Get all scheduled/delayed tests for this student."""
        return self._get_tests(
            status_filters=[TestStatus.SCHEDULED, TestStatus.DELAYED],
            subject_filter=subject_filter,
            course_id=course_id,
            include_final_grade=False
        )

    def get_subjects(self) -> List[SubjectName]:
        """Get all unique subjects for this student's courses."""
        from .subject_models import Course
        from .associations import CourseStudent

        session = get_current_session()
        subjects = (
            session
            .query(Course.subject_name)
            .join(CourseStudent, Course.id == CourseStudent.course_id)
            .filter(CourseStudent.student_id == self.id)
            .distinct()
            .all()
        )

        return [subject[0] for subject in subjects]

    def get_average_grade(self, course_id: Optional[int] = None) -> Optional[float]:
        """Calculate the average tests grade for this student."""
        from .associations import TestStudent

        session = get_current_session()
        query = (
            session
            .query(func.avg(TestStudent.final_grade))
            .filter(
                TestStudent.student_id == self.id,
                TestStudent.final_grade.isnot(None)
            )
        )

        if course_id is not None:
            query = query.filter(TestStudent.course_id == course_id)

        avg_grade = query.scalar()

        return round(avg_grade, 1) if avg_grade else None

    def get_average_feedback(
            self,
            course_id: int,
            days: int = 30,
            include_home: bool = True,
            include_school: bool = True
    ) -> Optional[Dict[str, float]]:
        """Calculate the average student feedback for a specific course from recent study sessions."""
        from .session_models import HomeHoursStudySession, SchoolHoursStudySession
        from .associations import (
            HomeHoursStudySessionStudent, SchoolHoursStudySessionStudent,
            LearningUnitsHomeHoursStudySession, LearningUnitsSchoolHoursStudySession
        )

        session = get_current_session()
        cutoff_date = datetime.now() - timedelta(days=days)

        def get_session_feedback(
                student_assoc_model,
                study_session_model,
                learning_units_assoc_model,
                session_id_field: str
        ):
            """ Generic function to query feedback from either home or school study sessions."""
            return (
                session.query(
                    func.avg(student_assoc_model.difficulty_feedback).label('avg_difficulty'),
                    func.avg(student_assoc_model.understanding_feedback).label('avg_understanding')
                )
                .join(study_session_model,
                      getattr(student_assoc_model, session_id_field) == study_session_model.id)
                .join(learning_units_assoc_model,
                      getattr(learning_units_assoc_model, session_id_field) == study_session_model.id)
                .filter(
                    student_assoc_model.student_id == self.id,
                    learning_units_assoc_model.course_id == course_id,
                    study_session_model.start_time >= cutoff_date,
                    student_assoc_model.difficulty_feedback.isnot(None),
                    student_assoc_model.understanding_feedback.isnot(None)
                )
                .first()
            )

        feedback_results = []

        if include_home:
            home_feedback = get_session_feedback(
                HomeHoursStudySessionStudent,
                HomeHoursStudySession,
                LearningUnitsHomeHoursStudySession,
                'home_hours_study_session_id'
            )
            feedback_results.append(home_feedback)

        if include_school:
            school_feedback = get_session_feedback(
                SchoolHoursStudySessionStudent,
                SchoolHoursStudySession,
                LearningUnitsSchoolHoursStudySession,
                'school_hours_study_session_id'
            )
            feedback_results.append(school_feedback)

        # Combine feedback from selected session types
        difficulties = [f[0] for f in feedback_results if f and f[0] is not None]
        understandings = [f[1] for f in feedback_results if f and f[1] is not None]

        if not difficulties and not understandings:
            return None

        avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else None
        avg_understanding = sum(understandings) / len(understandings) if understandings else None

        overall_scores = [s for s in [avg_difficulty, avg_understanding] if s is not None]
        avg_overall = sum(overall_scores) / len(overall_scores) if overall_scores else None

        return {
            'difficulty': round(avg_difficulty, 1) if avg_difficulty else None,
            'understanding': round(avg_understanding, 1) if avg_understanding else None,
            'overall': round(avg_overall, 1) if avg_overall else None
        }

    def get_attendance_behavior(self, days: int = 30) -> dict:
        """Get attendance statistics for this student."""
        from .session_models import HomeHoursStudySession, SchoolHoursStudySession
        from .associations import HomeHoursStudySessionStudent, SchoolHoursStudySessionStudent

        session = get_current_session()
        cutoff_date = datetime.now() - timedelta(days=days)

        def _get_stats(assoc_model, session_model):
            """Get total and attended counts in a single query."""
            result = session.query(
                func.count(assoc_model.student_id).label('total'),
                func.sum(cast(func.coalesce(assoc_model.is_attendant, False), Integer)).label('attended')
            ).join(
                session_model,
                assoc_model.school_hours_study_session_id == session_model.id
                if assoc_model == SchoolHoursStudySessionStudent
                else assoc_model.home_hours_study_session_id == session_model.id
            ).filter(
                assoc_model.student_id == self.id,
                session_model.start_time >= cutoff_date
            ).one()

            total, attended = result.total or 0, int(result.attended or 0)
            rate = (attended / total * 100) if total > 0 else None

            return {
                'total_sessions': total,
                'attended_sessions': attended,
                'attendance_rate': round(rate, 1) if rate is not None else None
            }

        return {
            'school_hours': _get_stats(SchoolHoursStudySessionStudent, SchoolHoursStudySession),
            'home_hours': _get_stats(HomeHoursStudySessionStudent, HomeHoursStudySession),
            'period_days': days
        }

    def get_recent_evaluations(self, evaluation_type: EvaluationType,
                               limit: int = 5) -> List[Dict]:
        """Get the most recent evaluations of a specific type for this student."""
        from .evaluation_models import (
            SessionalProficiencyEvaluation,
            SessionalInvestmentEvaluation,
            SessionalSocialEvaluation
        )

        session = get_current_session()
        evaluation_config = {
            EvaluationType.PROFICIENCY: {
                'model': SessionalProficiencyEvaluation,
                'descriptions': {'description': 'evaluator_evaluation_description'}
            },
            EvaluationType.INVESTMENT: {
                'model': SessionalInvestmentEvaluation,
                'descriptions': {
                    'ai_description': 'evaluator_evaluation_description',
                    'manager_description': 'class_manager_evaluation_description'
                }
            },
            EvaluationType.SOCIAL: {
                'model': SessionalSocialEvaluation,
                'descriptions': {'description': 'class_manager_evaluation_description'}
            }
        }

        config = evaluation_config.get(evaluation_type)
        if not config:
            return []

        evals = (
            session
            .query(config['model'])
            .filter(config['model'].student_id == self.id)
            .order_by(desc(config['model'].date))
            .limit(limit)
            .all()
        )

        evaluations = []
        for evaluation in evals:
            eval_dict = evaluation.to_dict()
            eval_dict['type'] = evaluation_type.value.capitalize()

            for key, attr_name in config['descriptions'].items():
                eval_dict[key] = getattr(evaluation, attr_name)

            evaluations.append(eval_dict)

        return evaluations

    def get_all_recent_evaluations(self, limit: int = 5) -> List[Dict]:
        """Get the most recent evaluations of all types for this student."""
        all_evaluations = []

        for eval_type in EvaluationType:
            evaluations = self.get_recent_evaluations(eval_type, limit)
            all_evaluations.extend(evaluations)

        all_evaluations.sort(key=lambda x: x['date'], reverse=True)
        return all_evaluations[:limit]

    def get_learning_units_progress(self, course_id: int) -> List[dict]:
        """Get learning units progress for a specific course in sequential order."""
        from .subject_models import LearningUnit
        from .associations import LearningUnitStudent

        session = get_current_session()
        query: Query = (
            session.query(LearningUnit)
            .filter(LearningUnit.course_id == course_id)
            .add_entity(LearningUnitStudent)
            .outerjoin(
                LearningUnitStudent,
                (LearningUnit.course_id == LearningUnitStudent.course_id) &
                (LearningUnit.name == LearningUnitStudent.learning_unit_name) &
                (LearningUnitStudent.student_id == self.id)
            )
        )

        results = query.all()

        units_dict = {}
        student_progress = {}

        for learning_unit, unit_student in results:
            units_dict[learning_unit.name] = learning_unit

            if unit_student:
                student_progress[learning_unit.name] = {
                    'progress': (unit_student.progress * 100) if unit_student.progress else 0,
                    'state': unit_student.state
                }
            else:
                student_progress[learning_unit.name] = {
                    'progress': 0,
                    'state': 'not started'
                }

        ordered_units = self._order_learning_units_by_sequence(units_dict)

        learning_units_data = []
        for unit_name in ordered_units:
            learning_unit = units_dict[unit_name]
            progress_data = student_progress[unit_name]

            unit_dict = learning_unit.to_dict()
            unit_dict.update({
                'state': progress_data['state'],
                'progress': round(progress_data['progress'], 1)
            })
            learning_units_data.append(unit_dict)

        return learning_units_data

    @staticmethod
    def _order_learning_units_by_sequence(units_dict: dict) -> list:
        """Order learning units based on their previous/next relationships."""
        if not units_dict:
            return []

        # Find the first unit (one with no previous_learning_unit or previous not in dict)
        first_unit = None
        for unit_name, unit in units_dict.items():
            if not unit.previous_learning_unit or unit.previous_learning_unit not in units_dict:
                first_unit = unit_name
                break

        # If no clear first unit found, fall back to alphabetical
        if first_unit is None:
            return sorted(units_dict.keys())

        # Follow the chain from first to last
        ordered = []
        current = first_unit
        visited = set()  # Prevent infinite loops in case of cycles

        while current and current in units_dict and current not in visited:
            ordered.append(current)
            visited.add(current)

            next_unit = units_dict[current].next_learning_unit

            if next_unit and next_unit in units_dict:
                current = next_unit
            else:
                current = None

        remaining = sorted(set(units_dict.keys()) - visited)
        ordered.extend(remaining)

        return ordered
