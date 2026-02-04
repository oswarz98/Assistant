from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional


class CacheStore:
    def __init__(self, path: str = "oddscope.db") -> None:
        self.path = Path(path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    league TEXT,
                    payload TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS odds_snapshots (
                    key TEXT PRIMARY KEY,
                    league TEXT,
                    payload TEXT,
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

    def cache_game(self, game_id: str, league: str, payload: dict, updated_at: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO games (id, league, payload, updated_at) VALUES (?, ?, ?, ?)",
                (game_id, league, json.dumps(payload), updated_at),
            )
            conn.commit()

    def cache_snapshot(self, key: str, league: str, payload: dict, updated_at: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO odds_snapshots (key, league, payload, updated_at) VALUES (?, ?, ?, ?)",
                (key, league, json.dumps(payload), updated_at),
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
