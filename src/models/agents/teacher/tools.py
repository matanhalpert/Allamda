"""
Tool implementations for Teacher agent.

This module contains all tool methods used by the Teacher agent for
retrieving student progress, Q&A resources, and test history.
"""

from typing import Dict, Any, Optional

from src.database.session_context import get_current_session
from ..base import agent_tool, ToolResponse
from .schemas import (
    LearningUnitMasteryParams,
    QAResourcesParams,
    StudentTestHistoryParams,
    RecentStudentEvaluationsParams,
    PrerequisiteUnitsStatusParams,
)
from src.utils.logger import Logger
from src.models.student_models import Student
from src.models.subject_models import QA, LearningUnit
from src.models.associations import LearningUnitStudent
from src.enums import QAType, EvaluationType


@agent_tool(
    description="Get student's mastery level for specific learning units in current session. Shows progress %, completion state, and recent proficiency scores. Essential for adaptive teaching - know if student is seeing this content for first time or fifth time.",
    parameters=LearningUnitMasteryParams.to_openai_schema()
)
def get_learning_unit_mastery(
        self, student_id: int, course_id: int, learning_unit_names: list[str]
) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve mastery information for specific learning units.
    Shows progress, completion state, and recent proficiency evaluations for each unit.
    Helps teacher adapt difficulty and pacing based on student's current mastery level.
    """
    student = Student.get_by(first=True, id=student_id)
    if not student:
        return ToolResponse.error_response(
            error_message="Student data not available",
            error_type="not_found",
            context={"student_id": student_id}
        )

    try:
        session = get_current_session()
        mastery_data = []
        
        for unit_name in learning_unit_names:
            learning_unit = LearningUnit.get_by(
                first=True,
                course_id=course_id,
                name=unit_name
            )
            if not learning_unit:
                mastery_data.append({
                    "learning_unit_name": unit_name,
                    "error": "Learning unit not found"
                })
                continue

            unit_progress = LearningUnitStudent.get_by(
                first=True,
                student_id=student_id,
                course_id=course_id,
                learning_unit_name=unit_name
            )
            
            if not unit_progress:
                # Student hasn't started this unit yet
                mastery_data.append({
                    "learning_unit_name": unit_name,
                    "description": learning_unit.description,
                    "state": "not_started",
                    "progress": 0.0,
                    "recent_proficiency_scores": [],
                    "is_first_time": True
                })
                continue
            
            recent_evals = student.get_recent_evaluations(
                EvaluationType.PROFICIENCY,
                limit=5
            )

            recent_scores = [eval_data.get('score') for eval_data in recent_evals if eval_data.get('score')]
            
            mastery_data.append({
                "learning_unit_name": unit_name,
                "description": learning_unit.description,
                "type": learning_unit.type.value if learning_unit.type else None,
                "state": unit_progress.state.value if unit_progress.state else "unknown",
                "progress": round(unit_progress.progress * 100, 1) if unit_progress.progress else 0.0,
                "recent_proficiency_scores": recent_scores[:3],  # Last 3 scores
                "is_first_time": unit_progress.progress == 0.0 or unit_progress.state.value == "not_started"
            })
        
        data = {
            "student_id": student_id,
            "student_name": student.full_name,
            "course_id": course_id,
            "learning_units": mastery_data,
            "summary": {
                "total_units": len(learning_unit_names),
                "not_started": sum(1 for u in mastery_data if u.get("state") == "not_started"),
                "in_progress": sum(1 for u in mastery_data if u.get("state") == "in_progress"),
                "completed": sum(1 for u in mastery_data if u.get("state") == "completed")
            }
        }
        
        return ToolResponse.success_response(data=data)
    except Exception as e:
        Logger.error(f"Error retrieving learning unit mastery for student {student_id}: {e}")
        return ToolResponse.error_response(
            error_message="Learning unit mastery data temporarily unavailable",
            error_type="unavailable",
            context={"student_id": student_id, "course_id": course_id, "exception": str(e)}
        )


@agent_tool(
    description="Get curriculum-aligned Q&A resources for a learning unit. Returns questions, answers, and exercises filtered by type (for_test/for_study) and difficulty (1-4). Use for examples, practice problems, and structured teaching content.",
    parameters=QAResourcesParams.to_openai_schema()
)
def get_qa_resources(
    self,
    course_id: int,
    learning_unit_name: str,
    qa_type: Optional[str] = None,
    level: Optional[int] = None
) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve Q&A resources for a specific learning unit.
    These resources provide teaching materials, examples, and exercises for the topic.
    The teacher can filter by Q&A type (for_test vs for_study) and difficulty level (1-4).
    Ensures curriculum alignment and pedagogical consistency.
    """
    try:
        filters = {
            'course_id': course_id,
            'learning_unit_name': learning_unit_name
        }
        if qa_type:
            # Convert "for_test" to "for test" (underscore to space) to match enum values
            filters['type'] = QAType(qa_type.replace('_', ' ').lower())
        if level:
            filters['level'] = level
        
        qas = QA.get_by(**filters)
        qa_list = [qa.to_dict() for qa in qas]
        
        data = {
            "course_id": course_id,
            "learning_unit_name": learning_unit_name,
            "filters": {
                "qa_type": qa_type,
                "level": level
            },
            "qas": qa_list,
            "total_count": len(qa_list)
        }
        
        return ToolResponse.success_response(data=data)
    except Exception as e:
        Logger.error(f"Error retrieving Q&A resources for course {course_id}, unit {learning_unit_name}: {e}")
        return ToolResponse.error_response(
            error_message="Q&A resources temporarily unavailable",
            error_type="unavailable",
            context={"course_id": course_id, "learning_unit_name": learning_unit_name, "exception": str(e)}
        )


@agent_tool(
    description="Get student's historical test performance, optionally filtered by learning units. Shows test scores, averages, and upcoming tests. Filter by current learning units to see relevant test history.",
    parameters=StudentTestHistoryParams.to_openai_schema()
)
def get_student_test_history(
        self,
        student_id: int,
        course_id: Optional[int] = None,
        learning_unit_names: Optional[list[str]] = None
) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve a student's test history and performance.
    Helps the teacher identify areas where the student needs additional support or excels.
    Can be filtered by course and/or specific learning units to focus on relevant content.
    """
    student = Student.get_by(first=True, id=student_id)
    if not student:
        return ToolResponse.error_response(
            error_message="Student data not available",
            error_type="not_found",
            context={"student_id": student_id}
        )

    try:
        test_history = student.get_test_history(course_id=course_id)
        upcoming_tests = student.get_upcoming_tests(course_id=course_id)

        if learning_unit_names:
            filtered_history = []
            for test in test_history:
                if test.get('learning_units'):
                    test_units = [lu.get('name') for lu in test.get('learning_units', [])]
                    if any(unit_name in test_units for unit_name in learning_unit_names):
                        filtered_history.append(test)
            
            filtered_upcoming = []
            for test in upcoming_tests:
                if test.get('learning_units'):
                    test_units = [lu.get('name') for lu in test.get('learning_units', [])]
                    if any(unit_name in test_units for unit_name in learning_unit_names):
                        filtered_upcoming.append(test)
            
            test_history = filtered_history
            upcoming_tests = filtered_upcoming
        
        data = {
            "student_id": student_id,
            "student_name": student.full_name,
            "filters": {
                "course_id": course_id,
                "learning_unit_names": learning_unit_names
            },
            "average_grade": student.get_average_grade(),
            "test_history": test_history,
            "test_count": len(test_history),
            "upcoming_tests": upcoming_tests
        }
        
        return ToolResponse.success_response(data=data)
    except Exception as e:
        Logger.error(f"Error retrieving test history for student {student_id}: {e}")
        return ToolResponse.error_response(
            error_message="Test history temporarily unavailable",
            error_type="unavailable",
            context={"student_id": student_id, "course_id": course_id, "exception": str(e)}
        )


@agent_tool(
    description="Get recent proficiency or investment evaluations with qualitative feedback. Shows what previous evaluators said about student's understanding and performance. Use to understand student's recent strengths and weaknesses.",
    parameters=RecentStudentEvaluationsParams.to_openai_schema()
)
def get_recent_student_evaluations(
        self,
        student_id: int,
        limit: int = 5,
        evaluation_type: str = "proficiency"
) -> ToolResponse[Dict[str, Any]]:
    """
    Retrieve recent AI evaluations with scores and descriptive feedback.
    Helps teacher understand recent performance trajectory and recurring issues.
    Proficiency evaluations focus on understanding; investment on engagement.
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

        scores = [e.get('score') for e in evaluations if e.get('score')]
        avg_score = round(sum(scores) / len(scores), 1) if scores else None

        trend = "stable"
        if len(scores) >= 3:
            recent_avg = sum(scores[:2]) / 2
            older_avg = sum(scores[-2:]) / 2
            if recent_avg > older_avg + 1:
                trend = "improving"
            elif recent_avg < older_avg - 1:
                trend = "declining"
        
        data = {
            "student_id": student_id,
            "student_name": student.full_name,
            "evaluation_type": evaluation_type,
            "evaluations": evaluations,
            "count": len(evaluations),
            "insights": {
                "average_score": avg_score,
                "score_range": f"{min(scores)}-{max(scores)}" if scores else None,
                "trend": trend,
                "latest_score": scores[0] if scores else None
            }
        }
        
        return ToolResponse.success_response(data=data)
    except Exception as e:
        Logger.error(f"Error retrieving evaluations for student {student_id}: {e}")
        return ToolResponse.error_response(
            error_message="Evaluation data temporarily unavailable",
            error_type="unavailable",
            context={"student_id": student_id, "exception": str(e)}
        )


@agent_tool(
    description="Check if student has mastered prerequisite learning units before teaching advanced concepts. Returns completion status and proficiency for prerequisites. Prevents teaching without foundational knowledge.",
    parameters=PrerequisiteUnitsStatusParams.to_openai_schema()
)
def get_prerequisite_units_status(
        self,
        student_id: int,
        course_id: int,
        learning_unit_names: list[str]
) -> ToolResponse[Dict[str, Any]]:
    """
    Check prerequisite mastery for learning units being taught.
    Returns status of all prerequisite units to ensure student has foundational knowledge.
    Helps teacher decide whether to review prerequisites before advancing.
    """
    student = Student.get_by(first=True, id=student_id)
    if not student:
        return ToolResponse.error_response(
            error_message="Student data not available",
            error_type="not_found",
            context={"student_id": student_id}
        )

    try:
        session = get_current_session()
        prerequisite_data = []
        all_prerequisites_met = True
        
        for unit_name in learning_unit_names:
            # Get learning unit
            learning_unit = LearningUnit.get_by(
                first=True,
                course_id=course_id,
                name=unit_name
            )
            
            if not learning_unit or not learning_unit.previous_learning_unit:
                prerequisite_data.append({
                    "learning_unit_name": unit_name,
                    "has_prerequisite": False,
                    "prerequisite_met": True
                })
                continue

            prereq_name = learning_unit.previous_learning_unit
            prereq_progress = LearningUnitStudent.get_by(
                first=True,
                student_id=student_id,
                course_id=course_id,
                learning_unit_name=prereq_name
            )
            
            if not prereq_progress:
                prerequisite_data.append({
                    "learning_unit_name": unit_name,
                    "has_prerequisite": True,
                    "prerequisite_name": prereq_name,
                    "prerequisite_state": "not_started",
                    "prerequisite_progress": 0.0,
                    "prerequisite_met": False
                })
                all_prerequisites_met = False
                continue

            is_met = (
                prereq_progress.state.value == "completed" or
                (prereq_progress.progress and prereq_progress.progress >= 0.7)  # 70% threshold
            )
            
            if not is_met:
                all_prerequisites_met = False
            
            prerequisite_data.append({
                "learning_unit_name": unit_name,
                "has_prerequisite": True,
                "prerequisite_name": prereq_name,
                "prerequisite_state": prereq_progress.state.value if prereq_progress.state else "unknown",
                "prerequisite_progress": round(prereq_progress.progress * 100, 1) if prereq_progress.progress else 0.0,
                "prerequisite_met": is_met
            })
        
        data = {
            "student_id": student_id,
            "student_name": student.full_name,
            "course_id": course_id,
            "learning_units_checked": learning_unit_names,
            "prerequisites": prerequisite_data,
            "all_prerequisites_met": all_prerequisites_met,
            "units_with_unmet_prerequisites": sum(1 for p in prerequisite_data if not p.get("prerequisite_met"))
        }
        
        return ToolResponse.success_response(data=data)
    except Exception as e:
        Logger.error(f"Error checking prerequisites for student {student_id}: {e}")
        return ToolResponse.error_response(
            error_message="Prerequisite status temporarily unavailable",
            error_type="unavailable",
            context={"student_id": student_id, "course_id": course_id, "exception": str(e)}
        )
