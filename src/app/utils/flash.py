"""Flash message handling utilities for displaying temporary messages to users."""
from flask import session


def flash_message(message, category="info"):
    """Add a flash message to the session.
    
    Args:
        message: The message text to display
        category: Message category (info, success, warning, error)
    """
    if "messages" not in session:
        session["messages"] = []
    session["messages"].append({"text": message, "category": category})
    session.modified = True


def get_flash_messages():
    """Get and clear all flash messages from the session.
    
    Returns:
        List of message dictionaries with 'text' and 'category' keys
    """
    messages = session.get("messages", [])
    session["messages"] = []
    session.modified = True
    return messages

