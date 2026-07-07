from __future__ import annotations

import asyncio
import logging
import secrets
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from .ai import generate_draft
from .auth_service import (
    authenticate_user,
    create_password_reset,
    create_session,
    create_user,
    ensure_default_admin,
    get_user_by_session,
    reset_password,
    revoke_session,
)
from .channel_service import CHANNEL_LABELS, SUPPORTED_CHANNELS, available_channels, pick_channel, send_channel_message, test_channel_connection
from .config import settings
from .db import (
    add_message,
    create_lead,
    dashboard_stats,
    delete_lead,
    get_lead,
    get_setting,
    get_settings,
    import_leads_csv,
    init_db,
    list_campaign_runs,
    list_leads,
    list_messages,
    record_campaign_run,
    set_setting,
    update_lead,
)
from .maps_service import discover_leads, test_maps_connection
from .runtime_config import (
    get_broadcast_rate_limit_ms,
    get_vk_confirmation_code,
    integration_status,
    is_demo_mode,
    is_manual_first_contact_allowed,
    save_integration_settings,
    telegram_bot_is_configured,
)
from .telegram_service import polling_loop
from .webhook_service import handle_max_webhook, handle_vk_webhook, handle_whatsapp_webhook

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-LidraFlow-Key", auto_error=False)
session_header = APIKeyHeader(name="X-LidraFlow-Session", auto_error=False)

STATUS_LABELS = {
    "new": "Новый",
    "drafted": "Есть черновик",
    "contacted": "Написали",
    "replied": "Ответил",
    "qualified": "Квалифицирован",
    "closed": "Закрыт",
}

CONSENT_LABELS = {
    "pending": "Нет согласия / только черновик",
    "opted_in": "Можно отвечать",
    "opted_out": "Не писать",
}


def require_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    expected = settings.frontend_api_key or "dev-local-key"
    if not api_key or not secrets.compare_digest(api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return api_key


def require_user_session(
    _api_key: str = Depends(require_api_key),
    session_token: str | None = Depends(session_header),
) -> dict[str, Any]:
    user = get_user_by_session(session_token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия не найдена или истекла")
    return user


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ensure_default_admin()
    stop_event = asyncio.Event()
    task = asyncio.create_task(polling_loop(stop_event))
    yield
    stop_event.set()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginPayload(BaseModel):
    identifier: str = Field(default="", max_length=180)
    password: str = Field(default="", max_length=200)


class RegisterPayload(BaseModel):
    email: str = Field(default="", max_length=180)
    full_name: str = Field(default="", max_length=120)
    company_name: str = Field(default="", max_length=180)
    username: str = Field(default="", max_length=80)
    password: str = Field(default="", max_length=200)


class ForgotPasswordPayload(BaseModel):
    identifier: str = Field(default="", max_length=180)


class ResetPasswordPayload(BaseModel):
    identifier: str = Field(default="", max_length=180)
    code: str = Field(default="", max_length=32)
    password: str = Field(default="", max_length=200)


class LeadPayload(BaseModel):
    organization: str = Field(default="", max_length=250)
    contact_name: str = ""
    niche: str = ""
    region: str = ""
    city: str = ""
    district: str = ""
    address: str = ""
    latitude: float | None = None
    longitude: float | None = None
    phone: str = ""
    telegram_username: str = ""
    telegram_chat_id: str = ""
    whatsapp_phone: str = ""
    max_user_id: str = ""
    max_chat_id: str = ""
    vk_user_id: str = ""
    vk_peer_id: str = ""
    website: str = ""
    source_url: str = ""
    preferred_channel: str = "auto"
    notes: str = ""


class LeadPatchPayload(LeadPayload):
    status: str | None = None
    consent_status: str | None = None


class StatusPayload(BaseModel):
    status: str
    consent_status: str


class TextPayload(BaseModel):
    body: str = ""
    channel: str = "auto"
    whatsapp_template_name: str = ""
    whatsapp_language: str = ""


class DraftPayload(BaseModel):
    extra_context: str = ""


class SettingsPayload(BaseModel):
    workspace_name: str = ""
    client_company_name: str = ""
    client_offer: str = ""
    client_site: str = ""
    manager_name: str = ""
    default_goal: str = ""
    default_template: str = ""
    bot_welcome: str = ""
    bot_ack: str = ""
    bot_stop: str = ""


class IntegrationSettingsPayload(BaseModel):
    telegram_bot_token: str = ""
    telegram_bot_id: str = ""
    enable_bot_polling: bool = True
    demo_mode: bool = False
    allow_manual_first_contact: bool = False
    maps_provider: str = "openstreetmap_overpass"
    yandex_maps_api_key: str = ""
    yandex_maps_endpoint: str = "https://search-maps.yandex.ru/v1/"
    osm_overpass_endpoint: str = "https://overpass-api.de/api/interpreter"
    osm_nominatim_endpoint: str = "https://nominatim.openstreetmap.org/search"
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_business_account_id: str = ""
    whatsapp_api_base_url: str = "https://graph.facebook.com"
    whatsapp_api_version: str = "v23.0"
    whatsapp_default_template: str = ""
    whatsapp_default_language: str = "ru"
    whatsapp_verify_token: str = ""
    max_bot_token: str = ""
    max_bot_id: str = ""
    max_api_base_url: str = "https://platform-api2.max.ru"
    vk_community_token: str = ""
    vk_group_id: str = ""
    vk_confirmation_code: str = ""
    vk_secret_key: str = ""
    vk_api_base_url: str = "https://api.vk.com/method"
    vk_api_version: str = "5.199"
    broadcast_rate_limit_ms: int = 800
    broadcast_default_channel_order: str = "whatsapp,telegram,max,vk"


class DiscoveryPayload(BaseModel):
    provider: str = "openstreetmap_overpass"
    query: str = Field(default="", max_length=200)
    region: str = Field(default="", max_length=120)
    city: str = Field(default="", max_length=100)
    district: str = Field(default="", max_length=120)
    latitude: float | None = None
    longitude: float | None = None
    radius_m: int = Field(default=5000, ge=250, le=50000)
    limit: int = Field(default=20, ge=1, le=50)
    require_no_site: bool = True
    require_contact: bool = True
    import_results: bool = True


class BroadcastPayload(BaseModel):
    name: str = ""
    body: str = Field(default="", max_length=4000)
    channel: str = "auto"
    status_filter: str = ""
    consent_filter: str = "opted_in"
    city_filter: str = ""
    region_filter: str = ""
    district_filter: str = ""
    niche_filter: str = ""
    max_recipients: int = Field(default=50, ge=1, le=500)
    dry_run: bool = True
    whatsapp_template_name: str = ""
    whatsapp_language: str = ""


def _decorate_lead(lead: dict[str, Any]) -> dict[str, Any]:
    lead = dict(lead)
    lead["available_channels"] = available_channels(lead)
    return lead


def lead_with_messages(lead_id: int) -> dict[str, Any]:
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"lead": _decorate_lead(lead), "messages": list_messages(lead_id)}


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "app": settings.app_name,
        "bot_configured": telegram_bot_is_configured(),
        "demo_mode": is_demo_mode(),
    }


@app.post("/api/auth/login", dependencies=[Depends(require_api_key)])
async def api_auth_login(payload: LoginPayload, request: Request) -> dict[str, Any]:
    user = authenticate_user(payload.identifier, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email/логин или пароль")
    session = create_session(int(user["id"]), request.headers.get("user-agent", ""), _client_ip(request))
    return {"ok": True, "user": user, "token": session["token"], "expires_at": session["expires_at"]}


@app.post("/api/auth/register", dependencies=[Depends(require_api_key)])
async def api_auth_register(payload: RegisterPayload, request: Request) -> dict[str, Any]:
    try:
        user = create_user(
            payload.email,
            payload.password,
            full_name=payload.full_name,
            username=payload.username,
            company_name=payload.company_name,
        )
        session = create_session(int(user["id"]), request.headers.get("user-agent", ""), _client_ip(request))
        return {"ok": True, "user": user, "token": session["token"], "expires_at": session["expires_at"]}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/auth/me", dependencies=[Depends(require_api_key)])
async def api_auth_me(session_token: str | None = Depends(session_header)) -> dict[str, Any]:
    user = get_user_by_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Сессия не найдена или истекла")
    return {"ok": True, "user": user}


@app.post("/api/auth/logout", dependencies=[Depends(require_api_key)])
async def api_auth_logout(session_token: str | None = Depends(session_header)) -> dict[str, Any]:
    revoke_session(session_token or "")
    return {"ok": True}


@app.post("/api/auth/forgot", dependencies=[Depends(require_api_key)])
async def api_auth_forgot_password(payload: ForgotPasswordPayload) -> dict[str, Any]:
    data = create_password_reset(payload.identifier)
    return {
        "ok": True,
        "message": "Если аккаунт существует, код восстановления создан.",
        "demo_code": data.get("demo_code", ""),
        "expires_at": data.get("expires_at", ""),
        "email": data.get("email", ""),
    }


@app.post("/api/auth/reset", dependencies=[Depends(require_api_key)])
async def api_auth_reset_password(payload: ResetPasswordPayload, request: Request) -> dict[str, Any]:
    try:
        user = reset_password(payload.identifier, payload.code, payload.password)
        session = create_session(int(user["id"]), request.headers.get("user-agent", ""), _client_ip(request))
        return {"ok": True, "user": user, "token": session["token"], "expires_at": session["expires_at"]}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/meta", dependencies=[Depends(require_user_session)])
async def meta() -> dict[str, Any]:
    return {
        "app_name": settings.app_name,
        "tagline": settings.app_tagline,
        "bot_configured": telegram_bot_is_configured(),
        "demo_mode": is_demo_mode(),
        "allow_manual_first_contact": is_manual_first_contact_allowed(),
        "status_labels": STATUS_LABELS,
        "consent_labels": CONSENT_LABELS,
        "channel_labels": CHANNEL_LABELS,
        "stats": dashboard_stats(),
    }


@app.get("/api/leads", dependencies=[Depends(require_user_session)])
async def api_list_leads(
    q: str = "",
    status_filter: str = "",
    consent_filter: str = "",
    city_filter: str = "",
    region_filter: str = "",
    district_filter: str = "",
    niche_filter: str = "",
    channel_filter: str = "",
) -> dict[str, Any]:
    leads = list_leads(
        q=q,
        status=status_filter,
        consent=consent_filter,
        city=city_filter,
        region=region_filter,
        district=district_filter,
        niche=niche_filter,
        channel=channel_filter,
    )
    return {
        "items": [_decorate_lead(lead) for lead in leads],
        "stats": dashboard_stats(),
        "status_labels": STATUS_LABELS,
        "consent_labels": CONSENT_LABELS,
        "channel_labels": CHANNEL_LABELS,
    }


@app.post("/api/leads", dependencies=[Depends(require_user_session)])
async def api_create_lead(payload: LeadPayload) -> dict[str, Any]:
    if not payload.organization.strip():
        raise HTTPException(status_code=422, detail="organization is required")
    lead_id = create_lead(payload.model_dump())
    return lead_with_messages(lead_id)


@app.post("/api/leads/import", dependencies=[Depends(require_user_session)])
async def api_import_leads(file: UploadFile = File(...)) -> dict[str, Any]:
    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw_bytes.decode("cp1251", errors="replace")
    count, warnings = import_leads_csv(text)
    return {"imported": count, "warnings": warnings, "stats": dashboard_stats()}


@app.get("/api/leads/{lead_id}", dependencies=[Depends(require_user_session)])
async def api_get_lead(lead_id: int) -> dict[str, Any]:
    data = lead_with_messages(lead_id)
    data["status_labels"] = STATUS_LABELS
    data["consent_labels"] = CONSENT_LABELS
    data["channel_labels"] = CHANNEL_LABELS
    return data


@app.patch("/api/leads/{lead_id}", dependencies=[Depends(require_user_session)])
async def api_update_lead(lead_id: int, payload: LeadPatchPayload) -> dict[str, Any]:
    if not get_lead(lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    update_lead(lead_id, payload.model_dump(exclude_none=True))
    return lead_with_messages(lead_id)


@app.patch("/api/leads/{lead_id}/status", dependencies=[Depends(require_user_session)])
async def api_update_status(lead_id: int, payload: StatusPayload) -> dict[str, Any]:
    if payload.status not in STATUS_LABELS:
        raise HTTPException(status_code=422, detail="Unknown lead status")
    if payload.consent_status not in CONSENT_LABELS:
        raise HTTPException(status_code=422, detail="Unknown consent status")
    if not get_lead(lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    update_lead(lead_id, {"status": payload.status, "consent_status": payload.consent_status})
    return lead_with_messages(lead_id)


@app.delete("/api/leads/{lead_id}", dependencies=[Depends(require_user_session)])
async def api_delete_lead(lead_id: int) -> dict[str, Any]:
    if not get_lead(lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    delete_lead(lead_id)
    return {"ok": True}


@app.post("/api/leads/{lead_id}/draft", dependencies=[Depends(require_user_session)])
async def api_make_draft(lead_id: int, payload: DraftPayload) -> dict[str, Any]:
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    draft = await generate_draft(lead, extra_context=payload.extra_context)
    add_message(lead_id, draft, direction="draft", channel="web", sender_name="ai")
    update_lead(lead_id, {"status": "drafted"})
    return {"draft": draft, **lead_with_messages(lead_id)}


@app.post("/api/leads/{lead_id}/send", dependencies=[Depends(require_user_session)])
async def api_send_message(lead_id: int, payload: TextPayload) -> dict[str, Any]:
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="Message body is required")
    if lead.get("consent_status") == "opted_out":
        raise HTTPException(status_code=403, detail="Контакт отказался от сообщений. Отправка заблокирована.")
    if lead.get("consent_status") != "opted_in" and not is_manual_first_contact_allowed():
        raise HTTPException(
            status_code=403,
            detail="Первая отправка заблокирована: включите ручное первое касание или отметьте согласие/основание в карточке.",
        )
    try:
        used_channel, external_message_id = await send_channel_message(
            lead,
            body,
            channel=payload.channel,
            options={"whatsapp_template_name": payload.whatsapp_template_name, "whatsapp_language": payload.whatsapp_language},
        )
        add_message(lead_id, body, direction="out", channel=used_channel, sender_name="manager", external_message_id=external_message_id)
        update_lead(lead_id, {"status": "contacted"})
        return {"channel": used_channel, "external_message_id": external_message_id, **lead_with_messages(lead_id)}
    except Exception as exc:
        logger.warning("Message send failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Не удалось отправить: {exc}") from exc


@app.post("/api/leads/{lead_id}/note", dependencies=[Depends(require_user_session)])
async def api_add_note(lead_id: int, payload: TextPayload) -> dict[str, Any]:
    if not get_lead(lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    body = payload.body.strip()
    if body:
        add_message(lead_id, body, direction="system", channel="web", sender_name="note")
    return lead_with_messages(lead_id)


@app.post("/api/discovery/search", dependencies=[Depends(require_user_session)])
async def api_discovery_search(payload: DiscoveryPayload) -> dict[str, Any]:
    if not payload.query.strip():
        raise HTTPException(status_code=422, detail="Укажите поисковый запрос")
    try:
        result = await discover_leads(payload.model_dump())
        result["stats"] = dashboard_stats()
        return result
    except Exception as exc:
        logger.warning("Discovery failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Поиск по картам не выполнен: {exc}") from exc


@app.post("/api/broadcast", dependencies=[Depends(require_user_session)])
async def api_broadcast(payload: BroadcastPayload) -> dict[str, Any]:
    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="Текст рассылки обязателен")
    channel = (payload.channel or "auto").strip().lower()
    if channel not in SUPPORTED_CHANNELS:
        raise HTTPException(status_code=422, detail="Неизвестный канал")

    filters = {
        "status": payload.status_filter,
        "consent": payload.consent_filter,
        "region": payload.region_filter,
        "city": payload.city_filter,
        "district": payload.district_filter,
        "niche": payload.niche_filter,
        "channel": channel,
    }
    candidates = list_leads(
        status=payload.status_filter,
        consent=payload.consent_filter,
        city=payload.city_filter,
        region=payload.region_filter,
        district=payload.district_filter,
        niche=payload.niche_filter,
        channel="" if channel == "auto" else channel,
        limit=1000,
    )

    recipients: list[tuple[dict[str, Any], str]] = []
    skipped: list[dict[str, str]] = []
    for lead in candidates:
        if len(recipients) >= payload.max_recipients:
            break
        organization = str(lead.get("organization") or "")
        if lead.get("consent_status") == "opted_out":
            skipped.append({"organization": organization, "reason": "opted_out"})
            continue
        if lead.get("consent_status") != "opted_in" and not is_manual_first_contact_allowed():
            skipped.append({"organization": organization, "reason": "no_opt_in"})
            continue
        try:
            used_channel = pick_channel(lead, channel)
        except Exception as exc:
            skipped.append({"organization": organization, "reason": str(exc)})
            continue
        recipients.append((lead, used_channel))

    channel_breakdown: dict[str, int] = {}
    for _, used_channel in recipients:
        channel_breakdown[used_channel] = channel_breakdown.get(used_channel, 0) + 1

    if payload.dry_run:
        campaign_id = record_campaign_run(
            payload.name or "Проверка рассылки",
            channel,
            body,
            filters,
            True,
            len(recipients),
            0,
            0,
            len(skipped),
        )
        return {
            "ok": True,
            "campaign_id": campaign_id,
            "dry_run": True,
            "eligible": len(recipients),
            "sent": 0,
            "failed": 0,
            "skipped_count": len(skipped),
            "channel_breakdown": channel_breakdown,
            "skipped": skipped[:50],
            "stats": dashboard_stats(),
        }

    sent = 0
    failures: list[dict[str, str]] = []
    rate_limit = get_broadcast_rate_limit_ms() / 1000
    for lead, used_channel in recipients:
        try:
            _, external_message_id = await send_channel_message(
                lead,
                body,
                channel=used_channel,
                options={"whatsapp_template_name": payload.whatsapp_template_name, "whatsapp_language": payload.whatsapp_language},
            )
            add_message(int(lead["id"]), body, direction="out", channel=used_channel, sender_name="broadcast", external_message_id=external_message_id)
            update_lead(int(lead["id"]), {"status": "contacted"})
            sent += 1
            if rate_limit:
                await asyncio.sleep(rate_limit)
        except Exception as exc:
            failures.append({"organization": str(lead.get("organization") or ""), "reason": str(exc)})

    campaign_id = record_campaign_run(
        payload.name or "Рассылка",
        channel,
        body,
        filters,
        False,
        len(recipients),
        sent,
        len(failures),
        len(skipped),
    )
    return {
        "ok": True,
        "campaign_id": campaign_id,
        "dry_run": False,
        "eligible": len(recipients),
        "sent": sent,
        "failed": len(failures),
        "skipped_count": len(skipped),
        "channel_breakdown": channel_breakdown,
        "failures": failures[:50],
        "skipped": skipped[:50],
        "stats": dashboard_stats(),
    }


@app.get("/api/campaigns", dependencies=[Depends(require_user_session)])
async def api_campaigns() -> dict[str, Any]:
    return {"items": list_campaign_runs()}


@app.get("/api/settings", dependencies=[Depends(require_user_session)])
async def api_get_settings() -> dict[str, Any]:
    return {"settings": get_settings()}


@app.put("/api/settings", dependencies=[Depends(require_user_session)])
async def api_save_settings(payload: SettingsPayload) -> dict[str, Any]:
    for key, value in payload.model_dump().items():
        set_setting(key, value)
    return {"settings": get_settings()}


@app.get("/api/integrations", dependencies=[Depends(require_user_session)])
async def api_get_integrations() -> dict[str, Any]:
    return {"integrations": integration_status(), "channel_labels": CHANNEL_LABELS}


@app.put("/api/integrations", dependencies=[Depends(require_user_session)])
async def api_save_integrations(payload: IntegrationSettingsPayload) -> dict[str, Any]:
    return {"integrations": save_integration_settings(payload.model_dump()), "channel_labels": CHANNEL_LABELS}


@app.post("/api/integrations/test/{channel}", dependencies=[Depends(require_user_session)])
async def api_test_channel(channel: str) -> dict[str, Any]:
    try:
        return await test_channel_connection(channel)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"{channel} не подключился: {exc}") from exc


@app.post("/api/integrations/test-maps", dependencies=[Depends(require_user_session)])
async def api_test_maps() -> dict[str, Any]:
    try:
        return await test_maps_connection()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Карты не подключились: {exc}") from exc


@app.get("/api/webhooks/whatsapp")
async def whatsapp_verify(request: Request) -> PlainTextResponse:
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    expected = get_setting("whatsapp_verify_token")
    if mode == "subscribe" and challenge and (not expected or token == expected):
        return PlainTextResponse(challenge)
    raise HTTPException(status_code=403, detail="Invalid WhatsApp verify token")


@app.post("/api/webhooks/whatsapp")
async def whatsapp_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    return handle_whatsapp_webhook(payload)


@app.post("/api/webhooks/max")
async def max_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    return handle_max_webhook(payload)


@app.post("/api/webhooks/vk", response_model=None)
async def vk_webhook(payload: dict[str, Any]) -> Any:
    result = handle_vk_webhook(payload)
    if result == "confirmation":
        return PlainTextResponse(get_vk_confirmation_code())
    return result
