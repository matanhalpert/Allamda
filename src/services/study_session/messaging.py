"""
Study Session Messaging

Functions for handling chat messages during study sessions.
"""

from datetime import datetime
from typing import List, Dict, Any

from src.database.session_context import get_current_session
from src.models.session_models import HomeHoursStudySession, SchoolHoursStudySession
from src.models.student_models import Student
from src.models.message_models import Message, Attachment
from src.models.agents import Teacher
from src.enums import SessionStatus, MessageType, MessageModality, FileType
from .exceptions import SessionNotFoundError, InvalidSessionStateError, StudySessionError
from src.utils.logger import Logger
from src.utils.file_handler import FileHandler


def get_session_messages(
        session_id: int
) -> List[Dict[str, Any]]:
    """Retrieve conversation history for a study session."""
    messages = Message.get_messages(session_id, order_by_timestamp=True)

    return [
        {
            'id': msg.id,
            'content': msg.content,
            'type': msg.type,
            'timestamp': msg.timestamp.isoformat(),
            'is_student': msg.type == MessageType.PROMPT,
            'attachments': [
                {'url': att.url, 'file_type': att.file_type.value}
                for att in msg.attachments
            ]
        }
        for msg in messages
    ]


def send_message(
        session_id: int,
        student_id: int,
        message_content: str,
        uploaded_files: list = None,
        modality: MessageModality = None
) -> Dict[str, Any]:
    """
    Send a student message and get Teacher agent response. Works for both home and school sessions.
    
    Args:
        session_id: ID of the study session
        student_id: ID of the student sending the message
        message_content: Text content of the message
        uploaded_files: Optional list of file attachments
        modality: Optional message modality (defaults to TEXT_ONLY, or MULTIMODAL if images present)
    """
    session = get_current_session()

    study_session = SchoolHoursStudySession.get_by(id=session_id, first=True)

    is_school_session = True
    if not study_session:
        study_session = HomeHoursStudySession.get_by(id=session_id, first=True)
        is_school_session = False
    
    if not study_session:
        raise SessionNotFoundError(f"Session {session_id} not found")

    if study_session.status != SessionStatus.ACTIVE:
        raise InvalidSessionStateError(
            f"Cannot send messages in {study_session.status} state"
        )

    teacher: Teacher = study_session.teacher
    if not teacher:
        raise StudySessionError("No teacher assigned to this session")

    history_messages = study_session.get_messages(order_by_timestamp=True)
    student = Student.get_by(id=student_id, first=True)

    try:
        last_message = None
        if history_messages:
            last_message = history_messages[-1]

        message_modality = modality if modality is not None else MessageModality.TEXT_ONLY
        
        message_kwargs = {
            'content': message_content,
            'timestamp': datetime.now(),
            'type': MessageType.PROMPT,
            'modality': message_modality,
            'student_id': student_id,
            'previous_message_id': last_message.id if last_message else None
        }
        
        if is_school_session:
            message_kwargs['school_study_session_id'] = session_id
        else:
            message_kwargs['home_study_session_id'] = session_id
        
        student_message = Message(**message_kwargs)
        session.add(student_message)
        session.flush()  # Get the message ID for file naming

        if last_message:
            last_message.next_message_id = student_message.id

        file_metadata = []
        has_images = False
        
        if uploaded_files:
            for file in uploaded_files:
                if file and file.filename:
                    is_allowed, file_type = FileHandler.allowed_file(file.filename)
                    if not is_allowed:
                        raise StudySessionError(f"File type not allowed: {file.filename}")

                    file_url = FileHandler.save_study_session_file(file, session_id, student_message.id)

                    attachment = Attachment(
                        message_id=student_message.id,
                        url=file_url,
                        file_type=file_type
                    )
                    session.add(attachment)

                    if file_type == FileType.IMAGE:
                        has_images = True

                    file_metadata.append({
                        'url': file_url,
                        'file_type': file_type.value
                    })

            session.flush()

        if has_images and student_message.modality != MessageModality.MULTIMODAL:
            student_message.modality = MessageModality.MULTIMODAL
            session.flush()

        session.refresh(student_message)

        try:
            messages_for_ai = [Message.to_openai_format(msg) for msg in history_messages]

            current_message_formatted = Message.to_openai_format(student_message)
            messages_for_ai.append(current_message_formatted)
            
            response_content = teacher.generate_response(
                messages=messages_for_ai,
                students=student,
                study_session=study_session
            )
        except Exception as ai_error:
            Logger.error(f"Error generating AI response for session {session_id}: {str(ai_error)}")
            session.rollback()
            raise StudySessionError(
                f"Failed to generate teacher response. "
                f"This may be due to image processing issues or API limitations. "
                f"Error: {str(ai_error)}"
            )

        teacher_message_kwargs = {
            'content': response_content,
            'timestamp': datetime.now(),
            'type': MessageType.RESPONSE,
            'modality': MessageModality.TEXT_ONLY,
            'teacher_ai_model_id': teacher.ai_model_id,
            'teacher_name': teacher.name,
            'previous_message_id': student_message.id
        }
        
        if is_school_session:
            teacher_message_kwargs['school_study_session_id'] = session_id
        else:
            teacher_message_kwargs['home_study_session_id'] = session_id
        
        teacher_message = Message(**teacher_message_kwargs)
        session.add(teacher_message)
        session.flush()

        student_message.next_message_id = teacher_message.id

        session.commit()

        return {
            'id': teacher_message.id,
            'content': response_content,
            'timestamp': teacher_message.timestamp.isoformat(),
            'type': 'response',
            'student_message': {
                'id': student_message.id,
                'attachments': file_metadata or []
            }
        }

    except StudySessionError:
        raise
    except Exception as e:
        session.rollback()
        Logger.error(f"Unexpected error processing message for session {session_id}: {str(e)}")
        raise StudySessionError(f"Error processing message: {str(e)}")


def send_welcome_message(
        session_id: int,
        student_id: int
) -> Dict[str, Any]:
    """
    Generate and send an automatic welcome message from the teacher agent.
    Works for both home and school study sessions.
    
    This function is called when a student enters a study session for the first time.
    """
    session = get_current_session()

    study_session = SchoolHoursStudySession.get_by(id=session_id, first=True)
    is_school_session = True
    if not study_session:
        study_session = HomeHoursStudySession.get_by(id=session_id, first=True)
        is_school_session = False
    
    if not study_session:
        raise SessionNotFoundError(f"Session {session_id} not found")

    teacher = study_session.teacher
    if not teacher:
        raise StudySessionError("No teacher assigned to this session")

    student = Student.get_by(id=student_id, first=True)
    
    try:
        welcome_prompt = """
        Welcome the student to this study session. 
        
        Your welcome message should:
        0. Introduce yourself (name + role)
        1. Greet the student warmly
        2. Briefly explain what you'll be covering in this session
        3. Mention the learning units you'll work through together
        4. Encourage the student to ask questions and engage actively
        5. Set a positive and supportive tone
        6. Address the student's current emotional state if needed
        
        Keep the message friendly, encouraging, and concise (2-3 paragraphs).
        """

        welcome_content = teacher.generate_response(
            messages=[{"role": "user", "content": welcome_prompt}],
            students=student,
            study_session=study_session
        )

        message_kwargs = {
            'content': welcome_content,
            'timestamp': datetime.now(),
            'type': MessageType.RESPONSE,
            'modality': MessageModality.TEXT_ONLY,
            'teacher_ai_model_id': teacher.ai_model_id,
            'teacher_name': teacher.name,
        }
        
        if is_school_session:
            message_kwargs['school_study_session_id'] = session_id
        else:
            message_kwargs['home_study_session_id'] = session_id
        
        welcome_message = Message(**message_kwargs)
        session.add(welcome_message)
        session.commit()

        return {
            'id': welcome_message.id,
            'content': welcome_content,
            'timestamp': welcome_message.timestamp.isoformat(),
            'type': 'response'
        }
        
    except Exception as e:
        session.rollback()
        Logger.error(f"Error generating welcome message for session {session_id}: {str(e)}")
        raise StudySessionError(f"Error generating welcome message: {str(e)}")
