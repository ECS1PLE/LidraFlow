"use server";

import { redirect } from "next/navigation";
import { apiFetch } from "./api";
import { clearSession, getBackendSessionToken, setSession } from "./auth";
import { field, messagePath } from "./utils";

type AuthUser = {
  id: number;
  email: string;
  username: string;
  full_name: string;
  name?: string;
  company_name?: string;
  role: string;
};

type AuthResponse = {
  ok: boolean;
  user: AuthUser;
  token: string;
  expires_at: string;
};

type RestoreResponse = {
  ok: boolean;
  email?: string;
  demo_code?: string;
  expires_at?: string;
};

function requireField(formData: FormData, name: string, label: string) {
  const value = field(formData, name);
  if (!value) throw new Error(`Заполните поле “${label}”`);
  return value;
}

function safeNext(value: string) {
  return value && value.startsWith("/") && !value.startsWith("//") ? value : "/leads";
}

function authRedirect(path: string, message: string, level: "ok" | "warn" = "warn"): never {
  redirect(messagePath(path, message, level));
}

export async function loginAction(formData: FormData) {
  const target = safeNext(field(formData, "next") || "/leads");
  try {
    const identifier = requireField(formData, "identifier", "Email или логин");
    const password = requireField(formData, "password", "Пароль");
    const data = await apiFetch<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ identifier, password })
    });
    await setSession(data.token, data.expires_at, data.user);
  } catch (error) {
    authRedirect("/login", error instanceof Error ? error.message : "Не удалось войти");
  }
  redirect(target);
}

export async function registerAction(formData: FormData) {
  try {
    const fullName = requireField(formData, "full_name", "Имя");
    const email = requireField(formData, "email", "Почта");
    const password = requireField(formData, "password", "Пароль");
    const passwordRepeat = requireField(formData, "password_repeat", "Повтор пароля");
    if (password !== passwordRepeat) throw new Error("Пароли не совпадают");
    if (password.length < 8) throw new Error("Пароль должен быть не короче 8 символов");

    const data = await apiFetch<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email,
        full_name: fullName,
        company_name: field(formData, "company_name"),
        username: field(formData, "username"),
        password
      })
    });
    await setSession(data.token, data.expires_at, data.user);
  } catch (error) {
    authRedirect("/register", error instanceof Error ? error.message : "Регистрация не выполнена");
  }
  redirect(messagePath("/leads", "Аккаунт создан", "ok"));
}

export async function forgotPasswordAction(formData: FormData) {
  let target = "/restore";
  const identifier = field(formData, "identifier");
  try {
    if (!identifier) throw new Error("Укажите email или логин");
    const data = await apiFetch<RestoreResponse>("/api/auth/forgot", {
      method: "POST",
      body: JSON.stringify({ identifier })
    });
    const params = new URLSearchParams({
      identifier,
      msg: "Код восстановления создан. В MVP он показывается на этой странице; для продакшена подключи SMTP/почтовый сервис.",
      level: "ok"
    });
    if (data.demo_code) params.set("code", data.demo_code);
    target = `/restore?${params.toString()}`;
  } catch (error) {
    authRedirect("/restore", error instanceof Error ? error.message : "Не удалось создать код восстановления");
  }
  redirect(target);
}

export async function resetPasswordAction(formData: FormData) {
  const identifier = field(formData, "identifier");
  const code = field(formData, "code");
  try {
    const password = requireField(formData, "password", "Новый пароль");
    const passwordRepeat = requireField(formData, "password_repeat", "Повтор пароля");
    if (!identifier || !code) throw new Error("Не хватает email/логина или кода восстановления");
    if (password !== passwordRepeat) throw new Error("Пароли не совпадают");
    if (password.length < 8) throw new Error("Пароль должен быть не короче 8 символов");

    const data = await apiFetch<AuthResponse>("/api/auth/reset", {
      method: "POST",
      body: JSON.stringify({ identifier, code, password })
    });
    await setSession(data.token, data.expires_at, data.user);
  } catch (error) {
    const params = new URLSearchParams({
      identifier,
      code,
      msg: error instanceof Error ? error.message : "Пароль не обновлён",
      level: "warn"
    });
    redirect(`/restore?${params.toString()}`);
  }
  redirect(messagePath("/leads", "Пароль обновлён", "ok"));
}

export async function logoutAction() {
  const backendToken = await getBackendSessionToken();
  if (backendToken) {
    try {
      await apiFetch("/api/auth/logout", {
        method: "POST",
        headers: { "X-LidraFlow-Session": backendToken }
      });
    } catch {
    }
  }
  await clearSession();
  redirect(messagePath("/login", "Вы вышли из аккаунта", "ok"));
}
