"""
Teacher Agent implementation.

This module contains the Teacher agent class responsible for providing
personalized instruction to students.
"""

from typing import List, Union, Optional, Any
from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ..base import AIAgentMixin
from ...base import Agent
from src.enums import SubjectName, EmotionalState, HomeHoursStudySessionType, SchoolHoursStudySessionType
from src.models.session_models import HomeHoursStudySession
from .tools import (
    get_learning_unit_mastery,
    get_qa_resources,
    get_student_test_history,
    get_recent_student_evaluations,
    get_prerequisite_units_status
)


class Teacher(Agent, AIAgentMixin):
    """
    Teacher Agent for personalized instruction.
    
    This agent provides adaptive teaching based on:
    - Student learning profiles (learning style, routine preference, collaboration style)
    - Session type (individual, group, test preparation, homework)
    - Emotional states of students
    - Learning content (courses, learning units)
    
    The teacher adapts explanations, pacing, and interaction style to maximize
    learning effectiveness for each student.
    """
    
    __tablename__ = 'teachers'

    subject_name = Column(Enum(SubjectName), ForeignKey('subjects.name'), nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="teachers")
    home_study_sessions = relationship("HomeHoursStudySession", back_populates="teacher")
    school_study_sessions = relationship("SchoolHoursStudySession", back_populates="teacher")
    sent_messages = relationship("Message", back_populates="teacher")
    test_students = relationship("TestStudent", back_populates="teacher")

    # Tools
    get_learning_unit_mastery = get_learning_unit_mastery
    get_qa_resources = get_qa_resources
    get_student_test_history = get_student_test_history
    get_recent_student_evaluations = get_recent_student_evaluations
    get_prerequisite_units_status = get_prerequisite_units_status
    
    def _get_teacher_role_context(self) -> List[str]:
        """Generate basic teacher role and expertise context."""
        subject = self.subject_name
        return [
            f"Your name is {self.name}",
            f"You are a {subject.title()} Teacher Agent with multimodal vision capabilities",
            f"Your subject expertise is in {subject}",
            "You help students learn effectively through personalized guidance",
            "You adapt your teaching style to each student's learning preferences",
            "You provide clear explanations and encourage critical thinking",
            "You communicate clearly and foster a supportive learning environment",
            "",
            "MULTIMODAL CAPABILITIES:",
            "- You have full vision capabilities and CAN see and analyze images that students send",
            "- When students share images, directly describe what you see and provide specific feedback",
            "- Do NOT say you cannot see or identify images - you have complete visual access",
            "- Confidently analyze diagrams, photos, equations, handwriting, or any visual content",
            "- Use the visual information to provide detailed, relevant guidance"
        ]
    
    @staticmethod
    def _get_student_profiles_context(students: List[Any]) -> List[str]:
        """Generate learning profile context for one or more students."""
        context_parts = []
        
        if len(students) == 1:
            # Single student - original format
            student = students[0]
            learning_profile = student.get_learning_profile()
            context_parts.extend([
                "\n--- Student Profile ---",
                f"Student Name: {student.full_name}",
                f"Learning Style: {learning_profile.get('learning_style')}",
                "Please adapt your explanations and examples to match this learning style",
                f"Routine Preference: {learning_profile.get('routine_style')}",
                "Adjust your pacing and structure to align with this routine preference",
                f"Collaboration Style: {learning_profile.get('collaboration_style')}",
                "Tailor your interaction approach to match this collaboration style"
            ])
        else:
            # Multiple students - group format
            context_parts.append("\n--- Student Profiles ---")
            context_parts.append(f"This is a group session with {len(students)} students:")
            
            for student in students:
                learning_profile = student.get_learning_profile()
                context_parts.extend([
                    f"\nStudent: {student.full_name}",
                    f"  Learning Style: {learning_profile.get('learning_style')}",
                    f"  Routine Preference: {learning_profile.get('routine_style')}",
                    f"  Collaboration Style: {learning_profile.get('collaboration_style')}"
                ])
            
            context_parts.append("\nAdapt your teaching to accommodate diverse learning styles in this group setting")
        
        return context_parts
    
    @staticmethod
    def _get_session_type_context(study_session: Any) -> List[str]:
        """Generate session type and category context with appropriate guidance."""
        context_parts = ["\n--- Current Session Context ---"]
        
        session_type = study_session.type
        session_category = "Home Study" if isinstance(study_session, HomeHoursStudySession) else "School Study"
        
        context_parts.append(f"Session Category: {session_category}")
        context_parts.append(f"Session Type: {session_type.title()}")
        
        # Session type guidance
        if session_type in [HomeHoursStudySessionType.TEST_PREPARATION, HomeHoursStudySessionType.HOMEWORK]:
            context_parts.append(f"This is a {session_type} session - focus on practical application and reinforcement")
        elif session_type == SchoolHoursStudySessionType.INDIVIDUAL:
            context_parts.append("This is an individual session - provide personalized, focused instruction")
        elif session_type == SchoolHoursStudySessionType.GROUP:
            context_parts.append("This is a group session - encourage collaboration and peer learning")
        
        return context_parts
    
    @staticmethod
    def _get_learning_content_context(study_session: Any) -> List[str]:
        """Generate learning content context including course and learning units information."""
        context_parts = []

        if not study_session.learning_units:
            return context_parts

        learning_units = list(study_session.learning_units)
        course = learning_units[0].course

        context_parts.append("\n--- Learning Content ---")
        context_parts.append(f"Course: {course.name}")
        if course.description:
            context_parts.append(f"Course Description: {course.description}")

        unit_count = len(learning_units)
        unit_word = "learning unit" if unit_count == 1 else "learning units"
        context_parts.append(f"This session covers {unit_count} {unit_word}:")

        for unit in learning_units:
            context_parts.append(f"\nLearning Unit: {unit.name}")
            context_parts.append(f"  Type: {unit.type.title()}")
            if unit.description:
                context_parts.append(f"  Description: {unit.description}")
            if unit.previous_learning_unit:
                context_parts.append(f"  Previous Unit: {unit.previous_learning_unit}")
            if unit.next_learning_unit:
                context_parts.append(f"  Next Unit: {unit.next_learning_unit}")

        return context_parts
    
    def _get_emotional_states_context(
        self,
        study_session: Any,
        students: List[Any]
    ) -> List[str]:
        """Generate emotional state context for all students in the session."""
        context_parts = []

        student_emotions = []
        for student in students:
            student_session_record = self._get_student_session_record(study_session, student.id)
            if student_session_record and student_session_record.emotional_state_before:
                student_emotions.append({
                    'student': student,
                    'state': student_session_record.emotional_state_before
                })
        
        if not student_emotions:
            return context_parts
        
        if len(student_emotions) == 1:
            emotional_state = student_emotions[0]['state']
            context_parts.append(f"\nStudent's Emotional State at Session Start: {emotional_state.title()}")
            
            if emotional_state == EmotionalState.NEGATIVE:
                context_parts.append("The student is feeling negative - be extra supportive, patient, and encouraging")
            elif emotional_state == EmotionalState.EXTREME:
                context_parts.append("The student is in an extreme emotional state - prioritize emotional support and take a gentle approach")
            elif emotional_state == EmotionalState.POSITIVE:
                context_parts.append("The student is feeling positive - leverage this energy for engaging and challenging content")
            elif emotional_state == EmotionalState.NEUTRAL:
                context_parts.append("The student is in a neutral state - maintain a balanced and engaging approach")
        else:
            context_parts.append("\n--- Student Emotional States at Session Start ---")
            for item in student_emotions:
                student = item['student']
                emotional_state = item['state']
                context_parts.append(f"{student.full_name}: {emotional_state.title()}")

            context_parts.append("\nBe mindful of the diverse emotional states in the group:")
            
            if any(item['state'] == EmotionalState.EXTREME for item in student_emotions):
                context_parts.append("- Some students are in extreme emotional states - prioritize emotional support")
            if any(item['state'] == EmotionalState.NEGATIVE for item in student_emotions):
                context_parts.append("- Some students are feeling negative - provide extra encouragement and patience")
            if any(item['state'] == EmotionalState.POSITIVE for item in student_emotions):
                context_parts.append("- Some students are feeling positive - leverage their energy to uplift the group")
        
        return context_parts
    
    @staticmethod
    def _get_student_session_record(
        study_session: Any,
        student_id: int
    ) -> Optional[Any]:
        """Get the student's record from the study session to access emotional state and other data."""
        for student_record in study_session.students:
            if student_record.student_id == student_id:
                return student_record
        return None
    
    @staticmethod
    def _get_adaptive_teaching_guidance(study_session: Any, students: List[Any]) -> List[str]:
        """Generate guidance on adaptive teaching and tool usage."""
        learning_units = list(study_session.learning_units) if study_session.learning_units else []
        course = learning_units[0].course if learning_units else None
        student = students[0] if len(students) == 1 else None
        
        context_parts = [
            "\n--- Adaptive Teaching Strategy ---",
            ""
        ]
        
        if student and course and learning_units:
            # Single student - provide specific mandatory guidance
            unit_names = [unit.name for unit in learning_units]
            unit_names_str = ", ".join(f"'{name}'" for name in unit_names)
            
            context_parts.extend([
                "═══════════════════════════════════════════",
                "🚨 CRITICAL: YOU MUST USE TOOLS 🚨",
                "═══════════════════════════════════════════",
                "",
                "Tools are ESSENTIAL for adaptive teaching. You MUST use them to provide personalized instruction.",
                "",
                "MANDATORY AT SESSION START (first teacher response):",
                "",
                "1. ALWAYS call get_learning_unit_mastery FIRST:",
                f"   → get_learning_unit_mastery(student_id={student.id}, course_id={course.id}, learning_unit_names=[{unit_names_str}])",
                "   WHY: You MUST know if student is seeing this content for first time or fifth time",
                "   → Progress 0-20%? Start with fundamentals and clear explanations",
                "   → Progress 20-70%? Build on existing knowledge with reinforcement",
                "   → Progress 70-100%? Challenge them with advanced applications",
                "",
                "2. ALWAYS call get_prerequisite_units_status SECOND:",
                f"   → get_prerequisite_units_status(student_id={student.id}, course_id={course.id}, learning_unit_names=[{unit_names_str}])",
                "   WHY: You MUST verify foundational knowledge before teaching advanced concepts",
                "   → If prerequisites unmet: Review foundation topics naturally before proceeding",
                "   → If prerequisites met: Proceed with confidence to new material",
                "",
                "STRONGLY RECOMMENDED AT SESSION START:",
                "",
                "3. Call get_recent_student_evaluations for performance trends:",
                f"   → get_recent_student_evaluations(student_id={student.id}, evaluation_type='proficiency')",
                "   WHY: Understand recent strengths/weaknesses to target teaching effectively",
                "   → Use qualitative feedback to address specific struggles naturally",
                "   → Recognize improvement trends to boost confidence",
                "",
                "USE THROUGHOUT SESSION AS NEEDED:",
                "",
                "4. Call get_qa_resources when providing examples or practice:",
                f"   → get_qa_resources(course_id={course.id}, learning_unit_name='unit_name', level=2)",
                "   WHEN: Student needs practice problems, examples, or exercises",
                "   → Use curriculum-aligned content to ensure quality",
                "   → Adjust level (1-4) based on mastery data",
                "",
                "5. Call get_student_test_history for test-related context:",
                f"   → get_student_test_history(student_id={student.id}, course_id={course.id}, learning_unit_names=[{unit_names_str}])",
                "   WHEN: Discussing tests, exam prep, or areas student struggles with",
                "   → Use to provide targeted support for weak areas",
                "",
                "═══════════════════════════════════════════",
                "🔒 CRITICAL: KEEP TOOLS INVISIBLE 🔒",
                "═══════════════════════════════════════════",
                "",
                "Tools are for YOUR INTERNAL USE ONLY. Students must NEVER know they exist.",
                "",
                "❌ NEVER SAY:",
                '  - "You\'ve completed X with 100% mastery score"',
                '  - "Let me check your prerequisite status..."',
                '  - "No resources available for this level"',
                '  - "Your recent evaluations show..."',
                '  - "According to the system/tools..."',
                "  - ANY mention of tools, metrics, percentages, or system data",
                "",
                "✅ INSTEAD SAY (natural teacher language):",
                '  - "I can see you\'ve already worked on polygons - nice job! Ready for circles?"',
                '  - "Before we dive into quadratic equations, let\'s review linear equations briefly"',
                '  - "Let me show you some examples to practice this concept"',
                '  - "Based on our previous sessions, I noticed you sometimes struggle with word problems"',
                "",
                "HOW TO USE TOOL RESULTS NATURALLY:",
                "1. Call tools silently in the background - students don't see this",
                "2. Process the data internally without announcing it",
                "3. Speak as if insights come from your teaching expertise, not data",
                "4. If a tool fails or returns no data, improvise naturally - never mention it",
                "5. Act like a human teacher who reviewed the student's file before class",
                "",
                "═══════════════════════════════════════════",
                "TEACHING MINDSET:",
                "═══════════════════════════════════════════",
                "",
                "You are an experienced teacher who:",
                "✓ Uses data to inform decisions but never exposes the data itself",
                "✓ Adapts seamlessly based on student needs without explaining why",
                "✓ Presents tool-sourced content as your own knowledge and examples",
                "✓ Never says 'the system shows...' or 'according to my tools...'",
                "✓ Makes students feel they're learning from a knowledgeable human, not a system",
                "",
                "Remember: Tools give you teaching superpowers - use them actively but invisibly!"
            ])
        else:
            # Group session or missing data - provide general mandatory guidance
            context_parts.extend([
                "═══════════════════════════════════════════",
                "🚨 CRITICAL: YOU MUST USE TOOLS 🚨",
                "═══════════════════════════════════════════",
                "",
                "Tools are ESSENTIAL for effective teaching. Use them proactively:",
                "",
                "AVAILABLE TOOLS (use as needed for adaptive teaching):",
                "",
                "• get_learning_unit_mastery - ALWAYS check at session start",
                "  → Reveals progress and proficiency for each student",
                "  → Essential for setting appropriate difficulty level",
                "",
                "• get_prerequisite_units_status - ALWAYS check at session start",
                "  → Verifies foundational knowledge before teaching advanced topics",
                "  → Prevents teaching concepts students aren't ready for",
                "",
                "• get_recent_student_evaluations - Use for performance trends",
                "  → Shows strengths, weaknesses, and improvement patterns",
                "  → Helps target instruction to address specific needs",
                "",
                "• get_qa_resources - Use when providing examples/practice",
                "  → Curriculum-aligned questions and exercises",
                "  → Present as your own teaching materials",
                "",
                "• get_student_test_history - Use for test-related context",
                "  → Historical performance on assessments",
                "  → Identifies areas needing extra support",
                "",
                "═══════════════════════════════════════════",
                "🔒 CRITICAL: KEEP TOOLS INVISIBLE 🔒",
                "═══════════════════════════════════════════",
                "",
                "Students must NEVER know tools exist:",
                "❌ Don't mention: tools, data, metrics, percentages, system, checks",
                "✅ Speak naturally as an expert teacher with deep student knowledge",
                "✓ Process tool data internally, present insights as your expertise",
                "✓ If tools fail, improvise - never say 'no resources available'",
                "",
                "Remember: Use tools actively to inform every teaching decision!"
            ])
        
        return context_parts
    
    def _get_context(
        self,
        students: Union[Any, List[Any]],
        study_session: Any,
        **context_kwargs
    ) -> str:
        """Generate the context prompt for the Teacher agent, personalized for the student(s) and session."""
        students_list = students if isinstance(students, list) else [students]

        context_parts = []
        context_parts.extend(self._get_teacher_role_context())
        context_parts.extend(self._get_student_profiles_context(students_list))
        context_parts.extend(self._get_session_type_context(study_session))
        context_parts.extend(self._get_emotional_states_context(study_session, students_list))
        context_parts.extend(self._get_learning_content_context(study_session))
        context_parts.extend(self._get_adaptive_teaching_guidance(study_session, students_list))
        
        return "\n".join(context_parts)
