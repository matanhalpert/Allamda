![λllamda](src/app/static/images/intro_logo.png)

# λllamda

**An AI-Driven Educational Platform Exploring Adaptive, Personalized Learning**

*A student project demonstrating a vision for the future of education*

---

## About This Project

λllamda is my exploration of how AI could transform education through personalized, adaptive learning. As a student passionate about both education and technology, I wanted to build something that demonstrates a different approach to how we might think about teaching and learning in the AI era.

This project started from a question: *What if we could give every student a personal AI tutor that adapts to their learning style, and free up human teachers to focus on mentorship and facilitation?*

Traditional education often follows a one-size-fits-all model. In λllamda, I've explored an inverted model where **AI Teacher Agents** provide personalized instruction tailored to each student's needs, while human **Class Managers** take on a supervisory role—managing class dynamics and providing the human touch where it matters most.

The goal was to build a working proof of concept that demonstrates scalable, data-driven, adaptive learning with real AI integration.

---

## Core Concepts

This project explores several key ideas for improving education through technology:

### 🎯 **Adaptive Learning**
The system adjusts lesson content and explanations based on each student's current level, learning pace, and comprehension style—aiming to provide personalized instruction at scale.

### 🤖 **AI Teacher Agents**
GPT-powered virtual instructors provide subject-specific teaching that's available 24/7, adapting responses based on conversation context and student learning profiles.

### 📊 **Data-Driven Insights**
Comprehensive analytics track student progress and engagement, making it possible to identify patterns and areas where students might need additional support.

### 🔄 **Intelligent Course Prioritization**
An algorithm that determines which subjects need attention by weighing factors like upcoming tests, current proficiency levels, performance trends, and student-provided feedback.

### 👥 **Reimagined Teacher Role**
The model explores how human teachers could focus on class management and mentorship while AI handles personalized instruction—potentially improving the effective student-teacher ratio.

### 🧠 **Mental State Tracking**
The system records students' emotional and cognitive states before and after sessions, providing data on when learning is most effective.

---

## What I Built

This repository contains a working **proof of concept** that demonstrates the core functionality of this vision. While a full implementation would encompass entire schools and districts, I focused on building the **essential student-AI teacher interaction** within intelligent study sessions, along with the supporting infrastructure.

### Implementation Highlights

✅ **AI-Powered Teaching Sessions**  
Built chat-based study sessions where students interact with GPT-powered Teacher Agents that adapt responses based on learning style, conversation history, and current learning objectives.

✅ **Voice Interaction**  
Integrated speech-to-text and text-to-speech capabilities for natural, conversational learning experiences.

✅ **Intelligent Post-Session Evaluation**  
Implemented AI Evaluator Agents that analyze complete session transcripts to assess student proficiency (knowledge retention) and investment (engagement level), generating 1-10 scores with detailed descriptions.

✅ **Dynamic Course Prioritization Algorithm**  
Developed an intelligent ranking system that determines which courses students should study next, weighing factors like upcoming test dates, current proficiency, performance trends, and student feedback.

✅ **Smart Learning Unit Assignment**  
Created automatic content selection logic that chooses appropriate learning units based on student progress, session duration constraints, and prerequisite dependencies.

✅ **Multi-Role User System**  
Designed and implemented a complete role hierarchy (Students, Parents, Class Managers, School Managers, Regional Supervisors) with role-specific dashboards, permissions, and analytics views.

✅ **Comprehensive Database Architecture**  
Modeled a normalized relational schema supporting educational entities, user relationships, session state management, conversation history, and multi-dimensional evaluation tracking.

✅ **Service-Oriented Architecture**  
Structured the codebase with clear separation of concerns: presentation layer (Flask routes/templates), service layer (business logic), model layer (AI agents + ORM), and data access layer.

---

## Core Features

### For Students
- 🎓 **Interactive Study Sessions**: Engage with AI teachers through chat or voice
- 📚 **Course Dashboard**: View enrolled courses, progress, and upcoming tests
- 🎯 **Smart Prioritization**: System recommends which course to study next
- 📈 **Progress Tracking**: Visualize learning unit completion and proficiency scores
- 💬 **Conversational Learning**: Ask questions naturally, get personalized explanations

### For Parents
- 👨‍👩‍👧 **Children's Overview**: Monitor all children's academic progress in one place
- 📊 **Analytics Dashboard**: Review study session history and evaluation scores
- 🎯 **Performance Insights**: Track proficiency and engagement trends over time
- 📅 **Test Preparation**: See upcoming tests and preparation progress

### For Class Managers (Teachers)
- 🏫 **Class Oversight**: Supervise school-hours study sessions
- 📊 **Class Analytics**: View class-wide performance and engagement metrics
- ✍️ **Manual Evaluations**: Provide investment and social behavior assessments
- 👥 **Student Monitoring**: Track individual and collective progress

### For School Managers
- 🏛️ **School-Wide Analytics**: Overview of all classes and students
- 📈 **Performance Reporting**: Generate insights across grades and subjects
- 📊 **Resource Allocation**: Data-driven decisions on curriculum and support needs

---

## User Roles & Use Cases

The system supports multiple user roles, each with specific capabilities and workflows:

<a href="src/app/static/images/use_case_diagram.png" target="_blank">
  <img src="src/app/static/images/use_case_diagram.png" alt="λllamda Use Case Diagram" width="70%">
</a>

<i>Click image to view full size</i>

---

## System Architecture

λllamda follows a **layered architecture** that separates concerns and promotes maintainability:

```
┌─────────────────────────────────────────┐
│         Client Layer                     │
│    (Web Browser + WebSocket)            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Presentation Layer (Flask)          │
│  Routes | Templates | Static Assets     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Service Layer                    │
│  Study Sessions | Prioritization |      │
│  Unit Assignment | Analytics             │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│          Model Layer                     │
│   AI Agents | Database Models           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Data Access & Infrastructure          │
│  MySQL | Session Store | File Storage   │
└─────────────────────────────────────────┘
```

### Study Session Lifecycle

Study sessions follow a clear state-based lifecycle:

1. **PENDING** → Session created with assigned learning units, teacher agent, and mental state recorded
2. **ACTIVE** → Student sends messages, AI teacher responds, conversation persisted in real-time
3. **PAUSED** → Session temporarily suspended (can be resumed)
4. **COMPLETED** → Feedback collected, AI evaluation generated, progress updated

### Database Schema Overview

The system uses a comprehensive relational database design supporting all educational entities, user hierarchies, study sessions, and evaluations:

<a href="src/app/static/images/allamda_erd.png" target="_blank">
  <img src="src/app/static/images/allamda_erd.png" alt="λllamda ERD" width="70%">
</a>

<i>Click image to view full size</i>

*The ERD shows the complete database schema including Users, Students, Courses, Learning Units, Study Sessions, Messages, and Evaluations with their relationships.*

For comprehensive architecture details including sequence diagrams, service interactions, and AI agent integration patterns, see **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

## Technology Stack

### Backend
- **Flask 2.x** - Web framework
- **SQLAlchemy 2.x** - ORM for database modeling
- **Python 3.9+** - Core language
- **Flask-Session** - Server-side session management
- **Flask-SocketIO** - WebSocket support for real-time features

### Database
- **MySQL 8.x** - Relational database with complex schema supporting educational entities, sessions, evaluations, and user hierarchies

### AI & Machine Learning
- **OpenAI API** (GPT-4/3.5-turbo) - Powers Teacher and Evaluator agents
- **Custom Agent Framework** - Tool-equipped agents with database access for contextual responses

### Frontend
- **Jinja2** - Server-side templating
- **Vanilla JavaScript** - Client-side interactivity and WebSocket handling
- **CSS3** - Modern, responsive styling
- **Plotly** - Interactive analytics visualizations

---

## Project Structure

```
λllamda/
├── src/
│   ├── app/                          # Flask application
│   │   ├── routes/                   # HTTP route handlers
│   │   │   ├── auth.py              # Authentication
│   │   │   ├── student.py           # Student dashboard & features
│   │   │   ├── parent.py            # Parent monitoring
│   │   │   ├── class_manager.py     # Class management
│   │   │   ├── school_manager.py    # School oversight
│   │   │   └── study/               # Study session routes
│   │   ├── templates/               # Jinja2 HTML templates
│   │   └── static/                  # CSS, JavaScript, images
│   │
│   ├── models/                       # Domain models
│   │   ├── agents/                  # AI agent implementations
│   │   │   ├── teacher/             # Teacher agent with tools
│   │   │   └── evaluator/           # Evaluator agent
│   │   ├── user_models.py           # User hierarchy
│   │   ├── school_models.py         # School, Class entities
│   │   ├── subject_models.py        # Subjects, Courses, Learning Units
│   │   ├── session_models.py        # Study sessions
│   │   └── evaluation_models.py     # AI-generated evaluations
│   │
│   ├── services/                     # Business logic layer
│   │   ├── study_session/           # Session lifecycle management
│   │   ├── course_prioritization/   # Intelligent course ranking
│   │   ├── learning_unit_assignment/# Adaptive content selection
│   │   ├── analytics/               # Progress tracking & reporting
│   │   └── voice_mode/              # Speech interaction
│   │
│   ├── database/                     # Database management
│   │   ├── setup.py                 # Schema creation
│   │   ├── session_context.py       # Thread-safe session handling
│   │   └── decorators.py            # Transaction management
│   │
│   └── utils/                        # Shared utilities
│       ├── logger.py                # Logging configuration
│       └── file_handler.py          # File operations
│
├── requirements.txt                  # Python dependencies
├── run.py                           # Application entry point
├── ARCHITECTURE.md                  # Detailed technical documentation
└── README.md                        # This file
```

---

## Getting Started

### Prerequisites
- Python 3.9 or higher
- MySQL 8.x
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd allamda
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_NAME=allamda
   SECRET_KEY=your_flask_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Initialize the database**
   ```python
   python run.py
   # In Python shell:
   from src.database import DatabaseManager
   DatabaseManager.create_tables()
   DatabaseManager.populate_sample_data(clear_existing=True)
   ```

6. **Run the application**
   ```bash
   python run.py
   ```
   
   The application will be available at `http://localhost:5000`

### Default Login Credentials (Sample Data)

After populating sample data, you can log in as:
- **Student**: Check the created sample users in the database
- **Parent**: Sample parent accounts with linked children
- **Class Manager**: Sample teachers managing classes
- **School Manager**: Sample administrators

---

## Key Services Explained

### 📚 Study Session Service
Manages the complete lifecycle of study sessions from creation through AI evaluation. Handles state transitions, message persistence, teacher-student interactions, and automatic assessment generation.

**Location**: `src/services/study_session/`  
**Documentation**: [Study Session README](src/services/study_session/README.md)

### 🎯 Course Prioritization Service
Intelligent ranking algorithm that determines which courses students should focus on next. Considers multiple factors:
- Upcoming test dates and preparation time
- Current proficiency levels
- Recent performance trends
- Student-provided feedback and preferences
- Course difficulty and progress

**Location**: `src/services/course_prioritization/`  
**Documentation**: [Course Prioritization README](src/services/course_prioritization/README.md)

### 📖 Learning Unit Assignment Service
Automatically selects appropriate learning units for study sessions based on:
- Student's current progress in the course
- Session duration and time constraints
- Learning unit dependencies and prerequisites
- Estimated completion time for each unit

**Location**: `src/services/learning_unit_assignment/`  
**Documentation**: [Learning Unit Assignment README](src/services/learning_unit_assignment/README.md)

### 🤖 AI Teacher Agents
GPT-4 powered agents equipped with specialized tools:
- `get_student_progress` - Retrieve real-time progress data
- `get_qa_for_learning_unit` - Access relevant Q&A content
- `get_upcoming_tests` - Check test schedules
- `search_qa_by_question` - Find specific content

Agents adapt responses based on student learning style, session type, and conversation history.

**Location**: `src/models/agents/teacher/`

### 📊 AI Evaluator Agents
Post-session assessment agents that analyze complete transcripts to generate:
- **Proficiency Evaluation** (1-10): Knowledge understanding and retention
- **Investment Evaluation** (1-10): Engagement, effort, and participation quality

**Location**: `src/models/agents/evaluator/`

---

## Potential Extensions

While this POC demonstrates the core concept, there are many directions this could grow:

### 🌍 **Scaling to Multiple Schools**
The architecture could support multi-school deployments with district-wide analytics and centralized curriculum coordination.

### 📱 **Mobile Applications**
Native iOS/Android apps would enable learning on the go with offline mode and push notifications for study reminders.

### 🎮 **Gamification Elements**
Adding achievement systems, learning streaks, and progress-based rewards could increase student motivation and engagement.

### 🧠 **Enhanced AI Models**
- Fine-tuning models for specific subjects and grade levels
- Multimodal learning with image analysis and diagram generation
- Predictive analytics to identify students who might need extra support
- Better emotional intelligence to detect frustration or confusion in conversations

### 🤝 **Collaborative Learning**
Supporting peer study sessions with AI moderation, group projects, and student-to-student knowledge sharing.

### 🌐 **Internationalization**
Multi-language support and cultural adaptation to make this accessible globally.

### 📊 **Advanced Analytics Dashboard**
Real-time visualizations, predictive modeling for outcomes, and data-driven insights for educators.

### 🔗 **LMS Integrations**
Connecting with existing platforms like Canvas, Moodle, or Google Classroom to fit into current educational workflows.

---

## Documentation

### Architecture & Technical Details
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Comprehensive technical documentation including database schema, sequence diagrams, and integration patterns

### Service-Specific Documentation
- **[Study Session Service](src/services/study_session/README.md)** - Session lifecycle and state management
- **[Course Prioritization](src/services/course_prioritization/README.md)** - Prioritization algorithm details
- **[Learning Unit Assignment](src/services/learning_unit_assignment/README.md)** - Content selection logic

### Model Documentation
- **[AI Agents Overview](src/models/agents/README.md)** - Agent architecture and tool system

---

## Technical Skills Demonstrated

This project showcases:
- **Backend Development**: Flask web framework, RESTful API design, WebSocket implementation
- **Database Design**: Complex relational modeling with SQLAlchemy ORM, normalized schema design
- **AI Integration**: OpenAI API integration, custom agent framework with tool usage
- **Software Architecture**: Layered architecture, service-oriented design, separation of concerns
- **Algorithm Design**: Course prioritization logic, learning unit assignment algorithms
- **Full-Stack Development**: Server-side rendering, JavaScript, CSS, responsive design
- **System Design**: State management, transaction handling, session lifecycle management

---

## What I Learned

Building λllamda taught me a lot about:
- Designing systems with clear separation of concerns and maintainable architecture
- Working with AI APIs and building agents that use tools to access real-time data
- Complex database modeling for educational domains with multiple entity relationships
- State management patterns and handling complex business logic flows
- Building multi-role systems with different permission levels and user experiences
- Integrating voice capabilities and real-time features with WebSockets
- The challenges of creating adaptive, personalized experiences at scale

---

## License

See [LICENSE](LICENSE) file for details.

---

## Contact

If you have questions, suggestions, or want to discuss the project, feel free to reach out through the repository's issues or discussions.

---

*A student project exploring the intersection of AI and education*
