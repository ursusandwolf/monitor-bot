# MonitorBot

Мониторинг Telegram-каналов по ключевым словам.

Стек MVP: Python 3.11+, Telethon (user-сессия) + aiogram (команды и уведомления), SQLite.

## Быстрый старт

1. Создайте виртуальное окружение и установите зависимости:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Скопируйте `.env.example` → `.env` и заполните значения:

- `API_ID` / `API_HASH` — https://my.telegram.org
- `PHONE` — номер user-аккаунта
- `BOT_TOKEN` — токен от @BotFather
- `NOTIFY_CHAT_ID` — ваш Telegram user id (админ бота)

3. Smoke-проверка (опционально): отредактируйте константы в `smoke_test.py` и запустите:

```bash
python smoke_test.py
```

4. Запуск приложения:

```bash
python -m app.main
```

При первом запуске Telethon запросит код из Telegram и сохранит сессию в `sessions/`.

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие |
| `/help` | Список команд |
| `/add_keyword <слово>` | Добавить ключевое слово |
| `/del_keyword <слово>` | Удалить ключевое слово |
| `/keywords` | Список ключевых слов |
| `/add_channel @channel` | Добавить канал |
| `/del_channel @channel` | Удалить канал |
| `/channels` | Список каналов |
| `/status` | Статус мониторинга |
| `/pause` / `/resume` | Пауза / возобновление |

Команды принимает только чат с `NOTIFY_CHAT_ID`.

## Структура

```
app/
  main.py
  config.py
  database.py
  monitor/engine.py
  monitor/rules.py
  bot/handlers.py
  bot/notifications.py
```

## Учебник

Пошаговый путеводитель по коду (стиль Head First, с нуля):  
[`docs/HEAD_FIRST_MONITORBOT.md`](docs/HEAD_FIRST_MONITORBOT.md)

Подробности по требованиям: `TZ-telegram-monitor-bot.md`.
