import { NextRequest, NextResponse } from "next/server";

const SESSION_COOKIE = "lidraflow_session";
const PUBLIC_PATHS = ["/login", "/register", "/restore", "/favicon.ico", "/sample_leads.csv"];

function isPublicPath(pathname: string) {
  return PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

function authSecret() {
  return process.env.LIDRAFLOW_AUTH_SECRET || process.env.AUTH_SECRET || process.env.LIDRAFLOW_API_KEY || process.env.FRONTEND_API_KEY || "dev-auth-secret-change-me";
}

function stringToBytes(value: string) {
  return new TextEncoder().encode(value);
}

function base64urlToBytes(value: string) {
  const base64 = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  const raw = atob(base64);
  return Uint8Array.from(raw, (char) => char.charCodeAt(0));
}

function timingSafeEqual(a: Uint8Array, b: Uint8Array) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let index = 0; index < a.length; index += 1) result |= a[index] ^ b[index];
  return result === 0;
}

async function hmacSha256(body: string) {
  const key = await crypto.subtle.importKey(
    "raw",
    stringToBytes(authSecret()),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign("HMAC", key, stringToBytes(body));
  return new Uint8Array(signature);
}

async function validSession(token?: string) {
  if (!token || !token.includes(".")) return false;
  const [body, signature] = token.split(".");
  if (!body || !signature) return false;

  let incoming: Uint8Array;
  try {
    incoming = base64urlToBytes(signature);
  } catch {
    return false;
  }

  const expected = await hmacSha256(body);
  if (!timingSafeEqual(incoming, expected)) return false;

  try {
    const payload = JSON.parse(new TextDecoder().decode(base64urlToBytes(body))) as { exp?: number; backend_token?: string };
    return Boolean(payload.exp && payload.exp > Math.floor(Date.now() / 1000) && payload.backend_token);
  } catch {
    return false;
  }
}

function redirectToLogin(request: NextRequest) {
  const url = new URL("/login", request.url);
  if (request.nextUrl.pathname !== "/") {
    url.searchParams.set("next", `${request.nextUrl.pathname}${request.nextUrl.search}`);
  }
  const response = NextResponse.redirect(url);
  response.cookies.delete(SESSION_COOKIE);
  return response;
}

export async function middleware(request: NextRequest) {
  if (process.env.DISABLE_WEB_AUTH === "true") return NextResponse.next();

  const { pathname } = request.nextUrl;
  if (pathname.startsWith("/_next") || pathname.startsWith("/assets") || pathname.includes(".")) return NextResponse.next();

  const hasSession = await validSession(request.cookies.get(SESSION_COOKIE)?.value);

  if (isPublicPath(pathname)) {
    if (hasSession && ["/login", "/register", "/restore"].includes(pathname)) {
      return NextResponse.redirect(new URL("/leads", request.url));
    }
    return NextResponse.next();
  }

  if (!hasSession) return redirectToLogin(request);

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|sample_leads.csv).*)"]
};
