/**
 * Stateless dashboard sessions and OAuth CSRF state.
 *
 * A session is an HMAC-signed, expiring blob in an HttpOnly cookie holding the
 * visitor's login and the installation ids they were entitled to at sign-in.
 * The GitHub user token used to *learn* those ids is discarded immediately and
 * never stored — the hosted service holds no customer credentials, which is the
 * property that lets app/DATA-HANDLING.md make that promise honestly.
 *
 * The cost of statelessness is that entitlement is a snapshot: revoking a
 * user's org access takes effect at the next sign-in, up to SESSION_TTL later.
 * TTL is therefore short (8h) and the dashboard is read-only, so the worst case
 * is a departed admin briefly seeing routing telemetry they already saw.
 */

import { b64url, b64urlBytes } from "./github.js";

export const SESSION_COOKIE = "githubai_session";
export const SESSION_TTL_SECONDS = 8 * 3600;
export const STATE_TTL_SECONDS = 600;

export async function signPayload(secret, payload, expiresAtMs) {
  requireSecret(secret);
  const body = b64url(JSON.stringify({ ...payload, exp: Math.floor(expiresAtMs / 1000) }));
  return `${body}.${await hmac(secret, body)}`;
}

/** Verify and decode a signed payload. Returns null for tampered or expired input. */
export async function verifyPayload(secret, token, nowMs) {
  if (!secret || typeof token !== "string") return null;
  const dot = token.lastIndexOf(".");
  if (dot <= 0) return null;
  const body = token.slice(0, dot);
  const signature = token.slice(dot + 1);
  if (!timingSafeEqual(await hmac(secret, body), signature)) return null;
  let payload;
  try {
    payload = JSON.parse(new TextDecoder().decode(fromB64url(body)));
  } catch {
    return null;
  }
  if (typeof payload?.exp !== "number" || payload.exp * 1000 <= nowMs) return null;
  return payload;
}

export function sessionCookie(value, maxAgeSeconds = SESSION_TTL_SECONDS) {
  return `${SESSION_COOKIE}=${value}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAgeSeconds}`;
}

export function clearedSessionCookie() {
  return `${SESSION_COOKIE}=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`;
}

export function readCookie(request, name) {
  const header = request.headers.get("cookie") || "";
  for (const part of header.split(";")) {
    const eq = part.indexOf("=");
    if (eq === -1) continue;
    if (part.slice(0, eq).trim() === name) return part.slice(eq + 1).trim();
  }
  return null;
}

/** HMAC-SHA256 the webhook body and compare against GitHub's header. */
export async function verifyWebhookSignature(secret, header, body) {
  if (!secret || typeof header !== "string" || !header.startsWith("sha256=")) return false;
  const expected = `sha256=${await hmacHex(secret, body)}`;
  return timingSafeEqual(expected, header);
}

async function importHmacKey(secret) {
  return crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
}

async function hmac(secret, message) {
  const key = await importHmacKey(secret);
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return b64urlBytes(new Uint8Array(mac));
}

async function hmacHex(secret, message) {
  const key = await importHmacKey(secret);
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return Array.from(new Uint8Array(mac), (b) => b.toString(16).padStart(2, "0")).join("");
}

function fromB64url(value) {
  const b64 = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  const raw = atob(b64);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
  return bytes;
}

export function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function requireSecret(secret) {
  if (!secret || String(secret).length < 16) {
    throw new Error("SESSION_SECRET must be set to at least 16 characters");
  }
}
