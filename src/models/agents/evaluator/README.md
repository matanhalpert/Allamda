# Evaluator Agent

AI-powered assessment agent that analyzes study session transcripts and supporting data to generate objective, detailed evaluations of student performance across proficiency and investment dimensions.

## Overview

The Evaluator agent provides data-driven assessments of student study sessions. After a session completes, it analyzes the complete chat transcript, uses specialized tools to gather quantitative metrics, and generates scores (1-10) with detailed descriptions across two key dimensions: **Proficiency** (academic understanding and mastery) and **Investment** (engagement, focus, and dedication). These evaluations help track student progress and identify areas for improvement.

## Structure

```
evaluator/
├── __init__.py    # Package exports
├── agent.py       # Evaluator class implementation
├── tools.py       # Tool method implementations
├── schemas.py     # Pydantic parameter schemas
└── README.md      # This file
```

## Evaluator Agent Class

### Inheritance
```python
class Evaluator(Agent, AIAgentMixin):
    # Database persistence from Agent
    # AI capabilities from AIAgentMixin
```

### Database Fields

```python
ai_model_id: Integer (PK, FK)
name: String(100) (PK)
```

### Relationships

- `sessional_proficiency_evaluations` - One-to-many
- `quarter_proficiency_evaluations` - One-to-many
- `sessional_investment_evaluations` - One-to-many
- `quarter_investment_evaluations` - One-to-many

## Evaluation Dimensions

### Proficiency Evaluation

**What it Measures:**
- Academic understanding and knowledge retention
- Quality and depth of student answers
- Ability to explain concepts and apply knowledge
- Critical thinking and problem-solving skills
- Correctness of responses relative to learning objectives
- Progress in understanding throughout session

**Scoring Scale (1-10):**
- **9-10**: Exceptional mastery, advanced understanding
- **7-8**: Strong grasp, minor gaps
- **5-6**: Adequate understanding, some confusion
- **3-4**: Significant knowledge gaps
- **1-2**: Minimal understanding, requires foundational review

**Key Factors:**
- Transcript analysis: Answer quality, questions asked, explanations given
- Session context: Course, learning units, objectives
- Test performance: Historical grades in subject
- Evaluation history: Proficiency trends over time

### Investment Evaluation

**What it Measures:**
- Engagement level and active participation
- Focus and dedication throughout session
- Consistency of involvement
- Question frequency and depth
- Effort demonstrated in responses
- Session continuity (pauses vs active time)

**Scoring Scale (1-10):**
- **9-10**: Highly engaged, minimal distractions, excellent focus
- **7-8**: Consistently engaged, good participation
- **5-6**: Moderate engagement, some distraction
- **3-4**: Frequently distracted, minimal effort
- **1-2**: Disengaged, mostly paused or absent

**Key Factors:**
- Transcript analysis: Message frequency, question quality, response depth
- Pause statistics: % of session paused vs active (CRITICAL METRIC)
- Message statistics: Count, length, question frequency
- Evaluation history: Investment trends over time

## Available Tools

### 1. get_session_context (MANDATORY for Proficiency)

**Purpose**: Get course, subject, and learning unit information for the session

**Why Critical:**
- Cannot assess mastery without knowing what was studied
- Provides learning objectives to evaluate against
- Essential first step for proficiency evaluation

**Parameters:**
```python
{
    "session_id": int,
    "session_type": str  # "home" or "school"
}
```

**Returns:**
```python
{
    "session_id": int,
    "course": {
        "name": str,
        "subject": str,
        "grade_level": str
    },
    "learning_units": [
        {
            "name": str,
            "description": str,
            "type": str,
            "objectives": [str]
        }
    ]
}
```

### 2. get_session_pause_statistics (MANDATORY for Investment)

**Purpose**: Get pause metrics - THE MOST IMPORTANT investment indicator

**Why Critical:**
- Pause percentage directly correlates with engagement
- Low pause % (0-10%) = High investment
- Moderate pause % (10-25%) = Average investment
- High pause % (25%+) = Low investment
- Must be included in investment evaluation description

**Parameters:**
```python
{
    "session_id": int,
    "session_type": str  # "home" or "school"
}
```

**Returns:**
```python
{
    "session_id": int,
    "total_duration_minutes": float,
    "active_duration_minutes": float,
    "paused_duration_minutes": float,
    "pause_percentage": float,  # KEY METRIC
    "num_pauses": int,
    "average_pause_duration_minutes": float,
    "longest_pause_minutes": float
}
```

### 3. get_session_message_statistics

**Purpose**: Quantify conversational engagement

**Parameters:**
```python
{
    "session_id": int,
    "session_type": str  # "home" or "school"
}
```

**Returns:**
```python
{
    "session_id": int,
    "total_messages": int,
    "student_messages": int,
    "teacher_messages": int,
    "average_student_message_length": float,
    "questions_asked": int,  # Messages ending with '?'
    "response_rate": float  # Student/teacher message ratio
}
```

**Use Cases:**
- Supplement pause statistics
- Assess active participation level
- Identify curious, engaged learners (high question count)
- Detect brief, low-effort responses

### 4. get_student_test_performance

**Purpose**: Compare session performance with test scores

**Parameters:**
```python
{
    "student_id": int,
    "course_id": int,
    "limit": int  # Optional, default 5
}
```

**Returns:**
```python
{
    "student_id": int,
    "course_id": int,
    "tests": [
        {
            "test_name": str,
            "grade": float,
            "percentage": float,
            "date": str
        }
    ],
    "average_grade": float
}
```

**Use Cases:**
- Validate proficiency evaluation against actual test results
- Identify if session understanding translates to test performance
- Contextualize current performance

### 5. get_student_evaluation_history

**Purpose**: Review past evaluation trends

**Parameters:**
```python
{
    "student_id": int,
    "evaluation_type": str,  # "proficiency" or "investment"
    "limit": int  # Optional, default 10
}
```

**Returns:**
```python
{
    "student_id": int,
    "evaluation_type": str,
    "evaluations": [
        {
            "date": str,
            "score": int,
            "description": str,
            "session_type": str
        }
    ],
    "average_score": float,
    "trend": str  # "improving", "declining", "stable"
}
```

**Use Cases:**
- Ensure consistency with historical patterns
- Identify improvement or decline trends
- Contextualize current evaluation
- Avoid outlier scores without justification

## Evaluation Workflow

### Proficiency Evaluation Process

```
1. Receive transcript and session context (session_id, session_type)
   ↓
2. MANDATORY: Call get_session_context() FIRST
   - Understand what course/learning units were studied
   - Cannot assess without knowing learning objectives
   ↓
3. Analyze transcript for academic content
   - Quality of student answers
   - Depth of understanding demonstrated
   - Correct vs incorrect responses
   - Critical thinking shown
   ↓
4. OPTIONAL: Call get_student_test_performance()
   - Compare with historical test scores
   - Validate assessment against actual performance
   ↓
5. OPTIONAL: Call get_student_evaluation_history()
   - Check consistency with past proficiency trends
   - Identify improvement or decline patterns
   ↓
6. Generate score (1-10) and detailed description
   - Reference specific transcript examples
   - Mention course/learning units from context
   - Justify score with concrete evidence
```

### Investment Evaluation Process

```
1. Receive transcript and session context (session_id, session_type)
   ↓
2. MANDATORY: Call get_session_pause_statistics()
   - THIS IS THE PRIMARY INVESTMENT METRIC
   - Pause % indicates focus vs distraction
   - MUST include in evaluation description
   ↓
3. Call get_session_message_statistics()
   - Quantify participation level
   - Count questions asked (curiosity indicator)
   - Assess response consistency
   ↓
4. Analyze transcript for engagement signals
   - Message frequency and depth
   - Question quality
   - Effort in responses
   - Enthusiasm and curiosity
   ↓
5. OPTIONAL: Call get_student_evaluation_history()
   - Check consistency with past investment trends
   - Identify engagement patterns
   ↓
6. Generate score (1-10) and detailed description
   - MUST reference pause percentage
   - Include message statistics
   - Cite specific transcript examples
   - Justify score with quantitative data
```

## Scoring Guidelines

### Proficiency Score Calibration

**9-10 - Exceptional:**
- Correct answers with detailed explanations
- Advanced understanding beyond learning objectives
- Able to apply concepts to new problems
- Minimal errors, quickly self-corrects

**7-8 - Strong:**
- Mostly correct answers
- Good grasp of key concepts
- Some advanced understanding
- Minor gaps or occasional errors

**5-6 - Adequate:**
- Basic understanding demonstrated
- Some correct answers mixed with errors
- Grasps main ideas but struggles with details
- Needs reinforcement

**3-4 - Struggling:**
- Significant knowledge gaps
- More errors than correct answers
- Confusion on key concepts
- Requires substantial review

**1-2 - Minimal:**
- Little to no understanding
- Cannot explain basic concepts
- Mostly incorrect or confused responses
- Needs foundational restart

### Investment Score Calibration

**9-10 - Highly Engaged:**
- Pause % < 10%
- Frequent, thoughtful questions
- Consistent participation
- Long, detailed responses
- Minimal distraction

**7-8 - Engaged:**
- Pause % 10-20%
- Regular participation
- Good question frequency
- Solid response quality
- Some brief pauses

**5-6 - Moderate:**
- Pause % 20-30%
- Inconsistent participation
- Occasional questions
- Variable response quality
- Notable distractions

**3-4 - Low Engagement:**
- Pause % 30-50%
- Minimal participation
- Few questions
- Brief, low-effort responses
- Frequent distractions

**1-2 - Disengaged:**
- Pause % > 50%
- Rare participation
- No questions asked
- Minimal responses
- Mostly absent

## Usage Example

```python
from src.services.study_session import evaluate_session

# Automatically called after session completion
proficiency_eval, investment_eval = evaluate_session(
    session_id=123,
    student_id=456,
    session_type='home'
)

# Proficiency Evaluation
print(f"Proficiency Score: {proficiency_eval.score}/10")
print(f"Description: {proficiency_eval.description}")

# Investment Evaluation  
print(f"Investment Score: {investment_eval.score}/10")
print(f"Description: {investment_eval.description}")
```

## Evaluation Description Format

### Good Proficiency Description Example

```
The student demonstrated strong understanding of algebraic equations 
(Learning Unit: Linear Equations). They correctly solved 4 out of 5 
practice problems and explained the substitution method clearly. They 
showed ability to apply concepts to word problems. Minor error in the 
last problem with negative numbers, but self-corrected with guidance. 
Consistent with test average of 82% in Algebra. Score: 8/10.
```

### Good Investment Description Example

```
The student showed excellent engagement throughout the session. Pause 
statistics indicate only 8% of the session was paused (5 minutes out 
of 60), demonstrating strong focus. They sent 23 messages averaging 45 
words each, and asked 12 questions showing genuine curiosity. Responses 
were detailed and thoughtful. Participation was consistent from start to 
finish. Score: 9/10.
```

## Integration Points

### Study Session Service
Called by `src/services/study_session/evaluation.py`:
- `evaluate_session()` triggers evaluations after completion
- Transcript and context provided
- Results saved to database

### Evaluation Models
Creates database records:
- SessionalProficiencyEvaluation
- SessionalInvestmentEvaluation
- Links to student and session

### Analytics Service
Evaluations used for:
- Progress tracking over time
- Trend analysis
- Performance reporting
- Parent/teacher dashboards

## Best Practices

### Tool Usage
1. **Always** call get_session_context() for proficiency
2. **Always** call get_session_pause_statistics() for investment
3. Use supporting tools to validate and enrich evaluation
4. Don't rely solely on transcript - use quantitative data

### Evaluation Writing
1. Be specific with examples from transcript
2. Reference quantitative metrics (pause %, scores, etc.)
3. Justify the score with concrete evidence
4. Be constructive and objective
5. Note both strengths and areas for improvement

### Consistency
1. Check evaluation history for typical patterns
2. Avoid extreme score shifts without clear justification
3. Calibrate scores relative to learning objectives
4. Maintain consistency across similar performances

## Dependencies

- **OpenAI API**: GPT-4 or GPT-3.5-turbo (lower temperature for consistency)
- **Base Agent Infrastructure**: AIAgentMixin, tool system
- **Database Models**: Student, Session, Message, Test, Evaluation
- **Pydantic**: Parameter validation

## Notes

- Evaluator uses lower temperature (0.3) for consistency
- Pause statistics are THE most important investment metric
- Session context is essential for proficiency evaluation
- Evaluations are automatically generated, not manual
- Both dimensions evaluated independently
- Scores should align with test performance over time
- Detailed descriptions more valuable than scores alone

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

