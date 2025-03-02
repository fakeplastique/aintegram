import sqlite3
import logging
from typing import Optional
from config import DB_FILE
from database.models import Message, Error, CREATE_MESSAGES_TABLE, CREATE_ERRORS_TABLE

# Global connection and cursor
conn = None
cursor = None
logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize database connection and create tables if they don't exist."""
    global conn, cursor
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(CREATE_MESSAGES_TABLE)
        cursor.execute(CREATE_ERRORS_TABLE)
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

def close_connection() -> None:
    """Close the database connection."""
    if conn:
        conn.commit()
        conn.close()
        logger.info("Database connection closed")

def save_message(message: Message) -> None:
    """Save a message to the database."""
    try:
        cursor.execute(
            "INSERT INTO messages (msg_tg_id, username, user_id, date, prompt, response) VALUES (?, ?, ?, ?, ?, ?)",
            (message.msg_tg_id, message.username, message.user_id, message.date, message.prompt, message.response)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        conn.rollback()

def update_message_response(msg_tg_id: int, response: str) -> None:
    """Update the response field for a message."""
    try:
        cursor.execute(
            "UPDATE messages SET response = ? WHERE msg_tg_id = ?",
            (response, msg_tg_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating message response: {e}")
        conn.rollback()

def save_error(error: Error) -> None:
    """Save an error to the database."""
    try:
        cursor.execute(
            "INSERT INTO errors (msg_tg_id, error_text) VALUES (?, ?)",
            (error.msg_tg_id, error.error_text)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving error record: {e}")
        conn.rollback()