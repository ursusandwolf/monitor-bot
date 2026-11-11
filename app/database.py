from __future__ import annotations

from pathlib import Path

import aiosqlite


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA foreign_keys = ON")
        await self._init_schema()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        return self._conn

    async def _init_schema(self) -> None:
        await self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL COLLATE NOCASE UNIQUE
            );

            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            INSERT OR IGNORE INTO settings (key, value) VALUES ('paused', '0');
            """
        )
        await self.conn.commit()

    async def seed_if_empty(
        self, keywords: list[str], channels: list[str]
    ) -> None:
        async with self.conn.execute("SELECT COUNT(*) AS c FROM keywords") as cur:
            kw_count = (await cur.fetchone())["c"]
        async with self.conn.execute("SELECT COUNT(*) AS c FROM channels") as cur:
            ch_count = (await cur.fetchone())["c"]

        if kw_count == 0:
            for word in keywords:
                await self.add_keyword(word)
        if ch_count == 0:
            for username in channels:
                await self.add_channel(username)

    async def list_keywords(self) -> list[str]:
        async with self.conn.execute(
            "SELECT word FROM keywords ORDER BY word COLLATE NOCASE"
        ) as cur:
            rows = await cur.fetchall()
        return [row["word"] for row in rows]

    async def add_keyword(self, word: str) -> bool:
        cleaned = word.strip()
        if not cleaned:
            return False
        try:
            await self.conn.execute(
                "INSERT INTO keywords (word) VALUES (?)", (cleaned,)
            )
            await self.conn.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

    async def delete_keyword(self, word: str) -> bool:
        cur = await self.conn.execute(
            "DELETE FROM keywords WHERE word = ? COLLATE NOCASE", (word.strip(),)
        )
        await self.conn.commit()
        return cur.rowcount > 0

    async def list_channels(self) -> list[str]:
        async with self.conn.execute(
            "SELECT username FROM channels ORDER BY username COLLATE NOCASE"
        ) as cur:
            rows = await cur.fetchall()
        return [row["username"] for row in rows]

    async def add_channel(self, username: str) -> bool:
        cleaned = normalize_channel(username)
        if not cleaned:
            return False
        try:
            await self.conn.execute(
                "INSERT INTO channels (username) VALUES (?)", (cleaned,)
            )
            await self.conn.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

    async def delete_channel(self, username: str) -> bool:
        cleaned = normalize_channel(username)
        cur = await self.conn.execute(
            "DELETE FROM channels WHERE username = ? COLLATE NOCASE", (cleaned,)
        )
        await self.conn.commit()
        return cur.rowcount > 0

    async def is_paused(self) -> bool:
        async with self.conn.execute(
            "SELECT value FROM settings WHERE key = 'paused'"
        ) as cur:
            row = await cur.fetchone()
        return bool(row and row["value"] == "1")

    async def set_paused(self, paused: bool) -> None:
        await self.conn.execute(
            "INSERT INTO settings (key, value) VALUES ('paused', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            ("1" if paused else "0",),
        )
        await self.conn.commit()


def normalize_channel(value: str) -> str:
    """Приводит @name / t.me/name / https://t.me/name к username без @."""
    cleaned = value.strip()
    if cleaned.startswith("https://t.me/"):
        cleaned = cleaned.removeprefix("https://t.me/")
    elif cleaned.startswith("t.me/"):
        cleaned = cleaned.removeprefix("t.me/")
    cleaned = cleaned.lstrip("@").split("/")[0].split("?")[0]
    return cleaned
