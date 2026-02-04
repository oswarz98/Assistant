from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


class CacheStore:
    def __init__(self, path: str = "marketscope.db") -> None:
        self.path = Path(path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            conn.commit()

    def get(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("SELECT value FROM cache WHERE key = ?", (key,)).fetchone()
            return row[0] if row else None

    def set(self, key: str, value: str, updated_at: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, updated_at),
            )
            conn.commit()

    def get_setting(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row[0] if row else None

    def set_setting(self, key: str, value: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
            conn.commit()
