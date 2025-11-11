from enum import StrEnum


class ConfigName(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
    DEFAULT = "default"


class UserType(StrEnum):
    STUDENT = "student"
    PARENT = "parent"
    CLASS_MANAGER = "class manager"
    SCHOOL_MANAGER = "school manager"
    REGIONAL_SUPERVISOR = "regional supervisor"


class LearningStyle(StrEnum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading/writing"
    MIXED = "mixed"


class RoutineStyle(StrEnum):
    STRUCTURED = "structured"
    FLEXIBLE = "flexible"
    EXPLORATORY = "exploratory"


class CollaborationStyle(StrEnum):
    COLLABORATIVE = "collaborative"
    INDEPENDENT = "independent"
    MIXED = "mixed"


class OS(StrEnum):
    IOS = "ios"
    ANDROID = "android"
    WINDOWS = "windows"
    CHROME_OS = "chrome os"


class TabletCondition(StrEnum):
    FUNCTIONAL = "functional"
    DEFECTIVE = "defective"
    NON_FUNCTIONAL = "non-functional"


class SubjectName(StrEnum):
    MATH = "math"
    ENGLISH = "english"
    LITERATURE = "literature"
    HEBREW = "hebrew"
    MUSIC = "music"
    HISTORY = "history"
    CIVICS = "civics"
    SCIENCE = "science"
    COMPUTER_SCIENCE = "computer science"
    PHYSICAL_EDUCATION = "physical education"
    ART = "art"
    BIBLE_STUDIES = "bible studies"


class Region(StrEnum):
    NORTH = "north"
    HAIFA = "haifa"
    CENTER = "center"
    TEL_AVIV = "tel aviv"
    JERUSALEM = "jerusalem"
    SOUTH = "south"


class CourseType(StrEnum):
    MANDATORY = "mandatory"
    OPTIONAL = "optional"


class LearningUnitType(StrEnum):
    INTRO = "intro"
    CHAPTER = "chapter"
    SUMMARY = "summary"


class TestType(StrEnum):
    QUIZ = "quiz"
    MID_TERM = "mid term"
    FINAL_EXAM = "final exam"
    MEITZAV = "meitzav"
    BAGRUT = "bagrut"
    FINAL_PROJECT = "final project"


class AIModelStatus(StrEnum):
    OPERATIONAL = "operational"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"
    DEVELOPMENT = "development"
    TESTING = "testing"


class HomeHoursStudySessionType(StrEnum):
    TEST_PREPARATION = "test preparation"
    HOMEWORK = "homework"


class SchoolHoursStudySessionType(StrEnum):
    INDIVIDUAL = "individual"
    GROUP = "group"
    SOCIAL = "social"


class EmotionalState(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    EXTREME = "extreme"


class AttendanceReason(StrEnum):
    SICK = "sick"
    EXCUSED = "excused"
    UNEXCUSED = "unexcused"


class CourseState(StrEnum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"


class GradeLevel(StrEnum):
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    FOURTH = "4th"
    FIFTH = "5th"
    SIXTH = "6th"
    SEVENTH = "7th"
    EIGHTH = "8th"
    NINTH = "9th"
    TENTH = "10th"
    ELEVENTH = "11th"
    TWELFTH = "12th"


class TestStatus(StrEnum):
    SCHEDULED = "scheduled"
    DELAYED = "delayed"
    FAILED = "failed"
    PASSED = "passed"


class MessageType(StrEnum):
    PROMPT = "prompt"
    RESPONSE = "response"


class MessageModality(StrEnum):
    TEXT_ONLY = "text_only"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    MULTIMODAL = "multimodal"


class FileType(StrEnum):
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    PDF = "pdf"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"


class QAType(StrEnum):
    FOR_TEST = "for test"
    FOR_STUDY = "for study"


class EvaluationType(StrEnum):
    PROFICIENCY = "proficiency"
    INVESTMENT = "investment"
    SOCIAL = "social"


class GroupAggregationStrategy(StrEnum):
    AVERAGE = "average"
    WEIGHTED_AVERAGE = "weighted_average"
    HIGHEST_NEED = "highest_need"
    MAX_BASED = "max_based"
    BALANCED = "balanced"


class SessionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    