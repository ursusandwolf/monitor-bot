from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

from app.bot.notifications import send_match_notification
from app.database import Database
from app.monitor.rules import find_matches

logger = logging.getLogger(__name__)


class MonitorEngine:
    """Слушает новые сообщения Telethon и шлёт уведомления при совпадении ключей."""

    def __init__(
        self,
        client: TelegramClient,
        bot: Bot,
        db: Database,
        notify_chat_id: int,
    ) -> None:
        self.client = client
        self.bot = bot
        self.db = db
        self.notify_chat_id = notify_chat_id
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        self.client.add_event_handler(self._on_new_message, events.NewMessage)
        self._started = True
        channels = await self.db.list_channels()
        logger.info("Monitor engine started; channels=%s", channels)

    async def stop(self) -> None:
        if not self._started:
            return
        self.client.remove_event_handler(self._on_new_message, events.NewMessage)
        self._started = False

    async def _on_new_message(self, event: events.NewMessage.Event) -> None:
        """Happy path: pause? → наш канал? → есть ключи? → уведомить."""
        try:
            if await self.db.is_paused():
                return

            username, display_name = await self._resolve_chat(event)
            if not await self._is_watched(username):
                return

            text = event.raw_text or ""
            matched = find_matches(text, await self.db.list_keywords())
            if not matched:
                return

            await send_match_notification(
                bot=self.bot,
                chat_id=self.notify_chat_id,
                channel_name=display_name,
                text=text,
                matched=matched,
                link=_public_message_link(username, event.id),
            )
            logger.info("Match in @%s keys=%s", display_name, matched)
        except FloodWaitError as exc:
            logger.warning("FloodWait %ss", exc.seconds)
            await asyncio.sleep(exc.seconds)
        except Exception:
            logger.exception("Error while handling message")

    async def _resolve_chat(self, event: events.NewMessage.Event) -> tuple[str | None, str]:
        chat = await event.get_chat()
        username = getattr(chat, "username", None)
        title = getattr(chat, "title", None)
        fallback = str(getattr(chat, "id", "unknown"))
        display_name = username or title or fallback
        return username, display_name

    async def _is_watched(self, username: str | None) -> bool:
        if not username:
            return False
        watched = {name.lower() for name in await self.db.list_channels()}
        return bool(watched) and username.lower() in watched


def _public_message_link(username: str | None, message_id: int) -> str:
    if not username:
        return ""
    return f"https://t.me/{username}/{message_id}"
