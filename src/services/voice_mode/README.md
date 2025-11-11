# Voice Mode Service

Voice interaction capabilities for study sessions using OpenAI's Whisper (Speech-to-Text) and TTS (Text-to-Speech) APIs. Enables students to have conversational learning experiences through voice input and audio responses.

## Overview

The Voice Mode Service provides bidirectional voice communication in study sessions. Students can speak their questions (transcribed via Whisper API), and the AI teacher's responses are converted to natural-sounding speech (via OpenAI TTS API). The service handles audio validation, temporary storage, transcription, speech generation, and caching.

## Structure

```
voice_mode/
├── __init__.py           # Module exports
├── speech_to_text.py     # SpeechToTextService (Whisper API)
├── text_to_speech.py     # TextToSpeechService (TTS API)
└── README.md             # This file
```

## Key Components

### SpeechToTextService

Handles audio file validation and transcription using OpenAI Whisper API.

**Supported Audio Formats:**
- webm, mp4, mp3, wav, m4a, ogg, flac

**Maximum File Size:**
- 25MB (Whisper API limit)

**Key Methods:**

```python
validate_audio_file(file: FileStorage) -> tuple[bool, Optional[str]]
transcribe_audio(file: FileStorage) -> str
```

### TextToSpeechService

Generates natural-sounding speech from text using OpenAI TTS API with intelligent caching.

**Available Voices:**
- `alloy` - Neutral, balanced voice
- `echo` - Clear, authoritative voice
- `fable` - Warm, expressive voice
- `onyx` - Deep, confident voice
- `nova` - Friendly, engaging voice (default)
- `shimmer` - Soft, gentle voice

**TTS Models:**
- `tts-1` - Faster response time (used by default)
- `tts-1-hd` - Higher audio quality

**Key Methods:**

```python
generate_speech(text: str, voice: str = None) -> bytes
save_tts_audio(message_id: int, audio_bytes: bytes) -> str
get_or_generate_tts(message_id: int, text: str, voice: str = None) -> str
audio_exists(message_id: int) -> bool
```

## Usage

### Speech-to-Text (Whisper)

```python
from src.services.voice_mode import SpeechToTextService
from flask import request

@app.route('/transcribe', methods=['POST'])
def transcribe_route():
    audio_file = request.files.get('audio')
    
    # Validate audio file
    is_valid, error_msg = SpeechToTextService.validate_audio_file(audio_file)
    if not is_valid:
        return {'error': error_msg}, 400
    
    # Transcribe audio
    try:
        transcript = SpeechToTextService.transcribe_audio(audio_file)
        return {'text': transcript}, 200
    except Exception as e:
        return {'error': str(e)}, 500
```

### Text-to-Speech (OpenAI TTS)

```python
from src.services.voice_mode import TextToSpeechService

# Simple generation
audio_bytes = TextToSpeechService.generate_speech(
    text="Hello, how can I help you today?",
    voice="nova"  # Optional, defaults to 'nova'
)

# Save to file
audio_url = TextToSpeechService.save_tts_audio(
    message_id=123,
    audio_bytes=audio_bytes
)
# Returns: "/uploads/tts_audio/123.mp3"

# Get or generate with caching
audio_url = TextToSpeechService.get_or_generate_tts(
    message_id=123,
    text="Hello, how can I help you today?",
    voice="nova"
)
# Returns cached audio if exists, generates if not
```

### Complete Voice Interaction Flow

```python
from src.services.voice_mode import SpeechToTextService, TextToSpeechService
from src.services.study_session import send_message

# 1. Receive audio from student
audio_file = request.files['audio']

# 2. Transcribe to text
student_message = SpeechToTextService.transcribe_audio(audio_file)

# 3. Get AI teacher response
response = send_message(
    session=db_session,
    session_id=session_id,
    student_id=student_id,
    message_content=student_message
)

# 4. Convert teacher response to speech
audio_url = TextToSpeechService.get_or_generate_tts(
    message_id=response['id'],
    text=response['content'],
    voice='nova'
)

# 5. Return both text and audio URL
return {
    'text': response['content'],
    'audio_url': audio_url
}
```

## Features

### Speech-to-Text Features

**Automatic Validation:**
- File format validation
- File size checking (25MB limit)
- Descriptive error messages

**Temporary File Handling:**
- Creates temporary files for Whisper API
- Automatic cleanup after transcription
- Thread-safe file operations

**Error Handling:**
- Validates file exists and has name
- Checks file extension
- Handles API failures gracefully

### Text-to-Speech Features

**Intelligent Caching:**
- Checks if audio already generated for message ID
- Reuses cached audio to save API costs
- Automatic cache lookup via `get_or_generate_tts()`

**Voice Selection:**
- 6 distinct voice options
- Voice validation with helpful error messages
- Default voice (nova) for consistency

**File Management:**
- Saves to `uploads/tts_audio/` directory
- Filename format: `{message_id}.mp3`
- Returns URL paths ready for frontend use

**Audio Format:**
- MP3 format (universal browser support)
- Optimized for web streaming
- Reasonable file sizes

## Integration Points

### Study Session Routes
Used in `src/app/routes/study/chat.py` for:
- Voice message transcription
- AI response audio generation
- Real-time voice interactions

### WebSocket Handler
Integrated in `src/app/routes/websocket.py` for:
- Real-time voice streaming
- Live transcription feedback
- Audio response delivery

### Message Models
Links with `src/models/message_models.py`:
- Message IDs used for TTS caching
- Audio URLs stored with messages
- Message modality tracking (TEXT, VOICE, MULTIMODAL)

### Study Session Service
Works with `src/services/study_session/messaging.py`:
- Transcripts treated as regular messages
- Teacher responses converted to audio
- Session context maintained across voice interactions

## File Storage

### Audio Upload Storage
```
uploads/
└── tts_audio/
    ├── 1.mp3      # Message ID 1
    ├── 2.mp3      # Message ID 2
    └── ...
```

### Configuration
Requires Flask app configuration:

```python
# In src/app/config.py
TTS_AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'tts_audio')
```

## API Requirements

### Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key
```

### OpenAI API Endpoints

**Whisper (Speech-to-Text):**
- Endpoint: `client.audio.transcriptions.create()`
- Model: `whisper-1`
- Input: Audio file
- Output: Text transcript

**TTS (Text-to-Speech):**
- Endpoint: `client.audio.speech.create()`
- Model: `tts-1` or `tts-1-hd`
- Input: Text + voice selection
- Output: MP3 audio bytes

## Error Handling

### Speech-to-Text Errors

```python
# Validation errors
(False, "No audio file provided")
(False, "Invalid file format")
(False, "Unsupported audio format: xyz")
(False, "File size exceeds 25MB limit")

# Transcription errors
Exception: "Failed to transcribe audio: [API error message]"
```

### Text-to-Speech Errors

```python
# Voice validation
ValueError: "Invalid voice 'xyz'. Available voices: alloy, echo, fable, onyx, nova, shimmer"

# Generation errors
Exception: "Failed to generate text-to-speech: [API error message]"

# File errors
Exception: "Failed to save TTS audio: [filesystem error]"
```

## Performance Considerations

### Speech-to-Text
- Transcription typically takes 2-5 seconds for 30-second audio
- File validation is instant
- Temporary files cleaned up automatically

### Text-to-Speech
- Generation takes 1-3 seconds depending on text length
- Caching eliminates repeated API calls for same message
- MP3 format provides good quality/size balance

### Optimization Tips
1. **Cache aggressively**: Use `get_or_generate_tts()` instead of direct generation
2. **Limit audio length**: Long responses may take longer to generate
3. **Pre-generate**: Generate TTS immediately after AI response
4. **Voice consistency**: Use same voice throughout session for user experience

## WebSocket Integration

For real-time voice interactions:

```python
# Client sends audio chunks via WebSocket
@socketio.on('voice_input')
def handle_voice_input(data):
    audio_data = data['audio']
    session_id = data['session_id']
    
    # Transcribe
    transcript = SpeechToTextService.transcribe_audio(audio_data)
    
    # Get response
    response = send_message(session_id, transcript)
    
    # Generate audio
    audio_url = TextToSpeechService.get_or_generate_tts(
        response['id'],
        response['content']
    )
    
    # Emit back to client
    emit('voice_response', {
        'text': response['content'],
        'audio_url': audio_url
    })
```

## Voice Selection Guide

Choosing the right voice for different contexts:

| Voice | Characteristics | Best For |
|-------|----------------|----------|
| **alloy** | Neutral, balanced | General purpose, default choice |
| **echo** | Clear, authoritative | Lectures, formal content |
| **fable** | Warm, expressive | Storytelling, engaging explanations |
| **onyx** | Deep, confident | Professional content, older students |
| **nova** | Friendly, engaging | Primary choice, approachable learning |
| **shimmer** | Soft, gentle | Younger students, sensitive topics |

## Dependencies

- **OpenAI Python SDK**: `openai` package
- **Flask**: For `current_app` configuration access
- **Werkzeug**: For `FileStorage` handling
- **Python 3.7+**: Type hints and pathlib support

## Security Considerations

1. **File Validation**: Always validate before processing
2. **Size Limits**: Enforce 25MB limit to prevent abuse
3. **Temporary Files**: Clean up after transcription
4. **API Key**: Store in environment variables, never commit
5. **Audio Storage**: Consider cleanup policies for old files

## Future Enhancements

Potential additions:
- Real-time streaming transcription
- Speaker diarization for group sessions
- Voice activity detection (VAD)
- Audio compression for faster upload
- Multi-language support
- Voice cloning for personalized teachers
- Emotion detection from voice tone
- Background noise cancellation

## Troubleshooting

### Common Issues

**Transcription fails:**
- Check OPENAI_API_KEY is set
- Verify audio format is supported
- Ensure file is under 25MB
- Check internet connectivity

**TTS generation fails:**
- Verify API key has TTS access
- Check text length (max 4096 chars)
- Ensure voice name is valid
- Verify upload directory exists and is writable

**Audio not playing in browser:**
- Check file permissions
- Verify URL path is correct
- Ensure MP3 format is supported by browser

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

