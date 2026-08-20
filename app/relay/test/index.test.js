import assert from "node:assert/strict";
import test, { afterEach, beforeEach } from "node:test";

import worker from "../src/index.js";
import { OUTCOMES, createStore, resetFallbackStore } from "../src/store.js";
import { SESSION_TTL_SECONDS, sessionCookie, signPayload } from "../src/session.js";
import { SESSION_SECRET, makeEnv, signedRequest } from "./helpers.js";

const ORIGIN = "https://relay.example.com";
const realFetch = globalThis.fetch;

beforeEach(() => resetFallbackStore());
afterEach(() => {
  globalThis.fetch = realFetch;
});

const get = (path, headers = {}) => new Request(`${ORIGIN}${path}`, { headers });

async function signedInHeaders(ids, login = "octo") {
  const token = await signPayload(
    SESSION_SECRET,
    { login, ids },
    Date.now() + SESSION_TTL_SECONDS * 1000,
  );
  return { cookie: sessionCookie(token).split(";")[0] };
}

test("unknown paths 404 and the webhook rejects non-POST", async () => {
  const env = makeEnv();
  assert.equal((await worker.fetch(get("/nope"), env, {})).status, 404);
  assert.equal((await worker.fetch(get("/webhook"), env, {})).status, 405);
});

test("health reports configuration presence without leaking values", async () => {
  // Incomplete configuration is unhealthy: a relay missing its private key
  // accepts webhooks it can never dispatch, so it must fail its own check.
  const incomplete = await worker.fetch(get("/health"), makeEnv(), {});
  assert.equal(incomplete.status, 503);
  const body = await incomplete.json();
  assert.equal(body.ok, false);
  assert.deepEqual(body.configured, {
    app_id: true,
    private_key: false,
    webhook_secret: true,
    session_secret: true,
    oauth: false,
    database: false,
  });
  assert.equal(JSON.stringify(body).includes(SESSION_SECRET), false, "secrets must never appear");

  const env = makeEnv({
    GITHUB_APP_PRIVATE_KEY: "-----BEGIN PRIVATE KEY-----\nx\n-----END PRIVATE KEY-----",
  });
  const healthy = await worker.fetch(get("/health"), env, {});
  assert.equal(healthy.status, 200);
  const ok = await healthy.json();
  assert.equal(ok.ok, true);
  assert.equal(ok.store_reachable, true);
  assert.equal(ok.configured.private_key, true);
  assert.equal(ok.counts.installations, 0);

  assert.equal(
    (await worker.fetch(get("/health"), makeEnv({ WEBHOOK_SECRET: "" }), {})).status,
    503,
  );
});

test("the landing page is served to signed-out visitors with a strict CSP", async () => {
  const response = await worker.fetch(get("/"), makeEnv(), {});
  assert.equal(response.status, 200);
  const csp = response.headers.get("content-security-policy");
  assert.match(csp, /default-src 'none'/);
  assert.match(csp, /style-src 'nonce-[0-9a-f]{32}'/);
  assert.ok(!csp.includes("unsafe-inline"), "no unsafe-inline anywhere");
  assert.match(csp, /form-action 'self'/);
  assert.equal(response.headers.get("x-frame-options"), "DENY");
  assert.equal(response.headers.get("cache-control"), "no-store");

  const body = await response.text();
  assert.match(body, /Sign in with GitHub/);
  assert.ok(!body.includes("<script"), "the dashboard ships no scripts");
});

test("the dashboard and API are closed to visitors without a valid session", async () => {
  const env = makeEnv();
  const dashboard = await worker.fetch(get("/dashboard"), env, {});
  assert.match(await dashboard.text(), /Sign in with GitHub/);

  for (const path of ["/api/installations", "/api/activity"]) {
    const response = await worker.fetch(get(path), env, {});
    assert.equal(response.status, 401);
  }

  const forged = await worker.fetch(
    get("/api/activity", { cookie: "githubai_session=forged.token" }),
    env,
    {},
  );
  assert.equal(forged.status, 401);
});

test("a session only ever sees its own installations", async () => {
  const env = makeEnv();
  const store = createStore(env);
  await store.upsertInstallation({ id: 1, accountLogin: "acme", now: "2026-08-19T12:00:00.000Z" });
  await store.upsertInstallation({ id: 2, accountLogin: "rival", now: "2026-08-19T12:00:00.000Z" });
  await store.recordActivity({
    installationId: 1,
    repo: "acme/api",
    event: "issues",
    outcome: OUTCOMES.DISPATCHED,
    now: "2026-08-19T12:00:00.000Z",
  });
  await store.recordActivity({
    installationId: 2,
    repo: "rival/secret-service",
    event: "issues",
    outcome: OUTCOMES.DISPATCHED,
    now: "2026-08-19T12:00:00.000Z",
  });

  const headers = await signedInHeaders([1]);
  const page = await worker.fetch(get("/dashboard", headers), env, {});
  const html = await page.text();
  assert.match(html, /acme\/api/);
  assert.ok(!html.includes("rival"), "another tenant's data must never render");

  const api = await (await worker.fetch(get("/api/activity", headers), env, {})).json();
  assert.deepEqual(api.activity.map((row) => row.repo), ["acme/api"]);
  const installs = await (await worker.fetch(get("/api/installations", headers), env, {})).json();
  assert.deepEqual(installs.installations.map((row) => row.accountLogin), ["acme"]);
});

test("rendered tenant data is HTML-escaped", async () => {
  const env = makeEnv();
  const store = createStore(env);
  await store.upsertInstallation({ id: 1, accountLogin: "acme", now: "2026-08-19T12:00:00.000Z" });
  await store.recordActivity({
    installationId: 1,
    repo: "acme/<img src=x onerror=alert(1)>",
    event: "issues",
    outcome: OUTCOMES.IGNORED,
    detail: '"><script>alert(1)</script>',
    now: "2026-08-19T12:00:00.000Z",
  });

  const html = await (await worker.fetch(get("/dashboard", await signedInHeaders([1])), env, {})).text();
  assert.ok(!html.includes("<img src=x"), "markup from a repo name must be escaped");
  assert.ok(!html.includes("<script>"), "markup from event detail must be escaped");
  assert.match(html, /&lt;img src=x/);
});

test("logout clears the session cookie", async () => {
  const response = await worker.fetch(get("/logout", await signedInHeaders([1])), makeEnv(), {});
  assert.equal(response.status, 302);
  assert.match(response.headers.get("set-cookie"), /githubai_session=; .*Max-Age=0/);
});

test("sign-in is disabled unless OAuth credentials are configured", async () => {
  const response = await worker.fetch(get("/login"), makeEnv(), {});
  assert.equal(response.status, 501);
});

test("the OAuth round trip issues a session and rejects a bad state", async () => {
  const env = makeEnv({ GITHUB_CLIENT_ID: "Iv1.test", GITHUB_CLIENT_SECRET: "shh" });

  const login = await worker.fetch(get("/login"), env, {});
  assert.equal(login.status, 302);
  const authorize = new URL(login.headers.get("location"));
  assert.equal(authorize.origin + authorize.pathname, "https://github.com/login/oauth/authorize");
  assert.equal(authorize.searchParams.get("redirect_uri"), `${ORIGIN}/oauth/callback`);
  const state = authorize.searchParams.get("state");
  const nonce = /githubai_oauth_state=([^;]+)/.exec(login.headers.get("set-cookie"))[1];

  globalThis.fetch = async (url) => {
    const href = String(url);
    if (href.includes("login/oauth/access_token")) {
      return new Response(JSON.stringify({ access_token: "gho_user" }), {
        headers: { "content-type": "application/json" },
      });
    }
    if (href.endsWith("/user")) {
      return new Response(JSON.stringify({ login: "octo" }), {
        headers: { "content-type": "application/json" },
      });
    }
    if (href.includes("/user/installations")) {
      return new Response(JSON.stringify({ installations: [{ id: 42 }] }), {
        headers: { "content-type": "application/json" },
      });
    }
    throw new Error(`unexpected fetch: ${href}`);
  };

  const callback = await worker.fetch(
    get(`/oauth/callback?code=abc&state=${encodeURIComponent(state)}`, {
      cookie: `githubai_oauth_state=${nonce}`,
    }),
    env,
    {},
  );
  assert.equal(callback.status, 302);
  assert.equal(callback.headers.get("location"), "/dashboard");
  const cookies = callback.headers.getSetCookie();
  assert.equal(cookies.length, 2, "session and state-clearing cookies are separate headers");
  assert.match(cookies[0], /^githubai_session=.+HttpOnly/s);

  // The signed state alone is not enough: the cookie must match it.
  const csrf = await worker.fetch(
    get(`/oauth/callback?code=abc&state=${encodeURIComponent(state)}`, {
      cookie: "githubai_oauth_state=attacker-nonce",
    }),
    env,
    {},
  );
  assert.equal(csrf.status, 400);
  assert.match(await csrf.text(), /invalid oauth state/);
});

test("manifest registration stays off unless a setup token is configured", async () => {
  assert.equal((await worker.fetch(get("/manifest/new"), makeEnv(), {})).status, 404);
  assert.equal((await worker.fetch(get("/manifest/callback?code=x"), makeEnv(), {})).status, 404);

  const env = makeEnv({ SETUP_TOKEN: "correct-horse-battery" });
  assert.equal((await worker.fetch(get("/manifest/new?token=wrong"), env, {})).status, 403);

  const form = await worker.fetch(get("/manifest/new?token=correct-horse-battery"), env, {});
  assert.equal(form.status, 200);
  // This page - and only this page - may post its form off-origin to GitHub.
  assert.match(form.headers.get("content-security-policy"), /form-action https:\/\/github\.com/);
  const html = await form.text();
  assert.match(html, /action="https:\/\/github\.com\/settings\/apps\/new"/);
  assert.match(html, /relay\.example\.com\/webhook/);
  // Least privilege: the relay only needs to fire repository_dispatch.
  assert.match(html, /&quot;contents&quot;: ?&quot;write&quot;/);
  assert.ok(!html.includes("&quot;issues&quot;: &quot;write&quot;"), "no issue write permission");
});

test("the setup landing page explains the remaining per-repo steps", async () => {
  const response = await worker.fetch(get("/setup?installation_id=42"), makeEnv(), {});
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /claude-dispatch\.yml/);
  assert.match(html, /CLAUDE_CODE_OAUTH_TOKEN/);
});

test("webhook deliveries route through the worker entry point", async () => {
  const env = makeEnv();
  const payload = {
    action: "opened",
    installation: { id: 42 },
    repository: { full_name: "acme/api", owner: { login: "acme", type: "Organization" } },
    issue: { number: 7, user: { type: "User" }, labels: [{ name: "claude:skip" }] },
  };
  const response = await worker.fetch(signedRequest({ event: "issues", payload }), env, {});
  assert.equal(response.status, 200);
  assert.match(await response.text(), /claude:skip/);
});

test("an unreachable database is reported without exposing the cause", async () => {
  const broken = {
    ...makeEnv(),
    DB: {
      prepare: () => {
        throw new Error("D1 is down: connection string secret-dsn");
      },
    },
  };
  const response = await worker.fetch(get("/health"), broken, {});
  assert.equal(response.status, 503);
  const body = await response.text();
  assert.ok(!body.includes("secret-dsn"), "/health is unauthenticated: no internals in the body");
  assert.match(body, /"store_reachable": false/);
});

test("the scheduled handler prunes aged telemetry", async () => {
  const env = makeEnv();
  const store = createStore(env);
  await store.recordActivity({
    installationId: 1,
    event: "issues",
    outcome: OUTCOMES.IGNORED,
    now: "2026-01-01T00:00:00.000Z",
  });
  await store.recordActivity({
    installationId: 1,
    event: "issues",
    outcome: OUTCOMES.IGNORED,
    now: new Date().toISOString(),
  });

  await worker.scheduled({}, env, {});
  assert.equal((await store.listActivity([1], 10)).length, 1);
});
