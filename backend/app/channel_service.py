from __future__ import annotations

import random
from typing import Any

import httpx

from .db import normalize_phone
from .runtime_config import (
    get_broadcast_channel_order,
    get_max_api_base_url,
    get_max_bot_token,
    get_vk_api_base_url,
    get_vk_api_version,
    get_vk_community_token,
    get_whatsapp_access_token,
    get_whatsapp_api_base_url,
    get_whatsapp_api_version,
    get_whatsapp_default_language,
    get_whatsapp_default_template,
    get_whatsapp_phone_number_id,
    is_demo_mode,
    max_is_configured,
    telegram_bot_is_configured,
    vk_is_configured,
    whatsapp_is_configured,
)

SUPPORTED_CHANNELS = ["auto", "telegram", "whatsapp", "max", "vk"]
CHANNEL_LABELS = {
    "auto": "Автовыбор",
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "max": "MAX",
    "vk": "VK",
}


def recipient_for_channel(lead: dict[str, Any], channel: str) -> str:
    if channel == "telegram":
        return str(lead.get("telegram_chat_id") or "").strip()
    if channel == "whatsapp":
        return normalize_phone(lead.get("whatsapp_phone") or lead.get("phone") or "")
    if channel == "max":
        return str(lead.get("max_user_id") or lead.get("max_chat_id") or "").strip()
    if channel == "vk":
        return str(lead.get("vk_peer_id") or lead.get("vk_user_id") or "").strip()
    return ""


def available_channels(lead: dict[str, Any]) -> list[str]:
    return [channel for channel in ["telegram", "whatsapp", "max", "vk"] if recipient_for_channel(lead, channel)]


def pick_channel(lead: dict[str, Any], requested: str = "auto") -> str:
    requested = (requested or "auto").strip().lower()
    if requested in {"telegram", "whatsapp", "max", "vk"}:
        if recipient_for_channel(lead, requested):
            return requested
        raise RuntimeError(f"Для канала {CHANNEL_LABELS.get(requested, requested)} у лида нет получателя")

    preferred = str(lead.get("preferred_channel") or "auto").strip().lower()
    if preferred in {"telegram", "whatsapp", "max", "vk"} and recipient_for_channel(lead, preferred):
        return preferred

    for channel in get_broadcast_channel_order():
        if recipient_for_channel(lead, channel):
            return channel
    raise RuntimeError("У лида нет доступного канала для отправки")


async def _send_telegram(lead: dict[str, Any], text: str) -> str:
    from .telegram_service import send_telegram_message

    chat_id = recipient_for_channel(lead, "telegram")
    if not chat_id:
        raise RuntimeError("У лида нет Telegram chat_id")
    return await send_telegram_message(chat_id, text)


async def _send_whatsapp(lead: dict[str, Any], text: str, options: dict[str, Any]) -> str:
    to = recipient_for_channel(lead, "whatsapp")
    if not to:
        raise RuntimeError("У лида нет телефона для WhatsApp")
    if not whatsapp_is_configured():
        raise RuntimeError("WhatsApp не настроен: нужен access token и Phone Number ID")

    token = get_whatsapp_access_token()
    phone_number_id = get_whatsapp_phone_number_id()
    base = get_whatsapp_api_base_url().rstrip("/")
    version = get_whatsapp_api_version().strip().lstrip("/")
    url = f"{base}/{version}/{phone_number_id}/messages"
    template_name = str(options.get("whatsapp_template_name") or get_whatsapp_default_template() or "").strip()
    language = str(options.get("whatsapp_language") or get_whatsapp_default_language() or "ru").strip()

    if template_name:
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {"name": template_name, "language": {"code": language}},
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    messages = data.get("messages") or []
    if messages and isinstance(messages[0], dict):
        return str(messages[0].get("id") or "")
    return "whatsapp-sent"


async def _send_max(lead: dict[str, Any], text: str) -> str:
    recipient = recipient_for_channel(lead, "max")
    if not recipient:
        raise RuntimeError("У лида нет MAX user_id/chat_id")
    if not max_is_configured():
        raise RuntimeError("MAX не настроен: нужен Bot Token")

    token = get_max_bot_token()
    auth = token if token.lower().startswith("bearer ") else f"Bearer {token}"
    base = get_max_api_base_url().rstrip("/")
    params: dict[str, str] = {}
    if str(lead.get("max_user_id") or "").strip():
        params["user_id"] = str(lead.get("max_user_id"))
    else:
        params["chat_id"] = str(lead.get("max_chat_id"))
    headers = {"Authorization": auth, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{base}/messages", params=params, json={"text": text}, headers=headers)
        response.raise_for_status()
        data = response.json()
    return str(data.get("message_id") or data.get("id") or "max-sent")


async def _send_vk(lead: dict[str, Any], text: str) -> str:
    peer_id = recipient_for_channel(lead, "vk")
    if not peer_id:
        raise RuntimeError("У лида нет VK peer_id/user_id")
    if not vk_is_configured():
        raise RuntimeError("VK не настроен: нужен токен сообщества и Group ID")

    url = get_vk_api_base_url().rstrip("/") + "/messages.send"
    data = {
        "access_token": get_vk_community_token(),
        "v": get_vk_api_version(),
        "peer_id": peer_id,
        "random_id": random.randint(1, 2_147_483_647),
        "message": text,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, data=data)
        response.raise_for_status()
        result = response.json()
    if result.get("error"):
        raise RuntimeError(str(result["error"]))
    return str(result.get("response") or "vk-sent")


async def send_channel_message(
    lead: dict[str, Any],
    text: str,
    channel: str = "auto",
    options: dict[str, Any] | None = None,
) -> tuple[str, str]:
    options = options or {}
    selected = pick_channel(lead, channel)
    if is_demo_mode():
        return selected, f"demo-{selected}"
    if selected == "telegram":
        return selected, await _send_telegram(lead, text)
    if selected == "whatsapp":
        return selected, await _send_whatsapp(lead, text, options)
    if selected == "max":
        return selected, await _send_max(lead, text)
    if selected == "vk":
        return selected, await _send_vk(lead, text)
    raise RuntimeError(f"Неизвестный канал: {selected}")


async def test_channel_connection(channel: str) -> dict[str, Any]:
    channel = channel.strip().lower()
    if channel == "telegram":
        from .telegram_service import test_telegram_connection

        return await test_telegram_connection()
    if channel == "whatsapp":
        if not whatsapp_is_configured():
            raise RuntimeError("WhatsApp не настроен")
        url = f"{get_whatsapp_api_base_url().rstrip('/')}/{get_whatsapp_api_version().strip().lstrip('/')}/{get_whatsapp_phone_number_id()}"
        headers = {"Authorization": f"Bearer {get_whatsapp_access_token()}"}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return {"ok": True, "provider": "whatsapp", "data": response.json()}
    if channel == "max":
        if not max_is_configured():
            raise RuntimeError("MAX не настроен")
        return {"ok": True, "provider": "max", "base_url": get_max_api_base_url()}
    if channel == "vk":
        if not vk_is_configured():
            raise RuntimeError("VK не настроен")
        return {"ok": True, "provider": "vk", "group_id": get_vk_api_version()}
    raise RuntimeError("Неизвестный канал")
