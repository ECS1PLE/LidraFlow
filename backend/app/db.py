from __future__ import annotations

import csv
import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Iterable

from .config import ROOT_DIR, settings


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def db_path() -> Path:
    raw_path = (settings.database_path or "").strip()
    path = Path(raw_path) if raw_path else ROOT_DIR / "data" / "lidraflow.sqlite3"
    if not path.is_absolute():
        path = ROOT_DIR / path
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    except OSError:
        fallback = ROOT_DIR / "data" / "lidraflow.sqlite3"
        fallback.parent.mkdir(parents=True, exist_ok=True)
        return fallback


@contextmanager
def connect() -> Iterable[sqlite3.Connection]:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    finally:
        conn.close()


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    if not _column_exists(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                full_name TEXT DEFAULT '',
                company_name TEXT DEFAULT '',
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'owner',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_login_at TEXT DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

            CREATE TABLE IF NOT EXISTS user_sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                user_agent TEXT DEFAULT '',
                ip_address TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used_at TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_password_resets_user ON password_resets(user_id);

            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization TEXT NOT NULL,
                contact_name TEXT DEFAULT '',
                niche TEXT DEFAULT '',
                region TEXT DEFAULT '',
                city TEXT DEFAULT '',
                district TEXT DEFAULT '',
                address TEXT DEFAULT '',
                latitude REAL,
                longitude REAL,
                phone TEXT DEFAULT '',
                telegram_username TEXT DEFAULT '',
                telegram_chat_id TEXT DEFAULT '',
                whatsapp_phone TEXT DEFAULT '',
                max_user_id TEXT DEFAULT '',
                max_chat_id TEXT DEFAULT '',
                vk_user_id TEXT DEFAULT '',
                vk_peer_id TEXT DEFAULT '',
                website TEXT DEFAULT '',
                source_url TEXT DEFAULT '',
                maps_provider TEXT DEFAULT '',
                maps_external_id TEXT DEFAULT '',
                discovered_at TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'new',
                consent_status TEXT NOT NULL DEFAULT 'pending',
                preferred_channel TEXT DEFAULT 'auto',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_message_at TEXT DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
            CREATE INDEX IF NOT EXISTS idx_leads_consent ON leads(consent_status);
            CREATE INDEX IF NOT EXISTS idx_leads_geo ON leads(region, city, district);
            CREATE INDEX IF NOT EXISTS idx_leads_chat_id ON leads(telegram_chat_id);
            CREATE INDEX IF NOT EXISTS idx_leads_username ON leads(telegram_username);
            CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone);
            CREATE INDEX IF NOT EXISTS idx_leads_maps_external ON leads(maps_provider, maps_external_id);

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                direction TEXT NOT NULL,
                channel TEXT NOT NULL DEFAULT 'telegram',
                sender_name TEXT DEFAULT '',
                body TEXT NOT NULL,
                tg_message_id TEXT DEFAULT '',
                external_message_id TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_messages_lead_id ON messages(lead_id);
            CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

            CREATE TABLE IF NOT EXISTS campaign_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT DEFAULT '',
                channel TEXT NOT NULL DEFAULT 'auto',
                body TEXT NOT NULL,
                filters_json TEXT NOT NULL DEFAULT '{}',
                dry_run INTEGER NOT NULL DEFAULT 1,
                eligible INTEGER NOT NULL DEFAULT 0,
                sent INTEGER NOT NULL DEFAULT 0,
                failed INTEGER NOT NULL DEFAULT 0,
                skipped INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_campaign_runs_created ON campaign_runs(created_at);
            """
        )

        for column, definition in {
            "region": "TEXT DEFAULT ''",
            "district": "TEXT DEFAULT ''",
            "address": "TEXT DEFAULT ''",
            "latitude": "REAL",
            "longitude": "REAL",
            "whatsapp_phone": "TEXT DEFAULT ''",
            "max_user_id": "TEXT DEFAULT ''",
            "max_chat_id": "TEXT DEFAULT ''",
            "vk_user_id": "TEXT DEFAULT ''",
            "vk_peer_id": "TEXT DEFAULT ''",
            "preferred_channel": "TEXT DEFAULT 'auto'",
            "website": "TEXT DEFAULT ''",
            "maps_provider": "TEXT DEFAULT ''",
            "maps_external_id": "TEXT DEFAULT ''",
            "discovered_at": "TEXT DEFAULT ''",
        }.items():
            _ensure_column(conn, "leads", column, definition)
        _ensure_column(conn, "messages", "external_message_id", "TEXT DEFAULT ''")

        defaults = {
            "workspace_name": settings.app_name,
            "client_company_name": "Ваша компания",
            "client_offer": "помогаем бизнесу получать больше заявок без лишней рутины",
            "client_site": "",
            "manager_name": "Алексей",
            "default_goal": "получить короткий ответ: актуально / не актуально / кому лучше написать",
            "default_template": (
                "Здравствуйте! Я {manager_name}, представляю {client_company_name}. "
                "Увидел(а), что {organization} работает в направлении: {niche}. "
                "Мы {client_offer}. Подскажите, пожалуйста, кому у вас можно кратко описать идею?"
            ),
            "bot_welcome": (
                "Здравствуйте! Это рабочий бот LidraFlow. "
                "Ваше сообщение передано менеджеру. Если вы не хотите получать сообщения, отправьте /stop."
            ),
            "bot_stop": "Принято. Мы больше не будем писать в этот чат.",
            "bot_ack": "Спасибо! Сообщение получено, менеджер скоро увидит его в CRM.",
            "maps_provider": settings.maps_provider,
            "yandex_maps_endpoint": settings.yandex_maps_endpoint,
            "osm_overpass_endpoint": settings.osm_overpass_endpoint,
            "osm_nominatim_endpoint": settings.osm_nominatim_endpoint,
            "enable_bot_polling": "true" if settings.enable_bot_polling else "false",
            "demo_mode": "true" if settings.demo_mode else "false",
            "allow_manual_first_contact": "true" if settings.allow_manual_first_contact else "false",
            "whatsapp_api_base_url": "https://graph.facebook.com",
            "whatsapp_api_version": "v23.0",
            "whatsapp_default_language": "ru",
            "whatsapp_default_template": "",
            "max_api_base_url": "https://platform-api2.max.ru",
            "vk_api_base_url": "https://api.vk.com/method",
            "vk_api_version": "5.199",
            "broadcast_rate_limit_ms": "800",
            "broadcast_default_channel_order": "whatsapp,telegram,max,vk",
            "auth_allow_registration": "true" if settings.auth_allow_registration else "false",
            "auth_debug_reset_tokens": "true" if settings.auth_debug_reset_tokens else "false",
        }
        for key, value in defaults.items():
            conn.execute(
                "INSERT OR IGNORE INTO app_settings(key, value) VALUES(?, ?)",
                (key, value),
            )

        current_provider = conn.execute(
            "SELECT value FROM app_settings WHERE key = 'maps_provider'"
        ).fetchone()
        yandex_key = conn.execute(
            "SELECT value FROM app_settings WHERE key = 'yandex_maps_api_key'"
        ).fetchone()
        provider_value = str(current_provider["value"] if current_provider else "").strip().lower()
        yandex_key_value = str(yandex_key["value"] if yandex_key else "").strip()
        if provider_value in {"", "yandex"} and (not yandex_key_value or "PASTE_" in yandex_key_value):
            conn.execute(
                "INSERT INTO app_settings(key, value) VALUES('maps_provider', 'openstreetmap_overpass') "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value"
            )


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def get_setting(key: str, default: str = "") -> str:
    with connect() as conn:
        row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO app_settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


def _mask(value: str) -> str:
    value = str(value or "")
    if not value:
        return ""
    if len(value) <= 8:
        return "••••"
    return value[:4] + "…" + value[-4:]


def get_settings() -> dict[str, str]:
    with connect() as conn:
        rows = conn.execute("SELECT key, value FROM app_settings ORDER BY key").fetchall()
        values = {row["key"]: row["value"] for row in rows}
    for secret_key in [
        "telegram_bot_token",
        "yandex_maps_api_key",
        "whatsapp_access_token",
        "max_bot_token",
        "vk_community_token",
    ]:
        if secret_key in values:
            values[secret_key] = ""
            values[f"{secret_key}_masked"] = _mask(get_setting(secret_key))
    return values


def normalize_username(value: str | None) -> str:
    if not value:
        return ""
    value = str(value).strip()
    value = value.replace("https://t.me/", "").replace("http://t.me/", "")
    value = value.replace("t.me/", "")
    value = value.strip().lstrip("@").split("?")[0].split("/")[0]
    return value


def normalize_phone(value: str | None) -> str:
    if not value:
        return ""
    digits = re.sub(r"\D+", "", str(value))
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return digits


def _lead_fields(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    phone = str(data.get("phone", "") or "")
    whatsapp_phone = str(data.get("whatsapp_phone", "") or "")
    return {
        "organization": data.get("organization") or "Без названия",
        "contact_name": data.get("contact_name", ""),
        "niche": data.get("niche", ""),
        "region": data.get("region", ""),
        "city": data.get("city", ""),
        "district": data.get("district", ""),
        "address": data.get("address", ""),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "phone": phone,
        "telegram_username": normalize_username(data.get("telegram_username", "")),
        "telegram_chat_id": str(data.get("telegram_chat_id", "") or ""),
        "whatsapp_phone": normalize_phone(whatsapp_phone or phone),
        "max_user_id": str(data.get("max_user_id", "") or ""),
        "max_chat_id": str(data.get("max_chat_id", "") or ""),
        "vk_user_id": str(data.get("vk_user_id", "") or ""),
        "vk_peer_id": str(data.get("vk_peer_id", "") or ""),
        "website": data.get("website", ""),
        "source_url": data.get("source_url", ""),
        "maps_provider": data.get("maps_provider", ""),
        "maps_external_id": str(data.get("maps_external_id", "") or ""),
        "discovered_at": data.get("discovered_at", ""),
        "status": data.get("status", "new"),
        "consent_status": data.get("consent_status", "pending"),
        "preferred_channel": data.get("preferred_channel", "auto") or "auto",
        "notes": data.get("notes", ""),
        "created_at": data.get("created_at", now),
        "updated_at": data.get("updated_at", now),
        "last_message_at": data.get("last_message_at", ""),
    }


def create_lead(data: dict[str, Any]) -> int:
    fields = _lead_fields(data)
    keys = list(fields.keys())
    with connect() as conn:
        cur = conn.execute(
            f"INSERT INTO leads({', '.join(keys)}) VALUES({', '.join(['?'] * len(keys))})",
            [fields[k] for k in keys],
        )
        return int(cur.lastrowid)


def update_lead(lead_id: int, data: dict[str, Any]) -> None:
    allowed = set(_lead_fields({}).keys()) - {"created_at", "updated_at"}
    clean: dict[str, Any] = {k: v for k, v in data.items() if k in allowed}
    if "telegram_username" in clean:
        clean["telegram_username"] = normalize_username(clean["telegram_username"])
    if "whatsapp_phone" in clean:
        clean["whatsapp_phone"] = normalize_phone(clean["whatsapp_phone"])
    if not clean:
        return
    clean["updated_at"] = utc_now()
    parts = [f"{k} = ?" for k in clean.keys()]
    values = list(clean.values()) + [lead_id]
    with connect() as conn:
        conn.execute(f"UPDATE leads SET {', '.join(parts)} WHERE id = ?", values)


def get_lead(lead_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        return row_to_dict(conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone())


def _channel_clause(channel: str) -> str:
    if channel == "telegram":
        return "COALESCE(telegram_chat_id, '') != ''"
    if channel == "whatsapp":
        return "(COALESCE(whatsapp_phone, '') != '' OR COALESCE(phone, '') != '')"
    if channel == "max":
        return "(COALESCE(max_user_id, '') != '' OR COALESCE(max_chat_id, '') != '')"
    if channel == "vk":
        return "(COALESCE(vk_peer_id, '') != '' OR COALESCE(vk_user_id, '') != '')"
    return "1 = 1"


def list_leads(
    q: str = "",
    status: str = "",
    consent: str = "",
    city: str = "",
    region: str = "",
    district: str = "",
    niche: str = "",
    channel: str = "",
    limit: int = 250,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if q:
        clauses.append(
            "(organization LIKE ? OR contact_name LIKE ? OR niche LIKE ? OR region LIKE ? OR city LIKE ? OR district LIKE ? OR address LIKE ? OR phone LIKE ? OR telegram_username LIKE ? OR website LIKE ?)"
        )
        like = f"%{q}%"
        params.extend([like] * 10)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if consent:
        clauses.append("consent_status = ?")
        params.append(consent)
    if city:
        clauses.append("city LIKE ?")
        params.append(f"%{city}%")
    if region:
        clauses.append("region LIKE ?")
        params.append(f"%{region}%")
    if district:
        clauses.append("district LIKE ?")
        params.append(f"%{district}%")
    if niche:
        clauses.append("niche LIKE ?")
        params.append(f"%{niche}%")
    if channel and channel != "auto":
        clauses.append(_channel_clause(channel))

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    sql = f"""
        SELECT leads.*,
               (SELECT body FROM messages WHERE messages.lead_id = leads.id ORDER BY id DESC LIMIT 1) AS last_message,
               (SELECT COUNT(*) FROM messages WHERE messages.lead_id = leads.id) AS message_count
        FROM leads
        {where}
        ORDER BY COALESCE(NULLIF(last_message_at, ''), updated_at) DESC, id DESC
        LIMIT ?
    """
    params.append(max(1, min(int(limit), 1000)))
    with connect() as conn:
        return [row_to_dict(r) for r in conn.execute(sql, params).fetchall()]  # type: ignore[list-item]


def _find_existing_lead(conn: sqlite3.Connection, data: dict[str, Any]) -> sqlite3.Row | None:
    provider = str(data.get("maps_provider") or "")
    external_id = str(data.get("maps_external_id") or "")
    if provider and external_id:
        row = conn.execute(
            "SELECT * FROM leads WHERE maps_provider = ? AND maps_external_id = ? LIMIT 1",
            (provider, external_id),
        ).fetchone()
        if row:
            return row

    phone = normalize_phone(data.get("phone") or data.get("whatsapp_phone") or "")
    if phone:
        row = conn.execute(
            "SELECT * FROM leads WHERE REPLACE(REPLACE(REPLACE(REPLACE(phone, '+', ''), ' ', ''), '-', ''), '(', '') LIKE ? OR whatsapp_phone = ? ORDER BY id DESC LIMIT 1",
            (f"%{phone[-10:]}", phone),
        ).fetchone()
        if row:
            return row

    username = normalize_username(data.get("telegram_username", ""))
    if username:
        row = conn.execute(
            "SELECT * FROM leads WHERE telegram_username = ? ORDER BY id DESC LIMIT 1",
            (username,),
        ).fetchone()
        if row:
            return row

    org = str(data.get("organization") or "").strip()
    city = str(data.get("city") or "").strip()
    address = str(data.get("address") or "").strip()
    if org and (city or address):
        row = conn.execute(
            "SELECT * FROM leads WHERE organization = ? AND (city = ? OR address = ?) ORDER BY id DESC LIMIT 1",
            (org, city, address),
        ).fetchone()
        if row:
            return row
    return None


def create_or_update_discovered_lead(data: dict[str, Any]) -> tuple[int, bool]:
    now = utc_now()
    data = {**data, "discovered_at": data.get("discovered_at") or now}
    with connect() as conn:
        existing = _find_existing_lead(conn, data)
        if existing:
            lead_id = int(existing["id"])
            update: dict[str, Any] = {}
            for key in [
                "contact_name",
                "niche",
                "region",
                "city",
                "district",
                "address",
                "latitude",
                "longitude",
                "phone",
                "telegram_username",
                "telegram_chat_id",
                "whatsapp_phone",
                "max_user_id",
                "max_chat_id",
                "vk_user_id",
                "vk_peer_id",
                "website",
                "source_url",
                "maps_provider",
                "maps_external_id",
                "discovered_at",
            ]:
                incoming = data.get(key)
                current = existing[key] if key in existing.keys() else ""
                if incoming not in (None, "") and current in (None, ""):
                    update[key] = incoming
            incoming_notes = str(data.get("notes") or "").strip()
            current_notes = str(existing["notes"] or "").strip()
            if incoming_notes and incoming_notes not in current_notes:
                update["notes"] = (current_notes + "\n\n" + incoming_notes).strip()
            if update:
                update["updated_at"] = now
                parts = [f"{key} = ?" for key in update.keys()]
                conn.execute(f"UPDATE leads SET {', '.join(parts)} WHERE id = ?", list(update.values()) + [lead_id])
            return lead_id, False

        fields = _lead_fields({**data, "created_at": now, "updated_at": now, "consent_status": "pending", "status": "new"})
        keys = list(fields.keys())
        cur = conn.execute(
            f"INSERT INTO leads({', '.join(keys)}) VALUES({', '.join(['?'] * len(keys))})",
            [fields[k] for k in keys],
        )
        return int(cur.lastrowid), True


def get_or_create_lead_from_channel(
    channel: str,
    external_id: str,
    display_name: str = "",
    username: str = "",
    phone: str = "",
    chat_id: str = "",
) -> int:
    channel = channel.lower().strip()
    external_id = str(external_id or chat_id or phone or username).strip()
    now = utc_now()
    field_by_channel = {
        "telegram": "telegram_chat_id",
        "whatsapp": "whatsapp_phone",
        "max": "max_user_id",
        "vk": "vk_peer_id",
    }
    field = field_by_channel.get(channel, "telegram_chat_id")
    value = chat_id or external_id
    if channel == "whatsapp":
        value = normalize_phone(phone or external_id)
    with connect() as conn:
        row = conn.execute(f"SELECT * FROM leads WHERE {field} = ? ORDER BY id DESC LIMIT 1", (value,)).fetchone()
        if row:
            lead_id = int(row["id"])
            updates: dict[str, Any] = {"consent_status": "opted_in", "updated_at": now, "last_message_at": now}
            if channel == "telegram" and username and not row["telegram_username"]:
                updates["telegram_username"] = normalize_username(username)
            if channel == "whatsapp" and phone and not row["phone"]:
                updates["phone"] = phone
            parts = [f"{k} = ?" for k in updates.keys()]
            conn.execute(f"UPDATE leads SET {', '.join(parts)} WHERE id = ?", list(updates.values()) + [lead_id])
            return lead_id
        organization = display_name or username or phone or f"{channel.upper()} contact {external_id}"
        data = {
            "organization": organization,
            "contact_name": display_name,
            "status": "replied",
            "consent_status": "opted_in",
            "created_at": now,
            "updated_at": now,
            "last_message_at": now,
            "notes": f"Создано автоматически после входящего сообщения в {channel}.",
        }
        if channel == "telegram":
            data.update({"telegram_chat_id": chat_id or external_id, "telegram_username": username})
        elif channel == "whatsapp":
            data.update({"whatsapp_phone": normalize_phone(phone or external_id), "phone": phone or external_id})
        elif channel == "max":
            data.update({"max_user_id": external_id, "max_chat_id": chat_id})
        elif channel == "vk":
            data.update({"vk_peer_id": chat_id or external_id, "vk_user_id": external_id})
        fields = _lead_fields(data)
        keys = list(fields.keys())
        cur = conn.execute(
            f"INSERT INTO leads({', '.join(keys)}) VALUES({', '.join(['?'] * len(keys))})",
            [fields[k] for k in keys],
        )
        return int(cur.lastrowid)


def get_or_create_lead_from_telegram(chat_id: str, username: str = "", first_name: str = "", last_name: str = "") -> int:
    full_name = " ".join(p for p in [first_name, last_name] if p).strip()
    return get_or_create_lead_from_channel("telegram", chat_id, full_name, username, chat_id=chat_id)


def add_message(
    lead_id: int,
    body: str,
    direction: str = "in",
    channel: str = "telegram",
    sender_name: str = "",
    tg_message_id: str = "",
    external_message_id: str = "",
) -> int:
    now = utc_now()
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO messages(lead_id, direction, channel, sender_name, body, tg_message_id, external_message_id, created_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (lead_id, direction, channel, sender_name, body, tg_message_id, external_message_id or tg_message_id, now),
        )
        conn.execute(
            "UPDATE leads SET last_message_at = ?, updated_at = ?, status = CASE WHEN ? = 'in' THEN 'replied' ELSE status END WHERE id = ?",
            (now, now, direction, lead_id),
        )
        return int(cur.lastrowid)


def list_messages(lead_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        return [row_to_dict(r) for r in conn.execute("SELECT * FROM messages WHERE lead_id = ? ORDER BY id ASC", (lead_id,)).fetchall()]  # type: ignore[list-item]


def delete_lead(lead_id: int) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))


def import_leads_csv(raw: str) -> tuple[int, list[str]]:
    warnings: list[str] = []
    text = raw.lstrip("\ufeff").strip()
    if not text:
        return 0, ["Файл пустой"]
    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"
    reader = csv.DictReader(StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        return 0, ["Не найдены заголовки колонок"]
    aliases = {
        "organization": {"organization", "org", "company", "name", "название", "организация", "компания"},
        "contact_name": {"contact", "contact_name", "person", "контакт", "имя", "фио"},
        "niche": {"niche", "category", "rubric", "категория", "ниша", "рубрика"},
        "region": {"region", "область", "регион", "край", "республика"},
        "city": {"city", "город"},
        "district": {"district", "район", "округ", "area"},
        "address": {"address", "адрес"},
        "phone": {"phone", "tel", "telephone", "телефон", "номер"},
        "telegram_username": {"telegram", "tg", "username", "telegram_username", "тг", "телеграм"},
        "telegram_chat_id": {"telegram_chat_id", "chat_id", "tg_chat_id", "чат_id"},
        "whatsapp_phone": {"whatsapp", "whatsapp_phone", "wa", "вацап", "ватсап"},
        "max_user_id": {"max_user_id", "max", "max_id"},
        "max_chat_id": {"max_chat_id"},
        "vk_user_id": {"vk_user_id", "vk", "vk_id"},
        "vk_peer_id": {"vk_peer_id", "peer_id"},
        "website": {"website", "site", "url_site", "сайт"},
        "source_url": {"source", "url", "link", "source_url", "источник", "ссылка"},
        "preferred_channel": {"preferred_channel", "channel", "канал"},
        "notes": {"notes", "note", "комментарий", "заметки"},
    }
    normalized_headers = {h: h.strip().lower() for h in reader.fieldnames if h}

    def value(row: dict[str, str], target: str) -> str:
        accepted = aliases[target]
        for original, normalized in normalized_headers.items():
            if normalized in accepted:
                return (row.get(original) or "").strip()
        return ""

    imported = 0
    for index, row in enumerate(reader, start=2):
        organization = value(row, "organization")
        phone = value(row, "phone")
        username = value(row, "telegram_username")
        whatsapp = value(row, "whatsapp_phone")
        if not any([organization, username, phone, whatsapp, value(row, "vk_peer_id"), value(row, "max_user_id")]):
            warnings.append(f"Строка {index}: пропущена, нет названия или контакта")
            continue
        create_lead({target: value(row, target) for target in aliases.keys()} | {"organization": organization or username or phone or whatsapp})
        imported += 1
    return imported, warnings


def record_campaign_run(
    name: str,
    channel: str,
    body: str,
    filters: dict[str, Any],
    dry_run: bool,
    eligible: int,
    sent: int,
    failed: int,
    skipped: int,
) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO campaign_runs(name, channel, body, filters_json, dry_run, eligible, sent, failed, skipped, created_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, channel, body, json.dumps(filters, ensure_ascii=False), int(dry_run), eligible, sent, failed, skipped, utc_now()),
        )
        return int(cur.lastrowid)


def list_campaign_runs(limit: int = 50) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM campaign_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [row_to_dict(r) for r in rows]  # type: ignore[list-item]


def dashboard_stats() -> dict[str, int]:
    with connect() as conn:
        rows = conn.execute("SELECT status, COUNT(*) AS c FROM leads GROUP BY status").fetchall()
        status_counts = {row["status"]: int(row["c"]) for row in rows}
        total = int(conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()["c"])
        messages = int(conn.execute("SELECT COUNT(*) AS c FROM messages").fetchone()["c"])
        opted_in = int(conn.execute("SELECT COUNT(*) AS c FROM leads WHERE consent_status = 'opted_in'").fetchone()["c"])
        discovered = int(conn.execute("SELECT COUNT(*) AS c FROM leads WHERE COALESCE(maps_provider, '') != ''").fetchone()["c"])
        telegram_ready = int(conn.execute("SELECT COUNT(*) AS c FROM leads WHERE COALESCE(telegram_chat_id, '') != ''").fetchone()["c"])
        whatsapp_ready = int(conn.execute("SELECT COUNT(*) AS c FROM leads WHERE COALESCE(whatsapp_phone, '') != '' OR COALESCE(phone, '') != ''").fetchone()["c"])
        max_ready = int(conn.execute("SELECT COUNT(*) AS c FROM leads WHERE COALESCE(max_user_id, '') != '' OR COALESCE(max_chat_id, '') != ''").fetchone()["c"])
        vk_ready = int(conn.execute("SELECT COUNT(*) AS c FROM leads WHERE COALESCE(vk_peer_id, '') != '' OR COALESCE(vk_user_id, '') != ''").fetchone()["c"])
    return {
        "total": total,
        "messages": messages,
        "opted_in": opted_in,
        "discovered": discovered,
        "telegram": telegram_ready,
        "whatsapp": whatsapp_ready,
        "max": max_ready,
        "vk": vk_ready,
        "new": int(status_counts.get("new", 0)),
        "replied": int(status_counts.get("replied", 0)),
        "qualified": int(status_counts.get("qualified", 0)),
    }
