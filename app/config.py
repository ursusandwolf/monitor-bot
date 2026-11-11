from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip().lstrip("@") for part in value.split(",") if part.strip()]


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    phone: str
    bot_token: str
    notify_chat_id: int
    session_path: Path
    db_path: Path
    seed_channels: list[str]
    seed_keywords: list[str]


def load_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env")

    api_id_raw = os.getenv("API_ID", "").strip()
    api_hash = os.getenv("API_HASH", "").strip()
    phone = os.getenv("PHONE", "").strip()
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    notify_raw = os.getenv("NOTIFY_CHAT_ID", "").strip()

    missing = [
        name
        for name, value in [
            ("API_ID", api_id_raw),
            ("API_HASH", api_hash),
            ("PHONE", phone),
            ("BOT_TOKEN", bot_token),
            ("NOTIFY_CHAT_ID", notify_raw),
        ]
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")

    session_dir = ROOT_DIR / os.getenv("SESSION_DIR", "sessions")
    session_dir.mkdir(parents=True, exist_ok=True)
    db_path = ROOT_DIR / os.getenv("DB_PATH", "data/monitor.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return Settings(
        api_id=int(api_id_raw),
        api_hash=api_hash,
        phone=phone,
        bot_token=bot_token,
        notify_chat_id=int(notify_raw),
        session_path=session_dir / "monitor",
        db_path=db_path,
        seed_channels=_split_csv(os.getenv("CHANNELS")),
        seed_keywords=_split_csv(os.getenv("KEYWORDS")),
    )
