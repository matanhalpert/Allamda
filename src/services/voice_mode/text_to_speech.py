"""
Text-to-Speech Service using OpenAI TTS API.

This module provides functionality for:
- Text-to-speech generation using OpenAI TTS
- Audio file caching for performance
- Audio file management
"""

import os
from pathlib import Path
from typing import Optional
from openai import OpenAI
from flask import current_app

from src.utils.logger import Logger


class TextToSpeechService:
    """Service for handling text-to-speech generation and caching."""

    AVAILABLE_VOICES = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    DEFAULT_VOICE = 'nova'
    TTS_MODEL = 'tts-1'  # Use tts-1 for faster response, tts-1-hd for higher quality
    
    @staticmethod
    def generate_speech(text: str, voice: str = None) -> bytes:
        """
        Generate speech audio from text using OpenAI TTS API.
        
        Args:
            text: Text content to convert to speech
            voice: Voice to use (default: nova)
            
        Returns:
            Audio content as bytes (MP3 format)
            
        Raises:
            ValueError: If voice is invalid
            Exception: If TTS generation fails
        """
        if voice is None:
            voice = TextToSpeechService.DEFAULT_VOICE
        
        if voice not in TextToSpeechService.AVAILABLE_VOICES:
            raise ValueError(
                f"Invalid voice '{voice}'. Available voices: {', '.join(TextToSpeechService.AVAILABLE_VOICES)}"
            )
        
        try:
            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

            Logger.info(f"Generating TTS for text length: {len(text)} characters with voice: {voice}")
            
            response = client.audio.speech.create(
                model=TextToSpeechService.TTS_MODEL,
                voice=voice,
                input=text,
                response_format="mp3"
            )

            audio_bytes = response.content
            
            Logger.info(f"Successfully generated TTS audio: {len(audio_bytes)} bytes")
            
            return audio_bytes
            
        except Exception as e:
            Logger.error(f"Error generating TTS: {e}")
            raise Exception(f"Failed to generate text-to-speech: {str(e)}")
    
    @staticmethod
    def save_tts_audio(message_id: int, audio_bytes: bytes) -> str:
        """
        Save TTS audio file to filesystem.
        
        Args:
            message_id: ID of the message
            audio_bytes: Audio content as bytes
            
        Returns:
            URL path to the saved audio file
        """
        try:
            tts_folder = current_app.config['TTS_AUDIO_FOLDER']
            os.makedirs(tts_folder, exist_ok=True)

            filename = f"{message_id}.mp3"
            file_path = os.path.join(tts_folder, filename)

            with open(file_path, 'wb') as f:
                f.write(audio_bytes)
            
            Logger.info(f"Saved TTS audio file: {file_path}")

            return f"/uploads/tts_audio/{filename}"
            
        except Exception as e:
            Logger.error(f"Error saving TTS audio: {e}")
            raise Exception(f"Failed to save TTS audio: {str(e)}")
    
    @staticmethod
    def get_audio_path(message_id: int) -> Optional[str]:
        """
        Get the filesystem path for a message's TTS audio file.
        
        Args:
            message_id: ID of the message
            
        Returns:
            Filesystem path if file exists, None otherwise
        """
        try:
            tts_folder = current_app.config['TTS_AUDIO_FOLDER']
            file_path = os.path.join(tts_folder, f"{message_id}.mp3")
            
            if os.path.exists(file_path):
                return file_path
            return None
            
        except Exception as e:
            Logger.warning(f"Error checking TTS audio path: {e}")
            return None
    
    @staticmethod
    def audio_exists(message_id: int) -> bool:
        """
        Check if TTS audio file exists for a message.
        
        Args:
            message_id: ID of the message
            
        Returns:
            True if audio file exists, False otherwise
        """
        return TextToSpeechService.get_audio_path(message_id) is not None
    
    @staticmethod
    def get_or_generate_tts(message_id: int, text: str, voice: str = None) -> str:
        """
        Get existing TTS audio or generate if not cached.
        
        Args:
            message_id: ID of the message
            text: Text content to convert to speech
            voice: Voice to use (default: nova)
            
        Returns:
            URL path to the audio file
            
        Raises:
            Exception: If generation or saving fails
        """
        if TextToSpeechService.audio_exists(message_id):
            Logger.info(f"Using cached TTS audio for message {message_id}")
            return f"/uploads/tts_audio/{message_id}.mp3"

        Logger.info(f"Generating new TTS audio for message {message_id}")
        audio_bytes = TextToSpeechService.generate_speech(text, voice)
        
        # Save and return URL
        return TextToSpeechService.save_tts_audio(message_id, audio_bytes)
