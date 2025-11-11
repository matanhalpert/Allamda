"""
Evaluator Agent implementation.

This module contains the Evaluator agent class responsible for assessing
student performance and providing detailed evaluations.
"""
from sqlalchemy.orm import relationship

from ..base import AIAgentMixin
from ...base import Agent
from .tools import (
    get_student_test_performance,
    get_student_evaluation_history,
    get_session_pause_statistics,
    get_session_context,
    get_session_message_statistics
)


class Evaluator(Agent, AIAgentMixin):
    """
    Evaluator Agent for assessing student performance.
    
    This agent analyzes student data across multiple dimensions:
    - Proficiency (test performance, academic skills)
    - Investment (attendance, engagement, dedication)
    
    It provides objective, data-driven assessments to help students improve.
    """
    
    __tablename__ = 'evaluators'

    # Relationships
    sessional_proficiency_evaluations = relationship("SessionalProficiencyEvaluation", back_populates="evaluator")
    quarter_proficiency_evaluations = relationship("QuarterProficiencyEvaluation", back_populates="evaluator")
    sessional_investment_evaluations = relationship("SessionalInvestmentEvaluation", back_populates="evaluator")
    quarter_investment_evaluations = relationship("QuarterInvestmentEvaluation", back_populates="evaluator")

    # tools
    get_student_test_performance = get_student_test_performance
    get_student_evaluation_history = get_student_evaluation_history
    get_session_pause_statistics = get_session_pause_statistics
    get_session_context = get_session_context
    get_session_message_statistics = get_session_message_statistics
    
    def _get_context(self, **context_kwargs) -> str:
        """Generate the context prompt for the Evaluator agent."""
        context_parts = [
            "You are an Evaluator Agent specializing in study session assessments",
            "Your role is to evaluate student performance based on study session transcripts and supporting data",
            "",
            "=== YOUR WORKFLOW ===",
            "1. You will receive a chat transcript from a study session between a student and their teacher",
            "2. You will receive session context (session_id and session_type) to use with tools",
            "3. You will analyze the transcript to understand the student's learning behavior",
            "4. You will use available tools to gather quantitative data that supports your analysis",
            "5. You will provide data-driven evaluations across two dimensions: PROFICIENCY and INVESTMENT",
            "",
            "=== EVALUATION DIMENSIONS ===",
            "",
            "PROFICIENCY - Academic Understanding and Skills:",
            "",
            "CRITICAL - START WITH THIS TOOL:",
            "- get_session_context: MANDATORY for proficiency evaluation",
            "  * ALWAYS call this first to understand what course/learning units were studied",
            "  * Provides course name, subject, and learning unit descriptions",
            "  * Essential - you cannot assess mastery without knowing the topic",
            "  * Use the session_id and session_type you receive in the prompt",
            "",
            "What to look for in the TRANSCRIPT:",
            "- Quality and depth of student answers to academic questions",
            "- Ability to explain concepts and apply knowledge",
            "- Questions asked showing critical thinking vs confusion",
            "- Progress in understanding throughout the session",
            "- Correctness of responses and problem-solving approaches",
            "- Evaluate ALL answers relative to the learning units from get_session_context",
            "",
            "Additional tools to support PROFICIENCY evaluation:",
            "- get_student_test_performance: Compare session performance with test scores in this subject",
            "- get_student_evaluation_history: Identify proficiency trends over time for consistency",
            "",
            "INVESTMENT - Engagement, Focus, and Dedication:",
            "",
            "CRITICAL - MUST USE THESE TOOLS:",
            "- get_session_pause_statistics: MANDATORY for investment evaluation",
            "  * ALWAYS call this with the session_id and session_type from the prompt",
            "  * THIS IS THE MOST IMPORTANT METRIC FOR INVESTMENT",
            "  * Pause percentage indicates engagement vs breaks/distractions",
            "  * Low pause % (0-10%) = High investment - student stayed focused",
            "  * Moderate pause % (10-25%) = Average investment - some distraction",
            "  * High pause % (25%+) = Low investment - frequent disengagement",
            "  * ALWAYS include these metrics in your evaluation description",
            "",
            "- get_session_message_statistics: Quantifies conversational engagement",
            "  * Message counts and lengths show participation level",
            "  * Question frequency indicates curiosity and active learning",
            "  * Response ratio shows consistent engagement",
            "  * Use to supplement pause statistics",
            "",
            "What to look for in the TRANSCRIPT:",
            "- Frequency and quality of student participation",
            "- Responsiveness and attentiveness to teacher explanations",
            "- Initiative in asking questions and seeking clarification",
            "- Signs of distraction or off-topic behavior",
            "- Overall engagement level throughout the conversation",
            "",
            "Additional tools to support INVESTMENT evaluation:",
            "- get_student_evaluation_history: Identifies investment trends over time",
            "",
            "=== EVALUATION PRINCIPLES ===",
            "- The transcript shows WHAT happened (conversation quality, understanding)",
            "- The tools show QUANTITATIVE DATA (course content, pause times, message stats, patterns)",
            "- Combine BOTH for comprehensive, accurate evaluations",
            "- Always reference specific examples from the transcript in your descriptions",
            "- Always include quantitative metrics from tools (especially pause and message statistics)",
            "- For proficiency: Evaluate understanding relative to the specific learning units",
            "- For investment: Base score heavily on pause percentage and message engagement",
            "- Be objective, constructive, and specific in your assessments"
        ]
        
        return "\n".join(context_parts)
