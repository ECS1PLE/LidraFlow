from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from .config import settings
from .db import connect, get_setting, row_to_dict, utc_now

PBKDF2_ITERATIONS = 260_000
SESSION_DAYS = 14
RESET_MINUTES = 30


def _now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize_email(value: str) -> str:
    return str(value or "").strip().lower()


def _normalize_username(value: str, email: str = "") -> str:
    value = str(value or "").strip().lower()
    if not value and email:
        value = email.split("@", 1)[0]
    value = re.sub(r"[^a-z0-9_.-]+", "-", value).strip(".-_")
    return value[:64] or f"user_{secrets.token_hex(4)}"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, iterations_raw, salt, digest = stored_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations_raw)).hex()
        return hmac.compare_digest(candidate, digest)
    except Exception:
        return False


def _public_user(row: Any) -> dict[str, Any] | None:
    data = row_to_dict(row) if row is not None and not isinstance(row, dict) else dict(row or {})
    if not data:
        return None
    data.pop("password_hash", None)
    data["name"] = data.get("full_name") or data.get("username") or str(data.get("email", "")).split("@", 1)[0]
    return data


def ensure_default_admin() -> None:
    email_or_login = (settings.admin_user or "admin").strip()
    email = _normalize_email(email_or_login if "@" in email_or_login else f"{email_or_login}@lidraflow.local")
    username = _normalize_username(email_or_login.split("@", 1)[0], email)
    password = settings.admin_password or "change-me-now"
    now = utc_now()
    with connect() as conn:
        count = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
        if count:
            return
        conn.execute(
            """
            INSERT INTO users(email, username, full_name, company_name, password_hash, role, is_active, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?, 'owner', 1, ?, ?)
            """,
            (email, username, "Администратор", "LidraFlow", hash_password(password), now, now),
        )


def create_user(email: str, password: str, full_name: str = "", username: str = "", company_name: str = "") -> dict[str, Any]:
    if not settings.auth_allow_registration and get_setting("auth_allow_registration", "true") != "true":
        raise ValueError("Регистрация отключена")
    email = _normalize_email(email)
    if not email or "@" not in email or "." not in email.split("@", 1)[-1]:
        raise ValueError("Укажите корректный email")
    if len(password or "") < 8:
        raise ValueError("Пароль должен быть не короче 8 символов")
    username_base = _normalize_username(username, email)
    now = utc_now()
    with connect() as conn:
        if conn.execute("SELECT id FROM users WHERE lower(email) = ?", (email,)).fetchone():
            raise ValueError("Пользователь с такой почтой уже существует")
        username_candidate = username_base
        counter = 2
        while conn.execute("SELECT id FROM users WHERE lower(username) = ?", (username_candidate,)).fetchone():
            username_candidate = f"{username_base}{counter}"
            counter += 1
        cur = conn.execute(
            """
            INSERT INTO users(email, username, full_name, company_name, password_hash, role, is_active, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?, 'manager', 1, ?, ?)
            """,
            (email, username_candidate, (full_name or "").strip(), (company_name or "").strip(), hash_password(password), now, now),
        )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
        user = _public_user(row)
        if not user:
            raise ValueError("Не удалось создать пользователя")
        return user


def authenticate_user(identifier: str, password: str) -> dict[str, Any] | None:
    value = str(identifier or "").strip().lower()
    if not value or not password:
        return None
    now = utc_now()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE lower(email) = ? OR lower(username) = ? LIMIT 1",
            (value, value),
        ).fetchone()
        if not row or not int(row["is_active"] or 0):
            return None
        if not verify_password(password, row["password_hash"]):
            return None
        conn.execute("UPDATE users SET last_login_at = ?, updated_at = ? WHERE id = ?", (now, now, row["id"]))
        fresh = conn.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone()
        return _public_user(fresh)


def create_session(user_id: int, user_agent: str = "", ip_address: str = "") -> dict[str, Any]:
    token = secrets.token_urlsafe(40)
    token_hash = _sha256(token)
    now_dt = _now_dt()
    expires_at = (now_dt + timedelta(days=SESSION_DAYS)).isoformat()
    with connect() as conn:
        conn.execute("DELETE FROM user_sessions WHERE expires_at < ?", (now_dt.isoformat(),))
        conn.execute(
            """
            INSERT INTO user_sessions(token_hash, user_id, created_at, expires_at, last_seen_at, user_agent, ip_address)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (token_hash, user_id, now_dt.isoformat(), expires_at, now_dt.isoformat(), (user_agent or "")[:250], (ip_address or "")[:80]),
        )
    return {"token": token, "expires_at": expires_at}


def get_user_by_session(token: str | None) -> dict[str, Any] | None:
    token = str(token or "").strip()
    if not token:
        return None
    now = utc_now()
    token_hash = _sha256(token)
    with connect() as conn:
        row = conn.execute(
            """
            SELECT users.*
            FROM user_sessions
            JOIN users ON users.id = user_sessions.user_id
            WHERE user_sessions.token_hash = ? AND user_sessions.expires_at > ? AND users.is_active = 1
            LIMIT 1
            """,
            (token_hash, now),
        ).fetchone()
        if not row:
            return None
        conn.execute("UPDATE user_sessions SET last_seen_at = ? WHERE token_hash = ?", (now, token_hash))
        return _public_user(row)


def revoke_session(token: str | None) -> None:
    token = str(token or "").strip()
    if not token:
        return
    with connect() as conn:
        conn.execute("DELETE FROM user_sessions WHERE token_hash = ?", (_sha256(token),))


def _find_user(identifier: str) -> dict[str, Any] | None:
    value = str(identifier or "").strip().lower()
    if not value:
        return None
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE lower(email) = ? OR lower(username) = ? LIMIT 1",
            (value, value),
        ).fetchone()
        return _public_user(row)


def create_password_reset(identifier: str) -> dict[str, Any]:
    user = _find_user(identifier)
    if not user:
        return {"ok": True, "email": "", "demo_code": "", "expires_at": ""}
    code = f"{secrets.randbelow(1_000_000):06d}"
    now_dt = _now_dt()
    expires_dt = now_dt + timedelta(minutes=RESET_MINUTES)
    with connect() as conn:
        conn.execute("UPDATE password_resets SET used_at = ? WHERE user_id = ? AND used_at = ''", (now_dt.isoformat(), user["id"]))
        conn.execute(
            """
            INSERT INTO password_resets(user_id, code_hash, created_at, expires_at)
            VALUES(?, ?, ?, ?)
            """,
            (user["id"], _sha256(code), now_dt.isoformat(), expires_dt.isoformat()),
        )
    email = str(user.get("email", ""))
    masked = email[:2] + "***@" + email.split("@", 1)[1] if "@" in email else ""
    debug = settings.auth_debug_reset_tokens or get_setting("auth_debug_reset_tokens", "true") == "true"
    return {"ok": True, "email": masked, "demo_code": code if debug else "", "expires_at": expires_dt.isoformat()}


def reset_password(identifier: str, code: str, new_password: str) -> dict[str, Any]:
    if len(new_password or "") < 8:
        raise ValueError("Новый пароль должен быть не короче 8 символов")
    value = str(identifier or "").strip().lower()
    now = utc_now()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT password_resets.id AS reset_id, users.*
            FROM password_resets
            JOIN users ON users.id = password_resets.user_id
            WHERE (lower(users.email) = ? OR lower(users.username) = ?)
              AND password_resets.code_hash = ?
              AND password_resets.used_at = ''
              AND password_resets.expires_at > ?
            ORDER BY password_resets.id DESC
            LIMIT 1
            """,
            (value, value, _sha256(str(code or "").strip()), now),
        ).fetchone()
        if not row:
            raise ValueError("Неверный или просроченный код восстановления")
        conn.execute("UPDATE password_resets SET used_at = ? WHERE id = ?", (now, row["reset_id"]))
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (hash_password(new_password), now, row["id"]),
        )
        conn.execute("DELETE FROM user_sessions WHERE user_id = ?", (row["id"],))
        fresh = conn.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone()
        user = _public_user(fresh)
        if not user:
            raise ValueError("Пользователь не найден")
        return user
