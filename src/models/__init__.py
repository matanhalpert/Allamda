"""
Models package for the allamda system.

This package contains all SQLAlchemy models organized by domain.
All models are exposed at the package level for backward compatibility.
"""

# Declarative base and abstract base classes
from .base import (
    Base,
    User,
    Agent,
    StudySession,
    StudySessionPause,
    Evaluation,
    AIEvaluation,
    HumanEvaluation,
    StudySessionStudent,
    LearningUnitsStudySession,
    EvaluationStudySession
)

# User models
from .student_models import Student
from .user_models import (
    Parent,
    SchoolManager,
    ClassManager,
    RegionalSupervisor,
    Phone,
    Address
)

# School models
from .school_models import (
    School,
    Class,
    Tablet
)

# Course models
from .subject_models import (
    Subject,
    Course,
    LearningUnit,
    QA,
    Test
)

# Agent models
from .agents import (
    AIModel,
    Evaluator,
    Teacher
)

# Message models
from .message_models import (
    Message,
    Attachment
)

# Session models
from .session_models import (
    HomeHoursStudySession,
    SchoolHoursStudySession,
    HomeHoursStudySessionPause,
    SchoolHoursStudySessionPause
)

# Evaluation models
from .evaluation_models import (
    SessionalProficiencyEvaluation,
    QuarterProficiencyEvaluation,
    SessionalInvestmentEvaluation,
    QuarterInvestmentEvaluation,
    SessionalSocialEvaluation,
    QuarterSocialEvaluation
)

# Association tables
from .associations import (
    ParentStudent,
    ClassStudent,
    ClassClassManager,
    TabletStudent,
    SubjectRegionalSupervisor,
    CourseStudent,
    CoursePrerequisite,
    LearningUnitStudent,
    TestStudent,
    TestLearningUnit,
    HomeHoursStudySessionStudent,
    SchoolHoursStudySessionStudent,
    LearningUnitsHomeHoursStudySession,
    LearningUnitsSchoolHoursStudySession,
    SessionalProficiencyEvaluationHomeHoursStudySession,
    SessionalInvestmentEvaluationHomeHoursStudySession,
    SessionalProficiencyEvaluationSchoolHoursStudySession,
    SessionalInvestmentEvaluationSchoolHoursStudySession,
    SessionalSocialEvaluationSchoolHoursStudySession
)

# Expose all models at package level
__all__ = [
    # Base classes
    'Base',
    'User',
    'Agent',
    'StudySession',
    'StudySessionPause',
    'Evaluation',
    'AIEvaluation',
    'HumanEvaluation',
    'StudySessionStudent',
    'LearningUnitsStudySession',
    'EvaluationStudySession',
    
    # User models
    'Student',
    'Parent',
    'SchoolManager',
    'ClassManager',
    'RegionalSupervisor',
    'Phone',
    'Address',
    
    # School models
    'School',
    'Class',
    'Tablet',
    
    # Course models
    'Subject',
    'Course',
    'LearningUnit',
    'QA',
    'Test',
    
    # Agent models
    'AIModel',
    'Evaluator',
    'Teacher',
    
    # Message models
    'Message',
    'Attachment',
    
    # Session models
    'HomeHoursStudySession',
    'SchoolHoursStudySession',
    'HomeHoursStudySessionPause',
    'SchoolHoursStudySessionPause',
    
    # Evaluation models
    'SessionalProficiencyEvaluation',
    'QuarterProficiencyEvaluation',
    'SessionalInvestmentEvaluation',
    'QuarterInvestmentEvaluation',
    'SessionalSocialEvaluation',
    'QuarterSocialEvaluation',
    
    # Association tables
    'ParentStudent',
    'ClassStudent',
    'ClassClassManager',
    'TabletStudent',
    'SubjectRegionalSupervisor',
    'CourseStudent',
    'CoursePrerequisite',
    'LearningUnitStudent',
    'TestStudent',
    'TestLearningUnit',
    'HomeHoursStudySessionStudent',
    'SchoolHoursStudySessionStudent',
    'LearningUnitsHomeHoursStudySession',
    'LearningUnitsSchoolHoursStudySession',
    'SessionalProficiencyEvaluationHomeHoursStudySession',
    'SessionalInvestmentEvaluationHomeHoursStudySession',
    'SessionalProficiencyEvaluationSchoolHoursStudySession',
    'SessionalInvestmentEvaluationSchoolHoursStudySession',
    'SessionalSocialEvaluationSchoolHoursStudySession',
]
