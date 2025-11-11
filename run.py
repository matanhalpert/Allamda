"""Run script for the Flask application."""
from src.app import create_app

app, socketio = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
