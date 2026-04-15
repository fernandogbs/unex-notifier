from __future__ import annotations

import sqlite3
from pathlib import Path


class SeenEmailRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._setup()

    def _setup(self) -> None:
        with sqlite3.connect(self._db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_emails (
                  message_id TEXT PRIMARY KEY,
                  seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()

    def has_seen(self, message_id: str) -> bool:
        with sqlite3.connect(self._db_path) as connection:
            cursor = connection.execute(
                "SELECT 1 FROM seen_emails WHERE message_id = ? LIMIT 1",
                (message_id,),
            )
            row = cursor.fetchone()
        return row is not None

    def mark_seen_many(self, message_ids: list[str]) -> None:
        if not message_ids:
            return
        unique_ids = sorted(set(message_ids))
        with sqlite3.connect(self._db_path) as connection:
            connection.executemany(
                "INSERT OR IGNORE INTO seen_emails (message_id) VALUES (?)",
                [(message_id,) for message_id in unique_ids],
            )
            connection.commit()
