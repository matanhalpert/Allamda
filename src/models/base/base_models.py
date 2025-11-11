"""
Abstract base classes for SQLAlchemy models.

This module contains all abstract base classes used throughout the models package.
For the declarative base, see src.models.base.declarative_base.
"""
from mailbox import Message

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, ForeignKey, ForeignKeyConstraint, Integer, String,
    Text, CheckConstraint
)
from sqlalchemy.orm import relationship, declared_attr
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from src.enums import EmotionalState, AttendanceReason, SessionStatus, UserType
from src.database.session_context import get_current_session
from .declarative_base import Base


class User(Base):
    """Base user class with common user methods."""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthdate = Column(Date, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    # Relationships
    @declared_attr
    def phones(cls):
        return relationship(
            "Phone",
            primaryjoin=f"{cls.__name__}.id == foreign(Phone.user_id)",
            cascade="all, delete-orphan",
            overlaps="phones"
        )

    @declared_attr
    def addresses(cls):
        return relationship(
            "Address",
            primaryjoin=f"{cls.__name__}.id == foreign(Address.user_id)",
            cascade="all, delete-orphan",
            overlaps="addresses"
        )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def user_type(self):
        """Get the user type based on the class name."""
        class_name_to_enum = {
            'student': UserType.STUDENT,
            'parent': UserType.PARENT,
            'classmanager': UserType.CLASS_MANAGER,
            'schoolmanager': UserType.SCHOOL_MANAGER,
            'regionalsupervisor': UserType.REGIONAL_SUPERVISOR
        }
        return class_name_to_enum.get(self.__class__.__name__.lower())

    def to_dict(self) -> dict:
        """Convert user to dictionary for session storage."""
        result = super().to_dict()
        result['full_name'] = self.full_name
        result['user_type'] = self.user_type
        return result

    @classmethod
    def authenticate(cls, email: str, password: str):
        """
        Authenticate a user by email and password.
        
        Uses the current session from context.
        """
        session = get_current_session()
        user = session.query(cls).filter(cls.email == email).first()
        return user if (user and user.password == password) else None

    @classmethod
    def authenticate_any_user(cls, email: str, password: str):
        """
        Authenticate a user across all user types.
        
        Uses the current session from context.
        """
        # Import here to avoid circular imports
        from ..student_models import Student
        from ..user_models import Parent, SchoolManager, ClassManager, RegionalSupervisor

        user_classes = [Student, Parent, SchoolManager, ClassManager, RegionalSupervisor]

        for user_class in user_classes:
            user = user_class.authenticate(email, password)
            if user:
                return user

        return None


class Agent(Base):
    """Base agent class for AI-powered entities with database persistence."""
    __abstract__ = True

    ai_model_id = Column(Integer, ForeignKey('ai_models.id'), primary_key=True)
    name = Column(String(100), primary_key=True)

    # Relationships
    @declared_attr
    def ai_model(cls):
        agent_type = cls.__name__.lower() + 's'
        return relationship("AIModel", back_populates=agent_type)

    @property
    def agent_type(self):
        """Get the agent type based on the class name."""
        return self.__class__.__name__.lower()

    def to_dict(self):
        """Convert agent to dictionary for session storage."""
        result = super().to_dict()
        result['agent_type'] = self.agent_type
        return result


class StudySession(Base):
    """Base study session class with common fields and methods."""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.PENDING)
    teacher_ai_model_id = Column(Integer, nullable=True)
    teacher_name = Column(String(100), nullable=True)

    @declared_attr
    def __table_args__(cls):
        """Define the composite foreign key constraint to teachers table."""
        return (
            ForeignKeyConstraint(['teacher_ai_model_id', 'teacher_name'],
                                 ['teachers.ai_model_id', 'teachers.name']),
        )

    # Relationships
    @declared_attr
    def pauses(cls):
        # Each study session type has its own pause table
        if cls.__name__ == 'HomeHoursStudySession':
            return relationship(
                "HomeHoursStudySessionPause",
                cascade="all, delete-orphan",
                overlaps="pauses"
            )
        elif cls.__name__ == 'SchoolHoursStudySession':
            return relationship(
                "SchoolHoursStudySessionPause",
                cascade="all, delete-orphan",
                overlaps="pauses"
            )
        return None

    @declared_attr
    def teacher(cls):
        # Map each concrete study session class to its corresponding Teacher relationship
        class_to_relationship = {
            'HomeHoursStudySession': 'home_study_sessions',
            'SchoolHoursStudySession': 'school_study_sessions'
        }
        back_populates = class_to_relationship.get(cls.__name__)
        return relationship("Teacher",
                            foreign_keys=[cls.teacher_ai_model_id, cls.teacher_name],
                            back_populates=back_populates)

    @declared_attr
    def messages(cls):
        # Each study session type has its own foreign key in the Message table
        if cls.__name__ == 'HomeHoursStudySession':
            return relationship("Message", back_populates="home_study_session")
        elif cls.__name__ == 'SchoolHoursStudySession':
            return relationship("Message", back_populates="school_study_session")
        return None

    @declared_attr
    def students(cls):
        # Each study session type has its own student association table
        if cls.__name__ == 'HomeHoursStudySession':
            return relationship("HomeHoursStudySessionStudent", back_populates="study_session")
        elif cls.__name__ == 'SchoolHoursStudySession':
            return relationship("SchoolHoursStudySessionStudent", back_populates="study_session")
        return None

    @declared_attr
    def learning_units(cls):
        # Each study session type has its own secondary table for learning units
        if cls.__name__ == 'HomeHoursStudySession':
            return relationship("LearningUnit", secondary="learning_units_home_sessions",
                                back_populates="home_study_sessions")
        elif cls.__name__ == 'SchoolHoursStudySession':
            return relationship("LearningUnit", secondary="learning_units_school_sessions",
                                back_populates="school_study_sessions")
        return None

    @declared_attr
    def sessional_proficiency_evaluations(cls):
        # Each study session type has its own secondary table for sessional proficiency evaluations
        if cls.__name__ == 'HomeHoursStudySession':
            return relationship("SessionalProficiencyEvaluation", secondary="sessional_prof_eval_home_sessions",
                                back_populates="home_study_sessions")
        elif cls.__name__ == 'SchoolHoursStudySession':
            return relationship("SessionalProficiencyEvaluation", secondary="sessional_prof_eval_school_sessions",
                                back_populates="school_study_sessions")
        return None

    @declared_attr
    def sessional_investment_evaluations(cls):
        # Each study session type has its own secondary table for sessional investment evaluations
        if cls.__name__ == 'HomeHoursStudySession':
            return relationship("SessionalInvestmentEvaluation", secondary="sessional_inv_eval_home_sessions",
                                back_populates="home_study_sessions")
        elif cls.__name__ == 'SchoolHoursStudySession':
            return relationship("SessionalInvestmentEvaluation", secondary="sessional_inv_eval_school_sessions",
                                back_populates="school_study_sessions")
        return None

    @property
    def session_type(self):
        """Get the session type based on the class name."""
        return self.__class__.__name__.lower()

    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate session duration (current or final)."""
        if not self.start_time:
            return None

        now = self.end_time if self.end_time else datetime.now()
        return now - self.start_time

    def get_messages(self, order_by_timestamp: bool = True) -> List['Message']:
        """Get all messages for this study session."""
        messages = self.messages
        
        if order_by_timestamp and messages:
            messages = sorted(messages, key=lambda msg: msg.timestamp)
        
        return messages

    def get_transcript(self) -> str:
        """
        Get a formatted transcript of all messages in this study session.
        
        Returns:
            A formatted string with each message prefixed by sender type (Student/Teacher).
        """
        from src.enums import MessageType
        
        messages = self.get_messages(order_by_timestamp=True)
        
        transcript = "\n\n".join([
            f"{'Student' if msg.type == MessageType.PROMPT else 'Teacher'}: {msg.content}"
            for msg in messages
        ])
        
        return transcript

    def to_dict(self):
        """Convert study session to dictionary."""
        result = super().to_dict()
        result['session_type'] = self.session_type
        result['duration'] = str(self.duration) if self.duration else None
        return result

    @classmethod
    def get_recent_sessions_for_student(cls, student_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent study sessions for a student with feedback and course information."""
        session = get_current_session()

        query = (
            session.query(cls)
            .join(cls.students)
            .filter(cls.students.any(student_id=student_id))
            .order_by(cls.start_time.desc())
            .limit(limit)
        )
        
        sessions = query.all()
        result: List[Dict[str, Any]] = []
        
        for study_session in sessions:
            course_name = None
            course_subject = None
            if study_session.learning_units:
                first_unit = list(study_session.learning_units)[0]
                course = first_unit.course
                course_name = course.name
                course_subject = course.subject_name.value if hasattr(course.subject_name, 'value') else str(course.subject_name)

            duration_minutes = int(study_session.duration.total_seconds() / 60) if study_session.duration else None
            session_type_display = study_session.type.value.replace('_', ' ').title() if hasattr(study_session.type, 'value') else str(study_session.type)
            session_category = "Home Hours" if cls.__name__ == "HomeHoursStudySession" else "School Hours"
            status_str = study_session.status.value if hasattr(study_session.status, 'value') else str(study_session.status).lower()
            
            session_data = {
                'id': study_session.id,
                'start_time': study_session.start_time,
                'end_time': study_session.end_time,
                'category': session_category,
                'session_category': session_category,  # Keep for backward compatibility
                'session_type': session_type_display,
                'course_name': course_name,
                'course_subject': course_subject,
                'duration': duration_minutes,
                'duration_minutes': duration_minutes,  # Keep for backward compatibility
                'status': status_str,
            }
            
            result.append(session_data)
        
        return result

    @classmethod
    def get_by_id_and_student(cls, session_id: int, student_id: int) -> Optional['StudySession']:
        """
        Get session and verify student ownership via join with association table.
        Works polymorphically for both HomeHours and SchoolHours sessions.
        """
        session = get_current_session()

        if cls.__name__ == 'HomeHoursStudySession':
            from ..associations import HomeHoursStudySessionStudent as AssocModel
            session_id_field = AssocModel.home_hours_study_session_id
        elif cls.__name__ == 'SchoolHoursStudySession':
            from ..associations import SchoolHoursStudySessionStudent as AssocModel
            session_id_field = AssocModel.school_hours_study_session_id
        else:
            # Called on abstract base - shouldn't happen
            return None
        
        result = (
            session
            .query(cls)
            .join(AssocModel, cls.id == session_id_field)
            .filter(
                cls.id == session_id,
                AssocModel.student_id == student_id
            )
            .first()
        )
        return result

    @classmethod
    def get_active_by(cls, student_id: int) -> Optional['StudySession']:
        """
        Get active session (PENDING/ACTIVE/PAUSED) for a student.
        Works polymorphically for both HomeHours and SchoolHours sessions.
        """
        if cls.__name__ == 'HomeHoursStudySession':
            from ..associations import HomeHoursStudySessionStudent as AssocModel
        elif cls.__name__ == 'SchoolHoursStudySession':
            from ..associations import SchoolHoursStudySessionStudent as AssocModel
        else:
            # Called on abstract base - shouldn't happen
            return None

        associations = AssocModel.get_by(
            first=False,
            student_id=student_id
        )
        if not associations:
            return None

        if cls.__name__ == 'HomeHoursStudySession':
            session_ids = [assoc.home_hours_study_session_id for assoc in associations]
        else:
            session_ids = [assoc.school_hours_study_session_id for assoc in associations]
        
        active_statuses = [SessionStatus.PENDING, SessionStatus.ACTIVE, SessionStatus.PAUSED]

        return cls.get_by(
            first=True,
            id=session_ids,
            status=active_statuses
        )

    @classmethod
    def cleanup_pending_sessions(cls, timeout_minutes: int = 5):
        """
        Find and cancel stale PENDING sessions older than timeout.
        Works polymorphically for both HomeHours and SchoolHours sessions.
        
        Returns class reference for chaining.
        """
        session = get_current_session()
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        
        stale_sessions = (
            session.query(cls)
            .filter(
                cls.status == SessionStatus.PENDING,
                cls.start_time < cutoff_time
            )
            .all()
        )

        cancelled_count = 0
        for stale_session in stale_sessions:
            stale_session.status = SessionStatus.CANCELLED
            cancelled_count += 1
        
        if cancelled_count > 0:
            session.commit()
        
        return cls

    @classmethod
    def get_session_details(cls, session_id: int, requesting_user_id: int, requesting_user_type: UserType) -> Optional[Dict[str, Any]]:
        """Get comprehensive session details with role-based data filtering."""
        session = get_current_session()

        study_session = cls.get_by(id=session_id, first=True)
        if not study_session:
            return None

        is_class_manager = requesting_user_type == UserType.CLASS_MANAGER
        has_permission = False
        
        if requesting_user_type == UserType.STUDENT:
            if study_session.students:
                for student_assoc in study_session.students:
                    if student_assoc.student_id == requesting_user_id:
                        has_permission = True
                        break
        elif is_class_manager:
            # Class managers can view sessions they manage
            if cls.__name__ == 'SchoolHoursStudySession':
                # For school sessions, check if they're the class manager
                if hasattr(study_session, 'class_manager_id') and study_session.class_manager_id == requesting_user_id:
                    has_permission = True
            else:
                # For home sessions, check if any student belongs to their class
                from ..user_models import ClassManager
                manager = ClassManager.get_by(id=requesting_user_id, first=True)
                if manager:
                    managed_class = manager.get_class()
                    if managed_class and study_session.students:
                        student_ids = [s['id'] for s in managed_class.get_students()]
                        for student_assoc in study_session.students:
                            if student_assoc.student_id in student_ids:
                                has_permission = True
                                break
        
        if not has_permission:
            return None

        session_category = "School Hours" if cls.__name__ == "SchoolHoursStudySession" else "Home Hours"
        session_type_display = study_session.type.value.replace('_', ' ').title() if hasattr(study_session.type, 'value') else str(study_session.type)
        
        # Calculate duration
        duration_minutes = None
        duration_display = None
        if study_session.duration:
            duration_minutes = int(study_session.duration.total_seconds() / 60)
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            if hours > 0:
                duration_display = f"{hours}h {minutes}m"
            else:
                duration_display = f"{minutes} min"
        
        # Get learning units
        learning_units = []
        if study_session.learning_units:
            for unit in study_session.learning_units:
                learning_units.append({
                    'name': unit.name,
                    'course_name': unit.course.name,
                    'course_subject': unit.course.subject.name.value if unit.course.subject else None
                })
        
        # Get students data with feedback
        students_data = []
        for student_assoc in study_session.students or []:
            # If requesting user is a student, only include their own data
            if requesting_user_type == UserType.STUDENT and student_assoc.student_id != requesting_user_id:
                continue
            
            student = student_assoc.student
            student_info = {
                'id': student.id,
                'name': student.full_name,
                'is_attendant': student_assoc.is_attendant,
                'attendance_reason': student_assoc.attendance_reason.value if student_assoc.attendance_reason else None,
                'emotional_state_before': student_assoc.emotional_state_before.value if student_assoc.emotional_state_before else None,
                'emotional_state_after': student_assoc.emotional_state_after.value if student_assoc.emotional_state_after else None,
                'difficulty_feedback': student_assoc.difficulty_feedback,
                'understanding_feedback': student_assoc.understanding_feedback,
                'textual_feedback': student_assoc.textual_feedback
            }
            students_data.append(student_info)
        
        # Get pauses
        pauses = []
        total_pause_minutes = 0
        if study_session.pauses:
            for pause in study_session.pauses:
                pause_duration_minutes = None
                if pause.duration:
                    pause_duration_minutes = int(pause.duration.total_seconds() / 60)
                    total_pause_minutes += pause_duration_minutes
                
                pauses.append({
                    'start_time': pause.start_time,
                    'end_time': pause.end_time,
                    'duration_minutes': pause_duration_minutes
                })
        
        # Build base details
        details = {
            'id': study_session.id,
            'session_category': session_category,
            'session_type': session_type_display,
            'status': study_session.status.value,
            'start_time': study_session.start_time,
            'end_time': study_session.end_time,
            'duration_minutes': duration_minutes,
            'duration_display': duration_display,
            'teacher_name': study_session.teacher_name,
            'learning_units': learning_units,
            'students': students_data,
            'pauses': pauses,
            'total_pause_minutes': total_pause_minutes,
            'is_class_manager_view': is_class_manager
        }
        
        # Add school-specific data
        if cls.__name__ == 'SchoolHoursStudySession' and hasattr(study_session, 'planned_duration_minutes'):
            details['planned_duration_minutes'] = study_session.planned_duration_minutes
        
        # Add evaluations for class managers only
        if is_class_manager:
            # Proficiency evaluations
            proficiency_evals = []
            if study_session.sessional_proficiency_evaluations:
                for eval_obj in study_session.sessional_proficiency_evaluations:
                    proficiency_evals.append({
                        'id': eval_obj.id,
                        'student_id': eval_obj.student_id,
                        'student_name': eval_obj.student.full_name if eval_obj.student else None,
                        'score': eval_obj.score,
                        'date': eval_obj.date,
                        'description': eval_obj.evaluator_evaluation_description
                    })
            details['proficiency_evaluations'] = proficiency_evals
            
            # Investment evaluations
            investment_evals = []
            if study_session.sessional_investment_evaluations:
                for eval_obj in study_session.sessional_investment_evaluations:
                    investment_evals.append({
                        'id': eval_obj.id,
                        'student_id': eval_obj.student_id,
                        'student_name': eval_obj.student.full_name if eval_obj.student else None,
                        'score': eval_obj.score,
                        'date': eval_obj.date,
                        'ai_description': eval_obj.evaluator_evaluation_description,
                        'human_description': eval_obj.class_manager_evaluation_description
                    })
            details['investment_evaluations'] = investment_evals
            
            # Social evaluations (school sessions only)
            social_evals = []
            if cls.__name__ == 'SchoolHoursStudySession' and hasattr(study_session, 'sessional_social_evaluations'):
                if study_session.sessional_social_evaluations:
                    for eval_obj in study_session.sessional_social_evaluations:
                        social_evals.append({
                            'id': eval_obj.id,
                            'student_id': eval_obj.student_id,
                            'student_name': eval_obj.student.full_name if eval_obj.student else None,
                            'score': eval_obj.score,
                            'date': eval_obj.date,
                            'description': eval_obj.class_manager_evaluation_description
                        })
            details['social_evaluations'] = social_evals
        
        return details


class StudySessionPause(Base):
    """Base study session pause class with common fields."""
    __abstract__ = True

    start_time = Column(DateTime, primary_key=True)
    end_time = Column(DateTime, nullable=True)

    @property
    def pause_type(self):
        """Get the pause type based on the class name."""
        return self.__class__.__name__.lower()

    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate pause duration if end_time is set."""
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def to_dict(self):
        """Convert pause to dictionary."""
        result = super().to_dict()
        result['pause_type'] = self.pause_type
        result['duration'] = str(self.duration) if self.duration else None
        return result

    @classmethod
    def get_active_pause(cls, study_session_id: int) -> Optional['StudySessionPause']:
        """Get the active pause for a study session (pause without an end_time)."""
        if cls.__name__ == 'HomeHoursStudySessionPause':
            session_id_field = 'home_hours_study_session_id'
        elif cls.__name__ == 'SchoolHoursStudySessionPause':
            session_id_field = 'school_hours_study_session_id'
        else:
            return None
        
        session = get_current_session()
        return (
            session.query(cls)
            .filter(
                getattr(cls, session_id_field) == study_session_id,
                cls.end_time.is_(None)
            )
            .order_by(cls.start_time.desc())
            .first()
        )


class Evaluation(Base):
    """Base evaluation class with common fields and methods."""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    date = Column(Date, nullable=False)
    score = Column(Integer, CheckConstraint('score >= 1 AND score <= 10'), nullable=False)

    # Relationships
    @declared_attr
    def student(cls):
        # Map each concrete evaluation class to its corresponding Student relationship
        class_to_relationship = {
            'SessionalProficiencyEvaluation': 'sessional_proficiency_evaluations',
            'QuarterProficiencyEvaluation': 'quarter_proficiency_evaluations',
            'SessionalInvestmentEvaluation': 'sessional_investment_evaluations',
            'QuarterInvestmentEvaluation': 'quarter_investment_evaluations',
            'SessionalSocialEvaluation': 'sessional_social_evaluations',
            'QuarterSocialEvaluation': 'quarter_social_evaluations'
        }
        back_populates = class_to_relationship.get(cls.__name__)
        return relationship("Student", back_populates=back_populates)

    @property
    def evaluation_type(self):
        """Get the evaluation type based on the class name."""
        return self.__class__.__name__.lower()

    @property
    def is_sessional(self):
        """Check if this is a sessional evaluation."""
        return 'sessional' in self.evaluation_type

    @property
    def is_quarterly(self):
        """Check if this is a quarterly evaluation."""
        return 'quarter' in self.evaluation_type

    def to_dict(self):
        """Convert evaluation to dictionary."""
        result = super().to_dict()
        result['evaluation_type'] = self.evaluation_type
        result['is_sessional'] = self.is_sessional
        result['is_quarterly'] = self.is_quarterly
        return result


class AIEvaluation(Evaluation):
    """Abstract class for AI-generated evaluations."""
    __abstract__ = True

    evaluator_id = Column(Integer, ForeignKey('evaluators.ai_model_id'), nullable=False)
    evaluator_evaluation_description = Column(Text, nullable=True)

    # Relationships
    @declared_attr
    def evaluator(cls):
        # Map each concrete AI evaluation class to its corresponding Evaluator relationship
        class_to_relationship = {
            'SessionalProficiencyEvaluation': 'sessional_proficiency_evaluations',
            'QuarterProficiencyEvaluation': 'quarter_proficiency_evaluations',
            'SessionalInvestmentEvaluation': 'sessional_investment_evaluations',
            'QuarterInvestmentEvaluation': 'quarter_investment_evaluations'
        }
        back_populates = class_to_relationship.get(cls.__name__)
        if back_populates:
            return relationship("Evaluator", back_populates=back_populates)
        return None


class HumanEvaluation(Evaluation):
    """Abstract class for human-generated evaluations."""
    __abstract__ = True

    class_manager_id = Column(Integer, ForeignKey('class_managers.id'), nullable=False)
    class_manager_evaluation_description = Column(Text, nullable=True)

    # Relationships
    @declared_attr
    def class_manager(cls):
        # Map each concrete human evaluation class to its corresponding ClassManager relationship
        class_to_relationship = {
            'SessionalInvestmentEvaluation': 'sessional_investment_evaluations',
            'QuarterInvestmentEvaluation': 'quarter_investment_evaluations',
            'SessionalSocialEvaluation': 'sessional_social_evaluations',
            'QuarterSocialEvaluation': 'quarter_social_evaluations'
        }
        back_populates = class_to_relationship.get(cls.__name__)
        if back_populates:
            return relationship("ClassManager", back_populates=back_populates)
        return None


class StudySessionStudent(Base):
    """
    Abstract base class for study session student association tables.
    
    This class captures the shared structure for linking students to study sessions
    (both home and school hours) with common feedback and attendance fields.
    Subclasses need only specify their table name and the specific session ID column.
    """
    __abstract__ = True

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    emotional_state_before = Column(Enum(EmotionalState), nullable=True)
    emotional_state_after = Column(Enum(EmotionalState), nullable=True)
    is_attendant = Column(Boolean, nullable=False)
    attendance_reason = Column(Enum(AttendanceReason), nullable=True)
    difficulty_feedback = Column(
        Integer,
        CheckConstraint('difficulty_feedback >= 1 AND difficulty_feedback <= 10'),
        nullable=True
    )
    understanding_feedback = Column(
        Integer,
        CheckConstraint('understanding_feedback >= 1 AND understanding_feedback <= 10'),
        nullable=True
    )
    textual_feedback = Column(Text, nullable=True)

    @declared_attr
    def student(cls):
        class_to_relationship = {
            'HomeHoursStudySessionStudent': 'home_study_sessions',
            'SchoolHoursStudySessionStudent': 'school_study_sessions'
        }
        back_populates = class_to_relationship.get(cls.__name__)
        return relationship("Student", back_populates=back_populates)

    @declared_attr
    def study_session(cls):
        class_to_relationship = {
            'HomeHoursStudySessionStudent': ('HomeHoursStudySession', 'students'),
            'SchoolHoursStudySessionStudent': ('SchoolHoursStudySession', 'students')
        }
        session_class, back_populates = class_to_relationship.get(cls.__name__)
        return relationship(session_class, back_populates=back_populates)


class LearningUnitsStudySession(Base):
    """
    Abstract base class for learning unit-study session association tables.
    
    This class captures the shared structure for linking learning units to study sessions
    (both home and school hours). Subclasses need only specify their table name and the
    specific session ID column.
    """
    __abstract__ = True

    course_id = Column(Integer, primary_key=True)
    learning_unit_name = Column(String(100), primary_key=True)

    @declared_attr
    def __table_args__(cls):
        """
        Define the composite foreign key constraint to learning_units table.
        This is shared across all subclasses.
        """
        from sqlalchemy import ForeignKeyConstraint
        return (
            ForeignKeyConstraint(['course_id', 'learning_unit_name'],
                                 ['learning_units.course_id', 'learning_units.name']),
        )


class EvaluationStudySession(Base):
    """
    Abstract base class for evaluation-study session association tables.
    
    This class captures the shared pattern of linking evaluations (proficiency, investment,
    or social) to study sessions (home or school hours). Each concrete subclass defines:
    - The table name
    - The specific evaluation ID column with its foreign key
    - The specific study session ID column with its foreign key
    
    This follows the pattern established by other abstract classes in this module.
    """
    __abstract__ = True

    # Subclasses must define their own primary key columns:
    # - An evaluation_id column (named according to evaluation type)
    # - A study_session_id column (home_hours_study_session_id or school_hours_study_session_id)
