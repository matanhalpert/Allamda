"""
Study session-related models.

This module contains models for study sessions and their pauses.
"""

from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from typing import Optional
from datetime import datetime, timedelta

from .base import StudySession, StudySessionPause
from src.database.session_context import get_current_session
from src.enums import HomeHoursStudySessionType, SchoolHoursStudySessionType, SessionStatus


class HomeHoursStudySession(StudySession):
    __tablename__ = 'home_hours_study_sessions'

    type = Column(Enum(HomeHoursStudySessionType), nullable=False)


class SchoolHoursStudySession(StudySession):
    __tablename__ = 'school_hours_study_sessions'

    type = Column(Enum(SchoolHoursStudySessionType), nullable=False)
    class_manager_id = Column(Integer, ForeignKey('class_managers.id'), nullable=False)
    planned_duration_minutes = Column(Integer, nullable=False, default=60)

    # relationships
    class_manager = relationship("ClassManager", back_populates="school_study_sessions")
    sessional_social_evaluations = relationship("SessionalSocialEvaluation",
                                                secondary="sessional_soc_eval_school_sessions",
                                                back_populates="school_study_sessions")


class HomeHoursStudySessionPause(StudySessionPause):
    __tablename__ = 'home_hours_study_session_pauses'

    home_hours_study_session_id = Column(Integer, ForeignKey('home_hours_study_sessions.id'), primary_key=True)

    # Relationships
    study_session = relationship("HomeHoursStudySession", back_populates="pauses")


class SchoolHoursStudySessionPause(StudySessionPause):
    __tablename__ = 'school_hours_study_session_pauses'

    school_hours_study_session_id = Column(Integer, ForeignKey('school_hours_study_sessions.id'), primary_key=True)

    # Relationships
    study_session = relationship("SchoolHoursStudySession", back_populates="pauses")
