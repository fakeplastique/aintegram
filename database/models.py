import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Message:
    id: Optional[int] = None
    msg_tg_id: int = 0
    username: str = ""
    user_id: int = 0
    date: str = ""
    prompt: str = ""
    response: str = ""


@dataclass
class Error:
    id: Optional[int] = None
    msg_tg_id: int = 0
    error_text: str = ""


# SQL creation statements
CREATE_MESSAGES_TABLE = '''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_tg_id INTEGER,
    username TEXT,
    user_id INTEGER,
    date TEXT,
    prompt TEXT,
    response TEXT
)
'''

CREATE_ERRORS_TABLE = '''
CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_tg_id INTEGER,
    error_text TEXT
)
'''