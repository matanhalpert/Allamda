"""
Study Session Lifecycle Management

Functions for creating and ending study sessions.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Union
from sqlalchemy.exc import SQLAlchemyError

from src.database.session_context import get_current_session
from src.models.session_models import (
    HomeHoursStudySession, HomeHoursStudySessionPause,
    SchoolHoursStudySession, SchoolHoursStudySessionPause
)
from src.models.student_models import Student
from src.models.subject_models import Course, LearningUnit
from src.models.agents import Teacher
from src.models.user_models import ClassManager
from src.models.associations import (
    HomeHoursStudySessionStudent,
    LearningUnitsHomeHoursStudySession,
    SchoolHoursStudySessionStudent,
    LearningUnitsSchoolHoursStudySession
)
from src.enums import (
    HomeHoursStudySessionType, SchoolHoursStudySessionType, SessionStatus, EmotionalState
)
from src.services.course_prioritization import PrioritizationService
from src.services.course_prioritization.builder import ScorerBuilder
from src.services.learning_unit_assignment import assign_learning_units
from src.app.utils.websocket import emit_to_manager
from .exceptions import ActiveSessionExistsError, SessionNotFoundError, InvalidSessionStateError, StudySessionError
from .evaluation import evaluate_session


def create_home_study_session(
        student_id: int,
        session_type: HomeHoursStudySessionType,
        course_id: int,
        learning_unit_names: List[str],
        emotional_state_before: EmotionalState
) -> HomeHoursStudySession:
    """Create a new home study session."""
    session = get_current_session()
    
    active_session = (
        HomeHoursStudySession
        .cleanup_pending_sessions()
        .get_active_by(student_id)
    )
    if active_session:
        # Handle both dictionary and object responses
        session_id = active_session.get('id') if isinstance(active_session, dict) else active_session.id
        raise ActiveSessionExistsError(
            f"Student already has an active session (ID: {session_id})"
        )

    student = Student.get_by(id=student_id, first=True)
    if not student:
        raise StudySessionError(f"Student with ID {student_id} not found")

    course = Course.get_by(id=course_id, first=True)
    if not course:
        raise StudySessionError(f"Course with ID {course_id} not found")

    if not student.is_enrolled(course_id):
        raise StudySessionError(f"Student is not enrolled in course {course_id}")

    if not learning_unit_names:
        raise StudySessionError("At least one learning unit must be selected")

    learning_units = LearningUnit.get_by(course_id=course_id, name=learning_unit_names)

    if len(learning_units) != len(learning_unit_names):
        raise StudySessionError("One or more learning units not found")

    teacher = Teacher.get_by(first=True, subject_name=course.subject_name)
    if not teacher:
        raise StudySessionError(f"No teacher agent available for subject {course.subject_name}")

    try:
        study_session = HomeHoursStudySession(
            start_time=datetime.now(),
            status=SessionStatus.PENDING,
            teacher_ai_model_id=teacher.ai_model_id,
            teacher_name=teacher.name,
            type=session_type
        )
        session.add(study_session)
        session.flush()  # Get the session ID

        student_assoc = HomeHoursStudySessionStudent(
            home_hours_study_session_id=study_session.id,
            student_id=student_id,
            emotional_state_before=emotional_state_before,
            is_attendant=True  # Student is always attendant in home sessions
        )
        session.add(student_assoc)

        for learning_unit in learning_units:
            lu_assoc = LearningUnitsHomeHoursStudySession(
                home_hours_study_session_id=study_session.id,
                course_id=learning_unit.course_id,
                learning_unit_name=learning_unit.name
            )
            session.add(lu_assoc)

        session.commit()
        return study_session

    except SQLAlchemyError as e:
        session.rollback()
        raise StudySessionError(f"Database error creating session: {str(e)}")


def create_school_study_session(
        class_manager_id: int,
        duration_minutes: int = 60
) -> List[SchoolHoursStudySession]:
    """
    Create individual school study sessions for all students in a Class Manager's class.
    Each student gets their own session with their own prioritized course and learning units.
    """
    session = get_current_session()

    class_manager = ClassManager.get_by(id=class_manager_id, first=True)
    if not class_manager:
        raise StudySessionError(f"Class Manager with ID {class_manager_id} not found")

    managed_class = class_manager.get_class()
    if not managed_class:
        raise StudySessionError("Class Manager is not assigned to any class")

    students = managed_class.students
    if not students:
        raise StudySessionError("No students found in the class")

    scorer = ScorerBuilder().with_default_factors().build()
    prioritization_service = PrioritizationService(scorer)

    start_time = datetime.now()
    
    try:
        created_sessions = []

        for student in students:

            student_course = prioritization_service.get_next_course([student])
            if not student_course:
                print(f"Warning: No suitable course found for student {student.id}, skipping")
                continue

            assignment_result = assign_learning_units(
                students=[student],
                course=student_course,
                duration_minutes=duration_minutes
            )
            if not assignment_result.assigned_units:
                print(f"Warning: Could not assign learning units for student {student.id}: {assignment_result.reason}, skipping")
                continue

            teacher = Teacher.get_by(first=True, subject_name=student_course.subject_name)
            if not teacher:
                print(f"Warning: No teacher agent available for subject {student_course.subject_name}, skipping student {student.id}")
                continue

            study_session = SchoolHoursStudySession(
                start_time=start_time,
                status=SessionStatus.PENDING,
                teacher_ai_model_id=teacher.ai_model_id,
                teacher_name=teacher.name,
                type=SchoolHoursStudySessionType.INDIVIDUAL,
                class_manager_id=class_manager_id,
                planned_duration_minutes=duration_minutes
            )
            session.add(study_session)
            session.flush()  # Get the session ID

            student_assoc = SchoolHoursStudySessionStudent(
                school_hours_study_session_id=study_session.id,
                student_id=student.id,
                emotional_state_before=None,  # Set when student joins
                is_attendant=False  # Will be set to True when student actually joins
            )
            session.add(student_assoc)

            for learning_unit in assignment_result.assigned_units:
                lu_assoc = LearningUnitsSchoolHoursStudySession(
                    school_hours_study_session_id=study_session.id,
                    course_id=learning_unit.course_id,
                    learning_unit_name=learning_unit.name
                )
                session.add(lu_assoc)
            
            created_sessions.append(study_session)

        if not created_sessions:
            raise StudySessionError("Could not create sessions for any student in the class")
        
        session.commit()
        return created_sessions
    
    except SQLAlchemyError as e:
        session.rollback()
        raise StudySessionError(f"Database error creating school sessions: {str(e)}")


def join_school_session(
        session_id: int,
        student_id: int,
        emotional_state_before: EmotionalState
) -> SchoolHoursStudySession:
    """Allow a student to join a pending school study session."""
    session = get_current_session()

    study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
    if not study_session:
        raise StudySessionError(f"School session {session_id} not found for student {student_id}")
    
    if study_session.status != SessionStatus.PENDING:
        raise InvalidSessionStateError(
            f"Cannot join session in {study_session.status} state. Session must be PENDING."
        )
    
    # Check if session has already timed out based on planned duration
    if study_session.start_time:
        elapsed_time = datetime.now() - study_session.start_time
        planned_duration = timedelta(minutes=study_session.planned_duration_minutes)
        if elapsed_time > planned_duration:
            raise StudySessionError(f"Session has already ended ({study_session.planned_duration_minutes}-minute limit exceeded)")
    
    try:
        student_assoc = SchoolHoursStudySessionStudent.get_by(
            first=True,
            school_hours_study_session_id=session_id,
            student_id=student_id
        )

        if student_assoc:
            student_assoc.emotional_state_before = emotional_state_before
            student_assoc.is_attendant = True
        
        session.commit()
        
        try:
            student = Student.get_by(id=student_id, first=True)
            if student and study_session.class_manager_id:
                course_name = None
                if study_session.learning_units:
                    first_unit = list(study_session.learning_units)[0]
                    course_name = first_unit.course.name
                
                emit_to_manager(
                    manager_id=study_session.class_manager_id,
                    event='student_joined_session',
                    data={
                        'session_id': session_id,
                        'student_id': student_id,
                        'student_name': student.full_name,
                        'status': 'PENDING',  # Still pending until they start the chat
                        'is_attendant': True,
                        'course_name': course_name
                    }
                )
        except Exception as e:
            print(f"Warning: Failed to emit student_joined_session event: {e}")
        
        return study_session
    
    except SQLAlchemyError as e:
        session.rollback()
        raise StudySessionError(f"Database error joining session: {str(e)}")


def complete_expired_school_sessions(class_manager_id: int) -> int:
    """Auto-complete school study sessions that have been PENDING for 60+ minutes without any student joining."""
    session = get_current_session()
    
    cutoff_time = datetime.now() - timedelta(minutes=60)

    expired_sessions = (
        session.query(SchoolHoursStudySession)
        .filter(
            SchoolHoursStudySession.class_manager_id == class_manager_id,
            SchoolHoursStudySession.status == SessionStatus.PENDING,
            SchoolHoursStudySession.start_time < cutoff_time
        )
        .all()
    )
    
    completed_count = 0
    for study_session in expired_sessions:
        has_attendants = False
        if study_session.students:
            for student_assoc in study_session.students:
                if student_assoc.is_attendant:
                    has_attendants = True
                    break

        if not has_attendants:
            study_session.status = SessionStatus.COMPLETED

            study_session.end_time = study_session.start_time + timedelta(
                minutes=study_session.planned_duration_minutes
            )
            completed_count += 1
    
    if completed_count > 0:
        session.commit()
    
    return completed_count


def end_session(
        session_id: int,
        student_id: int,
        emotional_state_after: EmotionalState,
        difficulty_feedback: int,
        understanding_feedback: int,
        textual_feedback: Optional[str] = None,
        session_type: str = 'home'
) -> Optional[Union[HomeHoursStudySession, SchoolHoursStudySession]]:
    """
    Complete a study session and trigger evaluation.
    Works for both home and school sessions.
    """
    db_session = get_current_session()

    if session_type == 'school':
        SessionModel = SchoolHoursStudySession
        PauseModel = SchoolHoursStudySessionPause
        AssocModel = SchoolHoursStudySessionStudent
        session_id_field = 'school_hours_study_session_id'
    else:
        SessionModel = HomeHoursStudySession
        PauseModel = HomeHoursStudySessionPause
        AssocModel = HomeHoursStudySessionStudent
        session_id_field = 'home_hours_study_session_id'

    study_session = SessionModel.get_by(id=session_id, first=True)
    if not study_session:
        raise SessionNotFoundError(f"Session {session_id} not found")

    if study_session.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
        raise InvalidSessionStateError(
            f"Cannot end session in {study_session.status} state"
        )

    try:
        if study_session.status == SessionStatus.PAUSED:
            active_pause = PauseModel.get_active_pause(session_id)
            if active_pause:
                active_pause.end_time = datetime.now()

        study_session.status = SessionStatus.COMPLETED
        study_session.end_time = datetime.now()

        # Update student association
        student_assoc = AssocModel.get_by(
            first=True,
            **{session_id_field: session_id, 'student_id': student_id}
        )
        if student_assoc:
            student_assoc.emotional_state_after = emotional_state_after
            student_assoc.difficulty_feedback = difficulty_feedback
            student_assoc.understanding_feedback = understanding_feedback
            student_assoc.textual_feedback = textual_feedback

        db_session.commit()

        if (
                session_type == 'school'
                and hasattr(study_session, 'class_manager_id')
                and study_session.class_manager_id
        ):
            try:
                student = Student.get_by(id=student_id, first=True)
                if student:
                    emit_to_manager(
                        manager_id=study_session.class_manager_id,
                        event='session_completed',
                        data={
                            'session_id': session_id,
                            'student_id': student_id,
                            'student_name': student.full_name,
                            'difficulty_feedback': difficulty_feedback,
                            'understanding_feedback': understanding_feedback
                        }
                    )
            except Exception as e:
                print(f"Warning: Failed to emit session_completed event: {e}")

        try:
            evaluate_session(session_id, student_id, session_type)
        except Exception as e:
            print(f"Warning: Evaluation failed for session {session_id}: {str(e)}")

        return study_session

    except SQLAlchemyError as e:
        db_session.rollback()
        raise StudySessionError(f"Database error ending session: {str(e)}")
