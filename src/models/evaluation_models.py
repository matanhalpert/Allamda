"""
Evaluation-related models.

This module contains all evaluation models (proficiency, investment, and social).
"""

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.orm import relationship

from .base import AIEvaluation, HumanEvaluation
from src.enums import SubjectName


class SessionalProficiencyEvaluation(AIEvaluation):
    __tablename__ = 'sessional_proficiency_evaluations'

    # Relationships
    home_study_sessions = relationship("HomeHoursStudySession", secondary="sessional_prof_eval_home_sessions",
                                       back_populates="sessional_proficiency_evaluations")
    school_study_sessions = relationship("SchoolHoursStudySession", secondary="sessional_prof_eval_school_sessions",
                                         back_populates="sessional_proficiency_evaluations")


class QuarterProficiencyEvaluation(AIEvaluation):
    __tablename__ = 'quarter_proficiency_evaluations'

    subject_name = Column(Enum(SubjectName), ForeignKey('subjects.name'), nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="quarter_proficiency_evaluations")


class SessionalInvestmentEvaluation(AIEvaluation, HumanEvaluation):
    """Investment evaluation combining both AI and human assessment."""
    __tablename__ = 'sessional_invesment_evaluations'

    # Relationships
    home_study_sessions = relationship("HomeHoursStudySession", secondary="sessional_inv_eval_home_sessions",
                                       back_populates="sessional_investment_evaluations")
    school_study_sessions = relationship("SchoolHoursStudySession", secondary="sessional_inv_eval_school_sessions",
                                         back_populates="sessional_investment_evaluations")


class QuarterInvestmentEvaluation(AIEvaluation, HumanEvaluation):
    """Investment evaluation combining both AI and human assessment."""
    __tablename__ = 'quarter_invesment_evaluations'

    subject_name = Column(Enum(SubjectName), ForeignKey('subjects.name'), nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="quarter_investment_evaluations")


class SessionalSocialEvaluation(HumanEvaluation):
    __tablename__ = 'sessional_social_evaluations'

    # Relationships
    school_study_sessions = relationship("SchoolHoursStudySession", secondary="sessional_soc_eval_school_sessions",
                                         back_populates="sessional_social_evaluations")


class QuarterSocialEvaluation(HumanEvaluation):
    __tablename__ = 'quarter_social_evaluations'
