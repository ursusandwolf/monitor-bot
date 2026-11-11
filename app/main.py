from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from telethon import TelegramClient

from app.bot.handlers import setup_handlers
from app.config import Settings, load_settings
from app.database import Database
from app.monitor.engine import MonitorEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("monitorbot")


async def run() -> None:
    settings = load_settings()
    db = await _open_database(settings)
    bot, dispatcher = _build_bot(settings, db)
    client = await _start_telethon(settings)
    engine = MonitorEngine(client, bot, db, settings.notify_chat_id)
    await engine.start()

    # Два параллельных цикла: команды бота + прослушивание каналов.
    try:
        await asyncio.gather(
            dispatcher.start_polling(bot),
            client.run_until_disconnected(),
        )
    finally:
        await _shutdown(engine, db, bot, client)


async def _open_database(settings: Settings) -> Database:
    db = Database(settings.db_path)
    await db.connect()
    await db.seed_if_empty(settings.seed_keywords, settings.seed_channels)
    return db


def _build_bot(settings: Settings, db: Database) -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(setup_handlers(db, settings.notify_chat_id))
    return bot, dispatcher


async def _start_telethon(settings: Settings) -> TelegramClient:
    client = TelegramClient(
        str(settings.session_path),
        settings.api_id,
        settings.api_hash,
    )
    await client.start(phone=settings.phone)
    logger.info("Telethon session started")
    return client


async def _shutdown(
    engine: MonitorEngine,
    db: Database,
    bot: Bot,
    client: TelegramClient,
) -> None:
    await engine.stop()
    await db.close()
    await bot.session.close()
    if client.is_connected():
        await client.disconnect()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except ValueError as exc:
        logger.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
