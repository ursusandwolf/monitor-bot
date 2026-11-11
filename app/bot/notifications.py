from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter

logger = logging.getLogger(__name__)


async def send_match_notification(
    bot: Bot,
    chat_id: int,
    channel_name: str,
    text: str,
    matched: list[str],
    link: str,
) -> None:
    preview = (text or "")[:500]
    matched_line = ", ".join(matched) if matched else "—"
    body = (
        f"🔔 Совпадение в @{channel_name}\n\n"
        f"{preview}\n\n"
        f"Ключи: {matched_line}\n"
        f"{link}"
    ).strip()
    try:
        await bot.send_message(chat_id, body)
    except TelegramRetryAfter as exc:
        logger.warning("RetryAfter on notify: %ss", exc.retry_after)
        await asyncio.sleep(exc.retry_after)
        await bot.send_message(chat_id, body)
    except Exception:
        logger.exception("Failed to send notification")
        raise
