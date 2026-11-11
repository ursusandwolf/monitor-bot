from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.database import Database, normalize_channel


HELP_TEXT = (
    "/start — приветствие\n"
    "/help — список команд\n"
    "/add_keyword <слово>\n"
    "/del_keyword <слово>\n"
    "/keywords\n"
    "/add_channel @channel\n"
    "/del_channel @channel\n"
    "/channels\n"
    "/status\n"
    "/pause\n"
    "/resume"
)


class BotCommands:
    """Команды управления. Отвечает только админу (NOTIFY_CHAT_ID)."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def build_router(self, admin_id: int) -> Router:
        router = Router()
        router.message.filter(F.chat.id == admin_id)

        router.message.register(self.cmd_start, Command("start"))
        router.message.register(self.cmd_help, Command("help"))
        router.message.register(self.cmd_add_keyword, Command("add_keyword"))
        router.message.register(self.cmd_del_keyword, Command("del_keyword"))
        router.message.register(self.cmd_keywords, Command("keywords"))
        router.message.register(self.cmd_add_channel, Command("add_channel"))
        router.message.register(self.cmd_del_channel, Command("del_channel"))
        router.message.register(self.cmd_channels, Command("channels"))
        router.message.register(self.cmd_status, Command("status"))
        router.message.register(self.cmd_pause, Command("pause"))
        router.message.register(self.cmd_resume, Command("resume"))
        return router

    async def cmd_start(self, message: Message) -> None:
        await message.answer(
            "MonitorBot готов.\n"
            "Мониторинг каналов по ключевым словам.\n"
            "Команды: /help"
        )

    async def cmd_help(self, message: Message) -> None:
        await message.answer(HELP_TEXT)

    async def cmd_add_keyword(self, message: Message, command: CommandObject) -> None:
        word = (command.args or "").strip()
        if not word:
            await message.answer("Использование: /add_keyword <слово>")
            return
        if await self.db.add_keyword(word):
            await message.answer(f"Добавлено: {word}")
        else:
            await message.answer("Уже есть или пустое значение.")

    async def cmd_del_keyword(self, message: Message, command: CommandObject) -> None:
        word = (command.args or "").strip()
        if not word:
            await message.answer("Использование: /del_keyword <слово>")
            return
        deleted = await self.db.delete_keyword(word)
        await message.answer("Удалено." if deleted else "Не найдено.")

    async def cmd_keywords(self, message: Message) -> None:
        items = await self.db.list_keywords()
        if not items:
            await message.answer("Список ключевых слов пуст.")
            return
        lines = "\n".join(f"• {word}" for word in items)
        await message.answer(f"Ключевые слова:\n{lines}")

    async def cmd_add_channel(self, message: Message, command: CommandObject) -> None:
        raw = (command.args or "").strip()
        if not raw:
            await message.answer("Использование: /add_channel @channel")
            return
        if await self.db.add_channel(raw):
            await message.answer(f"Канал добавлен: @{normalize_channel(raw)}")
        else:
            await message.answer("Уже есть или некорректное имя.")

    async def cmd_del_channel(self, message: Message, command: CommandObject) -> None:
        raw = (command.args or "").strip()
        if not raw:
            await message.answer("Использование: /del_channel @channel")
            return
        deleted = await self.db.delete_channel(raw)
        await message.answer("Удалено." if deleted else "Не найдено.")

    async def cmd_channels(self, message: Message) -> None:
        items = await self.db.list_channels()
        if not items:
            await message.answer("Список каналов пуст.")
            return
        lines = "\n".join(f"• @{name}" for name in items)
        await message.answer(f"Каналы:\n{lines}")

    async def cmd_status(self, message: Message) -> None:
        paused = await self.db.is_paused()
        keywords = await self.db.list_keywords()
        channels = await self.db.list_channels()
        state = "пауза" if paused else "активен"
        await message.answer(
            f"Статус: {state}\n"
            f"Ключей: {len(keywords)}\n"
            f"Каналов: {len(channels)}"
        )

    async def cmd_pause(self, message: Message) -> None:
        await self.db.set_paused(True)
        await message.answer("Мониторинг на паузе.")

    async def cmd_resume(self, message: Message) -> None:
        await self.db.set_paused(False)
        await message.answer("Мониторинг возобновлён.")


def setup_handlers(db: Database, admin_id: int) -> Router:
    """Точка подключения команд к Dispatcher (см. app.main)."""
    return BotCommands(db).build_router(admin_id)
