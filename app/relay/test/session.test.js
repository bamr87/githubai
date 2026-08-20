import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import test from "node:test";

import {
  SESSION_COOKIE,
  clearedSessionCookie,
  readCookie,
  sessionCookie,
  signPayload,
  timingSafeEqual,
  verifyPayload,
  verifyWebhookSignature,
} from "../src/session.js";
import { SESSION_SECRET } from "./helpers.js";

const NOW = Date.parse("2026-08-19T12:00:00Z");

test("signed payloads round-trip", async () => {
  const token = await signPayload(SESSION_SECRET, { login: "octo", ids: [1, 2] }, NOW + 60_000);
  const payload = await verifyPayload(SESSION_SECRET, token, NOW);
  assert.equal(payload.login, "octo");
  assert.deepEqual(payload.ids, [1, 2]);
});

test("tampering, wrong secrets, and expiry all fail closed", async () => {
  const token = await signPayload(SESSION_SECRET, { login: "octo" }, NOW + 60_000);
  assert.equal(await verifyPayload(SESSION_SECRET, `${token}x`, NOW), null);
  assert.equal(await verifyPayload("another-secret-at-least-16", token, NOW), null);
  assert.equal(await verifyPayload(SESSION_SECRET, token, NOW + 61_000), null, "expired");
  assert.equal(await verifyPayload(SESSION_SECRET, "not-a-token", NOW), null);
  assert.equal(await verifyPayload(SESSION_SECRET, "", NOW), null);
  assert.equal(await verifyPayload("", token, NOW), null);

  // Re-signing a modified body with a different secret must not validate.
  const body = token.slice(0, token.lastIndexOf("."));
  const forged = `${body}.${createHmac("sha256", "wrong").update(body).digest("base64url")}`;
  assert.equal(await verifyPayload(SESSION_SECRET, forged, NOW), null);
});

test("a weak session secret is rejected at signing time", async () => {
  await assert.rejects(() => signPayload("short", {}, NOW + 1000), /SESSION_SECRET/);
});

test("session cookies are HttpOnly, Secure and SameSite=Lax", () => {
  const cookie = sessionCookie("value");
  assert.match(cookie, /^githubai_session=value;/);
  for (const attr of ["HttpOnly", "Secure", "SameSite=Lax", "Path=/"]) {
    assert.ok(cookie.includes(attr), `missing ${attr}`);
  }
  assert.match(clearedSessionCookie(), /Max-Age=0/);
});

test("cookies are parsed by exact name", () => {
  const request = new Request("https://relay.example.com/", {
    headers: { cookie: `other=1; ${SESSION_COOKIE}=abc.def; trailing=2` },
  });
  assert.equal(readCookie(request, SESSION_COOKIE), "abc.def");
  assert.equal(readCookie(request, "missing"), null);
  // A cookie whose name merely ends with ours must not be mistaken for it.
  const decoy = new Request("https://relay.example.com/", {
    headers: { cookie: `not_${SESSION_COOKIE}=evil` },
  });
  assert.equal(readCookie(decoy, SESSION_COOKIE), null);
});

test("webhook signatures verify against GitHub's scheme", async () => {
  const body = JSON.stringify({ action: "opened" });
  const good = `sha256=${createHmac("sha256", "s3cret").update(body).digest("hex")}`;
  assert.equal(await verifyWebhookSignature("s3cret", good, body), true);
  assert.equal(await verifyWebhookSignature("wrong", good, body), false);
  assert.equal(await verifyWebhookSignature("s3cret", good, `${body} `), false);
  assert.equal(await verifyWebhookSignature("s3cret", good.replace("sha256=", "sha1="), body), false);
  assert.equal(await verifyWebhookSignature("s3cret", null, body), false);
  assert.equal(await verifyWebhookSignature("", good, body), false, "unset secret must not pass");
});

test("comparison is length-checked and value-checked", () => {
  assert.equal(timingSafeEqual("abc", "abc"), true);
  assert.equal(timingSafeEqual("abc", "abd"), false);
  assert.equal(timingSafeEqual("abc", "abcd"), false);
  assert.equal(timingSafeEqual(undefined, "abc"), false);
});
