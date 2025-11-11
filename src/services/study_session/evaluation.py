"""
Study Session Evaluation

Functions for AI-powered evaluation of completed study sessions.
"""

from datetime import datetime
from typing import Tuple
from pydantic import ValidationError

from src.database.decorators import with_db_session
from src.database.session_context import get_current_session
from src.models.session_models import HomeHoursStudySession, SchoolHoursStudySession
from src.models.evaluation_models import SessionalProficiencyEvaluation, SessionalInvestmentEvaluation
from src.models.agents import Evaluator
from src.models.agents.evaluator import EvaluationResponse
from src.models.student_models import Student
from src.models.associations import (
    SessionalProficiencyEvaluationHomeHoursStudySession,
    SessionalInvestmentEvaluationHomeHoursStudySession,
    SessionalProficiencyEvaluationSchoolHoursStudySession,
    SessionalInvestmentEvaluationSchoolHoursStudySession
)
from src.utils.logger import Logger
from .exceptions import SessionNotFoundError, StudySessionError


@with_db_session
def evaluate_session(
        session_id: int,
        student_id: int,
        session_type: str = 'home'
) -> Tuple[SessionalProficiencyEvaluation, SessionalInvestmentEvaluation]:
    """Create AI-powered evaluations for a completed study session.
    
    Works for both home and school sessions.
    
    Args:
        session_id: ID of the study session
        student_id: ID of the student
        session_type: Type of session ('home' or 'school'), defaults to 'home'
    """
    session = get_current_session()

    if session_type == 'school':
        SessionModel = SchoolHoursStudySession
        ProficiencyAssocModel = SessionalProficiencyEvaluationSchoolHoursStudySession
        InvestmentAssocModel = SessionalInvestmentEvaluationSchoolHoursStudySession
        session_id_field = 'school_hours_study_session_id'
    else:
        SessionModel = HomeHoursStudySession
        ProficiencyAssocModel = SessionalProficiencyEvaluationHomeHoursStudySession
        InvestmentAssocModel = SessionalInvestmentEvaluationHomeHoursStudySession
        session_id_field = 'home_hours_study_session_id'

    study_session = SessionModel.get_by(id=session_id, first=True)
    if not study_session:
        raise SessionNotFoundError(f"Session {session_id} not found")

    evaluator = Evaluator.get_by(first=True)
    if not evaluator:
        raise StudySessionError("No evaluator agent available")

    transcript = study_session.get_transcript()

    try:
        proficiency_prompt = f"""
        Analyze this study session and evaluate the student's proficiency in the subject.
        
        SESSION CONTEXT:
        - Session ID: {session_id}
        - Session Type: {session_type}
        - Student ID: {student_id}
        
        YOUR TASK:
        Evaluate the student's understanding and mastery of the material covered in this session.
        
        CRITICAL - Use get_session_context first:
        - Call get_session_context({session_id}, "{session_type}") to understand what course and learning units were studied
        - Evaluate the student's responses relative to those specific learning units
        - If relevant, Reference specific learning unit concepts in your evaluation
        
        EVALUATION CRITERIA:
        - Correctness of answers to questions about the learning units
        - Depth of understanding demonstrated in explanations
        - Ability to apply concepts from the learning units
        - Progress made during the session
        - Quality of questions asked showing comprehension
        
        OPTIONAL TOOLS:
        - get_student_test_performance: Compare with historical test scores in this subject
        - get_student_evaluation_history: Check for trends in proficiency over time
        
        Do not consider investment factors (engagement, dedication) - focus only on proficiency.
        
        Transcript:
        {transcript}
        
        Provide a proficiency score from 1-10 and a detailed evaluation description (2-3 sentences minimum).
        Include specific references to learning unit concepts and student understanding.
        """

        proficiency_response = evaluator.generate_structured_response(
            messages=[{"role": "user", "content": proficiency_prompt}],
            response_model=EvaluationResponse,
            temperature=0.3
        )

        proficiency_eval = SessionalProficiencyEvaluation(
            student_id=student_id,
            evaluator_id=evaluator.ai_model_id,
            date=datetime.now().date(),
            score=proficiency_response.evaluation_score,
            evaluator_evaluation_description=proficiency_response.evaluation_description
        )
        session.add(proficiency_eval)
        session.flush()

        prof_session_link = ProficiencyAssocModel(
            sessional_proficiency_evaluation_id=proficiency_eval.id,
            **{session_id_field: session_id}
        )
        session.add(prof_session_link)

        investment_prompt = f"""
        Analyze this study session and evaluate the student's investment and engagement.
        
        SESSION CONTEXT:
        - Session ID: {session_id}
        - Session Type: {session_type}
        - Student ID: {student_id}
        
        YOUR TASK:
        Evaluate the student's effort, participation, focus, and dedication during this session.
        
        CRITICAL - MUST USE THESE TOOLS:
        - Call get_session_pause_statistics({session_id}, "{session_type}") - MANDATORY
          * This is the PRIMARY metric for investment evaluation
          * Pause percentage directly indicates engagement vs distraction
          * ALWAYS include pause statistics in your evaluation description
        
        - Call get_session_message_statistics({session_id}, "{session_type}") - HIGHLY RECOMMENDED
          * Provides quantitative engagement metrics from the conversation
          * Message counts, lengths, and question frequency
          * Supplements pause statistics with participation data
        
        EVALUATION CRITERIA:
        - Pause percentage (from tool) - primary factor in scoring
        - Message engagement metrics (from tool) - participation level
        - Quality of participation visible in transcript
        - Responsiveness and attentiveness
        - Initiative in asking questions and seeking clarification
        - Signs of distraction or off-topic behavior
        
        OPTIONAL TOOLS:
        - get_student_evaluation_history: Check for trends in investment over time
        
        Do not consider proficiency factors (understanding, correctness) - focus only on investment.
        
        Transcript:
        {transcript}
        
        Provide an investment score from 1-10 and a detailed evaluation description (2-3 sentences minimum).
        MUST include specific pause percentage and message statistics in your description.
        """

        investment_response = evaluator.generate_structured_response(
            messages=[{"role": "user", "content": investment_prompt}],
            response_model=EvaluationResponse,
            temperature=0.3
        )

        student = Student.get_by(id=student_id, first=True)

        class_manager = None
        if student and student.classes:
            student_class = student.classes[0]
            if student_class.class_managers:
                class_manager = student_class.class_managers[0]

        if class_manager:
            investment_eval = SessionalInvestmentEvaluation(
                student_id=student_id,
                evaluator_id=evaluator.ai_model_id,
                class_manager_id=class_manager.id,
                date=datetime.now().date(),
                score=investment_response.evaluation_score,
                evaluator_evaluation_description=investment_response.evaluation_description
            )
            session.add(investment_eval)
            session.flush()

            inv_session_link = InvestmentAssocModel(
                sessional_investment_evaluation_id=investment_eval.id,
                **{session_id_field: session_id}
            )
            session.add(inv_session_link)
        else:
            investment_eval = None

        session.commit()

        return proficiency_eval, investment_eval

    except ValidationError as e:
        session.rollback()
        Logger.error(f"Validation error in evaluation for session {session_id}: {e}")
        raise StudySessionError(f"Failed to validate evaluation response: {str(e)}")

    except ValueError as e:
        session.rollback()
        Logger.error(f"Value error in evaluation for session {session_id}: {e}")
        raise StudySessionError(f"Failed to parse evaluation response: {str(e)}")

    except Exception as e:
        session.rollback()
        Logger.error(f"Unexpected error creating evaluations for session {session_id}: {e}")
        raise StudySessionError(f"Error creating evaluations: {str(e)}")
