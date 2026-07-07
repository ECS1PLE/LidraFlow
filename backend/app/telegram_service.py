from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from .db import (
    add_message,
    get_or_create_lead_from_telegram,
    get_setting,
    set_setting,
    update_lead,
)
from .runtime_config import get_telegram_bot_token, is_bot_polling_enabled, is_demo_mode, telegram_bot_is_configured

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, token: str):
        self.token = token.strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def request(self, method: str, payload: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{self.base_url}/{method}", json=payload or {})
            response.raise_for_status()
            data = response.json()
            if not data.get("ok"):
                raise RuntimeError(f"Telegram API error: {data}")
            return data

    async def send_message(self, chat_id: str, text: str) -> dict[str, Any]:
        return await self.request(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
        )

    async def get_updates(self, offset: int, timeout: int = 25) -> list[dict[str, Any]]:
        data = await self.request(
            "getUpdates",
            {"offset": offset, "timeout": timeout, "allowed_updates": ["message"]},
            timeout=timeout + 10,
        )
        return list(data.get("result") or [])

    async def get_me(self) -> dict[str, Any]:
        data = await self.request("getMe")
        return dict(data.get("result") or {})


async def send_telegram_message(chat_id: str, text: str) -> str:
    token = get_telegram_bot_token()
    if not token or not telegram_bot_is_configured():
        if is_demo_mode():
            return "demo-mode"
        raise RuntimeError("TELEGRAM_BOT_TOKEN не настроен. Вставьте токен на странице Настройки → Интеграции.")
    client = TelegramClient(token)
    data = await client.send_message(chat_id, text)
    msg = data.get("result") or {}
    return str(msg.get("message_id", ""))


async def test_telegram_connection() -> dict[str, Any]:
    token = get_telegram_bot_token()
    if not token:
        raise RuntimeError("Telegram token не настроен")
    client = TelegramClient(token)
    me = await client.get_me()
    return {"ok": True, "bot": me}


async def handle_update(update: dict[str, Any]) -> None:
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    user = message.get("from") or {}
    text = (message.get("text") or "").strip()
    if not text:
        return

    chat_id = str(chat.get("id") or "")
    if not chat_id:
        return

    username = str(user.get("username") or "")
    first_name = str(user.get("first_name") or "")
    last_name = str(user.get("last_name") or "")
    sender_name = " ".join(p for p in [first_name, last_name] if p).strip() or username or chat_id
    lead_id = get_or_create_lead_from_telegram(chat_id, username, first_name, last_name)
    add_message(
        lead_id,
        text,
        direction="in",
        channel="telegram",
        sender_name=sender_name,
        tg_message_id=str(message.get("message_id", "")),
    )

    if text.startswith("/start"):
        welcome = get_setting("bot_welcome")
        await send_telegram_message(chat_id, welcome)
        add_message(lead_id, welcome, direction="out", channel="telegram", sender_name="bot")
    elif text.startswith("/stop"):
        update_lead(lead_id, {"consent_status": "opted_out", "status": "closed"})
        answer = get_setting("bot_stop")
        await send_telegram_message(chat_id, answer)
        add_message(lead_id, answer, direction="out", channel="telegram", sender_name="bot")
    else:
        ack = get_setting("bot_ack")
        await send_telegram_message(chat_id, ack)
        add_message(lead_id, ack, direction="out", channel="telegram", sender_name="bot")


async def polling_loop(stop_event: asyncio.Event) -> None:
    offset_raw = get_setting("telegram_update_offset", "0")
    try:
        offset = int(offset_raw)
    except ValueError:
        offset = 0

    current_token = ""
    client: TelegramClient | None = None

    while not stop_event.is_set():
        try:
            if not is_bot_polling_enabled():
                await asyncio.sleep(5)
                continue

            token = get_telegram_bot_token()
            if not token or not telegram_bot_is_configured():
                await asyncio.sleep(5)
                continue

            if token != current_token or client is None:
                client = TelegramClient(token)
                current_token = token
                try:
                    me = await client.get_me()
                    logger.info("Telegram bot connected: @%s", me.get("username"))
                except Exception as exc:
                    logger.warning("Telegram getMe failed: %s", exc)
                    await asyncio.sleep(5)
                    continue

            updates = await client.get_updates(offset=offset, timeout=25)
            for update in updates:
                update_id = int(update.get("update_id", 0))
                offset = max(offset, update_id + 1)
                await handle_update(update)
            set_setting("telegram_update_offset", str(offset))
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("Telegram polling error: %s", exc)
            await asyncio.sleep(3)
