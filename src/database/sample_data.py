"""
Sample data module for the allamda database.
This module provides comprehensive, realistic sample data for testing and development purposes.
"""

from datetime import date, datetime, timedelta
from src.database.session_context import get_current_session
from src.database.decorators import with_db_session
from src.utils import Logger
from src.models import *
from src.enums import *
import random

# Default password for all users
DEFAULT_PASSWORD = "1234"

# Global variables to track relationships
_parent_student_mapping = []
_tablet_serial_numbers = []
_student_grade_mapping = {}
_student_school_mapping = {}


@with_db_session
def populate_sample_data():
    """Populate the database with comprehensive sample data."""

    # Add sample data in order of dependencies
    add_ai_models()
    add_evaluators()
    add_schools_and_managers()
    add_regional_supervisors()
    add_subjects()
    add_teachers()
    add_classes_and_class_managers()
    add_students_and_parents()
    add_phones_and_addresses()
    add_tablets()
    add_courses_and_learning_units()
    add_tests()
    add_course_prerequisites()
    add_test_units()
    add_qas()
    add_study_sessions()
    add_study_session_pauses()
    add_learning_unit_sessions()
    add_messages_and_attachments()
    add_evaluations()
    add_quarter_evaluations()
    add_associations()
    add_evaluation_session_associations()

    Logger.info("Sample data populated successfully!")


def add_ai_models():
    """Add sample AI models"""
    session = get_current_session()
    ai_models = [
        AIModel(id=1, name="EduAI-GPT", version="v2.1", status=AIModelStatus.OPERATIONAL),
        AIModel(id=2, name="LearningAssist", version="v1.5", status=AIModelStatus.OPERATIONAL),
        AIModel(id=3, name="EvalBot", version="v3.0", status=AIModelStatus.OPERATIONAL),
        AIModel(id=4, name="TeachMaster", version="v2.0", status=AIModelStatus.OPERATIONAL),
        AIModel(id=5, name="StudyBuddy", version="v1.8", status=AIModelStatus.TESTING),
    ]

    session.add_all(ai_models)
    session.flush()


def add_evaluators():
    """Add sample evaluators"""
    session = get_current_session()
    evaluators = [
        Evaluator(ai_model_id=1, name="ProficiencyEvaluator"),
        Evaluator(ai_model_id=1, name="InvestmentEvaluator"),
        Evaluator(ai_model_id=2, name="ComprehensiveEvaluator"),
        Evaluator(ai_model_id=3, name="BetaEvaluator"),
        Evaluator(ai_model_id=4, name="AdvancedAnalyzer"),
    ]

    session.add_all(evaluators)
    session.flush()


def add_schools_and_managers():
    """Add sample schools and school managers"""
    session = get_current_session()
    # School managers
    managers = [
        SchoolManager(
            id=1001,
            first_name="David",
            last_name="Cohen",
            birthdate=date(1975, 3, 15),
            email="david.cohen@education.gov.il",
            password=DEFAULT_PASSWORD,
            employment_year=2010
        ),
        SchoolManager(
            id=1002,
            first_name="Sarah",
            last_name="Levy",
            birthdate=date(1980, 7, 22),
            email="sarah.levy@education.gov.il",
            password=DEFAULT_PASSWORD,
            employment_year=2015
        ),
        SchoolManager(
            id=1003,
            first_name="Moshe",
            last_name="Goldberg",
            birthdate=date(1978, 11, 10),
            email="moshe.goldberg@education.gov.il",
            password=DEFAULT_PASSWORD,
            employment_year=2012
        ),
    ]

    session.add_all(managers)
    session.flush()

    # Schools
    schools = [
        School(
            id=1,
            name="Tel Aviv High School",
            establishment_date=date(1995, 9, 1),
            country="Israel",
            city="Tel Aviv",
            street="Rothschild Blvd",
            num="45",
            phone="03-5551234",
            email="info@tlvhigh.edu.il",
            school_manager_id=1001
        ),
        School(
            id=2,
            name="Haifa Science Academy",
            establishment_date=date(2000, 9, 1),
            country="Israel",
            city="Haifa",
            street="Technion St",
            num="12",
            phone="04-8221567",
            email="admin@haifascience.edu.il",
            school_manager_id=1002
        ),
        School(
            id=3,
            name="Jerusalem Arts Center",
            establishment_date=date(2005, 9, 1),
            country="Israel",
            city="Jerusalem",
            street="King David St",
            num="33",
            phone="02-6667890",
            email="info@jerusalemarts.edu.il",
            school_manager_id=1003
        ),
    ]

    session.add_all(schools)
    session.flush()


def add_regional_supervisors():
    """Add sample regional supervisors"""
    session = get_current_session()
    supervisors = [
        RegionalSupervisor(
            id=2001,
            first_name="Michael",
            last_name="Rosen",
            birthdate=date(1970, 12, 5),
            email="michael.rosen@education.gov.il",
            password=DEFAULT_PASSWORD,
            employment_year=2005
        ),
        RegionalSupervisor(
            id=2002,
            first_name="Rachel",
            last_name="Goldberg",
            birthdate=date(1973, 8, 18),
            email="rachel.goldberg@education.gov.il",
            password=DEFAULT_PASSWORD,
            employment_year=2008
        ),
        RegionalSupervisor(
            id=2003,
            first_name="Amit",
            last_name="Shapiro",
            birthdate=date(1976, 4, 25),
            email="amit.shapiro@education.gov.il",
            password=DEFAULT_PASSWORD,
            employment_year=2011
        ),
    ]

    session.add_all(supervisors)
    session.flush()


def add_subjects():
    """Add sample subjects covering all major disciplines"""
    session = get_current_session()
    subjects = [
        Subject(name=SubjectName.MATH, region=Region.TEL_AVIV, year=2024,
                description="Mathematics curriculum for Tel Aviv region"),
        Subject(name=SubjectName.ENGLISH, region=Region.TEL_AVIV, year=2024,
                description="English language curriculum"),
        Subject(name=SubjectName.SCIENCE, region=Region.HAIFA, year=2024,
                description="General science curriculum for Haifa region"),
        Subject(name=SubjectName.HISTORY, region=Region.CENTER, year=2024,
                description="Israeli and world history curriculum"),
        Subject(name=SubjectName.COMPUTER_SCIENCE, region=Region.TEL_AVIV, year=2024,
                description="Computer science and programming curriculum"),
        Subject(name=SubjectName.LITERATURE, region=Region.JERUSALEM, year=2024,
                description="Literature and critical analysis curriculum"),
        Subject(name=SubjectName.HEBREW, region=Region.CENTER, year=2024,
                description="Hebrew language and grammar curriculum"),
        Subject(name=SubjectName.PHYSICAL_EDUCATION, region=Region.HAIFA, year=2024,
                description="Physical education and sports curriculum"),
    ]

    session.add_all(subjects)
    session.flush()


def add_teachers():
    """Add sample AI teachers across all subjects"""
    session = get_current_session()
    teachers = [
        # Math teachers
        Teacher(ai_model_id=1, name="MathTutor", subject_name=SubjectName.MATH),
        Teacher(ai_model_id=4, name="AlgebraExpert", subject_name=SubjectName.MATH),
        Teacher(ai_model_id=2, name="GeometryGuide", subject_name=SubjectName.MATH),

        # English teachers
        Teacher(ai_model_id=1, name="EnglishMentor", subject_name=SubjectName.ENGLISH),
        Teacher(ai_model_id=4, name="GrammarGuru", subject_name=SubjectName.ENGLISH),

        # Science teachers
        Teacher(ai_model_id=2, name="ScienceGuide", subject_name=SubjectName.SCIENCE),
        Teacher(ai_model_id=3, name="PhysicsPro", subject_name=SubjectName.SCIENCE),

        # History teachers
        Teacher(ai_model_id=2, name="HistoryExplorer", subject_name=SubjectName.HISTORY),
        Teacher(ai_model_id=1, name="ChronicleKeeper", subject_name=SubjectName.HISTORY),

        # Computer Science teachers
        Teacher(ai_model_id=1, name="CodeMaster", subject_name=SubjectName.COMPUTER_SCIENCE),
        Teacher(ai_model_id=4, name="PythonPro", subject_name=SubjectName.COMPUTER_SCIENCE),

        # Literature teachers
        Teacher(ai_model_id=3, name="LitAnalyst", subject_name=SubjectName.LITERATURE),
        Teacher(ai_model_id=1, name="BookWorm", subject_name=SubjectName.LITERATURE),

        # Hebrew teachers
        Teacher(ai_model_id=2, name="HebrewHelper", subject_name=SubjectName.HEBREW),

        # PE teachers
        Teacher(ai_model_id=5, name="FitnessCoach", subject_name=SubjectName.PHYSICAL_EDUCATION),
    ]

    session.add_all(teachers)
    session.flush()


def add_classes_and_class_managers():
    """Add sample classes and class managers"""
    session = get_current_session()
    # Class managers (3 per school)
    class_managers = [
        # Tel Aviv High School
        ClassManager(
            id=3001, first_name="Anna", last_name="Friedman",
            birthdate=date(1985, 4, 12), email="anna.friedman@tlvhigh.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2018, school_id=1
        ),
        ClassManager(
            id=3002, first_name="Yosef", last_name="Katz",
            birthdate=date(1982, 11, 30), email="yosef.katz@tlvhigh.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2016, school_id=1
        ),
        ClassManager(
            id=3003, first_name="Maya", last_name="Sharon",
            birthdate=date(1988, 6, 8), email="maya.sharon@tlvhigh.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2020, school_id=1
        ),

        # Haifa Science Academy
        ClassManager(
            id=3004, first_name="Dan", last_name="Mizrahi",
            birthdate=date(1983, 9, 15), email="dan.mizrahi@haifascience.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2017, school_id=2
        ),
        ClassManager(
            id=3005, first_name="Tal", last_name="Cohen",
            birthdate=date(1986, 3, 22), email="tal.cohen@haifascience.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2019, school_id=2
        ),
        ClassManager(
            id=3006, first_name="Noa", last_name="Shapira",
            birthdate=date(1990, 1, 10), email="noa.shapira@haifascience.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2021, school_id=2
        ),

        # Jerusalem Arts Center
        ClassManager(
            id=3007, first_name="Eli", last_name="Ben-Yosef",
            birthdate=date(1984, 7, 5), email="eli.benyosef@jerusalemarts.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2016, school_id=3
        ),
        ClassManager(
            id=3008, first_name="Shira", last_name="Levi",
            birthdate=date(1987, 12, 18), email="shira.levi@jerusalemarts.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2019, school_id=3
        ),
        ClassManager(
            id=3009, first_name="Oren", last_name="Davidov",
            birthdate=date(1989, 5, 25), email="oren.davidov@jerusalemarts.edu.il",
            password=DEFAULT_PASSWORD, employment_year=2020, school_id=3
        ),
    ]

    session.add_all(class_managers)
    session.flush()

    # Classes (4 per school - grades 9-12)
    classes = [
        # Tel Aviv High School
        Class(school_id=1, year=2024, grade_level=GradeLevel.NINTH, capacity=30),
        Class(school_id=1, year=2024, grade_level=GradeLevel.TENTH, capacity=28),
        Class(school_id=1, year=2024, grade_level=GradeLevel.ELEVENTH, capacity=25),
        Class(school_id=1, year=2024, grade_level=GradeLevel.TWELFTH, capacity=22),

        # Haifa Science Academy
        Class(school_id=2, year=2024, grade_level=GradeLevel.NINTH, capacity=32),
        Class(school_id=2, year=2024, grade_level=GradeLevel.TENTH, capacity=30),
        Class(school_id=2, year=2024, grade_level=GradeLevel.ELEVENTH, capacity=28),
        Class(school_id=2, year=2024, grade_level=GradeLevel.TWELFTH, capacity=25),

        # Jerusalem Arts Center
        Class(school_id=3, year=2024, grade_level=GradeLevel.NINTH, capacity=28),
        Class(school_id=3, year=2024, grade_level=GradeLevel.TENTH, capacity=26),
        Class(school_id=3, year=2024, grade_level=GradeLevel.ELEVENTH, capacity=24),
        Class(school_id=3, year=2024, grade_level=GradeLevel.TWELFTH, capacity=20),
    ]

    session.add_all(classes)
    session.flush()


def add_students_and_parents():
    """Add sample students and parents - approximately 50 students total"""
    session = get_current_session()

    # Student and parent data
    students_data = [
        # Tel Aviv High School - Grade 9
        ("Noam", "Ben-David", date(2009, 6, 15), 1, GradeLevel.NINTH, LearningStyle.VISUAL, RoutineStyle.STRUCTURED,
         CollaborationStyle.COLLABORATIVE),
        ("Maya", "Miller", date(2009, 11, 8), 1, GradeLevel.NINTH, LearningStyle.KINESTHETIC, RoutineStyle.FLEXIBLE,
         CollaborationStyle.MIXED),
        ("Yonatan", "Schwartz", date(2009, 3, 22), 1, GradeLevel.NINTH, LearningStyle.AUDITORY,
         RoutineStyle.EXPLORATORY, CollaborationStyle.COLLABORATIVE),
        ("Tamar", "Rosenberg", date(2009, 8, 17), 1, GradeLevel.NINTH, LearningStyle.MIXED, RoutineStyle.STRUCTURED,
         CollaborationStyle.INDEPENDENT),
        ("Ben", "Avraham", date(2009, 5, 3), 1, GradeLevel.NINTH, LearningStyle.READING_WRITING, RoutineStyle.FLEXIBLE,
         CollaborationStyle.COLLABORATIVE),

        # Tel Aviv High School - Grade 10
        ("Shira", "Cohen", date(2008, 8, 17), 1, GradeLevel.TENTH, LearningStyle.MIXED, RoutineStyle.STRUCTURED,
         CollaborationStyle.INDEPENDENT),
        ("Eitan", "Harel", date(2008, 4, 5), 1, GradeLevel.TENTH, LearningStyle.VISUAL, RoutineStyle.FLEXIBLE,
         CollaborationStyle.COLLABORATIVE),
        ("Noa", "Berkowitz", date(2008, 12, 1), 1, GradeLevel.TENTH, LearningStyle.READING_WRITING,
         RoutineStyle.STRUCTURED, CollaborationStyle.MIXED),
        ("Avi", "Goldstein", date(2008, 7, 20), 1, GradeLevel.TENTH, LearningStyle.KINESTHETIC,
         RoutineStyle.EXPLORATORY, CollaborationStyle.COLLABORATIVE),

        # Tel Aviv High School - Grade 11
        ("Liam", "Weiss", date(2007, 5, 14), 1, GradeLevel.ELEVENTH, LearningStyle.VISUAL, RoutineStyle.STRUCTURED,
         CollaborationStyle.INDEPENDENT),
        ("Emma", "Kaplan", date(2007, 9, 30), 1, GradeLevel.ELEVENTH, LearningStyle.AUDITORY, RoutineStyle.FLEXIBLE,
         CollaborationStyle.MIXED),
        ("Or", "Mizrachi", date(2007, 2, 18), 1, GradeLevel.ELEVENTH, LearningStyle.MIXED, RoutineStyle.EXPLORATORY,
         CollaborationStyle.COLLABORATIVE),
        ("Roni", "Shapiro", date(2007, 11, 5), 1, GradeLevel.ELEVENTH, LearningStyle.READING_WRITING,
         RoutineStyle.STRUCTURED, CollaborationStyle.INDEPENDENT),

        # Tel Aviv High School - Grade 12
        ("Daniel", "Rosen", date(2006, 1, 12), 1, GradeLevel.TWELFTH, LearningStyle.VISUAL, RoutineStyle.FLEXIBLE,
         CollaborationStyle.MIXED),
        ("Sarah", "Friedman", date(2006, 10, 8), 1, GradeLevel.TWELFTH, LearningStyle.AUDITORY, RoutineStyle.STRUCTURED,
         CollaborationStyle.COLLABORATIVE),
        ("Yoav", "Stein", date(2006, 4, 22), 1, GradeLevel.TWELFTH, LearningStyle.KINESTHETIC, RoutineStyle.EXPLORATORY,
         CollaborationStyle.INDEPENDENT),
        ("Michal", "Levy", date(2006, 8, 15), 1, GradeLevel.TWELFTH, LearningStyle.MIXED, RoutineStyle.FLEXIBLE,
         CollaborationStyle.MIXED),

        # Haifa Science Academy - Grade 9
        ("Amit", "Goldstein", date(2009, 3, 22), 2, GradeLevel.NINTH, LearningStyle.AUDITORY, RoutineStyle.EXPLORATORY,
         CollaborationStyle.COLLABORATIVE),
        ("Yael", "Ben-Ami", date(2009, 5, 20), 2, GradeLevel.NINTH, LearningStyle.AUDITORY, RoutineStyle.EXPLORATORY,
         CollaborationStyle.COLLABORATIVE),
        ("Gal", "Peretz", date(2009, 9, 10), 2, GradeLevel.NINTH, LearningStyle.VISUAL, RoutineStyle.STRUCTURED,
         CollaborationStyle.MIXED),
        ("Neta", "Avraham", date(2009, 12, 5), 2, GradeLevel.NINTH, LearningStyle.KINESTHETIC, RoutineStyle.FLEXIBLE,
         CollaborationStyle.COLLABORATIVE),
        ("Tomer", "Levi", date(2009, 7, 18), 2, GradeLevel.NINTH, LearningStyle.MIXED, RoutineStyle.EXPLORATORY,
         CollaborationStyle.INDEPENDENT),

        # Haifa Science Academy - Grade 10
        ("Omer", "David", date(2008, 6, 14), 2, GradeLevel.TENTH, LearningStyle.READING_WRITING,
         RoutineStyle.STRUCTURED, CollaborationStyle.INDEPENDENT),
        ("Lihi", "Biton", date(2008, 10, 28), 2, GradeLevel.TENTH, LearningStyle.VISUAL, RoutineStyle.FLEXIBLE,
         CollaborationStyle.MIXED),
        ("Itai", "Segal", date(2008, 2, 7), 2, GradeLevel.TENTH, LearningStyle.AUDITORY, RoutineStyle.EXPLORATORY,
         CollaborationStyle.COLLABORATIVE),
        ("Hila", "Golan", date(2008, 11, 19), 2, GradeLevel.TENTH, LearningStyle.MIXED, RoutineStyle.STRUCTURED,
         CollaborationStyle.COLLABORATIVE),

        # Haifa Science Academy - Grade 11
        ("Rotem", "Azoulay", date(2007, 4, 3), 2, GradeLevel.ELEVENTH, LearningStyle.VISUAL, RoutineStyle.FLEXIBLE,
         CollaborationStyle.INDEPENDENT),
        ("Stav", "Dahan", date(2007, 7, 21), 2, GradeLevel.ELEVENTH, LearningStyle.KINESTHETIC,
         RoutineStyle.EXPLORATORY, CollaborationStyle.MIXED),
        ("Ido", "Mor", date(2007, 1, 15), 2, GradeLevel.ELEVENTH, LearningStyle.READING_WRITING,
         RoutineStyle.STRUCTURED, CollaborationStyle.COLLABORATIVE),
        ("Ayala", "Chen", date(2007, 10, 30), 2, GradeLevel.ELEVENTH, LearningStyle.AUDITORY, RoutineStyle.FLEXIBLE,
         CollaborationStyle.INDEPENDENT),

        # Haifa Science Academy - Grade 12
        ("Guy", "Hazan", date(2006, 3, 8), 2, GradeLevel.TWELFTH, LearningStyle.MIXED, RoutineStyle.STRUCTURED,
         CollaborationStyle.MIXED),
        ("Chen", "Barkan", date(2006, 9, 25), 2, GradeLevel.TWELFTH, LearningStyle.VISUAL, RoutineStyle.EXPLORATORY,
         CollaborationStyle.COLLABORATIVE),
        ("Yuval", "Katz", date(2006, 5, 12), 2, GradeLevel.TWELFTH, LearningStyle.AUDITORY, RoutineStyle.FLEXIBLE,
         CollaborationStyle.INDEPENDENT),
        ("Merav", "Alon", date(2006, 12, 1), 2, GradeLevel.TWELFTH, LearningStyle.KINESTHETIC, RoutineStyle.STRUCTURED,
         CollaborationStyle.MIXED),

        # Jerusalem Arts Center - Grade 9
        ("Ariel", "Nadav", date(2009, 7, 7), 3, GradeLevel.NINTH, LearningStyle.VISUAL, RoutineStyle.FLEXIBLE,
         CollaborationStyle.COLLABORATIVE),
        ("Shani", "Gross", date(2009, 2, 14), 3, GradeLevel.NINTH, LearningStyle.KINESTHETIC, RoutineStyle.EXPLORATORY,
         CollaborationStyle.MIXED),
        ("Tom", "Romano", date(2009, 11, 23), 3, GradeLevel.NINTH, LearningStyle.AUDITORY, RoutineStyle.STRUCTURED,
         CollaborationStyle.INDEPENDENT),
        ("Yarden", "Malka", date(2009, 4, 18), 3, GradeLevel.NINTH, LearningStyle.MIXED, RoutineStyle.FLEXIBLE,
         CollaborationStyle.COLLABORATIVE),

        # Jerusalem Arts Center - Grade 10
        ("Alon", "Tzur", date(2008, 8, 9), 3, GradeLevel.TENTH, LearningStyle.READING_WRITING, RoutineStyle.STRUCTURED,
         CollaborationStyle.INDEPENDENT),
        ("Dana", "Elias", date(2008, 1, 26), 3, GradeLevel.TENTH, LearningStyle.VISUAL, RoutineStyle.EXPLORATORY,
         CollaborationStyle.MIXED),
        ("Nir", "Oren", date(2008, 6, 11), 3, GradeLevel.TENTH, LearningStyle.KINESTHETIC, RoutineStyle.FLEXIBLE,
         CollaborationStyle.COLLABORATIVE),
        ("Maya", "Sabag", date(2008, 10, 4), 3, GradeLevel.TENTH, LearningStyle.AUDITORY, RoutineStyle.STRUCTURED,
         CollaborationStyle.COLLABORATIVE),

        # Jerusalem Arts Center - Grade 11
        ("Elad", "Sharon", date(2007, 3, 17), 3, GradeLevel.ELEVENTH, LearningStyle.MIXED, RoutineStyle.FLEXIBLE,
         CollaborationStyle.INDEPENDENT),
        ("Keren", "Dror", date(2007, 12, 29), 3, GradeLevel.ELEVENTH, LearningStyle.VISUAL, RoutineStyle.EXPLORATORY,
         CollaborationStyle.MIXED),
        ("Uri", "Barak", date(2007, 6, 6), 3, GradeLevel.ELEVENTH, LearningStyle.READING_WRITING,
         RoutineStyle.STRUCTURED, CollaborationStyle.COLLABORATIVE),
        ("Noga", "Shimoni", date(2007, 9, 20), 3, GradeLevel.ELEVENTH, LearningStyle.KINESTHETIC, RoutineStyle.FLEXIBLE,
         CollaborationStyle.INDEPENDENT),

        # Jerusalem Arts Center - Grade 12
        ("Eden", "Peled", date(2006, 2, 10), 3, GradeLevel.TWELFTH, LearningStyle.AUDITORY, RoutineStyle.STRUCTURED,
         CollaborationStyle.MIXED),
        ("Lior", "Amos", date(2006, 7, 27), 3, GradeLevel.TWELFTH, LearningStyle.MIXED, RoutineStyle.EXPLORATORY,
         CollaborationStyle.COLLABORATIVE),
        ("Matan", "Zohar", date(2006, 11, 14), 3, GradeLevel.TWELFTH, LearningStyle.VISUAL, RoutineStyle.FLEXIBLE,
         CollaborationStyle.INDEPENDENT),
        ("Romi", "Ben-Haim", date(2006, 4, 1), 3, GradeLevel.TWELFTH, LearningStyle.KINESTHETIC,
         RoutineStyle.STRUCTURED, CollaborationStyle.MIXED),
    ]

    # Create students and parents
    students = []
    parents = []
    parent_student_mapping = []  # Track parent-student relationships
    student_grade_mapping = {}  # Track student ID to grade level
    student_school_mapping = {}  # Track student ID to school ID
    student_id = 5001
    parent_id = 4001

    for first_name, last_name, birthdate, school_id, grade_level, learning_style, routine_style, collaboration_style in students_data:
        # Create student
        student = Student(
            id=student_id,
            first_name=first_name,
            last_name=last_name,
            birthdate=birthdate,
            email=f"{first_name.lower()}.{last_name.lower()}@student.school{school_id}.edu.il",
            password=DEFAULT_PASSWORD,
            school_id=school_id,
            learning_style=learning_style,
            routine_style=routine_style,
            collaboration_style=collaboration_style
        )
        students.append(student)
        student_grade_mapping[student_id] = grade_level  # Track grade
        student_school_mapping[student_id] = school_id  # Track school

        # Create 1-2 parents per student
        num_parents = random.choice([1, 2])
        for i in range(num_parents):
            parent_first_name = random.choice(
                ["Avi", "David", "Yossi", "Dan", "Ron", "Miriam", "Tamar", "Dina", "Ruth", "Rachel"])
            parent = Parent(
                id=parent_id,
                first_name=parent_first_name,
                last_name=last_name,
                birthdate=date(random.randint(1970, 1985), random.randint(1, 12), random.randint(1, 28)),
                email=f"{parent_first_name.lower()}.{last_name.lower()}{parent_id}@gmail.com",
                password=DEFAULT_PASSWORD
            )
            parents.append(parent)
            parent_student_mapping.append((parent_id, student_id))  # Track the relationship
            parent_id += 1

        student_id += 1

    session.add_all(students)
    session.add_all(parents)
    session.flush()

    # Store the mappings globally so add_associations can use them
    global _parent_student_mapping, _student_grade_mapping, _student_school_mapping
    _parent_student_mapping = parent_student_mapping
    _student_grade_mapping = student_grade_mapping
    _student_school_mapping = student_school_mapping


def add_tablets():
    """Add sample tablets for students"""
    session = get_current_session()
    tablets = []
    tablet_serial_numbers = []  # Track serial numbers
    serial_num = 1

    os_options = [OS.IOS, OS.ANDROID, OS.WINDOWS]
    models = {
        OS.IOS: ["iPad Air 5th Gen", "iPad Pro 11", "iPad 9th Gen", "iPad Mini 6"],
        OS.ANDROID: ["Galaxy Tab S8", "Galaxy Tab A8", "Lenovo Tab P11", "Pixel Tablet"],
        OS.WINDOWS: ["Surface Go 3", "Surface Pro 8", "HP Elite x2", "Lenovo ThinkPad X1"]
    }

    for i in range(55):
        os = random.choice(os_options)
        model = random.choice(models[os])
        year = random.choice([2022, 2023, 2024])

        serial_number = f"TB{serial_num:03d}-{os.upper()}-{year}"
        tablet = Tablet(
            serial_number=serial_number,
            os=os,
            model=model,
            purchase_date=date(year, random.randint(1, 12), random.randint(1, 28)),
            condition=random.choice([TabletCondition.FUNCTIONAL, TabletCondition.FUNCTIONAL, TabletCondition.FUNCTIONAL,
                                     TabletCondition.DEFECTIVE])
        )
        tablets.append(tablet)
        tablet_serial_numbers.append(serial_number)
        serial_num += 1

    session.add_all(tablets)
    session.flush()

    # Store the serial numbers globally so add_associations can use them
    global _tablet_serial_numbers
    _tablet_serial_numbers = tablet_serial_numbers


def add_courses_and_learning_units():
    """Add comprehensive courses and learning units"""
    session = get_current_session()

    courses = [
        # Math courses
        Course(id=1, name="Algebra Fundamentals", grade_level=GradeLevel.NINTH, type=CourseType.MANDATORY,
               description="Basic algebraic concepts and operations", level=1, subject_name=SubjectName.MATH),
        Course(id=2, name="Geometry Basics", grade_level=GradeLevel.NINTH, type=CourseType.MANDATORY,
               description="Introduction to geometric shapes and proofs", level=1, subject_name=SubjectName.MATH),
        Course(id=3, name="Algebra II", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Advanced algebra with polynomials and functions", level=2, subject_name=SubjectName.MATH),
        Course(id=4, name="Trigonometry", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Study of triangles and trigonometric functions", level=2, subject_name=SubjectName.MATH),
        Course(id=5, name="Pre-Calculus", grade_level=GradeLevel.ELEVENTH, type=CourseType.MANDATORY,
               description="Preparation for calculus", level=3, subject_name=SubjectName.MATH),
        Course(id=6, name="Calculus I", grade_level=GradeLevel.TWELFTH, type=CourseType.OPTIONAL,
               description="Introduction to differential and integral calculus", level=4,
               subject_name=SubjectName.MATH),

        # English courses
        Course(id=7, name="English Composition I", grade_level=GradeLevel.NINTH, type=CourseType.MANDATORY,
               description="Basic writing and grammar skills", level=1, subject_name=SubjectName.ENGLISH),
        Course(id=8, name="English Composition II", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Advanced writing and essay techniques", level=2, subject_name=SubjectName.ENGLISH),
        Course(id=9, name="English Literature", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Introduction to classic English literature", level=2, subject_name=SubjectName.ENGLISH),
        Course(id=10, name="Advanced English", grade_level=GradeLevel.ELEVENTH, type=CourseType.MANDATORY,
               description="Advanced grammar and composition", level=3, subject_name=SubjectName.ENGLISH),
        Course(id=11, name="English for Bagrut", grade_level=GradeLevel.TWELFTH, type=CourseType.MANDATORY,
               description="Preparation for English matriculation exam", level=4, subject_name=SubjectName.ENGLISH),

        # Science courses
        Course(id=12, name="Biology Basics", grade_level=GradeLevel.NINTH, type=CourseType.MANDATORY,
               description="Fundamental concepts in biology", level=1, subject_name=SubjectName.SCIENCE),
        Course(id=13, name="Chemistry Fundamentals", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Introduction to chemistry and chemical reactions", level=2,
               subject_name=SubjectName.SCIENCE),
        Course(id=14, name="Physics I", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Basic principles of physics", level=2, subject_name=SubjectName.SCIENCE),
        Course(id=15, name="Advanced Biology", grade_level=GradeLevel.ELEVENTH, type=CourseType.OPTIONAL,
               description="Advanced topics in biology", level=3, subject_name=SubjectName.SCIENCE),
        Course(id=16, name="Physics II", grade_level=GradeLevel.ELEVENTH, type=CourseType.OPTIONAL,
               description="Advanced physics concepts", level=3, subject_name=SubjectName.SCIENCE),

        # History courses
        Course(id=17, name="Ancient History", grade_level=GradeLevel.NINTH, type=CourseType.MANDATORY,
               description="Study of ancient civilizations", level=1, subject_name=SubjectName.HISTORY),
        Course(id=18, name="Medieval History", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="The medieval period and its impact", level=2, subject_name=SubjectName.HISTORY),
        Course(id=19, name="Modern History", grade_level=GradeLevel.ELEVENTH, type=CourseType.MANDATORY,
               description="19th and 20th century history", level=3, subject_name=SubjectName.HISTORY),
        Course(id=20, name="Israeli History", grade_level=GradeLevel.TWELFTH, type=CourseType.MANDATORY,
               description="History of Israel and Zionism", level=4, subject_name=SubjectName.HISTORY),

        # Computer Science courses
        Course(id=21, name="Introduction to Programming", grade_level=GradeLevel.NINTH, type=CourseType.OPTIONAL,
               description="Basic programming concepts", level=1, subject_name=SubjectName.COMPUTER_SCIENCE),
        Course(id=22, name="Python Programming", grade_level=GradeLevel.TENTH, type=CourseType.OPTIONAL,
               description="Programming in Python", level=2, subject_name=SubjectName.COMPUTER_SCIENCE),
        Course(id=23, name="Data Structures", grade_level=GradeLevel.ELEVENTH, type=CourseType.OPTIONAL,
               description="Introduction to data structures and algorithms", level=3,
               subject_name=SubjectName.COMPUTER_SCIENCE),
        Course(id=24, name="Web Development", grade_level=GradeLevel.ELEVENTH, type=CourseType.OPTIONAL,
               description="HTML, CSS, and JavaScript fundamentals", level=3,
               subject_name=SubjectName.COMPUTER_SCIENCE),
        Course(id=25, name="Advanced Programming", grade_level=GradeLevel.TWELFTH, type=CourseType.OPTIONAL,
               description="Advanced programming techniques and projects", level=4,
               subject_name=SubjectName.COMPUTER_SCIENCE),

        # Literature courses
        Course(id=26, name="World Literature I", grade_level=GradeLevel.NINTH, type=CourseType.MANDATORY,
               description="Introduction to world literature", level=1, subject_name=SubjectName.LITERATURE),
        Course(id=27, name="World Literature II", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Continued study of world literature", level=2, subject_name=SubjectName.LITERATURE),
        Course(id=28, name="Israeli Literature", grade_level=GradeLevel.ELEVENTH, type=CourseType.MANDATORY,
               description="Study of Israeli authors and works", level=3, subject_name=SubjectName.LITERATURE),
        Course(id=29, name="Poetry and Drama", grade_level=GradeLevel.TWELFTH, type=CourseType.OPTIONAL,
               description="Analysis of poetry and dramatic works", level=4, subject_name=SubjectName.LITERATURE),

        # Hebrew courses
        Course(id=30, name="Hebrew Grammar I", grade_level=GradeLevel.NINTH, type=CourseType.MANDATORY,
               description="Basic Hebrew grammar and syntax", level=1, subject_name=SubjectName.HEBREW),
        Course(id=31, name="Hebrew Grammar II", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Advanced Hebrew grammar", level=2, subject_name=SubjectName.HEBREW),
        Course(id=32, name="Hebrew Composition", grade_level=GradeLevel.ELEVENTH, type=CourseType.MANDATORY,
               description="Writing skills in Hebrew", level=3, subject_name=SubjectName.HEBREW),
        Course(id=33, name="Hebrew for Bagrut", grade_level=GradeLevel.TWELFTH, type=CourseType.MANDATORY,
               description="Preparation for Hebrew matriculation exam", level=4, subject_name=SubjectName.HEBREW),

        # Physical Education courses
        Course(id=34, name="Physical Education 9", grade_level=GradeLevel.NINTH, type=CourseType.MANDATORY,
               description="Basic physical education and sports", level=1, subject_name=SubjectName.PHYSICAL_EDUCATION),
        Course(id=35, name="Physical Education 10", grade_level=GradeLevel.TENTH, type=CourseType.MANDATORY,
               description="Continued physical education", level=2, subject_name=SubjectName.PHYSICAL_EDUCATION),
        Course(id=36, name="Physical Education 11", grade_level=GradeLevel.ELEVENTH, type=CourseType.MANDATORY,
               description="Advanced physical education", level=3, subject_name=SubjectName.PHYSICAL_EDUCATION),
        Course(id=37, name="Physical Education 12", grade_level=GradeLevel.TWELFTH, type=CourseType.MANDATORY,
               description="Senior physical education", level=4, subject_name=SubjectName.PHYSICAL_EDUCATION),
    ]

    session.add_all(courses)
    session.flush()

    # Learning units for each course (3-4 per course)
    learning_units = []

    # Helper function to create learning units for a course
    def create_units(course_id, units_data):
        for i, (name, unit_type, weight, description, duration) in enumerate(units_data):
            prev_unit = units_data[i - 1][0] if i > 0 else None
            next_unit = units_data[i + 1][0] if i < len(units_data) - 1 else None

            learning_units.append(LearningUnit(
                course_id=course_id,
                name=name,
                type=unit_type,
                weight=weight,
                description=description,
                previous_learning_unit=prev_unit,
                next_learning_unit=next_unit,
                estimated_duration_minutes=duration
            ))

    # Algebra Fundamentals
    create_units(1, [
        ("Variables and Expressions", LearningUnitType.INTRO, 0.2, "Understanding variables and algebraic expressions", 45),
        ("Linear Equations", LearningUnitType.CHAPTER, 0.3, "Solving linear equations in one variable", 90),
        ("Systems of Equations", LearningUnitType.CHAPTER, 0.3, "Solving systems of linear equations", 105),
        ("Quadratic Functions", LearningUnitType.SUMMARY, 0.2, "Introduction to quadratic functions", 60),
    ])

    # Geometry Basics
    create_units(2, [
        ("Points, Lines, and Planes", LearningUnitType.INTRO, 0.25, "Basic geometric concepts", 50),
        ("Angles and Triangles", LearningUnitType.CHAPTER, 0.35, "Properties of angles and triangles", 95),
        ("Polygons and Circles", LearningUnitType.CHAPTER, 0.25, "Study of polygons and circles", 85),
        ("Geometric Proofs", LearningUnitType.SUMMARY, 0.15, "Introduction to geometric proofs", 70),
    ])

    # Algebra II
    create_units(3, [
        ("Polynomials", LearningUnitType.INTRO, 0.3, "Operations with polynomials", 55),
        ("Rational Expressions", LearningUnitType.CHAPTER, 0.3, "Working with rational expressions", 100),
        ("Exponential Functions", LearningUnitType.CHAPTER, 0.25, "Understanding exponential growth", 90),
        ("Logarithms", LearningUnitType.SUMMARY, 0.15, "Introduction to logarithms", 75),
    ])

    # Add similar units for courses 4-37 (abbreviated for brevity)
    # English Composition I
    create_units(7, [
        ("Sentence Structure", LearningUnitType.INTRO, 0.25, "Basic sentence construction", 45),
        ("Paragraph Writing", LearningUnitType.CHAPTER, 0.35, "Developing paragraphs", 95),
        ("Essay Basics", LearningUnitType.CHAPTER, 0.25, "Introduction to essay writing", 90),
        ("Grammar Review", LearningUnitType.SUMMARY, 0.15, "Comprehensive grammar review", 65),
    ])

    # English Literature
    create_units(9, [
        ("Poetry Analysis", LearningUnitType.INTRO, 0.3, "Analyzing themes in poetry", 50),
        ("Short Stories", LearningUnitType.CHAPTER, 0.35, "Understanding narrative structure", 100),
        ("Novel Study", LearningUnitType.CHAPTER, 0.2, "Reading and analyzing novels", 85),
        ("Literary Essay", LearningUnitType.SUMMARY, 0.15, "Writing about literature", 70),
    ])

    # Biology Basics
    create_units(12, [
        ("Cell Structure", LearningUnitType.INTRO, 0.3, "Understanding cell components", 55),
        ("Genetics Basics", LearningUnitType.CHAPTER, 0.35, "Introduction to heredity and DNA", 105),
        ("Ecosystems", LearningUnitType.CHAPTER, 0.2, "Understanding ecological relationships", 80),
        ("Evolution", LearningUnitType.SUMMARY, 0.15, "Basic principles of evolution", 65),
    ])

    # Introduction to Programming
    create_units(21, [
        ("Variables and Data Types", LearningUnitType.INTRO, 0.25, "Understanding programming basics", 45),
        ("Control Structures", LearningUnitType.CHAPTER, 0.25, "Loops and conditionals", 80),
        ("Functions", LearningUnitType.CHAPTER, 0.25, "Understanding functions", 85),
        ("Basic Algorithms", LearningUnitType.SUMMARY, 0.25, "Introduction to algorithms", 75),
    ])

    # Add units for remaining courses with similar patterns
    for course_id in range(4, 38):
        if course_id not in [1, 2, 3, 7, 9, 12, 21]:  # Skip ones we already did
            create_units(course_id, [
                (f"Unit 1 - Introduction", LearningUnitType.INTRO, 0.25, f"Introduction to course {course_id}", 50),
                (f"Unit 2 - Core Concepts", LearningUnitType.CHAPTER, 0.35, f"Core concepts for course {course_id}", 95),
                (f"Unit 3 - Advanced Topics", LearningUnitType.CHAPTER, 0.25,
                 f"Advanced topics for course {course_id}", 90),
                (f"Unit 4 - Review", LearningUnitType.SUMMARY, 0.15, f"Review for course {course_id}", 70),
            ])

    session.add_all(learning_units)
    session.flush()


def add_tests():
    """Add sample tests for courses"""
    session = get_current_session()
    tests = []

    # Add 2-3 tests per course
    for course_id in range(1, 38):
        # Quiz
        tests.append(Test(
            course_id=course_id,
            name=f"Course {course_id} Quiz",
            type=TestType.QUIZ,
            link=f"https://testplatform.edu.il/course{course_id}/quiz"
        ))

        # Midterm
        tests.append(Test(
            course_id=course_id,
            name=f"Course {course_id} Midterm",
            type=TestType.MID_TERM,
            link=f"https://testplatform.edu.il/course{course_id}/midterm"
        ))

        # Final exam for most courses
        if course_id % 4 == 0:
            tests.append(Test(
                course_id=course_id,
                name=f"Course {course_id} Final",
                type=TestType.FINAL_EXAM,
                link=f"https://testplatform.edu.il/course{course_id}/final"
            ))

    session.add_all(tests)
    session.flush()


def add_phones_and_addresses():
    """Add sample phone numbers and addresses for users"""
    session = get_current_session()
    phones = []
    addresses = []

    # Phones and addresses for managers (sample for first few)
    user_ids = list(range(1001, 1004)) + list(range(2001, 2004)) + list(range(3001, 3010)) + list(
        range(4001, 4075)) + list(range(5001, 5051))

    for user_id in user_ids[:30]:  # Add for first 30 users to keep it manageable
        phones.append(
            Phone(user_id=user_id, phone_number=f"05{random.randint(0, 9)}-{random.randint(1000000, 9999999)}"))

        cities = ["Tel Aviv", "Haifa", "Jerusalem", "Beer Sheva", "Netanya"]
        streets = ["Herzl St", "Ben Gurion Ave", "Rothschild Blvd", "Dizengoff St", "King George St"]

        addresses.append(Address(
            user_id=user_id,
            country="Israel",
            city=random.choice(cities),
            street=random.choice(streets),
            num=str(random.randint(1, 200))
        ))

    session.add_all(phones)
    session.add_all(addresses)
    session.flush()


def add_course_prerequisites():
    """Add sample course prerequisites"""
    session = get_current_session()
    prerequisites = []

    # Math progression
    prerequisites.append(CoursePrerequisite(course_id=3, prerequisite_course_id=1))  # Algebra II requires Algebra I
    prerequisites.append(CoursePrerequisite(course_id=5, prerequisite_course_id=3))  # Pre-Calc requires Algebra II
    prerequisites.append(CoursePrerequisite(course_id=5, prerequisite_course_id=4))  # Pre-Calc requires Trig
    prerequisites.append(CoursePrerequisite(course_id=6, prerequisite_course_id=5))  # Calculus requires Pre-Calc

    # English progression
    prerequisites.append(CoursePrerequisite(course_id=8, prerequisite_course_id=7))
    prerequisites.append(CoursePrerequisite(course_id=10, prerequisite_course_id=8))
    prerequisites.append(CoursePrerequisite(course_id=11, prerequisite_course_id=10))

    # Science progression
    prerequisites.append(
        CoursePrerequisite(course_id=15, prerequisite_course_id=12))  # Advanced Bio requires Bio Basics
    prerequisites.append(CoursePrerequisite(course_id=16, prerequisite_course_id=14))  # Physics II requires Physics I

    # CS progression
    prerequisites.append(CoursePrerequisite(course_id=22, prerequisite_course_id=21))  # Python requires Intro
    prerequisites.append(CoursePrerequisite(course_id=23, prerequisite_course_id=22))  # Data Structures requires Python
    prerequisites.append(
        CoursePrerequisite(course_id=25, prerequisite_course_id=23))  # Advanced Programming requires Data Structures

    session.add_all(prerequisites)
    session.flush()


def add_test_units():
    """Add sample test-learning unit relationships"""
    session = get_current_session()
    test_units = []

    # Link tests to learning units (each test covers 1-3 units)
    # Quiz for course 1
    test_units.append(TestLearningUnit(course_id=1, test_name="Course 1 Quiz", learning_unit_name="Variables and Expressions"))

    # Midterm for course 1
    test_units.append(TestLearningUnit(course_id=1, test_name="Course 1 Midterm", learning_unit_name="Linear Equations"))
    test_units.append(TestLearningUnit(course_id=1, test_name="Course 1 Midterm", learning_unit_name="Systems of Equations"))

    # Quiz for course 9
    test_units.append(TestLearningUnit(course_id=9, test_name="Course 9 Quiz", learning_unit_name="Poetry Analysis"))

    # Midterm for course 9
    test_units.append(TestLearningUnit(course_id=9, test_name="Course 9 Midterm", learning_unit_name="Short Stories"))
    test_units.append(TestLearningUnit(course_id=9, test_name="Course 9 Midterm", learning_unit_name="Novel Study"))

    # Quiz for course 12
    test_units.append(TestLearningUnit(course_id=12, test_name="Course 12 Quiz", learning_unit_name="Cell Structure"))

    # Midterm for course 12
    test_units.append(TestLearningUnit(course_id=12, test_name="Course 12 Midterm", learning_unit_name="Genetics Basics"))
    test_units.append(TestLearningUnit(course_id=12, test_name="Course 12 Midterm", learning_unit_name="Ecosystems"))

    # Final for course 12
    test_units.append(TestLearningUnit(course_id=12, test_name="Course 12 Final", learning_unit_name="Cell Structure"))
    test_units.append(TestLearningUnit(course_id=12, test_name="Course 12 Final", learning_unit_name="Genetics Basics"))
    test_units.append(TestLearningUnit(course_id=12, test_name="Course 12 Final", learning_unit_name="Ecosystems"))
    test_units.append(TestLearningUnit(course_id=12, test_name="Course 12 Final", learning_unit_name="Evolution"))

    session.add_all(test_units)
    session.flush()


def add_qas():
    """Add sample Q&A entries for learning units"""
    session = get_current_session()
    qas = []

    # Add some sample Q&As for key courses
    # Algebra Fundamentals
    qas.extend([
        QA(course_id=1, learning_unit_name="Variables and Expressions",
           question="What is a variable?",
           answer="A variable is a symbol (usually a letter) that represents a value that can change.",
           type=QAType.FOR_STUDY, level=1),
        QA(course_id=1, learning_unit_name="Linear Equations",
           question="How do you solve 2x + 5 = 13?",
           answer="Subtract 5 from both sides to get 2x = 8, then divide both sides by 2 to get x = 4.",
           type=QAType.FOR_TEST, level=2),
    ])

    # Biology Basics
    qas.extend([
        QA(course_id=12, learning_unit_name="Cell Structure",
           question="What is the function of mitochondria?",
           answer="Mitochondria are the powerhouses of the cell, producing ATP through cellular respiration.",
           type=QAType.FOR_STUDY, level=1),
        QA(course_id=12, learning_unit_name="Genetics Basics",
           question="What is DNA?",
           answer="DNA (deoxyribonucleic acid) is the molecule that carries genetic information.",
           type=QAType.FOR_STUDY, level=1),
    ])

    # Programming
    qas.extend([
        QA(course_id=21, learning_unit_name="Variables and Data Types",
           question="What is a variable in programming?",
           answer="A variable is a named storage location that holds a value which can be changed during program execution.",
           type=QAType.FOR_STUDY, level=1),
        QA(course_id=21, learning_unit_name="Control Structures",
           question="What is a loop?",
           answer="A loop is a programming construct that repeats a block of code multiple times.",
           type=QAType.FOR_STUDY, level=2),
    ])

    session.add_all(qas)
    session.flush()


def add_study_sessions():
    """Add sample study sessions"""
    session = get_current_session()
    base_date = datetime.now() - timedelta(days=180)  # 6 months of data

    home_sessions = []
    school_sessions = []

    # Valid teacher (ai_model_id, name) pairs from add_teachers function
    teacher_pairs = [
        (1, "MathTutor"), (4, "AlgebraExpert"), (2, "GeometryGuide"),
        (1, "EnglishMentor"), (4, "GrammarGuru"),
        (2, "ScienceGuide"), (3, "PhysicsPro"),
        (2, "HistoryExplorer"), (1, "ChronicleKeeper"),
        (1, "CodeMaster"), (4, "PythonPro"),
        (3, "LitAnalyst"), (1, "BookWorm"),
        (2, "HebrewHelper"),
        (5, "FitnessCoach")
    ]

    # Create multiple study sessions over the past 180 days (6 months)
    for day_offset in range(0, 180, 3):  # Every 3 days
        session_date = base_date + timedelta(days=day_offset)

        # Home sessions (2 per period)
        for session_num in range(2):
            # Determine session status based on how recent the session is
            days_ago = (datetime.now() - session_date).days
            
            if days_ago > 30:
                # Old sessions are completed
                status = SessionStatus.COMPLETED
            elif days_ago > 7:
                # Recent sessions are completed
                status = SessionStatus.COMPLETED
            elif days_ago > 1:
                # Yesterday's sessions are completed
                status = SessionStatus.COMPLETED
            elif days_ago == 0:
                # Today's sessions might be active, paused, or completed
                status = random.choice([SessionStatus.ACTIVE, SessionStatus.PAUSED, SessionStatus.COMPLETED])
            else:
                # Future sessions are pending
                status = SessionStatus.PENDING
            
            teacher_ai_model_id, teacher_name = random.choice(teacher_pairs)
            home_sessions.append(HomeHoursStudySession(
                id=len(home_sessions) + 1,
                start_time=session_date + timedelta(hours=16 + session_num * 2),
                end_time=session_date + timedelta(hours=17 + session_num * 2, minutes=30) if status == SessionStatus.COMPLETED else None,
                status=status,
                teacher_ai_model_id=teacher_ai_model_id,
                teacher_name=teacher_name,
                type=random.choice([HomeHoursStudySessionType.HOMEWORK, HomeHoursStudySessionType.TEST_PREPARATION])
            ))

        # School sessions (2 per period)
        for session_num in range(2):
            # Determine session status based on how recent the session is
            days_ago = (datetime.now() - session_date).days
            
            if days_ago > 30:
                # Old sessions are completed
                status = SessionStatus.COMPLETED
            elif days_ago > 7:
                # Recent sessions are completed
                status = SessionStatus.COMPLETED
            elif days_ago > 1:
                # Yesterday's sessions are completed
                status = SessionStatus.COMPLETED
            elif days_ago == 0:
                # Today's sessions might be active, paused, or completed
                status = random.choice([SessionStatus.ACTIVE, SessionStatus.PAUSED, SessionStatus.COMPLETED])
            else:
                # Future sessions are pending
                status = SessionStatus.PENDING
            
            teacher_ai_model_id, teacher_name = random.choice(teacher_pairs)
            school_sessions.append(SchoolHoursStudySession(
                id=len(school_sessions) + 1,
                start_time=session_date + timedelta(hours=9 + session_num * 2),
                end_time=session_date + timedelta(hours=10 + session_num * 2, minutes=30) if status == SessionStatus.COMPLETED else None,
                status=status,
                teacher_ai_model_id=teacher_ai_model_id,
                teacher_name=teacher_name,
                class_manager_id=random.randint(3001, 3009),
                type=random.choice([SchoolHoursStudySessionType.GROUP, SchoolHoursStudySessionType.INDIVIDUAL,
                                    SchoolHoursStudySessionType.SOCIAL])
            ))

    session.add_all(home_sessions)
    session.add_all(school_sessions)
    session.flush()
    
    # Add a few current active sessions for testing
    current_time = datetime.now()
    
    # Add 2-3 active home sessions for different students
    active_home_sessions = []
    for i in range(3):
        student_id = 5001 + i  # First 3 students
        teacher_ai_model_id, teacher_name = random.choice(teacher_pairs)
        active_home_sessions.append(HomeHoursStudySession(
            id=len(home_sessions) + len(active_home_sessions) + 1,
            start_time=current_time - timedelta(minutes=random.randint(5, 30)),
            end_time=None,  # Active sessions don't have end_time
            status=SessionStatus.ACTIVE,
            teacher_ai_model_id=teacher_ai_model_id,
            teacher_name=teacher_name,
            type=random.choice([HomeHoursStudySessionType.HOMEWORK, HomeHoursStudySessionType.TEST_PREPARATION])
        ))
    
    session.add_all(active_home_sessions)
    session.flush()
    
    # Add 1-2 paused sessions for testing
    paused_home_sessions = []
    for i in range(2):
        student_id = 5004 + i  # Next 2 students
        teacher_ai_model_id, teacher_name = random.choice(teacher_pairs)
        paused_home_sessions.append(HomeHoursStudySession(
            id=len(home_sessions) + len(active_home_sessions) + len(paused_home_sessions) + 1,
            start_time=current_time - timedelta(hours=1),
            end_time=None,  # Paused sessions don't have end_time yet
            status=SessionStatus.PAUSED,
            teacher_ai_model_id=teacher_ai_model_id,
            teacher_name=teacher_name,
            type=random.choice([HomeHoursStudySessionType.HOMEWORK, HomeHoursStudySessionType.TEST_PREPARATION])
        ))
    
    session.add_all(paused_home_sessions)
    session.flush()


def add_evaluations():
    """Add sample evaluations with realistic performance correlation"""
    session = get_current_session()
    eval_date = date.today() - timedelta(days=30)

    # Get student performance data from their test results to create consistent evaluations
    test_students = session.query(TestStudent).filter(
        TestStudent.final_grade.isnot(None)
    ).all()

    # Build student average grades
    student_avg_grades = {}
    for ts in test_students:
        if ts.student_id not in student_avg_grades:
            student_avg_grades[ts.student_id] = []
        student_avg_grades[ts.student_id].append(ts.final_grade)

    # Calculate averages
    for student_id in student_avg_grades:
        student_avg_grades[student_id] = sum(student_avg_grades[student_id]) / len(student_avg_grades[student_id])

    # Sessional proficiency evaluations - correlated with actual performance
    sessional_prof_evals = []
    for student_id in range(5001, 5051):  # All 50 students
        # Determine score based on test performance if available
        if student_id in student_avg_grades:
            avg_grade = student_avg_grades[student_id]
            if avg_grade >= 90:
                score = random.randint(9, 10)
                descriptions = [
                    "Outstanding analytical skills",
                    "Excellent performance across all topics",
                    "Demonstrates mastery of concepts",
                    "Exceptional understanding and application"
                ]
            elif avg_grade >= 80:
                score = random.randint(8, 9)
                descriptions = [
                    "Strong understanding of concepts",
                    "Excellent performance",
                    "Mastering core material well",
                    "Demonstrates critical thinking"
                ]
            elif avg_grade >= 70:
                score = random.randint(7, 8)
                descriptions = [
                    "Good progress, needs more practice",
                    "Shows dedication to learning",
                    "Consistent improvement",
                    "Steady progress in all subjects"
                ]
            else:
                score = random.randint(6, 7)
                descriptions = [
                    "Needs additional support in some areas",
                    "Working to improve understanding",
                    "Shows effort, requires more practice",
                    "Making gradual progress"
                ]
        else:
            # Student hasn't taken tests yet - moderate score
            score = random.randint(6, 8)
            descriptions = [
                "Beginning to engage with material",
                "Early progress observed",
                "Building foundational skills"
            ]

        sessional_prof_evals.append(SessionalProficiencyEvaluation(
            id=student_id - 5000,
            student_id=student_id,
            date=eval_date - timedelta(days=random.randint(0, 90)),
            score=score,
            evaluator_id=random.randint(1, 4),
            evaluator_evaluation_description=random.choice(descriptions)
        ))

    session.add_all(sessional_prof_evals)
    session.flush()

    # Sessional investment evaluations - correlated with proficiency
    sessional_inv_evals = []
    for idx, student_id in enumerate(range(5001, 5051)):  # All 50 students
        # Investment score should correlate with proficiency
        prof_score = sessional_prof_evals[idx].score
        # Add some variation but keep it close to proficiency score
        score = min(10, max(1, prof_score + random.randint(-1, 1)))

        if score >= 9:
            ai_desc = random.choice([
                "Highly motivated and focused",
                "Exceptional dedication to studies",
                "Active and enthusiastic learner",
                "Consistently goes above and beyond"
            ])
            manager_desc = random.choice([
                "Demonstrates strong work ethic",
                "Participates actively in all activities",
                "Shows outstanding initiative"
            ])
        elif score >= 7:
            ai_desc = random.choice([
                "Good engagement and participation",
                "Shows genuine interest in learning",
                "Consistent effort in all activities",
                "Good time management skills"
            ])
            manager_desc = random.choice([
                "Active in class discussions",
                "Completes assignments on time",
                "Shows initiative in learning",
                "Engaged and attentive in class"
            ])
        else:
            ai_desc = random.choice([
                "Needs encouragement to participate more",
                "Shows potential, needs more engagement",
                "Working on building consistency"
            ])
            manager_desc = random.choice([
                "Would benefit from more participation",
                "Needs support to stay engaged",
                "Developing study habits"
            ])

        sessional_inv_evals.append(SessionalInvestmentEvaluation(
            id=student_id - 5000,
            student_id=student_id,
            date=eval_date - timedelta(days=random.randint(0, 90)),
            score=score,
            evaluator_id=random.randint(1, 4),
            evaluator_evaluation_description=ai_desc,
            class_manager_id=random.randint(3001, 3009),
            class_manager_evaluation_description=manager_desc
        ))

    session.add_all(sessional_inv_evals)
    session.flush()

    # Sessional social evaluations - varied but realistic
    sessional_soc_evals = []
    for idx, student_id in enumerate(range(5001, 5051)):  # All 50 students
        # Social scores are more independent but still somewhat correlated
        score = random.randint(6, 10)

        if score >= 9:
            descriptions = [
                "Excellent collaboration skills",
                "Shows leadership potential",
                "Contributes positively to class environment",
                "Outstanding social awareness"
            ]
        elif score >= 7:
            descriptions = [
                "Works well in groups",
                "Good team player",
                "Helps other students",
                "Respectful and considerate of peers",
                "Shows empathy and understanding"
            ]
        else:
            descriptions = [
                "Needs improvement in peer interactions",
                "Working on collaboration skills",
                "Developing social confidence"
            ]

        sessional_soc_evals.append(SessionalSocialEvaluation(
            id=idx + 1,
            student_id=student_id,
            date=eval_date - timedelta(days=random.randint(0, 90)),
            score=score,
            class_manager_id=random.randint(3001, 3009),
            class_manager_evaluation_description=random.choice(descriptions)
        ))

    session.add_all(sessional_soc_evals)
    session.flush()


def _order_units_by_sequence(units_list):
    """
    Order learning units based on their previous/next relationships.
    
    Args:
        units_list: List of LearningUnit objects
        
    Returns:
        List of LearningUnit objects in sequential order
    """
    if not units_list:
        return []

    # Build a dictionary for quick lookup
    units_dict = {unit.name: unit for unit in units_list}

    # Find the first unit (one with no previous_learning_unit or previous not in dict)
    first_unit = None
    for unit in units_list:
        if not unit.previous_learning_unit or unit.previous_learning_unit not in units_dict:
            first_unit = unit
            break

    # If no clear first unit found, fall back to original order
    if first_unit is None:
        return units_list

    # Follow the chain from first to last
    ordered = []
    current = first_unit
    visited = set()  # Prevent infinite loops in case of cycles

    while current and current.name not in visited:
        ordered.append(current)
        visited.add(current.name)

        # Get the next unit
        next_unit_name = current.next_learning_unit

        # Only continue if next_unit exists in our dictionary
        if next_unit_name and next_unit_name in units_dict:
            current = units_dict[next_unit_name]
        else:
            current = None

    # Add any remaining units that weren't in the chain (orphaned units)
    for unit in units_list:
        if unit.name not in visited:
            ordered.append(unit)

    return ordered


def add_quarter_evaluations():
    """Add sample quarter evaluations consistent with sessional evaluations"""
    session = get_current_session()
    eval_date = date.today() - timedelta(days=120)

    # Get sessional evaluations to maintain consistency
    sessional_prof = session.query(SessionalProficiencyEvaluation).all()
    sessional_inv = session.query(SessionalInvestmentEvaluation).all()
    sessional_soc = session.query(SessionalSocialEvaluation).all()

    # Build maps for quick lookup
    prof_map = {eval.student_id: eval.score for eval in sessional_prof}
    inv_map = {eval.student_id: eval.score for eval in sessional_inv}
    soc_map = {eval.student_id: eval.score for eval in sessional_soc}

    # Quarter proficiency evaluations - correlated with sessional
    quarter_prof_evals = []
    for idx, student_id in enumerate(range(5001, 5051)):  # All 50 students
        # Quarter scores should be similar to or slightly lower than recent sessional scores
        base_score = prof_map.get(student_id, 7)
        score = max(1, min(10, base_score + random.randint(-1, 0)))  # Same or slightly lower

        if score >= 9:
            descriptions = [
                "Outstanding academic performance",
                "Excellent progress this quarter",
                "Demonstrates mastery across all topics"
            ]
        elif score >= 7:
            descriptions = [
                "Strong quarterly performance",
                "Solid understanding demonstrated",
                "Good mastery of subject matter",
                "Shows continuous improvement"
            ]
        else:
            descriptions = [
                "Making steady progress",
                "Building foundations this quarter",
                "Developing understanding"
            ]

        quarter_prof_evals.append(QuarterProficiencyEvaluation(
            id=idx + 1,
            student_id=student_id,
            date=eval_date,
            score=score,
            evaluator_id=random.randint(1, 4),
            evaluator_evaluation_description=random.choice(descriptions),
            subject_name=random.choice(
                [SubjectName.MATH, SubjectName.ENGLISH, SubjectName.SCIENCE, SubjectName.HISTORY])
        ))

    session.add_all(quarter_prof_evals)
    session.flush()

    # Quarter investment evaluations - correlated with sessional
    quarter_inv_evals = []
    for idx, student_id in enumerate(range(5001, 5051)):  # All 50 students
        base_score = inv_map.get(student_id, 7)
        score = max(1, min(10, base_score + random.randint(-1, 0)))

        if score >= 9:
            ai_desc = random.choice([
                "Excellent participation and effort",
                "Highly engaged in coursework",
                "Demonstrates sustained dedication"
            ])
            manager_desc = random.choice([
                "Shows excellent work habits",
                "Reliable and committed",
                "Always ready to learn"
            ])
        elif score >= 7:
            ai_desc = random.choice([
                "Consistent engagement throughout quarter",
                "Strong commitment to learning",
                "Good attendance and focus"
            ])
            manager_desc = random.choice([
                "Dedicated student",
                "Consistently prepared for class",
                "Positive attitude towards studies"
            ])
        else:
            ai_desc = random.choice([
                "Working on building engagement",
                "Shows potential for improvement",
                "Developing study habits"
            ])
            manager_desc = random.choice([
                "Needs support to stay focused",
                "Would benefit from more participation",
                "Building consistency"
            ])

        quarter_inv_evals.append(QuarterInvestmentEvaluation(
            id=idx + 1,
            student_id=student_id,
            date=eval_date,
            score=score,
            evaluator_id=random.randint(1, 4),
            evaluator_evaluation_description=ai_desc,
            class_manager_id=random.randint(3001, 3009),
            class_manager_evaluation_description=manager_desc,
            subject_name=random.choice(
                [SubjectName.MATH, SubjectName.ENGLISH, SubjectName.SCIENCE, SubjectName.HISTORY])
        ))

    session.add_all(quarter_inv_evals)
    session.flush()

    # Quarter social evaluations - correlated with sessional
    quarter_soc_evals = []
    for idx, student_id in enumerate(range(5001, 5051)):  # All 50 students
        base_score = soc_map.get(student_id, 7)
        score = max(1, min(10, base_score + random.randint(-1, 0)))

        if score >= 9:
            descriptions = [
                "Excellent social development this quarter",
                "Outstanding leadership in class activities",
                "Demonstrates maturity in social situations"
            ]
        elif score >= 7:
            descriptions = [
                "Strong progress in teamwork skills",
                "Positive peer relationships throughout quarter",
                "Good collaboration in group projects",
                "Shows consistent respect for others",
                "Helpful and supportive of classmates"
            ]
        else:
            descriptions = [
                "Growing confidence in social interactions",
                "Working on communication skills",
                "Developing peer interaction skills"
            ]

        quarter_soc_evals.append(QuarterSocialEvaluation(
            id=idx + 1,
            student_id=student_id,
            date=eval_date,
            score=score,
            class_manager_id=random.randint(3001, 3009),
            class_manager_evaluation_description=random.choice(descriptions)
        ))

    session.add_all(quarter_soc_evals)
    session.flush()


def add_associations():
    """Add association table data to connect entities"""
    session = get_current_session()

    # Declare all global variables at the beginning
    global _parent_student_mapping, _tablet_serial_numbers, _student_grade_mapping, _student_school_mapping

    # Parent-Student relationships (use the tracked mapping from add_students_and_parents)
    parent_students = []
    for parent_id, student_id in _parent_student_mapping:
        parent_students.append(ParentStudent(parent_id=parent_id, student_id=student_id))

    session.add_all(parent_students)
    session.flush()

    # Tablet-Student assignments (use the tracked serial numbers from add_tablets)
    tablet_students = []
    student_ids = sorted(_student_grade_mapping.keys())  # Get all student IDs
    for idx, student_id in enumerate(student_ids):
        if idx < len(_tablet_serial_numbers):  # Make sure we have a tablet available
            tablet_students.append(TabletStudent(
                serial_number=_tablet_serial_numbers[idx],
                student_id=student_id,
                start_date=date(2023, 9, 1),
                end_date=None
            ))

    session.add_all(tablet_students)
    session.flush()

    # Course-Student enrollments with realistic progress
    course_students = []
    learning_unit_students = []
    test_students = []

    # Get all learning units by course for later use
    all_learning_units = session.query(LearningUnit).all()
    course_to_units = {}
    for lu in all_learning_units:
        if lu.course_id not in course_to_units:
            course_to_units[lu.course_id] = []
        course_to_units[lu.course_id].append(lu)

    # Sort units by their sequence for each course
    for course_id in course_to_units:
        course_to_units[course_id] = _order_units_by_sequence(course_to_units[course_id])

    # Map students to appropriate courses based on grade level
    for student_id in _student_grade_mapping.keys():
        # Get the student's grade level from the mapping
        grade = _student_grade_mapping[student_id]

        # Assign a performance profile to each student (affects all their courses)
        # This creates realistic variation: some students are high-achievers, some struggle
        student_performance = random.choice(['high', 'high', 'medium', 'medium', 'medium', 'low'])

        # Get courses for this grade level (mandatory + some optional)
        if grade == GradeLevel.NINTH:
            course_ids = [1, 2, 7, 12, 17, 21, 26, 30, 34]  # 9 courses
        elif grade == GradeLevel.TENTH:
            course_ids = [3, 4, 8, 9, 13, 14, 18, 22, 27, 31, 35]  # 11 courses
        elif grade == GradeLevel.ELEVENTH:
            course_ids = [5, 10, 15, 16, 19, 23, 24, 28, 32, 36]  # 10 courses
        else:  # TWELFTH
            course_ids = [6, 11, 20, 25, 29, 33, 37]  # 7 courses

        # Enroll in courses with realistic progression
        for idx, course_id in enumerate(course_ids):
            # Determine course state and progress based on position in curriculum
            # Earlier courses are more likely to be completed
            course_position = idx / len(course_ids)

            # Generate realistic progress based on student performance and course position
            if student_performance == 'high':
                if course_position < 0.7:
                    # High performers complete most courses
                    progress = 1.0
                    state = CourseState.COMPLETED
                elif course_position < 0.9:
                    # Active in current courses
                    progress = random.uniform(0.5, 0.95)
                    state = CourseState.IN_PROGRESS
                else:
                    # Haven't started last courses yet
                    progress = random.choice([0.0, random.uniform(0.1, 0.3)])
                    state = CourseState.NOT_STARTED if progress == 0.0 else CourseState.IN_PROGRESS
            elif student_performance == 'medium':
                if course_position < 0.5:
                    # Medium performers complete half
                    progress = 1.0
                    state = CourseState.COMPLETED
                elif course_position < 0.8:
                    # Working through middle courses
                    progress = random.uniform(0.3, 0.85)
                    state = CourseState.IN_PROGRESS
                else:
                    # Last courses not started or just begun
                    progress = random.choice([0.0, 0.0, random.uniform(0.05, 0.2)])
                    state = CourseState.NOT_STARTED if progress == 0.0 else CourseState.IN_PROGRESS
            else:  # low performance
                if course_position < 0.3:
                    # Low performers complete fewer courses
                    progress = random.choice([1.0, random.uniform(0.7, 0.95)])
                    state = CourseState.COMPLETED if progress == 1.0 else CourseState.IN_PROGRESS
                elif course_position < 0.6:
                    # Struggling through current courses
                    progress = random.uniform(0.2, 0.6)
                    state = CourseState.IN_PROGRESS
                else:
                    # Many courses not yet started
                    progress = random.choice([0.0, 0.0, 0.0, random.uniform(0.05, 0.15)])
                    state = CourseState.NOT_STARTED if progress == 0.0 else CourseState.IN_PROGRESS

            course_students.append(CourseStudent(
                course_id=course_id,
                student_id=student_id,
                state=state,
                progress=progress
            ))

            # Add learning unit progress that matches course progress
            if course_id in course_to_units and progress > 0:
                units = course_to_units[course_id]
                units_completed = int(len(units) * progress)

                for unit_idx, unit in enumerate(units):
                    if unit_idx < units_completed:
                        # Completed units
                        learning_unit_students.append(LearningUnitStudent(
                            course_id=course_id,
                            learning_unit_name=unit.name,
                            student_id=student_id,
                            state=CourseState.COMPLETED,
                            progress=1.0
                        ))
                    elif unit_idx == units_completed and progress < 1.0:
                        # Current unit in progress
                        # Calculate partial progress within this unit
                        unit_progress = (progress * len(units)) - units_completed
                        learning_unit_students.append(LearningUnitStudent(
                            course_id=course_id,
                            learning_unit_name=unit.name,
                            student_id=student_id,
                            state=CourseState.IN_PROGRESS,
                            progress=unit_progress
                        ))
                        break  # Stop after current unit

            # Add test results for courses that have significant progress
            if progress >= 0.3:  # Only add tests if course is at least 30% complete
                # Get tests for this course
                tests = session.query(Test).filter(Test.course_id == course_id).all()

                for test in tests:
                    # Determine if student has taken this test based on progress
                    test_threshold = {
                        TestType.QUIZ: 0.3,
                        TestType.MID_TERM: 0.6,
                        TestType.FINAL_EXAM: 0.95
                    }.get(test.type, 0.5)

                    if progress >= test_threshold:
                        # Student has taken or should take this test
                        if progress >= test_threshold + 0.1:
                            # Test completed
                            # Grade correlates with student performance
                            if student_performance == 'high':
                                grade = random.randint(85, 100)
                            elif student_performance == 'medium':
                                grade = random.randint(70, 90)
                            else:
                                grade = random.randint(60, 80)

                            status = TestStatus.PASSED if grade >= 60 else TestStatus.FAILED
                            
                            # Generate realistic test dates based on course position and test type
                            # Earlier courses should have older test dates (up to 12 months ago)
                            # Later courses should have more recent test dates
                            
                            # Base days back increases with how early the course is in the curriculum
                            base_days_back = int(90 + (course_position * 270))  # 90 to 360 days ago
                            
                            # Add variation based on test type
                            if test.type == TestType.QUIZ:
                                # Quizzes happen earlier in the course
                                days_back = base_days_back + random.randint(0, 30)
                            elif test.type == TestType.MID_TERM:
                                # Midterms in the middle
                                days_back = base_days_back - random.randint(10, 40)
                            else:  # FINAL_EXAM
                                # Finals happen most recently for that course
                                days_back = base_days_back - random.randint(30, 60)
                            
                            # Ensure test date is at least 1 day ago
                            days_back = max(1, days_back)
                            test_date = date.today() - timedelta(days=days_back)
                        else:
                            # Test upcoming
                            grade = None
                            status = TestStatus.SCHEDULED
                            test_date = date.today() + timedelta(days=random.randint(3, 21))

                        # Get appropriate teacher for this course
                        course = session.query(Course).filter(Course.id == course_id).first()
                        teacher = session.query(Teacher).filter(
                            Teacher.subject_name == course.subject_name
                        ).first()

                        if teacher:
                            test_students.append(TestStudent(
                                course_id=course_id,
                                test_name=test.name,
                                student_id=student_id,
                                teacher_ai_model_id=teacher.ai_model_id,
                                teacher_name=teacher.name,
                                status=status,
                                date=test_date,
                                final_grade=grade
                            ))

    session.add_all(course_students)
    session.flush()

    session.add_all(learning_unit_students)
    session.flush()

    session.add_all(test_students)
    session.flush()

    # Class-ClassManager assignments
    class_managers = [
        # Tel Aviv
        ClassClassManager(school_id=1, class_year=2024, class_grade_level=GradeLevel.NINTH, class_manager_id=3001),
        ClassClassManager(school_id=1, class_year=2024, class_grade_level=GradeLevel.TENTH, class_manager_id=3002),
        ClassClassManager(school_id=1, class_year=2024, class_grade_level=GradeLevel.ELEVENTH, class_manager_id=3003),
        ClassClassManager(school_id=1, class_year=2024, class_grade_level=GradeLevel.TWELFTH, class_manager_id=3001),

        # Haifa
        ClassClassManager(school_id=2, class_year=2024, class_grade_level=GradeLevel.NINTH, class_manager_id=3004),
        ClassClassManager(school_id=2, class_year=2024, class_grade_level=GradeLevel.TENTH, class_manager_id=3005),
        ClassClassManager(school_id=2, class_year=2024, class_grade_level=GradeLevel.ELEVENTH, class_manager_id=3006),
        ClassClassManager(school_id=2, class_year=2024, class_grade_level=GradeLevel.TWELFTH, class_manager_id=3004),

        # Jerusalem
        ClassClassManager(school_id=3, class_year=2024, class_grade_level=GradeLevel.NINTH, class_manager_id=3007),
        ClassClassManager(school_id=3, class_year=2024, class_grade_level=GradeLevel.TENTH, class_manager_id=3008),
        ClassClassManager(school_id=3, class_year=2024, class_grade_level=GradeLevel.ELEVENTH, class_manager_id=3009),
        ClassClassManager(school_id=3, class_year=2024, class_grade_level=GradeLevel.TWELFTH, class_manager_id=3007),
    ]

    session.add_all(class_managers)
    session.flush()

    # Class-Student assignments (use the tracked mappings)
    class_students = []
    for student_id in _student_grade_mapping.keys():
        school_id = _student_school_mapping[student_id]
        grade = _student_grade_mapping[student_id]

        class_students.append(ClassStudent(
            school_id=school_id,
            class_year=2024,
            class_grade_level=grade,
            student_id=student_id
        ))

    session.add_all(class_students)
    session.flush()

    # Subject-RegionalSupervisor assignments
    subject_supervisors = [
        SubjectRegionalSupervisor(
            subject_name=SubjectName.MATH, subject_year=2024,
            subject_region=Region.TEL_AVIV, regional_supervisor_id=2001
        ),
        SubjectRegionalSupervisor(
            subject_name=SubjectName.SCIENCE, subject_year=2024,
            subject_region=Region.HAIFA, regional_supervisor_id=2002
        ),
        SubjectRegionalSupervisor(
            subject_name=SubjectName.HISTORY, subject_year=2024,
            subject_region=Region.CENTER, regional_supervisor_id=2003
        ),
    ]

    session.add_all(subject_supervisors)
    session.flush()

    # Study session participants with realistic attendance patterns
    home_session_students = []
    school_session_students = []
    all_student_ids = sorted(_student_grade_mapping.keys())

    # Get student performance profiles (correlate with investment evaluations if available)
    student_performance_profile = {}
    inv_evals = session.query(SessionalInvestmentEvaluation).all()
    for eval in inv_evals:
        if eval.score >= 9:
            student_performance_profile[eval.student_id] = 'high'
        elif eval.score >= 7:
            student_performance_profile[eval.student_id] = 'medium'
        else:
            student_performance_profile[eval.student_id] = 'low'

    # For students without evaluations, assign random profile
    for student_id in all_student_ids:
        if student_id not in student_performance_profile:
            student_performance_profile[student_id] = random.choice(['high', 'medium', 'medium', 'low'])

    for session_id in range(1, min(46, 100)):  # First 45 home sessions (40 original + 3 active + 2 paused)
        # Add 1-3 unique students per session
        num_students = random.randint(1, 3)
        selected_students = random.sample(all_student_ids, min(num_students, len(all_student_ids)))

        for student_id in selected_students:
            performance = student_performance_profile.get(student_id, 'medium')

            # High performers: always attend, positive emotions, good feedback
            if performance == 'high':
                is_attendant = True
                emotional_before = random.choice(
                    [EmotionalState.POSITIVE, EmotionalState.POSITIVE, EmotionalState.NEUTRAL])
                emotional_after = random.choice(
                    [EmotionalState.POSITIVE, EmotionalState.POSITIVE, EmotionalState.NEUTRAL])
                difficulty = random.randint(7, 10)
                understanding = random.randint(8, 10)
                feedback = random.choice([
                    "Great session!", "Very helpful", "Learned a lot today",
                    "Excellent explanation", "Really understand now"
                ])
            # Medium performers: usually attend, mixed emotions
            elif performance == 'medium':
                is_attendant = random.choice([True, True, True, False])
                emotional_before = random.choice(
                    [EmotionalState.POSITIVE, EmotionalState.NEUTRAL, EmotionalState.NEUTRAL])
                emotional_after = random.choice([EmotionalState.POSITIVE, EmotionalState.NEUTRAL])
                difficulty = random.randint(5, 8)
                understanding = random.randint(6, 9)
                feedback = random.choice([
                    "Good session", "Helpful", "Need more practice",
                    "Getting better", "Some parts were hard"
                ])
            # Low performers: sometimes miss, more negative emotions
            else:
                is_attendant = random.choice([True, True, False])
                emotional_before = random.choice(
                    [EmotionalState.NEUTRAL, EmotionalState.NEUTRAL, EmotionalState.NEGATIVE])
                emotional_after = random.choice([EmotionalState.NEUTRAL, EmotionalState.POSITIVE])
                difficulty = random.randint(4, 7)
                understanding = random.randint(5, 8)
                feedback = random.choice([
                    "Need more help", "Still confused", "Difficult topic",
                    "Need more time", "Trying my best"
                ])

            home_session_students.append(HomeHoursStudySessionStudent(
                home_hours_study_session_id=session_id,
                student_id=student_id,
                emotional_state_before=emotional_before,
                emotional_state_after=emotional_after,
                is_attendant=is_attendant,
                attendance_reason=None if is_attendant else random.choice(
                    [AttendanceReason.SICK, AttendanceReason.EXCUSED, None]),
                difficulty_feedback=difficulty if is_attendant else None,
                understanding_feedback=understanding if is_attendant else None,
                textual_feedback=feedback if is_attendant else None
            ))

    session.add_all(home_session_students)
    session.flush()

    for session_id in range(1, min(41, 100)):  # First 40 school sessions
        # Add 3-8 unique students per session (group sessions)
        num_students = random.randint(3, 8)
        selected_students = random.sample(all_student_ids, min(num_students, len(all_student_ids)))

        for student_id in selected_students:
            performance = student_performance_profile.get(student_id, 'medium')

            # Attendance rates vary by performance
            if performance == 'high':
                is_attendant = random.choice([True, True, True, True, True, False])  # 83% attendance
                difficulty = random.randint(7, 10)
                understanding = random.randint(8, 10)
                feedback = random.choice([
                    "Good class", "Learned a lot", "Interesting topic",
                    "Enjoyed the discussion", "Very productive"
                ])
            elif performance == 'medium':
                is_attendant = random.choice([True, True, True, False])  # 75% attendance
                difficulty = random.randint(5, 8)
                understanding = random.randint(6, 9)
                feedback = random.choice([
                    "Good session", "Fun activities", "Need more time",
                    "Helpful lesson", "Okay class"
                ])
            else:
                is_attendant = random.choice([True, True, False])  # 67% attendance
                difficulty = random.randint(4, 7)
                understanding = random.randint(5, 8)
                feedback = random.choice([
                    "Hard to follow", "Need more help", "Confusing",
                    "Didn't understand everything", "Need review"
                ])

            school_session_students.append(SchoolHoursStudySessionStudent(
                school_hours_study_session_id=session_id,
                student_id=student_id,
                emotional_state_before=random.choice(
                    [EmotionalState.POSITIVE, EmotionalState.NEUTRAL, EmotionalState.NEGATIVE]),
                emotional_state_after=random.choice([EmotionalState.POSITIVE, EmotionalState.NEUTRAL]),
                is_attendant=is_attendant,
                attendance_reason=None if is_attendant else random.choice(
                    [AttendanceReason.SICK, AttendanceReason.EXCUSED, None]),
                difficulty_feedback=difficulty if is_attendant else None,
                understanding_feedback=understanding if is_attendant else None,
                textual_feedback=feedback if is_attendant else None
            ))

    session.add_all(school_session_students)
    session.flush()


def add_study_session_pauses():
    """Add sample study session pauses"""
    session = get_current_session()
    base_date = datetime.now() - timedelta(days=60)

    home_pauses = []
    for session_id in range(1, min(21, 50)):  # First 20 home sessions
        session_start = base_date + timedelta(days=session_id * 3, hours=16)
        home_pauses.append(HomeHoursStudySessionPause(
            home_hours_study_session_id=session_id,
            start_time=session_start + timedelta(minutes=30),
            end_time=session_start + timedelta(minutes=35)
        ))

    session.add_all(home_pauses)
    session.flush()

    school_pauses = []
    for session_id in range(1, min(21, 50)):  # First 20 school sessions
        session_start = base_date + timedelta(days=session_id * 3, hours=9)
        school_pauses.append(SchoolHoursStudySessionPause(
            school_hours_study_session_id=session_id,
            start_time=session_start + timedelta(minutes=45),
            end_time=session_start + timedelta(minutes=55)
        ))

    session.add_all(school_pauses)
    session.flush()


def add_learning_unit_sessions():
    """Add sample learning unit session relationships"""
    session = get_current_session()
    # Home sessions
    home_unit_sessions = []
    for session_id in range(1, min(21, 50)):
        # Link to 1-2 learning units
        home_unit_sessions.append(LearningUnitsHomeHoursStudySession(
            course_id=1,
            learning_unit_name=random.choice(["Variables and Expressions", "Linear Equations"]),
            home_hours_study_session_id=session_id
        ))

    session.add_all(home_unit_sessions)
    session.flush()

    # School sessions
    school_unit_sessions = []
    for session_id in range(1, min(21, 50)):
        school_unit_sessions.append(LearningUnitsSchoolHoursStudySession(
            course_id=1,
            learning_unit_name=random.choice(["Systems of Equations", "Quadratic Functions"]),
            school_hours_study_session_id=session_id
        ))

    session.add_all(school_unit_sessions)
    session.flush()


def add_messages_and_attachments():
    """Add sample messages and attachments"""
    session = get_current_session()
    base_date = datetime.now() - timedelta(days=90)

    messages = []
    message_id = 1

    # Valid teacher (ai_model_id, name) pairs from add_teachers function
    teacher_pairs = [
        (1, "MathTutor"), (4, "AlgebraExpert"), (2, "GeometryGuide"),
        (1, "EnglishMentor"), (4, "GrammarGuru"),
        (2, "ScienceGuide"), (3, "PhysicsPro"),
        (2, "HistoryExplorer"), (1, "ChronicleKeeper"),
        (1, "CodeMaster"), (4, "PythonPro"),
        (3, "LitAnalyst"), (1, "BookWorm"),
        (2, "HebrewHelper"),
        (5, "FitnessCoach")
    ]

    # Create conversation chains for multiple sessions
    for session_num in range(1, 11):  # 10 sessions with conversations
        session_time = base_date + timedelta(days=session_num * 3, hours=16)

        teacher_ai_model_id, teacher_name = random.choice(teacher_pairs)

        # Teacher greeting
        messages.append(Message(
            id=message_id,
            content=f"Hi! Ready to work on today's lesson?",
            timestamp=session_time,
            type=MessageType.RESPONSE,
            modality=MessageModality.TEXT_ONLY,
            home_study_session_id=session_num,
            teacher_ai_model_id=teacher_ai_model_id,
            teacher_name=teacher_name,
            student_id=None,
            previous_message_id=None,
            next_message_id=message_id + 1
        ))
        message_id += 1

        # Student response
        messages.append(Message(
            id=message_id,
            content="Yes, I'm ready to learn!",
            timestamp=session_time + timedelta(minutes=1),
            type=MessageType.PROMPT,
            modality=MessageModality.TEXT_ONLY,
            home_study_session_id=session_num,
            teacher_ai_model_id=None,
            teacher_name=None,
            student_id=5001 + (session_num % 50),
            previous_message_id=message_id - 1,
            next_message_id=message_id + 1
        ))
        message_id += 1

        # Teacher instruction
        messages.append(Message(
            id=message_id,
            content="Great! Let's start with this problem...",
            timestamp=session_time + timedelta(minutes=2),
            type=MessageType.RESPONSE,
            modality=MessageModality.TEXT_ONLY,
            home_study_session_id=session_num,
            teacher_ai_model_id=teacher_ai_model_id,
            teacher_name=teacher_name,
            student_id=None,
            previous_message_id=message_id - 1,
            next_message_id=None
        ))
        message_id += 1

    # Insert messages
    for message in messages:
        message_copy = Message(
            id=message.id,
            content=message.content,
            timestamp=message.timestamp,
            type=message.type,
            modality=message.modality,
            previous_message_id=message.previous_message_id,
            next_message_id=None,
            home_study_session_id=message.home_study_session_id,
            school_study_session_id=message.school_study_session_id,
            student_id=message.student_id,
            teacher_ai_model_id=message.teacher_ai_model_id,
            teacher_name=message.teacher_name
        )
        session.add(message_copy)

    session.flush()

    # Update next_message_id
    for message in messages:
        if message.next_message_id is not None:
            session.query(Message).filter(Message.id == message.id).update({
                'next_message_id': message.next_message_id
            })

    session.flush()

    # Attachments
    attachments = []
    for msg_id in [3, 6, 9, 12, 15]:  # Add attachments to some messages
        attachments.append(Attachment(
            message_id=msg_id,
            url=f"https://eduplatform.com/resources/lesson_{msg_id}.pdf",
            file_type=FileType.PDF
        ))

    session.add_all(attachments)
    session.flush()


def add_evaluation_session_associations():
    """Add sample evaluation-session association tables"""
    session = get_current_session()
    # Link evaluations to sessions - expanded to match more evaluations
    prof_home_assocs = []
    for eval_id in range(1, min(41, 51)):  # Link more proficiency evaluations
        prof_home_assocs.append(SessionalProficiencyEvaluationHomeHoursStudySession(
            sessional_proficiency_evaluation_id=eval_id,
            home_hours_study_session_id=eval_id
        ))

    session.add_all(prof_home_assocs)
    session.flush()

    prof_school_assocs = []
    for eval_id in range(1, min(41, 51)):  # Link more proficiency evaluations
        prof_school_assocs.append(SessionalProficiencyEvaluationSchoolHoursStudySession(
            sessional_proficiency_evaluation_id=eval_id,
            school_hours_study_session_id=eval_id
        ))

    session.add_all(prof_school_assocs)
    session.flush()

    inv_home_assocs = []
    for eval_id in range(1, min(41, 51)):  # Link more investment evaluations
        inv_home_assocs.append(SessionalInvestmentEvaluationHomeHoursStudySession(
            sessional_investment_evaluation_id=eval_id,
            home_hours_study_session_id=eval_id
        ))

    session.add_all(inv_home_assocs)
    session.flush()

    inv_school_assocs = []
    for eval_id in range(1, min(41, 51)):  # Link more investment evaluations
        inv_school_assocs.append(SessionalInvestmentEvaluationSchoolHoursStudySession(
            sessional_investment_evaluation_id=eval_id,
            school_hours_study_session_id=eval_id
        ))

    session.add_all(inv_school_assocs)
    session.flush()

    soc_school_assocs = []
    for eval_id in range(1, min(41, 51)):  # Link more social evaluations to sessions
        soc_school_assocs.append(SessionalSocialEvaluationSchoolHoursStudySession(
            sessional_social_evaluation_id=eval_id,
            school_hours_study_session_id=eval_id
        ))

    session.add_all(soc_school_assocs)
    session.flush()
