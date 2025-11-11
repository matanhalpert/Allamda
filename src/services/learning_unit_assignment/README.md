# Learning Unit Assignment Service

Intelligent assignment of learning units to study sessions based on student progress, duration constraints, and unit dependencies. Works for both individual and group sessions.

## Overview

The Learning Unit Assignment Service automatically selects appropriate learning units for study sessions by considering:
- **Student Progress**: Individual completion levels for each learning unit
- **Group Dynamics**: In group sessions, aligns with the least advanced student
- **Duration Constraints**: Fits units within available session time (default: 60 minutes)
- **Unit Dependencies**: Respects sequential order and prerequisites

## Architecture

Simple, single-module service following the established pattern:

```
learning_unit_assignment/
├── __init__.py    # Module exports
├── service.py     # Main service implementation
└── README.md      # This file
```

### Core Components

**LearningUnitAssignmentService**  
Main service class providing:
- `assign()`: Universal method handling both individual and group sessions

**AssignmentResult**  
Dataclass containing:
- `assigned_units`: List of selected learning units
- `total_duration`: Total time required (minutes)
- `students_affected`: Students in the session
- `reason`: Human-readable explanation

**Model Layer Enhancement**  
Added `Course.get_ordered_learning_units()` to retrieve units in proper sequence.

## Usage

### Basic Usage

```python
from src.services import LearningUnitAssignmentService, assign_learning_units

# Quick convenience function
result = assign_learning_units(student, course)

print(f"Assigned: {[unit.name for unit in result.assigned_units]}")
print(f"Duration: {result.total_duration} minutes")
```

### Group Sessions

```python
students = [student1, student2, student3]
result = assign_learning_units(students, course, duration_minutes=90)

print(f"Assigned for {len(result.students_affected)} students")
print(f"Starting from: {result.assigned_units[0].name}")
```

### With Custom Duration

```python
service = LearningUnitAssignmentService(default_duration_minutes=45)
result = service.assign(student, course, duration_minutes=30)
```

### Integration with Prioritization Service

```python
from src.services import PrioritizationService, ScorerBuilder, LearningUnitAssignmentService

# Step 1: Determine which course to study
scorer = ScorerBuilder().with_default_factors().build()
prioritization = PrioritizationService(scorer)
course = prioritization.get_next_course(students)

# Step 2: Assign appropriate learning units
assignment = LearningUnitAssignmentService()
result = assignment.assign(students, course)

# Step 3: Create study session
study_session.learning_units = result.assigned_units
```

## Algorithm

### Individual Student
1. Get ordered learning units for the course
2. Find first incomplete unit for the student
3. Fit consecutive units within duration constraint
4. Return result with metadata

### Group Session (No Student Left Behind)
1. Get ordered learning units for the course
2. Find first incomplete unit across ALL students (earliest position)
3. Fit consecutive units starting from that position
4. Return result with metadata for all students

### Duration Constraint
```python
# Greedy algorithm: fit as many units as possible
remaining_time = duration_minutes
for unit in ordered_units:
    if unit.estimated_duration_minutes <= remaining_time:
        assigned.append(unit)
        remaining_time -= unit.estimated_duration_minutes

# Safety: always assign at least one unit
if not assigned and ordered_units:
    assigned.append(ordered_units[0])
```

## Design Decision

**Service Layer Implementation (Option B)**

This functionality is a service because:
- Involves multiple models: Course, LearningUnit, Student, LearningUnitStudent
- Contains complex business logic combining data from various sources
- Mirrors the learning_prioritization service pattern
- Separates data retrieval (models) from business logic (service)

## Performance

- **Batch Queries**: Fetches all progress records in one query
- **O(1) Lookups**: Uses dictionaries for fast student/unit access
- **Single Pass**: Traverses units only once

Example efficiency:
```python
# ❌ Naive: N×M queries
for student in students:
    for unit in units:
        progress = query(student, unit)

# ✅ Optimized: 1 batch query
all_progress = query_batch(students, units)
lookup = {(s_id, u_name): progress}
```

## API Reference

### LearningUnitAssignmentService

```python
class LearningUnitAssignmentService:
    def __init__(self, default_duration_minutes: int = 60):
        """Initialize with default session duration."""
    
    def assign(
        self, 
        students: Union[Student, List[Student]], 
        course: Course,
        duration_minutes: Optional[int] = None
    ) -> AssignmentResult:
        """
        Assign learning units for a study session.
        
        Handles both individual and group sessions. For group sessions,
        ensures no student is left behind by selecting units aligned with
        the least advanced student in the group.
        
        Uses session context manager pattern (get_current_session).
        """
```

### Convenience Function

```python
@with_session
def assign_learning_units(
    students: Union[Student, List[Student]],
    course: Course,
    duration_minutes: Optional[int] = None
) -> AssignmentResult:
    """
    Quick assignment without creating service instance.
    
    Decorated with @with_session to automatically manage database session.
    """
```

## Edge Cases

| Case | Behavior |
|------|----------|
| All units completed | Returns empty list with explanation |
| No units exist | Returns empty list with explanation |
| Unit exceeds duration | Assigns it anyway (better than nothing) |
| Empty student list | Returns empty list with explanation |
| Circular references | Handled with visited set tracking |

## Comparison with Learning Prioritization

| Aspect | Prioritization | Unit Assignment |
|--------|---------------|-----------------|
| **Purpose** | Which course to study | Which units within course |
| **Input** | Student(s) | Student(s) + Course |
| **Output** | Ranked courses | Assigned units |
| **Factors** | Progress, tests, feedback | Progress, duration, sequence |
| **Level** | Course-level | Unit-level |

Both services work together for complete intelligent study planning.

---

**Author**: Allamda Development Team  
**Created**: October 2025  
**Version**: 1.0

