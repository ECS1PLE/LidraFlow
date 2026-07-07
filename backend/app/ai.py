from __future__ import annotations

import html
from typing import Any

import httpx

from .config import settings
from .db import get_settings


SYSTEM_RULES = (
    "Ты пишешь короткие, спокойные B2B-сообщения на русском языке. "
    "Не обещай скидки, гарантии, встречи или результаты без подтверждения менеджера. "
    "Не дави, не манипулируй, не маскируйся под знакомого человека. "
    "Цель первого касания: вежливо спросить, актуально ли предложение и кому лучше написать."
)


def _safe_format(template: str, values: dict[str, str]) -> str:
    class SafeDict(dict):
        def __missing__(self, key: str) -> str:
            return ""

    try:
        return template.format_map(SafeDict(values))
    except Exception:
        return template


def rule_based_draft(lead: dict[str, Any], extra_context: str = "") -> str:
    cfg = get_settings()
    values = {
        "organization": str(lead.get("organization") or "ваша компания"),
        "contact_name": str(lead.get("contact_name") or ""),
        "niche": str(lead.get("niche") or "ваша сфера"),
        "region": str(lead.get("region") or ""),
        "city": str(lead.get("city") or ""),
        "district": str(lead.get("district") or ""),
        "address": str(lead.get("address") or ""),
        "phone": str(lead.get("phone") or ""),
        "telegram_username": str(lead.get("telegram_username") or ""),
        "website": str(lead.get("website") or ""),
        "source_url": str(lead.get("source_url") or ""),
        "client_company_name": cfg.get("client_company_name", "Ваша компания"),
        "client_offer": cfg.get("client_offer", "помогаем бизнесу получать больше заявок"),
        "client_site": cfg.get("client_site", ""),
        "manager_name": cfg.get("manager_name", "Алексей"),
        "default_goal": cfg.get("default_goal", "получить короткий ответ"),
        "extra_context": extra_context,
    }
    text = _safe_format(cfg.get("default_template", ""), values).strip()
    if extra_context:
        text += f"\n\nКонтекст: {extra_context.strip()}"
    return text.strip()


async def llm_draft(lead: dict[str, Any], extra_context: str = "") -> str | None:
    if not (settings.llm_base_url and settings.llm_api_key and settings.llm_model):
        return None

    cfg = get_settings()
    user_prompt = f"""
Сгенерируй одно короткое первое B2B-сообщение для Telegram.

Компания получателя: {lead.get('organization') or ''}
Контакт: {lead.get('contact_name') or ''}
Ниша: {lead.get('niche') or ''}
Регион: {lead.get('region') or ''}
Город: {lead.get('city') or ''}
Район: {lead.get('district') or ''}
Сайт получателя: {lead.get('website') or ''}
Источник: {lead.get('source_url') or ''}

Компания отправителя: {cfg.get('client_company_name', '')}
Предложение отправителя: {cfg.get('client_offer', '')}
Сайт отправителя: {cfg.get('client_site', '')}
Менеджер: {cfg.get('manager_name', '')}
Цель: {cfg.get('default_goal', '')}
Дополнительный контекст: {extra_context}

Верни только текст сообщения без markdown.
""".strip()

    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
    }
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        text = data["choices"][0]["message"]["content"]
        return str(text).strip()
    except Exception:
        return None


async def generate_draft(lead: dict[str, Any], extra_context: str = "") -> str:
    generated = await llm_draft(lead, extra_context)
    if generated:
        return generated
    return rule_based_draft(lead, extra_context)


def preview_html(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")
