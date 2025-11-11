"""File upload and validation utilities for study session attachments."""
import os
import shutil
import base64
from typing import Optional, Tuple
from flask import current_app

from src.enums import FileType
from src.utils.logger import Logger


class FileHandler:
    """
    Interface for handling file uploads, validation, and management
    for study session attachments.
    """

    @staticmethod
    def allowed_file(filename: str) -> Tuple[bool, Optional[FileType]]:
        """
        Check if file extension is allowed.

        Args:
            filename: Name of the file to check

        Returns:
            Tuple of (is_allowed, file_type)
            - is_allowed: Boolean indicating if file is allowed
            - file_type: FileType enum value if allowed, None otherwise
        """
        if '.' not in filename:
            return False, None
        
        ext = filename.rsplit('.', 1)[1].lower()

        for file_type, extensions in current_app.config['ALLOWED_EXTENSIONS'].items():
            if ext in extensions:
                return True, file_type
        
        return False, None

    @staticmethod
    def save_study_session_file(file, session_id: int, message_id: int) -> str:
        """
        Save uploaded file to filesystem and return URL path.
        
        Args:
            file: FileStorage object from request
            session_id: Study session ID
            message_id: Message ID
            
        Returns:
            Relative URL path to saved file (e.g., "/uploads/study_sessions/123/456_file.pdf")
        """
        filename = file.filename
        
        # Create session-specific directory
        session_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            str(session_id)
        )
        os.makedirs(session_dir, exist_ok=True)
        
        # Add message ID prefix to avoid collisions
        save_filename = f"{message_id}_{filename}"
        file_path = os.path.join(session_dir, save_filename)
        
        file.save(file_path)

        return f"/uploads/study_sessions/{session_id}/{save_filename}"

    @staticmethod
    def get_file_path(url: str) -> str:
        """
        Convert URL path to filesystem path.
        
        Args:
            url: URL path (e.g., "/uploads/study_sessions/123/456_file.pdf")
            
        Returns:
            Filesystem path
        """
        relative_path = url.lstrip('/')
        return os.path.join(current_app.root_path, '..', '..', relative_path)

    @staticmethod
    def delete_file(url: str) -> bool:
        """
        Delete a file given its URL path.

        Returns:
            True if file was deleted, False if file didn't exist
        """
        file_path = FileHandler.get_file_path(url)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    @staticmethod
    def get_image_mime_type(file_path: str) -> str:
        """
        Determine MIME type from file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string (e.g., "image/jpeg", "image/png")
        """
        ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
        
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
            'tiff': 'image/tiff',
            'tif': 'image/tiff'
        }
        
        return mime_types.get(ext, 'image/jpeg')  # Default to jpeg if unknown

    @staticmethod
    def encode_image_to_base64(file_path: str, max_size_mb: int = 20) -> str:
        """
        Read image file and return base64-encoded string.
        
        Args:
            file_path: Path to the image file
            max_size_mb: Maximum file size in MB (default: 20MB for OpenAI)
            
        Returns:
            Base64-encoded string of the image
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(
                f"Image file too large: {file_size_mb:.2f}MB exceeds maximum of {max_size_mb}MB"
            )
        
        try:
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()
                encoded_string = base64.b64encode(image_data).decode('utf-8')

                Logger.debug(
                    f"Encoded image {os.path.basename(file_path)}: "
                    f"{file_size_mb:.2f}MB -> {len(encoded_string)} chars"
                )
                
                return encoded_string
        except Exception as e:
            raise IOError(f"Error reading image file {file_path}: {str(e)}")

    @staticmethod
    def clear_uploads_directory() -> int:
        """
        Clear all files in the uploads directory.
        
        Returns:
            Number of files/directories deleted
        """
        uploads_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'uploads'
        )
        
        if not os.path.exists(uploads_dir):
            Logger.warning(f"Uploads directory does not exist: {uploads_dir}")
            return 0
        
        Logger.info(f"Clearing uploads directory: {uploads_dir}")
        
        deleted_count = 0
        for item in os.listdir(uploads_dir):
            item_path = os.path.join(uploads_dir, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    deleted_count += 1
                    Logger.info(f"Deleted file: {item}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    deleted_count += 1
                    Logger.info(f"Deleted directory: {item}")
            except Exception as e:
                Logger.error(f"Error deleting {item}: {e}")
        
        Logger.info(f"Total items deleted: {deleted_count}")
        return deleted_count


if __name__ == "__main__":
    FileHandler.clear_uploads_directory()
