/** Shared fakes for the relay tests. No network, no Cloudflare, no wrangler. */

import { createHmac } from "node:crypto";
import { memoryStore } from "../src/store.js";

export const WEBHOOK_SECRET = "test-webhook-secret";
export const SESSION_SECRET = "test-session-secret-at-least-16";

export function makeEnv(overrides = {}) {
  return {
    GITHUB_APP_ID: "12345",
    WEBHOOK_SECRET,
    SESSION_SECRET,
    RATE_LIMIT_PER_MINUTE: "60",
    ...overrides,
  };
}

export function signedRequest({
  event,
  payload,
  deliveryId = `delivery-${Math.random().toString(16).slice(2)}`,
  secret = WEBHOOK_SECRET,
  signature,
  url = "https://relay.example.com/webhook",
}) {
  const body = typeof payload === "string" ? payload : JSON.stringify(payload);
  const digest = signature ?? `sha256=${createHmac("sha256", secret).update(body).digest("hex")}`;
  return new Request(url, {
    method: "POST",
    headers: {
      "x-github-event": event,
      "x-github-delivery": deliveryId,
      "x-hub-signature-256": digest,
      "content-type": "application/json",
    },
    body,
  });
}

/**
 * Fake GitHub client with the same surface githubClient() exposes. `files`,
 * `dispatchError`, and `readError` stay writable so a test can change what
 * GitHub returns partway through, which is how the policy cache is exercised.
 */
export function fakeGithub({ files = {}, dispatchError = null, readError = null } = {}) {
  const fake = {
    files,
    dispatchError,
    readError,
    dispatches: [],
    async dispatch(installationId, repo, type, payload) {
      if (fake.dispatchError) throw fake.dispatchError;
      fake.dispatches.push({ installationId, repo, type, payload });
    },
    async readFile(installationId, repo, path) {
      if (fake.readError) throw fake.readError;
      const key = `${repo}/${path}`;
      return key in fake.files ? fake.files[key] : null;
    },
    async installationToken() {
      return "ghs_fake";
    },
  };
  return fake;
}

export function testContext({
  env = makeEnv(),
  store = memoryStore(),
  github = fakeGithub(),
  ttlSeconds,
  now,
} = {}) {
  let clock = now ?? Date.parse("2026-08-19T12:00:00Z");
  return {
    env,
    store,
    github,
    ttlSeconds,
    now: () => clock,
    advance(ms) {
      clock += ms;
    },
  };
}

export const issueOpened = (overrides = {}) => ({
  action: "opened",
  installation: { id: 42 },
  repository: { full_name: "acme/api", owner: { login: "acme", type: "Organization" } },
  issue: { number: 7, user: { type: "User" }, labels: [], ...overrides },
});

export const prOpened = (overrides = {}) => ({
  action: "opened",
  installation: { id: 42 },
  repository: { full_name: "acme/api", owner: { login: "acme", type: "Organization" } },
  pull_request: {
    number: 9,
    draft: false,
    user: { login: "octocat" },
    head: { repo: { full_name: "acme/api" } },
    labels: [],
    ...overrides,
  },
});
