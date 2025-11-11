"""WebSocket utility functions for emitting events."""
from typing import Any, Dict, Optional
from flask_socketio import emit
from src.app import socketio
from src.models import Student


def emit_to_class(school_id: int, year: int, grade_level: str, event: str, data: Dict[str, Any]) -> None:
    """Emit an event to all users in a specific class room."""
    # Create a unique room identifier using the composite primary key of a Class instance
    room = f"class_{school_id}_{year}_{grade_level}"
    socketio.emit(event, data, room=room)


def emit_to_manager(manager_id: int, event: str, data: Dict[str, Any]) -> None:
    """Emit an event to a specific Class Manager."""
    room = f"manager_{manager_id}"
    socketio.emit(event, data, room=room)


def emit_to_student(student_id: int, event: str, data: Dict[str, Any]) -> None:
    """Emit an event to a specific Student."""
    room = f"student_{student_id}"
    socketio.emit(event, data, room=room)


def get_student_class_room(student_id: int) -> Optional[str]:
    """Get the class room identifier for a student."""
    try:
        student = Student.get_by(id=student_id, first=True)
        if student and student.classes:
            student_class = student.classes[0]

            room = f"class_{student_class.school_id}_{student_class.year}_{student_class.grade_level.value}"
            return room
        return None
    except Exception as e:
        print(f"Error getting student class room: {e}")
        return None
