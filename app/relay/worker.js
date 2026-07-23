/**
 * GitHubAI relay — GitHub App webhook → repository_dispatch bridge.
 *
 * Zero-dependency Cloudflare Worker (any WebCrypto runtime works). The
 * GitHub App delivers webhooks here; the relay verifies the HMAC signature,
 * maps the event to a GitHubAI dispatch type, mints an installation token
 * with the App's private key, and fires repository_dispatch back at the
 * source repo — where template/workflows/claude-dispatch.yml routes it to
 * the same reusable workflows the Actions-only mode uses.
 *
 * Environment (Worker secrets):
 *   GITHUB_APP_ID          — numeric App ID
 *   GITHUB_APP_PRIVATE_KEY — the App's private key in PKCS#8 PEM. GitHub
 *                            downloads keys as PKCS#1; convert once with:
 *                            openssl pkcs8 -topk8 -nocrypt -in app.pem
 *   WEBHOOK_SECRET         — the App's webhook secret
 *
 * Deploy: `wrangler deploy` from this directory (see wrangler.toml), then
 * point the App's webhook URL at https://<worker>/webhook.
 */

const DISPATCH_PREFIX = "githubai";
const AUTO_MERGE_AUTHORS = ["dependabot[bot]", "renovate[bot]"];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/setup") {
      return new Response(
        "GitHubAI app installed. Add the dispatch workflow to each repo " +
          "(setup/install.sh --app) and you are done.",
        { status: 200 },
      );
    }
    if (url.pathname !== "/webhook" || request.method !== "POST") {
      return new Response("GitHubAI relay: POST /webhook", { status: 404 });
    }

    const body = await request.text();
    if (!(await verifySignature(env.WEBHOOK_SECRET, request, body))) {
      return new Response("bad signature", { status: 401 });
    }

    const event = request.headers.get("x-github-event") || "";
    let payload;
    try {
      payload = JSON.parse(body);
    } catch {
      return new Response("bad payload", { status: 400 });
    }

    const dispatch = mapEvent(event, payload);
    if (!dispatch) {
      return new Response("ignored", { status: 200 });
    }

    const repo = payload.repository && payload.repository.full_name;
    const installationId = payload.installation && payload.installation.id;
    if (!repo || !installationId) {
      return new Response("no repository/installation in payload", { status: 200 });
    }

    const token = await installationToken(env, installationId);
    const res = await fetch(`https://api.github.com/repos/${repo}/dispatches`, {
      method: "POST",
      headers: {
        authorization: `Bearer ${token}`,
        accept: "application/vnd.github+json",
        "user-agent": "githubai-relay",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        event_type: dispatch.type,
        client_payload: dispatch.payload,
      }),
    });
    if (!res.ok) {
      return new Response(`dispatch failed: ${res.status}`, { status: 502 });
    }
    return new Response(`dispatched ${dispatch.type}`, { status: 202 });
  },
};

/** Map a webhook (event name + payload) to a GitHubAI dispatch, or null. */
export function mapEvent(event, payload) {
  const action = payload.action;
  if (event === "issues") {
    const n = payload.issue && payload.issue.number;
    if (action === "opened" || action === "reopened") {
      return { type: `${DISPATCH_PREFIX}-triage`, payload: { issue_number: String(n) } };
    }
    if (action === "labeled" && payload.label && payload.label.name === "claude:implement") {
      return { type: `${DISPATCH_PREFIX}-implement`, payload: { issue_number: String(n) } };
    }
    return null;
  }
  if (event === "pull_request") {
    const pr = payload.pull_request || {};
    const n = pr.number;
    const sameRepo =
      pr.head && pr.head.repo && payload.repository &&
      pr.head.repo.full_name === payload.repository.full_name;
    if (!sameRepo) return null;
    if ((action === "opened" || action === "ready_for_review") && !pr.draft) {
      const byTrustedBot =
        action === "opened" && pr.user && AUTO_MERGE_AUTHORS.includes(pr.user.login);
      return byTrustedBot
        ? { type: `${DISPATCH_PREFIX}-auto-merge`, payload: { pr_number: String(n) } }
        : { type: `${DISPATCH_PREFIX}-review`, payload: { pr_number: String(n) } };
    }
    if (action === "labeled" && payload.label) {
      if (payload.label.name === "claude:auto-merge") {
        return { type: `${DISPATCH_PREFIX}-auto-merge`, payload: { pr_number: String(n) } };
      }
      if (payload.label.name === "claude:review") {
        return { type: `${DISPATCH_PREFIX}-review`, payload: { pr_number: String(n) } };
      }
    }
    return null;
  }
  return null;
}

async function verifySignature(secret, request, body) {
  const header = request.headers.get("x-hub-signature-256") || "";
  if (!secret || !header.startsWith("sha256=")) return false;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  const expected = "sha256=" + hex(new Uint8Array(mac));
  return timingSafeEqual(expected, header);
}

async function installationToken(env, installationId) {
  const now = Math.floor(Date.now() / 1000);
  const jwt = await signJwt(
    { alg: "RS256", typ: "JWT" },
    { iat: now - 60, exp: now + 540, iss: String(env.GITHUB_APP_ID) },
    env.GITHUB_APP_PRIVATE_KEY,
  );
  const res = await fetch(
    `https://api.github.com/app/installations/${installationId}/access_tokens`,
    {
      method: "POST",
      headers: {
        authorization: `Bearer ${jwt}`,
        accept: "application/vnd.github+json",
        "user-agent": "githubai-relay",
      },
    },
  );
  if (!res.ok) throw new Error(`installation token failed: ${res.status}`);
  const data = await res.json();
  return data.token;
}

async function signJwt(header, claims, pem) {
  if (!pem || !pem.includes("BEGIN PRIVATE KEY")) {
    throw new Error(
      "GITHUB_APP_PRIVATE_KEY must be PKCS#8 (BEGIN PRIVATE KEY); convert with: openssl pkcs8 -topk8 -nocrypt",
    );
  }
  const der = pemToDer(pem);
  const key = await crypto.subtle.importKey(
    "pkcs8",
    der,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const unsigned = `${b64url(JSON.stringify(header))}.${b64url(JSON.stringify(claims))}`;
  const sig = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    key,
    new TextEncoder().encode(unsigned),
  );
  return `${unsigned}.${b64urlBytes(new Uint8Array(sig))}`;
}

function pemToDer(pem) {
  const b64 = pem.replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
  const raw = atob(b64);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
  return bytes.buffer;
}

function b64url(str) {
  return b64urlBytes(new TextEncoder().encode(str));
}

function b64urlBytes(bytes) {
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function hex(bytes) {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i++) out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return out === 0;
}
