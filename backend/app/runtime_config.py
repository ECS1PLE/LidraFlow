from __future__ import annotations

from typing import Any

from .config import settings
from .db import get_setting, set_setting


def _bool_value(value: str | bool | None, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _mask(value: str) -> str:
    value = str(value or "")
    if not value:
        return ""
    if len(value) <= 8:
        return "••••"
    return value[:4] + "…" + value[-4:]


def _configured(value: str, *, telegram: bool = False) -> bool:
    value = str(value or "").strip()
    if not value or "PASTE_" in value:
        return False
    if telegram and ":" not in value:
        return False
    return True


YANDEX_ORG_SEARCH_ENDPOINT = "https://search-maps.yandex.ru/v1/"
OSM_OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"
OSM_NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"


def _normalize_yandex_endpoint(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return YANDEX_ORG_SEARCH_ENDPOINT
    lower = text.lower()
    if "api-maps.yandex" in lower or lower.rstrip("/").endswith("/v3"):
        return YANDEX_ORG_SEARCH_ENDPOINT
    if not text.startswith(("http://", "https://")):
        return "https://" + text.strip("/") + "/"
    return text


def get_telegram_bot_token() -> str:
    return get_setting("telegram_bot_token") or settings.telegram_bot_token


def get_telegram_bot_id() -> str:
    return get_setting("telegram_bot_id") or settings.telegram_bot_id


def telegram_bot_is_configured() -> bool:
    return _configured(get_telegram_bot_token(), telegram=True)


def is_bot_polling_enabled() -> bool:
    return _bool_value(get_setting("enable_bot_polling"), settings.enable_bot_polling)


def is_demo_mode() -> bool:
    return _bool_value(get_setting("demo_mode"), settings.demo_mode)


def is_manual_first_contact_allowed() -> bool:
    return _bool_value(get_setting("allow_manual_first_contact"), settings.allow_manual_first_contact)


def get_maps_provider() -> str:
    provider = (get_setting("maps_provider", settings.maps_provider) or "openstreetmap_overpass").strip().lower()
    if provider in {"osm", "osm_overpass"}:
        return "openstreetmap_overpass"
    return provider


def get_yandex_maps_api_key() -> str:
    return get_setting("yandex_maps_api_key") or settings.yandex_maps_api_key


def get_yandex_maps_endpoint() -> str:
    return _normalize_yandex_endpoint(get_setting("yandex_maps_endpoint", settings.yandex_maps_endpoint) or settings.yandex_maps_endpoint)


def get_osm_overpass_endpoint() -> str:
    return get_setting("osm_overpass_endpoint", settings.osm_overpass_endpoint) or OSM_OVERPASS_ENDPOINT


def get_osm_nominatim_endpoint() -> str:
    return get_setting("osm_nominatim_endpoint", settings.osm_nominatim_endpoint) or OSM_NOMINATIM_ENDPOINT


def get_whatsapp_access_token() -> str:
    return get_setting("whatsapp_access_token")


def get_whatsapp_phone_number_id() -> str:
    return get_setting("whatsapp_phone_number_id")


def get_whatsapp_business_account_id() -> str:
    return get_setting("whatsapp_business_account_id")


def get_whatsapp_api_base_url() -> str:
    return get_setting("whatsapp_api_base_url", "https://graph.facebook.com") or "https://graph.facebook.com"


def get_whatsapp_api_version() -> str:
    return get_setting("whatsapp_api_version", "v23.0") or "v23.0"


def get_whatsapp_default_template() -> str:
    return get_setting("whatsapp_default_template")


def get_whatsapp_default_language() -> str:
    return get_setting("whatsapp_default_language", "ru") or "ru"


def whatsapp_is_configured() -> bool:
    return _configured(get_whatsapp_access_token()) and bool(get_whatsapp_phone_number_id())


def get_max_bot_token() -> str:
    return get_setting("max_bot_token")


def get_max_bot_id() -> str:
    return get_setting("max_bot_id")


def get_max_api_base_url() -> str:
    return get_setting("max_api_base_url", "https://platform-api2.max.ru") or "https://platform-api2.max.ru"


def max_is_configured() -> bool:
    return _configured(get_max_bot_token())


def get_vk_community_token() -> str:
    return get_setting("vk_community_token")


def get_vk_group_id() -> str:
    return get_setting("vk_group_id")


def get_vk_confirmation_code() -> str:
    return get_setting("vk_confirmation_code")


def get_vk_secret_key() -> str:
    return get_setting("vk_secret_key")


def get_vk_api_base_url() -> str:
    return get_setting("vk_api_base_url", "https://api.vk.com/method") or "https://api.vk.com/method"


def get_vk_api_version() -> str:
    return get_setting("vk_api_version", "5.199") or "5.199"


def vk_is_configured() -> bool:
    return _configured(get_vk_community_token()) and bool(get_vk_group_id())


def get_broadcast_rate_limit_ms() -> int:
    try:
        return max(0, int(get_setting("broadcast_rate_limit_ms", "800") or "800"))
    except ValueError:
        return 800


def get_broadcast_channel_order() -> list[str]:
    raw = get_setting("broadcast_default_channel_order", "whatsapp,telegram,max,vk")
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    return [item for item in values if item in {"telegram", "whatsapp", "max", "vk"}] or ["whatsapp", "telegram", "max", "vk"]


def save_integration_settings(payload: dict[str, Any]) -> dict[str, Any]:
    bool_keys = {"enable_bot_polling", "demo_mode", "allow_manual_first_contact"}
    secret_keys = {
        "telegram_bot_token",
        "yandex_maps_api_key",
        "whatsapp_access_token",
        "max_bot_token",
        "vk_community_token",
    }
    allowed = {
        "telegram_bot_token",
        "telegram_bot_id",
        "enable_bot_polling",
        "demo_mode",
        "allow_manual_first_contact",
        "maps_provider",
        "yandex_maps_api_key",
        "yandex_maps_endpoint",
        "osm_overpass_endpoint",
        "osm_nominatim_endpoint",
        "whatsapp_access_token",
        "whatsapp_phone_number_id",
        "whatsapp_business_account_id",
        "whatsapp_api_base_url",
        "whatsapp_api_version",
        "whatsapp_default_template",
        "whatsapp_default_language",
        "whatsapp_verify_token",
        "max_bot_token",
        "max_bot_id",
        "max_api_base_url",
        "vk_community_token",
        "vk_group_id",
        "vk_confirmation_code",
        "vk_secret_key",
        "vk_api_base_url",
        "vk_api_version",
        "broadcast_rate_limit_ms",
        "broadcast_default_channel_order",
    }
    for key, value in payload.items():
        if key not in allowed:
            continue
        if key in bool_keys:
            set_setting(key, "true" if _bool_value(value) else "false")
            continue
        text = str(value or "").strip()
        if key in secret_keys and not text:
            continue
        if key == "yandex_maps_endpoint":
            text = _normalize_yandex_endpoint(text)
        if key in {"osm_overpass_endpoint", "osm_nominatim_endpoint"} and not text:
            text = OSM_OVERPASS_ENDPOINT if key == "osm_overpass_endpoint" else OSM_NOMINATIM_ENDPOINT
        set_setting(key, text)
    return integration_status()


def integration_status() -> dict[str, Any]:
    return {
        "telegram_bot_configured": telegram_bot_is_configured(),
        "telegram_bot_token_masked": _mask(get_telegram_bot_token()),
        "telegram_bot_id": get_telegram_bot_id(),
        "enable_bot_polling": is_bot_polling_enabled(),
        "demo_mode": is_demo_mode(),
        "allow_manual_first_contact": is_manual_first_contact_allowed(),
        "maps_provider": get_maps_provider(),
        "osm_overpass_endpoint": get_osm_overpass_endpoint(),
        "osm_nominatim_endpoint": get_osm_nominatim_endpoint(),
        "osm_maps_configured": True,
        "yandex_maps_configured": _configured(get_yandex_maps_api_key()),
        "yandex_maps_api_key_masked": _mask(get_yandex_maps_api_key()),
        "yandex_maps_endpoint": get_yandex_maps_endpoint(),
        "whatsapp_configured": whatsapp_is_configured(),
        "whatsapp_access_token_masked": _mask(get_whatsapp_access_token()),
        "whatsapp_phone_number_id": get_whatsapp_phone_number_id(),
        "whatsapp_business_account_id": get_whatsapp_business_account_id(),
        "whatsapp_api_base_url": get_whatsapp_api_base_url(),
        "whatsapp_api_version": get_whatsapp_api_version(),
        "whatsapp_default_template": get_whatsapp_default_template(),
        "whatsapp_default_language": get_whatsapp_default_language(),
        "whatsapp_verify_token": get_setting("whatsapp_verify_token"),
        "max_configured": max_is_configured(),
        "max_bot_token_masked": _mask(get_max_bot_token()),
        "max_bot_id": get_max_bot_id(),
        "max_api_base_url": get_max_api_base_url(),
        "vk_configured": vk_is_configured(),
        "vk_community_token_masked": _mask(get_vk_community_token()),
        "vk_group_id": get_vk_group_id(),
        "vk_confirmation_code": get_vk_confirmation_code(),
        "vk_secret_key_masked": _mask(get_vk_secret_key()),
        "vk_api_base_url": get_vk_api_base_url(),
        "vk_api_version": get_vk_api_version(),
        "broadcast_rate_limit_ms": get_broadcast_rate_limit_ms(),
        "broadcast_default_channel_order": ",".join(get_broadcast_channel_order()),
    }
