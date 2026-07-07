from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SECRET_FILE = ROOT_DIR / "config" / "secrets.env"

secret_file = Path(os.getenv("LIDRAFLOW_SECRET_FILE", DEFAULT_SECRET_FILE))
if secret_file.exists():
    load_dotenv(secret_file)
else:
    load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "LidraFlow")
    app_tagline: str = os.getenv("APP_TAGLINE", "Omnichannel AI SDR for local B2B")
    database_path: str = os.getenv("DATABASE_PATH", str(ROOT_DIR / "data" / "lidraflow.sqlite3"))

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_bot_id: str = os.getenv("TELEGRAM_BOT_ID", "")

    frontend_api_key: str = os.getenv("FRONTEND_API_KEY", "dev-local-key")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    admin_user: str = os.getenv("ADMIN_USER", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change-me-now")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

    auth_allow_registration: bool = _bool("AUTH_ALLOW_REGISTRATION", True)
    auth_debug_reset_tokens: bool = _bool("AUTH_DEBUG_RESET_TOKENS", True)

    enable_bot_polling: bool = _bool("ENABLE_BOT_POLLING", True)
    demo_mode: bool = _bool("DEMO_MODE", False)
    allow_manual_first_contact: bool = _bool("ALLOW_MANUAL_FIRST_CONTACT", False)

    maps_provider: str = os.getenv("MAPS_PROVIDER", "openstreetmap_overpass")
    yandex_maps_api_key: str = os.getenv("YANDEX_MAPS_API_KEY", "")
    yandex_maps_endpoint: str = os.getenv("YANDEX_MAPS_ENDPOINT", "https://search-maps.yandex.ru/v1/")
    osm_overpass_endpoint: str = os.getenv("OSM_OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter")
    osm_nominatim_endpoint: str = os.getenv("OSM_NOMINATIM_ENDPOINT", "https://nominatim.openstreetmap.org/search")
    max_discovery_limit: int = int(os.getenv("MAX_DISCOVERY_LIMIT", "50"))

    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    llm_model: str = os.getenv("LLM_MODEL", "")

    @property
    def bot_is_configured(self) -> bool:
        token = (self.telegram_bot_token or "").strip()
        return bool(token and "PASTE_" not in token and ":" in token)


settings = Settings()
