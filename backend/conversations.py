"""
Conversation manager for Dexter.

This module provides simple persistence for conversation history using SQLite. Each session is
identified by a session_id, and messages are stored with sender and timestamp metadata. This
allows Dexter and its collaborating models to recall past dialogues across sessions.
"""

from __future__ import annotations

from datetime import datetime
import sqlite3
from typing import List, Tuple


class ConversationManager:
    """Manage persistent conversation history for Dexter sessions."""

    def __init__(self, db_path: str = "conversations.sqlite3") -> None:
        # Connect to the SQLite database. If the file does not exist, it will be created.
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        """Create the conversations table if it does not already exist."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_message(self, session_id: str, sender: str, message: str) -> None:
        """Insert a new message into the conversation history."""
        timestamp = datetime.utcnow().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversations VALUES (?, ?, ?, ?)",
            (session_id, sender, message, timestamp),
        )
        self.conn.commit()

    def get_messages(self, session_id: str) -> List[Tuple[str, str, str]]:
        """Retrieve all messages for a given session, ordered by timestamp."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT sender, message, timestamp FROM conversations WHERE session_id = ? ORDER BY timestamp",
            (session_id,),
        )
        return cursor.fetchall()

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
