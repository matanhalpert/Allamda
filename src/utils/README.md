# Utilities

Shared utility modules used across the application.

## Structure

```
utils/
├── __init__.py      # Package exports
├── logger.py        # Logging configuration
└── file_handler.py  # File upload and management utilities
```

## Logger (`logger.py`)

Simple logging setup for the application.

### Features
- Configures Python's `logging` module
- Default log level: `INFO`
- Outputs to stdout with formatted messages
- Format: `%(asctime)s - %(levelname)s - %(message)s`

### Usage

```python
from src.utils.logger import Logger

Logger.info("Application started")
Logger.error("Something went wrong")
Logger.debug("Debug information")
```

### Default Logger
A default logger instance (`logger`) is created at module level for immediate use.

## File Handler (`file_handler.py`)

Utilities for handling file uploads and attachments in study sessions.

### FileHandler Class

**File Validation:**
- `allowed_file(filename)` - Checks if file extension is allowed
- Returns tuple: `(is_allowed: bool, file_type: FileType | None)`
- Validates against `ALLOWED_EXTENSIONS` config

**File Operations:**
- `save_study_file(file, session_id, message_id)` - Saves uploaded file
  - Creates session-specific directory structure
  - Adds message ID prefix to avoid collisions
  - Returns relative URL path
- `get_file_path(url)` - Converts URL to filesystem path
- `delete_file(url)` - Deletes file by URL path

**Image Handling:**
- `get_image_mime_type(file_path)` - Determines MIME type from extension
- `encode_image_to_base64(file_path, max_size_mb=20)` - Encodes image for AI processing
  - Validates file size (default 20MB max for OpenAI)
  - Returns base64-encoded string

**Directory Management:**
- `clear_uploads_directory()` - Clears all files in uploads directory
  - Returns count of deleted items
  - Useful for cleanup/maintenance

### Supported File Types

Based on `FileType` enum:
- **Images**: PNG, JPG, JPEG, GIF, WEBP
- **Documents**: DOC, DOCX
- **PDFs**: PDF
- **Text**: TXT, MD
- **Spreadsheets**: XLS, XLSX, CSV
- **Presentations**: PPT, PPTX

### File Structure

Uploaded files are stored in:
```
uploads/
└── study_sessions/
    └── <session_id>/
        └── <message_id>_<filename>
```

### Usage

```python
from src.utils.file_handler import FileHandler
from flask import request

# Validate file
is_allowed, file_type = FileHandler.allowed_file(filename)
if not is_allowed:
    return "File type not allowed", 400

# Save file
url_path = FileHandler.save_study_session_file(
    request.files['file'],
    session_id=123,
    message_id=456
)

# Encode image for AI
try:
    base64_image = FileHandler.encode_image_to_base64(image_path)
except ValueError as e:
    # File too large
    pass
```

## Integration

- **Logger**: Used throughout application for logging operations
- **FileHandler**: Used in study session routes for handling message attachments
- Both utilities are imported at application level for consistent usage

## Notes

- FileHandler requires Flask application context (uses `current_app.config`)
- Upload directory path configured in `src/app/config.py`
- Maximum file size: 16MB (configurable via `MAX_CONTENT_LENGTH`)
- Logger instance is singleton (shared across application)

