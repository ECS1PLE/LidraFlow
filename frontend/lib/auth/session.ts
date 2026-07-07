import crypto from "node:crypto";

export const SESSION_COOKIE = "lidraflow_session";

export type SessionPayload = {
  sub: string;
  email: string;
  name: string;
  role: string;
  backend_token: string;
  exp: number;
};

function authSecret() {
  return process.env.LIDRAFLOW_AUTH_SECRET || process.env.AUTH_SECRET || process.env.LIDRAFLOW_API_KEY || "dev-auth-secret-change-me";
}

function base64url(value: string | Buffer) {
  return Buffer.from(value).toString("base64url");
}

function sign(body: string) {
  return crypto.createHmac("sha256", authSecret()).update(body).digest("base64url");
}

export function createSessionToken(payload: Omit<SessionPayload, "exp">, ttlSeconds = 60 * 60 * 24 * 14) {
  const body = base64url(JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + ttlSeconds }));
  return `${body}.${sign(body)}`;
}

export function verifySessionToken(token: string | undefined | null): SessionPayload | null {
  if (!token || !token.includes(".")) return null;
  const [body, signature] = token.split(".");
  if (!body || !signature) return null;
  const expected = sign(body);
  const a = Buffer.from(signature);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try {
    const payload = JSON.parse(Buffer.from(body, "base64url").toString("utf8")) as SessionPayload;
    if (!payload.exp || payload.exp < Math.floor(Date.now() / 1000)) return null;
    if (!payload.backend_token) return null;
    return payload;
  } catch {
    return null;
  }
}
