"""
Message-related models.

This module contains models for Message and Attachment entities.
"""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, ForeignKeyConstraint, Integer, String, Text, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict

from .base import Base
from src.database.session_context import get_current_session
from src.enums import MessageType, MessageModality, FileType


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    type = Column(Enum(MessageType), nullable=False)
    modality = Column(Enum(MessageModality), nullable=False)
    previous_message_id = Column(Integer, ForeignKey('messages.id'), nullable=True)
    next_message_id = Column(Integer, ForeignKey('messages.id'), nullable=True)

    # Foreign keys to study sessions (mutually exclusive)
    home_study_session_id = Column(Integer, ForeignKey('home_hours_study_sessions.id'), nullable=True)
    school_study_session_id = Column(Integer, ForeignKey('school_hours_study_sessions.id'), nullable=True)

    # Sender identification (mutually exclusive)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=True)
    teacher_ai_model_id = Column(Integer, nullable=True)
    teacher_name = Column(String(100), nullable=True)

    # Relationships
    previous_message = relationship("Message", remote_side=[id], foreign_keys=[previous_message_id])
    next_message = relationship("Message", remote_side=[id], foreign_keys=[next_message_id])
    home_study_session = relationship("HomeHoursStudySession", back_populates="messages")
    school_study_session = relationship("SchoolHoursStudySession", back_populates="messages")
    student = relationship("Student", back_populates="sent_messages")
    teacher = relationship("Teacher", foreign_keys=[teacher_ai_model_id, teacher_name], back_populates="sent_messages")
    attachments = relationship("Attachment", back_populates="message")

    # Constraints
    __table_args__ = (
        ForeignKeyConstraint(['teacher_ai_model_id', 'teacher_name'],
                           ['teachers.ai_model_id', 'teachers.name']),
        CheckConstraint(
            '(home_study_session_id IS NOT NULL AND school_study_session_id IS NULL) OR '
            '(home_study_session_id IS NULL AND school_study_session_id IS NOT NULL)',
            name='check_single_study_session'
        ),
        CheckConstraint(
            '(student_id IS NOT NULL AND teacher_ai_model_id IS NULL AND teacher_name IS NULL) OR '
            '(student_id IS NULL AND teacher_ai_model_id IS NOT NULL AND teacher_name IS NOT NULL)',
            name='check_single_sender'
        ),
    )

    @classmethod
    def get_messages(
            cls, 
            session_id: int, 
            order_by_timestamp: bool = True,
            session_type: str = 'home'
    ) -> List['Message']:
        """Get all messages for a study session, ordered by timestamp."""
        session = get_current_session()
        
        if session_type == 'school':
            query = session.query(cls).filter(cls.school_study_session_id == session_id)
        else:  # default to 'home'
            query = session.query(cls).filter(cls.home_study_session_id == session_id)
        
        if order_by_timestamp:
            query = query.order_by(cls.timestamp.asc())
        
        return query.all()

    @staticmethod
    def to_openai_format(message: 'Message') -> Dict:
        """Convert database Message to OpenAI-compatible dict format."""
        from src.utils.file_handler import FileHandler
        from src.utils.logger import Logger
        
        role = "user" if message.type == MessageType.PROMPT else "assistant"

        image_attachments = []
        if message.attachments:
            image_attachments = [
                att for att in message.attachments 
                if att.file_type == FileType.IMAGE
            ]

        if not image_attachments:
            return {
                "role": role,
                "content": message.content
            }
        
        # Build multimodal content array with text and images
        content_parts = []

        if message.content:
            content_parts.append({
                "type": "text",
                "text": message.content
            })

        for attachment in image_attachments:
            try:
                file_path = FileHandler.get_file_path(attachment.url)
                base64_image = FileHandler.encode_image_to_base64(file_path)
                mime_type = FileHandler.get_image_mime_type(file_path)

                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                })
            except FileNotFoundError as e:
                Logger.warning(f"Image file not found for attachment {attachment.url}: {str(e)}")
                continue
            except ValueError as e:
                Logger.warning(f"Invalid image for attachment {attachment.url}: {str(e)}")
                continue
            except IOError as e:
                Logger.warning(f"Failed to read image {attachment.url}: {str(e)}")
                continue
            except Exception as e:
                Logger.error(f"Unexpected error encoding image {attachment.url}: {str(e)}")
                continue
        
        return {
            "role": role,
            "content": content_parts
        }


class Attachment(Base):
    __tablename__ = 'attachments'

    message_id = Column(Integer, ForeignKey('messages.id'), primary_key=True)
    url = Column(String(500), primary_key=True)
    file_type = Column(Enum(FileType), nullable=False)

    # Relationships
    message = relationship("Message", back_populates="attachments")
