"""
Speech-to-Text Service using OpenAI Whisper API.

This module provides functionality for:
- Audio file validation and temporary storage
- OpenAI Whisper API integration for transcription
- Audio file cleanup after transcription
"""

import os
import tempfile
from typing import Optional
from werkzeug.datastructures import FileStorage
from openai import OpenAI

from src.utils.logger import Logger


class SpeechToTextService:
    """Service for handling voice recording transcription."""

    SUPPORTED_FORMATS = {'webm', 'mp4', 'mp3', 'wav', 'm4a', 'ogg', 'flac'}
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB (Whisper API limit)
    
    @staticmethod
    def validate_audio_file(file: FileStorage) -> tuple[bool, Optional[str]]:
        """
        Validate audio file format and size.
        
        Args:
            file: FileStorage object from request
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file or not file.filename:
            return False, "No audio file provided"

        if '.' not in file.filename:
            return False, "Invalid file format"
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in SpeechToTextService.SUPPORTED_FORMATS:
            return False, (f"Unsupported audio format: {ext}. "
                           f"Supported formats: {', '.join(SpeechToTextService.SUPPORTED_FORMATS)}")

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > SpeechToTextService.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size is 25MB"
        
        if file_size == 0:
            return False, "Empty audio file"
        
        return True, None
    
    @staticmethod
    def transcribe_audio(audio_file: FileStorage) -> str:
        """
        Transcribe audio file using OpenAI Whisper API.
        
        Args:
            audio_file: FileStorage object containing audio data
            
        Returns:
            Transcribed text
            
        Raises:
            ValueError: If file validation fails
            Exception: If transcription fails
        """
        is_valid, error_message = SpeechToTextService.validate_audio_file(audio_file)
        if not is_valid:
            raise ValueError(error_message)

        temp_file_path = None
        try:
            ext = audio_file.filename.rsplit('.', 1)[1].lower()

            with tempfile.NamedTemporaryFile(mode='wb', suffix=f'.{ext}', delete=False) as temp_file:
                temp_file_path = temp_file.name
                audio_file.save(temp_file_path)
            
            Logger.info(f"Saved audio file temporarily: {temp_file_path}")

            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

            with open(temp_file_path, 'rb') as audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en"
                )
            
            transcribed_text = transcript.text.strip()
            Logger.info(f"Successfully transcribed audio: {len(transcribed_text)} characters")
            
            return transcribed_text
            
        except Exception as e:
            Logger.error(f"Error transcribing audio: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    Logger.debug(f"Deleted temporary audio file: {temp_file_path}")
                except Exception as e:
                    Logger.warning(f"Failed to delete temporary file {temp_file_path}: {e}")
