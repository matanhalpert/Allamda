"""WebSocket event handlers for real-time updates."""
from flask import session, request, current_app
from flask_socketio import join_room, leave_room, emit
from src.app import socketio
from src.enums import UserType
from src.app.utils.websocket import get_student_class_room
from src.database import with_db_session


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    current_app.logger.info(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    current_app.logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join')
@with_db_session
def handle_join(data):
    """
    Handle room join requests from clients.
    
    Expected data format:
    {
        "user_type": "STUDENT" | "CLASS_MANAGER",
        "user_id": int
    }
    """
    try:
        user_type = data.get('user_type')
        user_id = data.get('user_id')
        
        if not user_type or not user_id:
            emit('error', {'message': 'Missing user_type or user_id'})
            return
        
        # Join appropriate room based on user type
        if user_type == UserType.STUDENT.value or user_type == 'STUDENT':
            # Join class room
            room = get_student_class_room(user_id)
            if room:
                join_room(room)
                current_app.logger.info(f"Student {user_id} joined room: {room}")
            
            # Also join personal student room for direct messaging
            personal_room = f"student_{user_id}"
            join_room(personal_room)
            current_app.logger.info(f"Student {user_id} joined personal room: {personal_room}")
            
            if room:
                emit('joined', {'room': room, 'personal_room': personal_room, 'message': 'Successfully joined class and personal rooms'})
            else:
                emit('joined', {'personal_room': personal_room, 'message': 'Successfully joined personal room'})
                
        elif user_type == UserType.CLASS_MANAGER.value or user_type == 'CLASS_MANAGER':
            room = f"manager_{user_id}"
            join_room(room)
            current_app.logger.info(f"Class Manager {user_id} joined room: {room}")
            emit('joined', {'room': room, 'message': 'Successfully joined manager room'})
        else:
            emit('error', {'message': f'Unsupported user type: {user_type}'})
            
    except Exception as e:
        current_app.logger.error(f"Error in handle_join: {e}")
        emit('error', {'message': 'Failed to join room'})


@socketio.on('leave')
def handle_leave(data):
    """
    Handle room leave requests from clients.
    
    Expected data format:
    {
        "room": str
    }
    """
    try:
        room = data.get('room')
        if room:
            leave_room(room)
            current_app.logger.info(f"Client left room: {room}")
            emit('left', {'room': room, 'message': 'Successfully left room'})
    except Exception as e:
        print(f"Error in handle_leave: {e}")
        emit('error', {'message': 'Failed to leave room'})


@socketio.on('request_status')
def handle_request_status(data):
    """
    Handle status request from clients.
    Clients can use this to sync their UI state on reconnection.
    
    Expected data format:
    {
        "user_type": "STUDENT" | "CLASS_MANAGER",
        "user_id": int
    }
    """
    try:
        user_type = data.get('user_type')
        user_id = data.get('user_id')

        emit('status_acknowledged', {
            'message': 'Status request received',
            'user_type': user_type,
            'user_id': user_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in handle_request_status: {e}")
        emit('error', {'message': 'Failed to get status'})
