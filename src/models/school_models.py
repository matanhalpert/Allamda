"""
School-related models.

This module contains models for School, Class, and Tablet entities.
"""

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, func, extract
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from .base import Base
from .associations import CourseStudent, TestStudent, SchoolHoursStudySessionStudent
from .session_models import SchoolHoursStudySession
from src.enums import GradeLevel, OS, TabletCondition, CourseState
from src.database.session_context import get_current_session


class School(Base):
    __tablename__ = 'schools'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    establishment_date = Column(Date, nullable=False)
    country = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    street = Column(String(100), nullable=False)
    num = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    school_manager_id = Column(Integer, ForeignKey('school_managers.id'), nullable=False)

    # Relationships
    school_manager = relationship("SchoolManager", back_populates="schools")
    students = relationship("Student", back_populates="school")
    class_managers = relationship("ClassManager", back_populates="school")
    classes = relationship("Class", back_populates="school")

    def get_total_students_count(self) -> int:
        """Get total number of students in the school."""
        return len(self.students)

    def get_active_courses_count(self) -> int:
        """Get count of distinct active courses being taken by students in this school."""
        session = get_current_session()

        student_ids = [student.id for student in self.students]
        if not student_ids:
            return 0
        
        active_courses = session.query(func.count(func.distinct(CourseStudent.course_id))).filter(
            CourseStudent.student_id.in_(student_ids),
            CourseStudent.state == CourseState.IN_PROGRESS
        ).scalar()
        
        return active_courses or 0

    def get_school_average_grade(self, days: Optional[int] = None) -> Optional[float]:
        """Calculate the average test grade for all students in the school.
        
        Args:
            days: If provided, only consider tests from the last N days
        """
        session = get_current_session()

        student_ids = [student.id for student in self.students]
        if not student_ids:
            return None
        
        query = session.query(func.avg(TestStudent.final_grade)).filter(
            TestStudent.student_id.in_(student_ids),
            TestStudent.final_grade.isnot(None)
        )
        
        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(TestStudent.date >= cutoff_date)
        
        avg_grade = query.scalar()
        return round(avg_grade, 1) if avg_grade else None

    def get_school_attendance_rate(self, days: int = 30) -> Optional[float]:
        """Calculate the average attendance rate for all students in the school."""
        session = get_current_session()

        student_ids = [student.id for student in self.students]
        if not student_ids:
            return None
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = session.query(
            func.count(SchoolHoursStudySessionStudent.student_id).label('total'),
            func.sum(func.cast(SchoolHoursStudySessionStudent.is_attendant, Integer)).label('attended')
        ).join(
            SchoolHoursStudySession,
            SchoolHoursStudySessionStudent.school_hours_study_session_id == SchoolHoursStudySession.id
        ).filter(
            SchoolHoursStudySessionStudent.student_id.in_(student_ids),
            SchoolHoursStudySession.start_time >= cutoff_date
        ).one()
        
        total, attended = result.total or 0, int(result.attended or 0)
        
        if total == 0:
            return None
        
        attendance_rate = (attended / total) * 100
        return round(attendance_rate, 1)

    def get_average_grades_by_class(self) -> List[Dict]:
        """Get average grades for each class in the school."""
        class_data = []
        
        for class_obj in self.classes:
            avg_grade = class_obj.get_class_average_grade()
            class_data.append({
                'grade_level': class_obj.grade_level.value if class_obj.grade_level else 'Unknown',
                'year': class_obj.year,
                'average_grade': avg_grade,
                'student_count': len(class_obj.students)
            })

        class_data.sort(key=lambda x: (x['grade_level'], x['year']))
        return class_data

    def get_top_students(self, limit: int = 10) -> List[Dict]:
        """Get top performing students based on average test grades.
        
        Args:
            limit: Number of top students to return (default: 10)
        """
        session = get_current_session()

        student_ids = [student.id for student in self.students]
        if not student_ids:
            return []
        
        # Query to get average grade per student
        top_students_query = (
            session.query(
                TestStudent.student_id,
                func.avg(TestStudent.final_grade).label('avg_grade'),
                func.count(TestStudent.test_name).label('test_count')
            )
            .filter(
                TestStudent.student_id.in_(student_ids),
                TestStudent.final_grade.isnot(None)
            )
            .group_by(TestStudent.student_id)
            .order_by(func.avg(TestStudent.final_grade).desc())
            .limit(limit)
        )
        
        results = top_students_query.all()
        
        top_students = []
        for student_id, avg_grade, test_count in results:
            # Get student object
            student = next((s for s in self.students if s.id == student_id), None)
            if student:
                top_students.append({
                    'student_id': student_id,
                    'name': student.full_name,
                    'average_grade': round(avg_grade, 1) if avg_grade else None,
                    'test_count': test_count
                })
        
        return top_students

    def get_grade_trends_over_time(self, days: int = 90) -> List[Dict]:
        """Get average grade trends grouped by month."""
        session = get_current_session()

        student_ids = [student.id for student in self.students]
        if not student_ids:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Query to get average grades by month
        trends_query = (
            session.query(
                extract('year', TestStudent.date).label('year'),
                extract('month', TestStudent.date).label('month'),
                func.avg(TestStudent.final_grade).label('avg_grade'),
                func.count(TestStudent.test_name).label('test_count')
            )
            .filter(
                TestStudent.student_id.in_(student_ids),
                TestStudent.final_grade.isnot(None),
                TestStudent.date.isnot(None),
                TestStudent.date >= cutoff_date
            )
            .group_by(extract('year', TestStudent.date), extract('month', TestStudent.date))
            .order_by(extract('year', TestStudent.date), extract('month', TestStudent.date))
        )
        
        results = trends_query.all()
        
        trends = []
        for year, month, avg_grade, test_count in results:
            trends.append({
                'year': int(year),
                'month': int(month),
                'average_grade': round(avg_grade, 1) if avg_grade else None,
                'test_count': test_count
            })
        
        return trends

    def get_attendance_trends_over_time(self, days: int = 90) -> List[Dict]:
        """Get attendance rate trends grouped by week."""
        session = get_current_session()

        student_ids = [student.id for student in self.students]
        if not student_ids:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Query to get attendance by week
        trends_query = (
            session.query(
                extract('year', SchoolHoursStudySession.start_time).label('year'),
                extract('week', SchoolHoursStudySession.start_time).label('week'),
                func.count(SchoolHoursStudySessionStudent.student_id).label('total'),
                func.sum(func.cast(SchoolHoursStudySessionStudent.is_attendant, Integer)).label('attended')
            )
            .join(
                SchoolHoursStudySession,
                SchoolHoursStudySessionStudent.school_hours_study_session_id == SchoolHoursStudySession.id
            )
            .filter(
                SchoolHoursStudySessionStudent.student_id.in_(student_ids),
                SchoolHoursStudySession.start_time >= cutoff_date
            )
            .group_by(
                extract('year', SchoolHoursStudySession.start_time),
                extract('week', SchoolHoursStudySession.start_time)
            )
            .order_by(
                extract('year', SchoolHoursStudySession.start_time),
                extract('week', SchoolHoursStudySession.start_time)
            )
        )
        
        results = trends_query.all()
        
        trends = []
        for year, week, total, attended in results:
            attendance_rate = (int(attended or 0) / total * 100) if total > 0 else None
            trends.append({
                'year': int(year),
                'week': int(week),
                'attendance_rate': round(attendance_rate, 1) if attendance_rate is not None else None,
                'total_sessions': total
            })
        
        return trends


class Class(Base):
    __tablename__ = 'classes'

    school_id = Column(Integer, ForeignKey('schools.id'), primary_key=True)
    year = Column(Integer, primary_key=True)
    grade_level = Column(Enum(GradeLevel), primary_key=True)
    capacity = Column(Integer, nullable=False)

    # Relationships
    school = relationship("School", back_populates="classes")
    class_managers = relationship("ClassManager", secondary="classess_class_managers", back_populates="classes")
    students = relationship("Student", secondary="classes_students", back_populates="classes")

    def get_students(self) -> list[dict]:
        """Get all students in this class with their basic information."""
        return [student.to_dict() for student in self.students]

    def get_class_average_grade(self) -> Optional[float]:
        """Calculate the average test grade for all students in this class."""
        from .associations import TestStudent
        
        session = get_current_session()
        student_ids = [student.id for student in self.students]

        if not student_ids:
            return None

        avg_grade = session.query(func.avg(TestStudent.final_grade)).filter(
            TestStudent.student_id.in_(student_ids),
            TestStudent.final_grade.isnot(None)
        ).scalar()

        return round(avg_grade, 1) if avg_grade else None

    def get_weekly_attendance_rate(self, days=30) -> Optional[float]:
        """ Calculate the average attendance rate for the class."""
        from .session_models import SchoolHoursStudySession as session_model
        from .associations import SchoolHoursStudySessionStudent as assoc_model
        
        session = get_current_session()
        student_ids = [student.id for student in self.students]

        if not student_ids:
            return None

        cutoff_date = datetime.now() - timedelta(days=days)

        base_query = (
            session
            .query(func.count(assoc_model.student_id))
            .join(
                session_model,
                assoc_model.school_hours_study_session_id == session_model.id
            )
            .filter(
                assoc_model.student_id.in_(student_ids),
                session_model.start_time >= cutoff_date
            )
        )

        total_sessions = base_query.scalar()
        attended_sessions = base_query.filter(assoc_model.is_attendant == 1).scalar()

        if not total_sessions:
            return None

        attendance_rate = (attended_sessions / total_sessions) * 100
        return round(attendance_rate, 1)

    def to_dict(self):
        """Get basic class information."""
        result = super().to_dict()
        result['current_size'] = len(self.students)
        return result


class Tablet(Base):
    __tablename__ = 'tablets'

    serial_number = Column(String(50), primary_key=True)
    os = Column(Enum(OS), nullable=False)
    model = Column(String(50), nullable=False)
    purchase_date = Column(Date, nullable=False)
    condition = Column(Enum(TabletCondition), nullable=False)

    # Relationships
    students = relationship("TabletStudent", back_populates="tablet")
