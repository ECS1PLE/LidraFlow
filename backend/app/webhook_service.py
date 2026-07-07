from __future__ import annotations

from typing import Any

from .db import add_message, get_or_create_lead_from_channel, normalize_phone, update_lead


def _text_from_whatsapp_message(message: dict[str, Any]) -> str:
    if message.get("type") == "text":
        return str((message.get("text") or {}).get("body") or "")
    if message.get("type") == "button":
        return str((message.get("button") or {}).get("text") or "")
    if message.get("type") == "interactive":
        interactive = message.get("interactive") or {}
        return str((interactive.get("button_reply") or interactive.get("list_reply") or {}).get("title") or "[interactive]")
    return f"[{message.get('type') or 'message'}]"


def handle_whatsapp_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    created = 0
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            contacts_by_wa_id = {
                str(contact.get("wa_id") or ""): str((contact.get("profile") or {}).get("name") or "")
                for contact in value.get("contacts") or []
                if isinstance(contact, dict)
            }
            for message in value.get("messages") or []:
                if not isinstance(message, dict):
                    continue
                phone = normalize_phone(message.get("from") or "")
                if not phone:
                    continue
                display_name = contacts_by_wa_id.get(phone, "")
                lead_id = get_or_create_lead_from_channel("whatsapp", phone, display_name=display_name, phone=phone)
                text = _text_from_whatsapp_message(message)
                add_message(
                    lead_id,
                    text,
                    direction="in",
                    channel="whatsapp",
                    sender_name=display_name or phone,
                    external_message_id=str(message.get("id") or ""),
                )
                if text.strip().lower() in {"stop", "/stop", "стоп", "отписаться"}:
                    update_lead(lead_id, {"consent_status": "opted_out", "status": "closed"})
                created += 1
    return {"ok": True, "messages": created}


def handle_max_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    message = payload.get("message") or payload.get("event", {}).get("message") or payload
    body = message.get("body") or message.get("text") or {}
    text = body.get("text") if isinstance(body, dict) else body
    text = str(text or "")
    sender = message.get("sender") or message.get("user") or payload.get("user") or {}
    user_id = str(sender.get("user_id") or sender.get("id") or message.get("user_id") or "")
    chat_id = str(message.get("chat_id") or (message.get("recipient") or {}).get("chat_id") or "")
    name = " ".join(str(sender.get(k) or "") for k in ["first_name", "last_name"]).strip() or str(sender.get("name") or "")
    external = user_id or chat_id
    if not external or not text:
        return {"ok": True, "messages": 0}
    lead_id = get_or_create_lead_from_channel("max", external, display_name=name, chat_id=chat_id)
    add_message(lead_id, text, direction="in", channel="max", sender_name=name or external, external_message_id=str(message.get("id") or ""))
    if text.strip().lower() in {"stop", "/stop", "стоп", "отписаться"}:
        update_lead(lead_id, {"consent_status": "opted_out", "status": "closed"})
    return {"ok": True, "messages": 1}


def handle_vk_webhook(payload: dict[str, Any]) -> dict[str, Any] | str:
    if payload.get("type") == "confirmation":
        return "confirmation"
    if payload.get("type") != "message_new":
        return {"ok": True, "messages": 0}
    obj = payload.get("object") or {}
    message = obj.get("message") or obj
    text = str(message.get("text") or "")
    peer_id = str(message.get("peer_id") or "")
    user_id = str(message.get("from_id") or "")
    if not peer_id or not text:
        return {"ok": True, "messages": 0}
    lead_id = get_or_create_lead_from_channel("vk", user_id or peer_id, display_name=f"VK {user_id or peer_id}", chat_id=peer_id)
    add_message(lead_id, text, direction="in", channel="vk", sender_name=f"VK {user_id or peer_id}", external_message_id=str(message.get("id") or ""))
    if text.strip().lower() in {"stop", "/stop", "стоп", "отписаться"}:
        update_lead(lead_id, {"consent_status": "opted_out", "status": "closed"})
    return {"ok": True, "messages": 1}
