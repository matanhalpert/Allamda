"""Chat interface routes for study sessions."""

import os
from datetime import datetime, timedelta
from flask import render_template, redirect, request, session, jsonify, current_app, send_file

from ...auth import login_required, user_required
from ...utils import flash_message
from src.database import with_db_session
from src.models.session_models import HomeHoursStudySession, SchoolHoursStudySession
from src.enums import UserType, SessionStatus, MessageModality
from src.services.study_session import (
    get_session_messages,
    send_message,
    send_welcome_message,
    StudySessionError,
    InvalidSessionStateError
)
from src.services.voice_mode.speech_to_text import SpeechToTextService
from src.services.voice_mode.text_to_speech import TextToSpeechService

from src.app.routes.study import bp
from src.models.message_models import Message
from src.enums import MessageType


@bp.route("/study/chat/<int:session_id>", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def chat_interface(session_id):
    """Display chat interface for active study session. Works for both home and school sessions."""
    user = session.get("user")
    student_id = user.get("id")
    
    try:
        study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
        is_school_session = True
        if not study_session:
            study_session = HomeHoursStudySession.get_by_id_and_student(session_id, student_id)
            is_school_session = False
        
        if not study_session:
            flash_message("Access denied to this session.", "error")
            return redirect("/study")

        if study_session.status == SessionStatus.COMPLETED:
            flash_message("This session has already been completed.", "info")
            return redirect("/study")
        elif study_session.status == SessionStatus.CANCELLED:
            flash_message("This session has been cancelled.", "info")
            return redirect("/study")

        course = None
        learning_units = []
        if study_session.learning_units:
            learning_units = list(study_session.learning_units)
            if learning_units:
                course = learning_units[0].course

        messages = get_session_messages(session_id)

        duration_minutes = 0
        if study_session.duration:
            duration_minutes = int(study_session.duration.total_seconds() / 60)

        end_time = None
        remaining_seconds = None
        if is_school_session and study_session.start_time:
            duration = getattr(study_session, 'planned_duration_minutes', 60)
            end_time = study_session.start_time + timedelta(minutes=duration)
            remaining = end_time - datetime.now()
            remaining_seconds = max(0, int(remaining.total_seconds()))
        
        return render_template(
            "study_chat.html",
            user=user,
            session=study_session.to_dict(),
            session_id=session_id,
            status=study_session.status.value,
            course=course.to_dict() if course else None,
            learning_units=[lu.to_dict() for lu in learning_units],
            messages=messages,
            duration_minutes=duration_minutes,
            is_school_session=is_school_session,
            end_time=end_time.isoformat() if end_time else None,
            remaining_seconds=remaining_seconds
        )
        
    except Exception as e:
        flash_message("An error occurred while loading the chat.", "error")
        current_app.logger.error(f"Chat interface error: {e}")
        return redirect("/study")


@bp.route("/study/chat/<int:session_id>/welcome", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def send_welcome(session_id):
    """Generate welcome message for new session (AJAX endpoint)."""
    user = session.get("user")
    student_id = user.get("id")
    
    try:
        response = send_welcome_message(
            session_id=session_id,
            student_id=student_id
        )
            
        return jsonify(response)
        
    except StudySessionError as e:
        current_app.logger.error(f"Welcome message error: {e}")
        return jsonify({"error": "Failed to generate welcome message"}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected welcome message error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route("/study/chat/<int:session_id>/transcribe", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def transcribe_audio(session_id):
    """Transcribe audio recording to text (AJAX endpoint)."""
    user = session.get("user")
    student_id = user.get("id")

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    
    try:
        study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
        if not study_session:
            study_session = HomeHoursStudySession.get_by_id_and_student(session_id, student_id)
        
        if not study_session:
            return jsonify({"error": "Access denied to this session"}), 403

        if study_session.status != SessionStatus.ACTIVE:
            return jsonify({"error": "Session is not active"}), 400

        transcribed_text = SpeechToTextService.transcribe_audio(audio_file)
        
        return jsonify({
            "text": transcribed_text,
            "success": True
        })
        
    except ValueError as e:
        current_app.logger.warning(f"Audio validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Transcription error: {e}")
        return jsonify({"error": "Failed to transcribe audio"}), 500


@bp.route("/study/chat/message/<int:message_id>/audio", methods=["GET"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def get_message_audio(message_id):
    """Get or generate TTS audio for a teacher message (AJAX endpoint)."""
    user = session.get("user")
    student_id = user.get("id")
    
    try:
        message = Message.get_by(id=message_id, first=True)
        
        if not message:
            return jsonify({"error": "Message not found"}), 404

        if message.type != MessageType.RESPONSE:
            return jsonify({"error": "Audio only available for teacher messages"}), 400

        session_id = message.home_study_session_id or message.school_study_session_id
        is_school_session = message.school_study_session_id is not None
        
        if is_school_session:
            study_session = SchoolHoursStudySession.get_by_id_and_student(session_id, student_id)
        else:
            study_session = HomeHoursStudySession.get_by_id_and_student(session_id, student_id)
        
        if not study_session:
            return jsonify({"error": "Access denied to this message"}), 403

        audio_url = TextToSpeechService.get_or_generate_tts(
            message_id=message_id,
            text=message.content
        )

        audio_path = TextToSpeechService.get_audio_path(message_id)
        
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({"error": "Failed to generate audio"}), 500

        return send_file(
            audio_path,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name=f"message_{message_id}.mp3"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error getting message audio: {e}")
        return jsonify({"error": "Failed to get audio"}), 500


@bp.route("/study/chat/<int:session_id>/message", methods=["POST"])
@login_required
@user_required(UserType.STUDENT)
@with_db_session
def send_chat_message(session_id):
    """Send a message in the chat (AJAX endpoint)."""
    user = session.get("user")
    student_id = user.get("id")

    message_content = request.form.get("message", "").strip()
    files = request.files.getlist("attachments")
    modality_str = request.form.get("modality", None)

    if not message_content and not files:
        return jsonify({"error": "Message cannot be empty"}), 400

    modality = None
    if modality_str:
        try:
            modality = MessageModality(modality_str)
        except ValueError:
            current_app.logger.warning(f"Invalid modality value: {modality_str}")
            # Continue with default modality
    
    try:
        response = send_message(
            session_id=session_id,
            student_id=student_id,
            message_content=message_content,
            uploaded_files=files if files else None,
            modality=modality
        )
            
        return jsonify(response)
        
    except InvalidSessionStateError as e:
        return jsonify({"error": str(e)}), 400
    except StudySessionError as e:
        current_app.logger.error(f"Send message error: {e}")
        return jsonify({"error": "Failed to send message"}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected send message error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
