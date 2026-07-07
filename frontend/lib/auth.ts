import "server-only";

import { cookies } from "next/headers";
import { createSessionToken, SESSION_COOKIE, verifySessionToken, type SessionPayload } from "./auth/session";

export async function getSessionCookie() {
  return cookies().get(SESSION_COOKIE)?.value ?? "";
}

export async function getCurrentSession(): Promise<SessionPayload | null> {
  return verifySessionToken(await getSessionCookie());
}

export async function getBackendSessionToken() {
  return (await getCurrentSession())?.backend_token ?? "";
}

export async function setSession(
  backendToken: string,
  expiresAt: string | undefined,
  user: { id: number; email: string; username?: string; full_name?: string; name?: string; role?: string }
) {
  const expires = expiresAt ? new Date(expiresAt) : undefined;
  const ttlSeconds = expires ? Math.max(60, Math.floor((expires.getTime() - Date.now()) / 1000)) : 60 * 60 * 24 * 14;
  const token = createSessionToken(
    {
      sub: String(user.id),
      email: user.email,
      name: user.full_name || user.name || user.username || user.email,
      role: user.role || "manager",
      backend_token: backendToken
    },
    ttlSeconds
  );

  cookies().set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.AUTH_COOKIE_SECURE === "true",
    path: "/",
    expires
  });
}

export async function clearSession() {
  cookies().delete(SESSION_COOKIE);
}
