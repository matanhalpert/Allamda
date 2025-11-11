# Course Prioritization Service

A sophisticated, plugin-based course prioritization system designed to intelligently rank courses by learning priority for individual students or groups. This service uses a modular architecture built on the Strategy Pattern for maximum flexibility and extensibility.

## Overview

The Course Prioritization Service helps determine which courses students should focus on next based on multiple factors including:
- Course progress
- Upcoming test dates and urgency
- Historical test performance
- Student feedback from study sessions
- Course state (in-progress, not started, completed)

## Architecture

The service follows a **plugin-based architecture** with clear separation of concerns:

```
course_prioritization/
├── __init__.py                    # Main exports and convenience functions
├── scoring_factors.py             # Individual scoring components
├── aggregation_strategies.py     # Group score aggregation methods
├── scorer.py                      # Score calculation and combination
├── service.py                     # Main service API
├── builder.py                     # Builder pattern for configuration
└── README.md                      # This file
```

### Core Components

#### 1. **Scoring Factors** (`scoring_factors.py`)
Independent, testable components that evaluate specific aspects of course priority. Each factor:
- Returns a score between 0 and 1 (higher = higher priority)
- Has a configurable weight
- Can be easily added, removed, or customized

**Built-in Factors:**
- `CourseProgressFactor`: Prioritizes courses with lower completion (inverse relationship)
- `TestUrgencyFactor`: Prioritizes courses with upcoming tests (exponential decay)
- `TestPerformanceFactor`: Prioritizes courses with lower historical grades
- `StudentFeedbackFactor`: Prioritizes courses with negative student feedback
- `CourseStateFactor`: Prioritizes in-progress courses over not-started or completed

#### 2. **Course Scorer** (`scorer.py`)
Combines multiple scoring factors with normalized weights to produce an overall priority score:
- Automatically normalizes weights to sum to 1.0
- Can return detailed factor breakdowns for transparency
- Uses composition for flexibility

#### 3. **Aggregation Strategies** (`aggregation_strategies.py`)
Different approaches for combining individual student scores into group priorities:

- `AverageAggregation`: Democratic approach - simple average
- `WeightedAverageAggregation`: Prioritizes struggling students (lower grades = higher weight)
- `HighestNeedAggregation`: "No student left behind" - focuses on the student with highest priority score
- `MaxBasedAggregation`: Maximum engagement potential
- `BalancedAggregation`: 60% average + 40% highest-need (recommended default)

#### 4. **Prioritization Service** (`service.py`)
Main API providing:
- `rank_for_student()`: Rank courses for an individual
- `rank_for_group()`: Rank shared courses for a group
- `get_next_course()`: Get the single highest-priority course

#### 5. **Scorer Builder** (`builder.py`)
Builder pattern for easy configuration:
- `with_default_factors()`: Adds standard factors with recommended weights
- `add_factor()`: Add custom factors
- `build()`: Creates the configured scorer

## Usage

### Basic Usage

Use the builder and service for all prioritization needs:

```python
from src.services.course_prioritization import (
    ScorerBuilder, 
    PrioritizationService,
    BalancedAggregation
)
from sqlalchemy.orm import Session
from src.models.student_models import Student

# Build scorer with default factors
scorer = ScorerBuilder().with_default_factors().build()
service = PrioritizationService(scorer)

# Rank all courses for a single student
ranked_courses = service.rank_for_student(student, session)

# Get the next course to study
next_course = service.get_next_course(student, session)

# Rank for a group with specific strategy
ranked_for_group = service.rank_for_group(
    students=[student1, student2, student3],
    session=session,
    strategy=BalancedAggregation(),
    include_scores=False
)

# Rank with detailed breakdown
scored_courses = service.rank_for_student(
    student, 
    session, 
    include_scores=True
)

# Examine factor breakdown
for scored in scored_courses:
    print(f"Course: {scored.course.name}")
    print(f"Overall Score: {scored.score}")
    print(f"Factor Scores: {scored.factor_scores}")
```

### Advanced Usage (Custom Configuration)

For custom configurations with specific factors and weights:

```python
from src.services.course_prioritization import (
    ScorerBuilder, 
    PrioritizationService,
    CourseProgressFactor,
    TestUrgencyFactor,
)

# Build a custom scorer with specific weights
scorer = (ScorerBuilder()
    .add_factor(CourseProgressFactor(weight=0.5))
    .add_factor(TestUrgencyFactor(weight=0.5))
    .build())

# Create service and use
service = PrioritizationService(scorer)
ranked = service.rank_for_student(student, session)
```

### Creating Custom Scoring Factors

Extend the system by creating custom factors:

```python
from src.services.course_prioritization import ScoringFactor

class AttendanceFactor(ScoringFactor):
    """Prioritize courses with poor attendance."""
    
    @property
    def name(self) -> str:
        return "attendance"
    
    def calculate(self, course, course_student, student, session) -> float:
        attendance_rate = course_student.attendance_rate or 1.0
        return 1.0 - attendance_rate  # Lower attendance = higher priority

# Use it in a scorer
scorer = (ScorerBuilder()
    .with_default_factors()
    .add_factor(AttendanceFactor(weight=0.15))
    .build())
```

## Default Configuration

The default scorer (`with_default_factors()`) uses these weights:

| Factor | Weight | Description |
|--------|--------|-------------|
| Course Progress | 30% | Lower progress = higher priority |
| Test Urgency | 25% | Closer tests = higher priority |
| Test Performance | 20% | Lower grades = higher priority |
| Student Feedback | 15% | Negative feedback = higher priority |
| Course State | 10% | In-progress > Not started > Completed |

These weights are empirically balanced to provide good results across various scenarios.

## Group Prioritization Strategies

When prioritizing for groups, choose the strategy based on your teaching philosophy:

| Strategy | Use Case |
|----------|----------|
| **Balanced** (Default) | General purpose - balances individual needs with group averages |
| **Average** | Democratic approach - all students weighted equally |
| **Weighted Average** | Focus on struggling students - lower performers get higher weight |
| **Highest Need** | "No student left behind" - prioritize based on the student with highest need (highest priority score) |
| **Max-Based** | Maximum engagement - returns the raw maximum score without adjustments |

## API Reference

### Service API

```python
class PrioritizationService:
    def rank_for_student(
        self,
        student: Student,
        session: Session,
        courses: Optional[List[Course]] = None,
        include_scores: bool = False
    ) -> Union[List[Course], List[ScoredCourse]]:
        """Rank courses for a single student."""
    
    def rank_for_group(
        self,
        students: List[Student],
        session: Session,
        strategy: AggregationStrategy,
        include_scores: bool = False
    ) -> Union[List[Course], List[ScoredCourse]]:
        """Rank shared courses for a group."""
    
    def get_next_course(
        self,
        students: Union[Student, List[Student]],
        session: Session,
        strategy: Optional[AggregationStrategy] = None
    ) -> Optional[Course]:
        """Get the highest-priority course."""
```

## Design Patterns Used

1. **Strategy Pattern**: Scoring factors and aggregation strategies are interchangeable
2. **Builder Pattern**: ScorerBuilder provides fluent API for configuration
3. **Composition over Inheritance**: CourseScorer composes factors rather than inheriting
4. **Single Responsibility Principle**: Each module has one clear purpose
5. **Open/Closed Principle**: Easy to extend with new factors without modifying existing code

## Performance Considerations

- **Batch Queries**: Group prioritization fetches all course-student associations in one query
- **Efficient Lookups**: Uses dictionaries for O(1) lookups in group scoring
- **Lazy Evaluation**: Only calculates factor scores when needed
- **Normalized Weights**: Weights normalized once at initialization, not per calculation

## Testing

The modular architecture makes testing straightforward:

```python
# Test individual factors
factor = CourseProgressFactor(weight=1.0)
score = factor.calculate(course, course_student, student, session)
assert 0 <= score <= 1

# Test scorer with mock factors
scorer = CourseScorer([mock_factor1, mock_factor2])
score = scorer.score(course, course_student, student, session)

# Test strategies with known inputs
strategy = AverageAggregation()
result = strategy.aggregate([0.5, 0.7, 0.9], students, session)
assert result == 0.7
```

## Extension Points

The system is designed for easy extension:

1. **Add New Factors**: Create a class inheriting from `ScoringFactor`
2. **Add New Strategies**: Create a class inheriting from `AggregationStrategy`
3. **Custom Scoring Logic**: Override `CourseScorer.score()` for complex scenarios
4. **Data Sources**: Factors can query any data accessible through the session

## Dependencies

- SQLAlchemy ORM for database queries
- Python 3.7+ (uses dataclasses and type hints)
- Allamda system models: `Course`, `Student`, `CourseStudent`
- Enums: `CourseState`, `GroupAggregationStrategy`

## Future Enhancements

Potential extensions to consider:

- **Time-decay factors**: Reduce priority of recently studied courses
- **Learning style factors**: Consider student learning preferences
- **Prerequisite factors**: Prioritize prerequisites for upcoming courses
- **Collaborative filtering**: Use patterns from similar students
- **A/B testing framework**: Compare different factor configurations
- **Caching layer**: Cache scores for performance in large classes

---

**Author**: Allamda Development Team  
**Last Updated**: October 2025  
**Version**: 2.0 (Modular Architecture)

