---
name: telegram-monitor-bot
description: "Guide for developing MonitorBot — Telegram channel keyword monitor (Python MVP then Java portfolio). Use when working on this project: architecture, modules, stack decisions, sprint plan, or coding conventions."
type: knowledge
lifecycle: active
---

# MonitorBot — Project Guide

Use this skill when continuing development of **MonitorBot** (keyword-based Telegram channel monitor).

## Core Decisions (from TZ)

- **Approach:** Python MVP first (1–2 weeks) → later rewrite to Java for middle Java portfolio.
- **Monitoring:** User session via Telethon (not pure Bot API). Bot is used only for commands and notifications.
- **Matching (MVP):** Contains, case-insensitive. Later: Exact, Regex, Exclude.
- **Storage:** SQLite for MVP.
- **Priority:** Get working MVP (end of Sprint 2) before polishing.

## Project Structure (Python)

```
app/
├── main.py
├── config.py
├── database.py
├── monitor/engine.py + rules.py
├── bot/handlers.py + notifications.py
```

## Key Patterns to Follow

1. Separate user client (Telethon) from notification bot (aiogram).
2. Always handle `FloodWaitError`.
3. Persist last processed message IDs to avoid duplicates after restart.
4. Keep credentials only in `.env`.
5. Prefer simple Contains matching until MVP is stable.

## When Coding

- Reference the full TZ: `TZ-telegram-monitor-bot.md` (project name: MonitorBot)
- Smoke test lives in `smoke_test.py` (~50 lines).
- Do not over-engineer before Sprint 2 is complete.
- For Java phase: focus on clean architecture, not feature parity with Riniba/TelegramMonitor.

## Useful References from Competitors

- crazypeace/tg-keyword-monitor-bot — basic Telethon + bot notification pattern
- Riniba/TelegramMonitor — advanced matching rules (Exact/Contains/Regex/Exclude/Priority)
- streaming_overseer — simplicity of file-based config
