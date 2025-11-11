"""
Tool implementations for Evaluator agent.

This module contains all tool methods used by the Evaluator agent for
assessing student performance, attendance, and evaluation history.
"""

from typing import Dict, Any, Optional

from src.database.session_context import get_current_session
from ..base import agent_tool, ToolResponse
from .schemas import (
    StudentTestPerformanceParams,
    StudentEvaluationHistoryParams,
    SessionPauseStatisticsParams,
    SessionContextParams,
    SessionMessageStatisticsParams,
)
from src.utils.logger import Logger
from src.models.student_models import Student
from src.models.session_models import HomeHoursStudySession, SchoolHoursStudySession
from src.enums import SubjectName, EvaluationType, MessageType


@agent_tool(
    description="Get student's historical test performance to compare with session proficiency. Returns test scores, averages, and trends. Use to validate if session performance aligns with past academic achievement.",
    parameters=StudentTestPerformanceParams.to_openai_schema()
)
def get_student_test_performance(
        self, student_id: int, subject_name: Optional[str] = None
) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve comprehensive test performance data for a student.
    Returns test history, average grades, and performance trends for proficiency evaluation.
    Use this to provide historical context - does session performance match test scores?
    """
    student = Student.get_by(first=True, id=student_id)
    if not student:
        return ToolResponse.error_response(
            error_message="Student data not available",
            error_type="not_found",
            context={"student_id": student_id}
        )
    
    try:
        subject_filter = SubjectName(subject_name) if subject_name else None
        test_history = student.get_test_history(subject_filter=subject_filter)

        data = {
            "student_id": student_id,
            "student_name": student.full_name,
            "subject_filter": subject_name,
            "average_grade": student.get_average_grade(),
            "test_history": test_history,
            "upcoming_tests": student.get_upcoming_tests(subject_filter=subject_filter),
            "total_tests_completed": len(test_history)
        }
        
        return ToolResponse.success_response(data=data)
    except Exception as e:
        Logger.error(f"Error retrieving test performance for student {student_id}: {e}")
        return ToolResponse.error_response(
            error_message="Performance data temporarily unavailable",
            error_type="unavailable",
            context={"student_id": student_id, "exception": str(e)}
        )


@agent_tool(
    description="Get student's previous proficiency or investment evaluations to identify trends over time. Use to maintain evaluation consistency and avoid sudden score jumps. Helps contextualize current session relative to recent performance.",
    parameters=StudentEvaluationHistoryParams.to_openai_schema()
)
def get_student_evaluation_history(self, student_id: int, evaluation_type: str, limit: int = 5) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve previous evaluations for a student to understand performance trends.
    Helps provide context for new evaluations and identify improvement or decline patterns.
    Use this for consistency - are they improving, declining, or stable?
    """
    student = Student.get_by(first=True, id=student_id)
    if not student:
        return ToolResponse.error_response(
            error_message="Student data not available",
            error_type="not_found",
            context={"student_id": student_id}
        )
    
    try:
        eval_type = EvaluationType(evaluation_type.lower())
        evaluations = student.get_recent_evaluations(eval_type, limit=limit)
        
        data = {
            "student_id": student_id,
            "student_name": student.full_name,
            "evaluation_type": evaluation_type,
            "evaluations": evaluations,
            "total_returned": len(evaluations)
        }
        
        return ToolResponse.success_response(data=data)
    except Exception as e:
        Logger.error(f"Error retrieving evaluation history for student {student_id}: {e}")
        return ToolResponse.error_response(
            error_message="Evaluation history temporarily unavailable",
            error_type="unavailable",
            context={"student_id": student_id, "exception": str(e)}
        )


@agent_tool(
    description="CRITICAL for investment evaluation: Get pause statistics showing percentage of session time spent paused vs actively engaged. Low pause % = high investment, high pause % = poor engagement. This is the PRIMARY metric for assessing investment.",
    parameters=SessionPauseStatisticsParams.to_openai_schema()
)
def get_session_pause_statistics(
        self, session_id: int, session_type: str
) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve pause statistics for a study session.
    Returns the percentage of session time spent in pauses, which helps assess
    student investment and dedication during the session.
    MANDATORY for investment evaluations - this is one of the most important engagement metric.
    """
    if session_type.lower() == "home":
        study_session = HomeHoursStudySession.get_by(first=True, id=session_id)
    elif session_type.lower() == "school":
        study_session = SchoolHoursStudySession.get_by(first=True, id=session_id)
    else:
        return ToolResponse.error_response(
            error_message="Invalid session type",
            error_type="invalid_parameter",
            context={"session_type": session_type}
        )
    
    if not study_session:
        return ToolResponse.error_response(
            error_message="Study session not found",
            error_type="not_found",
            context={"session_id": session_id, "session_type": session_type}
        )
    
    if not study_session.end_time:
        return ToolResponse.error_response(
            error_message="Session has not ended yet, cannot calculate pause statistics",
            error_type="invalid_state",
            context={"session_id": session_id, "session_type": session_type}
        )
    
    try:
        session_duration_seconds = study_session.duration.total_seconds()
        pauses = study_session.pauses
        
        if not pauses or len(pauses) == 0:
            data = {
                "session_id": session_id,
                "session_type": session_type,
                "session_duration_minutes": round(session_duration_seconds / 60, 2),
                "total_pause_duration_minutes": 0,
                "pause_percentage": 0.0,
                "pause_count": 0
            }
            return ToolResponse.success_response(data=data)
        
        total_pause_seconds = 0
        for pause in pauses:
            if pause.duration:  # Only count completed pauses (those with duration)
                total_pause_seconds += pause.duration.total_seconds()

        pause_percentage = (total_pause_seconds / session_duration_seconds) * 100 if session_duration_seconds > 0 else 0.0
        
        data = {
            "session_id": session_id,
            "session_type": session_type,
            "session_duration_minutes": round(session_duration_seconds / 60, 2),
            "total_pause_duration_minutes": round(total_pause_seconds / 60, 2),
            "pause_percentage": round(pause_percentage, 2),
            "pause_count": len([p for p in pauses if p.duration])  # Count only completed pauses
        }
        
        return ToolResponse.success_response(data=data)
        
    except Exception as e:
        Logger.error(f"Error calculating pause statistics for session {session_id}: {e}")
        return ToolResponse.error_response(
            error_message="Failed to calculate pause statistics",
            error_type="unavailable",
            context={"session_id": session_id, "session_type": session_type, "exception": str(e)}
        )


@agent_tool(
    description="CRITICAL for proficiency evaluation: Get the course, subject, and learning units covered in the session. Essential to understand WHAT was being taught so you can assess mastery relative to specific learning objectives. Always call this FIRST for proficiency.",
    parameters=SessionContextParams.to_openai_schema()
)
def get_session_context(
        self, session_id: int, session_type: str
) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve comprehensive context about what was studied in a session.
    Returns course information, subject, and all learning units covered.
    Essential for evaluating proficiency relative to session content.
    MANDATORY for proficiency evaluations - you cannot assess understanding without knowing the topic.
    """
    if session_type.lower() == "home":
        study_session = HomeHoursStudySession.get_by(first=True, id=session_id)
    elif session_type.lower() == "school":
        study_session = SchoolHoursStudySession.get_by(first=True, id=session_id)
    else:
        return ToolResponse.error_response(
            error_message="Invalid session type",
            error_type="invalid_parameter",
            context={"session_type": session_type}
        )
    
    if not study_session:
        return ToolResponse.error_response(
            error_message="Study session not found",
            error_type="not_found",
            context={"session_id": session_id, "session_type": session_type}
        )
    
    try:
        learning_units = study_session.learning_units
        
        if not learning_units or len(learning_units) == 0:
            return ToolResponse.error_response(
                error_message="No learning units associated with this session",
                error_type="not_found",
                context={"session_id": session_id, "session_type": session_type}
            )

        first_unit = learning_units[0]
        course = first_unit.course
        subject = course.subject if course else None
        
        learning_units_data = []
        for unit in learning_units:
            learning_units_data.append({
                "name": unit.name,
                "description": unit.description,
                "type": unit.type.value if unit.type else None,
                "weight": unit.weight,
                "estimated_duration_minutes": unit.estimated_duration_minutes
            })
        
        data = {
            "session_id": session_id,
            "session_type": session_type,
            "course": {
                "id": course.id if course else None,
                "name": course.name if course else None,
                "grade_level": course.grade_level.value if course and course.grade_level else None,
                "type": course.type.value if course and course.type else None,
                "level": course.level if course else None,
                "description": course.description if course else None
            },
            "subject": {
                "name": subject.name.value if subject and subject.name else None,
                "description": subject.description if subject else None
            },
            "learning_units": learning_units_data,
            "total_learning_units": len(learning_units_data)
        }
        
        return ToolResponse.success_response(data=data)
        
    except Exception as e:
        Logger.error(f"Error retrieving session context for session {session_id}: {e}")
        return ToolResponse.error_response(
            error_message="Failed to retrieve session context",
            error_type="unavailable",
            context={"session_id": session_id, "session_type": session_type, "exception": str(e)}
        )


@agent_tool(
    description="Get quantitative conversation metrics for investment evaluation: student message count, average length, question frequency, and response ratio. Complements pause statistics by measuring active participation level. High message count + questions = strong engagement.",
    parameters=SessionMessageStatisticsParams.to_openai_schema()
)
def get_session_message_statistics(
        self, session_id: int, session_type: str
) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve message-level statistics for a study session.
    Returns counts, lengths, and patterns of student vs teacher messages.
    Helps assess student engagement through conversation metrics.
    Use alongside pause statistics for comprehensive investment assessment.
    """
    if session_type.lower() == "home":
        study_session = HomeHoursStudySession.get_by(first=True, id=session_id)
    elif session_type.lower() == "school":
        study_session = SchoolHoursStudySession.get_by(first=True, id=session_id)
    else:
        return ToolResponse.error_response(
            error_message="Invalid session type",
            error_type="invalid_parameter",
            context={"session_type": session_type}
        )
    
    if not study_session:
        return ToolResponse.error_response(
            error_message="Study session not found",
            error_type="not_found",
            context={"session_id": session_id, "session_type": session_type}
        )
    
    try:
        messages = study_session.get_messages(order_by_timestamp=True)
        
        if not messages or len(messages) == 0:
            return ToolResponse.error_response(
                error_message="No messages found in this session",
                error_type="not_found",
                context={"session_id": session_id, "session_type": session_type}
            )
        
        student_messages = [msg for msg in messages if msg.type == MessageType.PROMPT]
        teacher_messages = [msg for msg in messages if msg.type == MessageType.RESPONSE]

        student_count = len(student_messages)
        teacher_count = len(teacher_messages)
        
        student_avg_length = sum(len(msg.content) for msg in student_messages) / student_count if student_count > 0 else 0
        teacher_avg_length = sum(len(msg.content) for msg in teacher_messages) / teacher_count if teacher_count > 0 else 0

        student_question_count = sum(1 for msg in student_messages if '?' in msg.content)

        response_ratio = student_count / teacher_count if teacher_count > 0 else 0
        
        data = {
            "session_id": session_id,
            "session_type": session_type,
            "total_messages": len(messages),
            "student_messages": {
                "count": student_count,
                "average_length_chars": round(student_avg_length, 2),
                "question_count": student_question_count
            },
            "teacher_messages": {
                "count": teacher_count,
                "average_length_chars": round(teacher_avg_length, 2)
            },
            "engagement_metrics": {
                "student_response_ratio": round(response_ratio, 2),
                "question_frequency": round(student_question_count / student_count, 2) if student_count > 0 else 0
            }
        }
        
        return ToolResponse.success_response(data=data)
        
    except Exception as e:
        Logger.error(f"Error calculating message statistics for session {session_id}: {e}")
        return ToolResponse.error_response(
            error_message="Failed to calculate message statistics",
            error_type="unavailable",
            context={"session_id": session_id, "session_type": session_type, "exception": str(e)}
        )
