import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from aiogram import Bot

# === ЗАПОЛНИ СВОИ ДАННЫЕ ===
API_ID = 12345678
API_HASH = "your_api_hash"
PHONE = "+79991234567"
BOT_TOKEN = "123456:ABC-DEF..."
NOTIFY_CHAT_ID = 123456789          # твой Telegram ID

CHANNELS = ["durov", "telegram"]    # без @
KEYWORDS = ["bitcoin", "тест", "hello"]

# =================================

user = TelegramClient("session", API_ID, API_HASH)
bot = Bot(token=BOT_TOKEN)

def match(text: str) -> bool:
    text = (text or "").lower()
    return any(k.lower() in text for k in KEYWORDS)

@user.on(events.NewMessage)
async def handler(event):
    try:
        if not match(event.raw_text):
            return
        chat = await event.get_chat()
        name = getattr(chat, "username", None) or getattr(chat, "title", str(chat.id))
        link = f"https://t.me/{name}/{event.id}" if getattr(chat, "username", None) else ""
        text = (
            f"🔔 Совпадение в @{name}\n\n"
            f"{event.raw_text[:500]}\n\n"
            f"{link}"
        )
        await bot.send_message(NOTIFY_CHAT_ID, text)
        print(f"[MATCH] {name}")
    except FloodWaitError as e:
        print(f"FloodWait {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print("Error:", e)

async def main():
    await user.start(phone=PHONE)
    print("Мониторинг запущен. Ctrl+C для остановки.")
    await user.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
