import asyncio
import logging
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from config import DB_FILE
from database.models import (
    Message,
    Error,
    CREATE_MESSAGES_TABLE,
    CREATE_MESSAGES_INDEX,
    CREATE_ERRORS_TABLE,
)

logger = logging.getLogger(__name__)


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    """Open a short-lived connection, commit on success, roll back on error.

    A fresh connection per operation avoids sharing a single cursor across the
    event loop's worker threads, which sqlite3 does not allow.
    """
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables and indexes if they don't exist."""
    try:
        with _connect() as conn:
            conn.execute(CREATE_MESSAGES_TABLE)
            conn.execute(CREATE_MESSAGES_INDEX)
            conn.execute(CREATE_ERRORS_TABLE)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


def save_message(message: Message) -> None:
    """Save a message to the database."""
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO messages (msg_tg_id, username, user_id, date, prompt, response) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    message.msg_tg_id,
                    message.username,
                    message.user_id,
                    message.date,
                    message.prompt,
                    message.response,
                ),
            )
    except Exception as e:
        logger.error(f"Error saving message: {e}")


def update_message_response(msg_tg_id: int, response: str) -> None:
    """Update the response field for a message."""
    try:
        with _connect() as conn:
            conn.execute(
                "UPDATE messages SET response = ? WHERE msg_tg_id = ?",
                (response, msg_tg_id),
            )
    except Exception as e:
        logger.error(f"Error updating message response: {e}")


def save_error(error: Error) -> None:
    """Save an error to the database."""
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO errors (msg_tg_id, error_text) VALUES (?, ?)",
                (error.msg_tg_id, error.error_text),
            )
    except Exception as e:
        logger.error(f"Error saving error record: {e}")


# Async wrappers so handlers never block the event loop on disk I/O.

async def asave_message(message: Message) -> None:
    await asyncio.to_thread(save_message, message)


async def aupdate_message_response(msg_tg_id: int, response: str) -> None:
    await asyncio.to_thread(update_message_response, msg_tg_id, response)


async def asave_error(error: Error) -> None:
    await asyncio.to_thread(save_error, error)
