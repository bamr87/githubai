/**
 * GitHubAI hosted relay — entry point.
 *
 * A multi-tenant GitHub App that routes org events into each repository's own
 * GitHubAI workflows. What it is emphatically *not* is a place where AI runs:
 * Claude executes only inside the tenant's Actions, with the tenant's own
 * CLAUDE_CODE_OAUTH_TOKEN. This service holds installation metadata, cached org
 * policy, and routing telemetry — no code, no credentials, no model traffic.
 *
 *   GitHub event ──▶ /webhook ──▶ verify HMAC ──▶ dedupe delivery
 *                                     │
 *                                     ├─ installation lifecycle → tenant record
 *                                     └─ repo event → route → org policy → rate limit
 *                                                                  │
 *                                                repository_dispatch (githubai-*)
 *                                                                  ▼
 *                                             .github/workflows/claude-dispatch.yml
 *
 * Bindings and secrets: see wrangler.toml and app/OPERATIONS.md.
 */

import { githubClient } from "./github.js";
import { escapeHtml, html, json, randomNonce, redirect, text } from "./http.js";
import { createStore, retentionCutoff } from "./store.js";
import { handleWebhook } from "./webhook.js";
import { renderDashboard, renderLanding, renderPage } from "./dashboard.js";
import {
  SESSION_COOKIE,
  SESSION_TTL_SECONDS,
  STATE_TTL_SECONDS,
  clearedSessionCookie,
  readCookie,
  sessionCookie,
  signPayload,
  timingSafeEqual,
  verifyPayload,
} from "./session.js";

const ACTIVITY_LIMIT = 100;
/** Cookie size guard: entitlement snapshots stay small or sign-in breaks. */
const MAX_SESSION_INSTALLATIONS = 100;
const STATE_COOKIE = "githubai_oauth_state";

export default {
  async fetch(request, env) {
    const ctx = makeContext(env);
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    try {
      if (path === "/webhook") {
        if (request.method !== "POST") return text("POST required", 405);
        return await handleWebhook(request, ctx);
      }
      if (path === "/health") return await health(ctx, env);
      if (path === "/login") return await login(env, url);
      if (path === "/oauth/callback") return await oauthCallback(request, ctx, env, url);
      if (path === "/logout") return redirect("/", { "set-cookie": clearedSessionCookie() });
      if (path === "/setup") return setupLanding(url);
      if (path === "/manifest/new") return manifestForm(url, env);
      if (path === "/manifest/callback") return await manifestCallback(ctx, url, env);
      if (path === "/" || path === "/dashboard") return await dashboard(request, ctx, env, url);
      if (path === "/api/installations" || path === "/api/activity") {
        return await apiHandler(path, request, ctx, env);
      }
      return text("not found", 404);
    } catch (err) {
      // Never leak internals to a public endpoint; the message goes to logs.
      console.error("relay error", path, err?.stack || err);
      return text("internal error", 500);
    }
  },

  /** Cron trigger: age out telemetry so retention is enforced, not aspirational. */
  async scheduled(_event, env, executionContext) {
    const ctx = makeContext(env);
    const work = ctx.store.prune(retentionCutoff(ctx.now()));
    if (executionContext?.waitUntil) executionContext.waitUntil(work);
    else await work;
  },
};

function makeContext(env) {
  const now = () => Date.now();
  return {
    env,
    now,
    store: createStore(env),
    github: githubClient(env, { now }),
    ttlSeconds: numberOrUndefined(env.POLICY_TTL_SECONDS),
  };
}

function numberOrUndefined(value) {
  const parsed = Number(value);
  return value && Number.isFinite(parsed) && parsed >= 0 ? parsed : undefined;
}

async function health(ctx, env) {
  const configured = {
    app_id: Boolean(env.GITHUB_APP_ID),
    private_key: Boolean(env.GITHUB_APP_PRIVATE_KEY),
    webhook_secret: Boolean(env.WEBHOOK_SECRET),
    session_secret: Boolean(env.SESSION_SECRET),
    oauth: Boolean(env.GITHUB_CLIENT_ID && env.GITHUB_CLIENT_SECRET),
    database: ctx.store.kind === "d1",
  };
  let counts = null;
  let storeOk = true;
  try {
    counts = await ctx.store.health();
  } catch (err) {
    // /health is unauthenticated: log the cause, publish only that it failed.
    console.error("health: store unreachable", err?.stack || err);
    storeOk = false;
  }
  const required = ["app_id", "private_key", "webhook_secret"];
  const ok = storeOk && required.every((key) => configured[key]);
  return json({ ok, store_reachable: storeOk, configured, counts }, ok ? 200 : 503);
}

// ---------------------------------------------------------------------------
// Dashboard sign-in (GitHub App user-to-server OAuth)
// ---------------------------------------------------------------------------

async function login(env, url) {
  if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) {
    return text("dashboard sign-in is not configured on this deployment", 501);
  }
  const nonce = randomNonce();
  const state = await signPayload(env.SESSION_SECRET, { nonce }, Date.now() + STATE_TTL_SECONDS * 1000);
  const authorize = new URL("https://github.com/login/oauth/authorize");
  authorize.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  authorize.searchParams.set("redirect_uri", `${url.origin}/oauth/callback`);
  authorize.searchParams.set("state", state);
  return redirect(authorize.toString(), {
    "set-cookie": `${STATE_COOKIE}=${nonce}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${STATE_TTL_SECONDS}`,
  });
}

async function oauthCallback(request, ctx, env, url) {
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  if (!code || !state) return text("missing code or state", 400);

  // CSRF: the state must be signed by us *and* match the cookie set at /login.
  const decoded = await verifyPayload(env.SESSION_SECRET, state, Date.now());
  const cookieNonce = readCookie(request, STATE_COOKIE);
  if (!decoded || !cookieNonce || !timingSafeEqual(String(decoded.nonce), cookieNonce)) {
    return text("invalid oauth state", 400);
  }

  const userToken = await ctx.github.exchangeUserCode(code);
  const [user, installations] = await Promise.all([
    ctx.github.getUser(userToken),
    ctx.github.listUserInstallations(userToken),
  ]);
  // The user token has done its only job. It is never stored or re-used.

  const ids = installations.map((inst) => inst.id).slice(0, MAX_SESSION_INSTALLATIONS);
  const session = await signPayload(
    env.SESSION_SECRET,
    { login: user.login, ids },
    Date.now() + SESSION_TTL_SECONDS * 1000,
  );
  return redirect("/dashboard", [
    ["set-cookie", sessionCookie(session)],
    ["set-cookie", `${STATE_COOKIE}=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`],
  ]);
}

async function currentSession(request, env) {
  const raw = readCookie(request, SESSION_COOKIE);
  if (!raw) return null;
  return verifyPayload(env.SESSION_SECRET, raw, Date.now());
}

async function dashboard(request, ctx, env, url) {
  const nonce = randomNonce();
  const session = await currentSession(request, env);
  if (!session) {
    const reason = url.searchParams.get("signed_out") ? "Your session expired. Sign in again." : "";
    return html(renderLanding({ nonce, installUrl: env.APP_INSTALL_URL || "", signedOutReason: reason }), {
      nonce,
    });
  }

  const ids = Array.isArray(session.ids) ? session.ids : [];
  const [installations, activity] = await Promise.all([
    ctx.store.listInstallations(ids),
    ctx.store.listActivity(ids, ACTIVITY_LIMIT),
  ]);
  const policies = new Map();
  for (const installation of installations) {
    const cached = await ctx.store.getPolicy(installation.id);
    if (cached) policies.set(installation.id, cached);
  }
  return html(
    renderDashboard({ nonce, login: session.login, installations, activity, policies }),
    { nonce },
  );
}

async function apiHandler(path, request, ctx, env) {
  const session = await currentSession(request, env);
  if (!session) return json({ error: "not signed in" }, 401);
  const ids = Array.isArray(session.ids) ? session.ids : [];
  if (path === "/api/installations") {
    return json({ installations: await ctx.store.listInstallations(ids) });
  }
  return json({ activity: await ctx.store.listActivity(ids, ACTIVITY_LIMIT) });
}

// ---------------------------------------------------------------------------
// Install + App Manifest flows
// ---------------------------------------------------------------------------

function setupLanding(url) {
  const nonce = randomNonce();
  const account = url.searchParams.get("installation_id") ? "your account" : "";
  const body = `
<h1>GitHubAI is installed</h1>
<p>Events from ${escapeHtml(account || "your repositories")} now route to this relay. Two steps remain, both inside your repositories:</p>
<ol>
  <li><strong>Add the dispatch workflow.</strong> Run <code>setup/install.sh --app</code> in each repository (or copy <code>template/workflows/claude-dispatch.yml</code>). Without it, dispatched events have nothing to run.</li>
  <li><strong>Set the Claude Code token.</strong> <code>claude setup-token</code>, then <code>gh secret set CLAUDE_CODE_OAUTH_TOKEN</code> — an organization secret covers every repository at once.</li>
</ol>
<p>Optional: create <code>.github/githubai-org.yml</code> in your <code>.github</code> repository to set org-wide routing policy.</p>
<p class="actions"><a class="button" href="/dashboard">Open the dashboard</a></p>`;
  return html(renderPage({ title: "GitHubAI installed", nonce, body }), { nonce });
}

/**
 * Self-hosters can register their own App from a manifest instead of clicking
 * through settings. Disabled unless SETUP_TOKEN is configured, because the
 * endpoint publishes this deployment's intended webhook URL and permissions.
 */
function manifestForm(url, env) {
  if (!env.SETUP_TOKEN) return text("manifest registration is disabled on this deployment", 404);
  if (!timingSafeEqual(url.searchParams.get("token") || "", env.SETUP_TOKEN)) {
    return text("invalid setup token", 403);
  }
  const nonce = randomNonce();
  const manifest = {
    name: env.APP_NAME || "GitHubAI",
    url: "https://github.com/bamr87/githubai",
    description:
      "Wires Claude Code into the whole SDLC: triage, implementation, review, auto-merge, maintenance, and releases.",
    hook_attributes: { url: `${url.origin}/webhook`, active: true },
    redirect_url: `${url.origin}/manifest/callback`,
    setup_url: `${url.origin}/setup`,
    public: false,
    default_permissions: {
      contents: "write",
      issues: "read",
      pull_requests: "read",
      metadata: "read",
    },
    default_events: ["issues", "pull_request", "installation", "installation_repositories"],
  };
  const target = env.MANIFEST_ORG
    ? `https://github.com/organizations/${encodeURIComponent(env.MANIFEST_ORG)}/settings/apps/new`
    : "https://github.com/settings/apps/new";
  const body = `
<h1>Register the GitHubAI App</h1>
<p>Submitting this form hands the manifest below to GitHub, which creates the App and returns its credentials once.</p>
<form method="post" action="${escapeHtml(target)}">
  <input type="hidden" name="manifest" value="${escapeHtml(JSON.stringify(manifest))}">
  <p class="actions"><button class="button" type="submit">Create the App on GitHub</button></p>
</form>
<pre class="notice mono">${escapeHtml(JSON.stringify(manifest, null, 2))}</pre>`;
  // This is the one page that posts a form off-origin, to GitHub's App
  // registration endpoint; every other page keeps form-action 'self'.
  return html(renderPage({ title: "Register the GitHubAI App", nonce, body }), {
    nonce,
    formAction: "https://github.com",
  });
}

async function manifestCallback(ctx, url, env) {
  if (!env.SETUP_TOKEN) return text("manifest registration is disabled on this deployment", 404);
  const code = url.searchParams.get("code");
  if (!code) return text("missing manifest code", 400);

  const app = await ctx.github.convertManifest(code);
  const nonce = randomNonce();
  const commands = [
    `wrangler secret put GITHUB_APP_ID        # ${app.id}`,
    "wrangler secret put GITHUB_APP_PRIVATE_KEY  # PKCS#8 — see below",
    `wrangler secret put WEBHOOK_SECRET       # ${app.webhook_secret ? "shown below" : "set one in App settings"}`,
    `wrangler secret put GITHUB_CLIENT_ID     # ${app.client_id}`,
    "wrangler secret put GITHUB_CLIENT_SECRET # shown below",
    "wrangler secret put SESSION_SECRET       # any 32+ random characters",
  ].join("\n");
  const body = `
<h1>App created: ${escapeHtml(app.name || "GitHubAI")}</h1>
<p class="notice"><strong>These credentials are shown once.</strong> Store them as Worker secrets now — this page is never cached and cannot be reloaded.</p>
<h2>Secrets to set</h2>
<pre class="notice mono">${escapeHtml(commands)}</pre>
<h2>Values</h2>
<pre class="notice mono">GITHUB_APP_ID=${escapeHtml(app.id)}
GITHUB_CLIENT_ID=${escapeHtml(app.client_id)}
GITHUB_CLIENT_SECRET=${escapeHtml(app.client_secret)}
WEBHOOK_SECRET=${escapeHtml(app.webhook_secret || "(none — set one in App settings)")}</pre>
<h2>Private key (convert to PKCS#8 before storing)</h2>
<pre class="notice mono">${escapeHtml(app.pem || "")}</pre>
<p>Convert with <code>openssl pkcs8 -topk8 -nocrypt -in app.pem</code>, then store the <code>BEGIN PRIVATE KEY</code> form.</p>
<p><a href="${escapeHtml(app.html_url || "https://github.com/settings/apps")}">Install the app →</a></p>`;
  return html(renderPage({ title: "GitHubAI App created", nonce, body }), { nonce });
}
