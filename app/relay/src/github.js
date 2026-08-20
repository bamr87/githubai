/**
 * GitHub API surface used by the relay.
 *
 * Three credential kinds, deliberately separated:
 *   - App JWT             — proves we are the App; only used to mint the next two.
 *   - Installation token  — short-lived, per-tenant; fires repository_dispatch and
 *                           reads the org policy file. Cached in-isolate, never stored.
 *   - User access token   — obtained during dashboard sign-in to learn which
 *                           installations the visitor may see, then discarded. It is
 *                           never written to D1 or to a cookie.
 */

const API = "https://api.github.com";
const UA = "githubai-relay";

/** Org policy files can be malformed or enormous; refuse to parse past this. */
export const MAX_POLICY_BYTES = 64 * 1024;

export class GitHubError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "GitHubError";
    this.status = status;
  }
}

/**
 * Installation tokens, keyed by installation id and scoped to this isolate.
 * Bounded because a busy multi-tenant relay would otherwise accumulate one
 * entry per tenant for the life of the isolate.
 */
const tokenCache = new Map();
const MAX_CACHED_TOKENS = 500;

export function githubClient(env, deps = {}) {
  const doFetch = deps.fetch || globalThis.fetch;
  const now = deps.now || (() => Date.now());

  async function api(path, { token, method = "GET", body, accept } = {}) {
    const res = await doFetch(`${API}${path}`, {
      method,
      headers: {
        authorization: `Bearer ${token}`,
        accept: accept || "application/vnd.github+json",
        "x-github-api-version": "2022-11-28",
        "user-agent": UA,
        ...(body ? { "content-type": "application/json" } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    return res;
  }

  async function appJwt() {
    const issued = Math.floor(now() / 1000);
    return signJwt(
      { alg: "RS256", typ: "JWT" },
      // iat backdated 60s to tolerate clock skew; GitHub caps exp at 10 minutes.
      { iat: issued - 60, exp: issued + 540, iss: String(env.GITHUB_APP_ID) },
      env.GITHUB_APP_PRIVATE_KEY,
    );
  }

  async function installationToken(installationId) {
    const cached = tokenCache.get(installationId);
    // Refresh a minute early rather than racing the expiry.
    if (cached && cached.expiresAt - 60_000 > now()) return cached.token;

    const res = await api(`/app/installations/${installationId}/access_tokens`, {
      token: await appJwt(),
      method: "POST",
    });
    if (!res.ok) {
      tokenCache.delete(installationId);
      throw new GitHubError(`installation token failed: ${res.status}`, res.status);
    }
    const data = await res.json();
    if (tokenCache.size >= MAX_CACHED_TOKENS) evictTokens(now());
    tokenCache.set(installationId, {
      token: data.token,
      expiresAt: Date.parse(data.expires_at) || now() + 3_000_000,
    });
    return data.token;
  }

  return {
    appJwt,
    installationToken,

    /** Fire repository_dispatch at a tenant repo. Requires contents:write. */
    async dispatch(installationId, repoFullName, eventType, clientPayload) {
      const res = await api(`/repos/${repoFullName}/dispatches`, {
        token: await installationToken(installationId),
        method: "POST",
        body: { event_type: eventType, client_payload: clientPayload },
      });
      if (res.status === 204) return;
      const detail = await res.text().catch(() => "");
      throw new GitHubError(
        `dispatch ${eventType} to ${repoFullName} failed: ${res.status} ${detail.slice(0, 200)}`,
        res.status,
      );
    },

    /**
     * Read a text file from a tenant repo. Returns null when absent (404) — an
     * org with no policy file is the normal case, not an error.
     */
    async readFile(installationId, repoFullName, path) {
      const res = await api(`/repos/${repoFullName}/contents/${path}`, {
        token: await installationToken(installationId),
        accept: "application/vnd.github.raw+json",
      });
      if (res.status === 404) return null;
      if (!res.ok) throw new GitHubError(`read ${repoFullName}/${path}: ${res.status}`, res.status);
      const text = await res.text();
      if (text.length > MAX_POLICY_BYTES) {
        throw new GitHubError(`${path} exceeds ${MAX_POLICY_BYTES} bytes`, 413);
      }
      return text;
    },

    /** Exchange an OAuth code for a user access token (used once, never stored). */
    async exchangeUserCode(code) {
      const res = await doFetch("https://github.com/login/oauth/access_token", {
        method: "POST",
        headers: { accept: "application/json", "content-type": "application/json", "user-agent": UA },
        body: JSON.stringify({
          client_id: env.GITHUB_CLIENT_ID,
          client_secret: env.GITHUB_CLIENT_SECRET,
          code,
        }),
      });
      if (!res.ok) throw new GitHubError(`oauth exchange failed: ${res.status}`, res.status);
      const data = await res.json();
      if (!data.access_token) {
        throw new GitHubError(`oauth exchange rejected: ${data.error || "no token"}`, 401);
      }
      return data.access_token;
    },

    async getUser(userToken) {
      const res = await api("/user", { token: userToken });
      if (!res.ok) throw new GitHubError(`user lookup failed: ${res.status}`, res.status);
      return res.json();
    },

    /** Installations of *this* App that the signed-in user can administer. */
    async listUserInstallations(userToken) {
      const res = await api("/user/installations?per_page=100", { token: userToken });
      if (!res.ok) throw new GitHubError(`installations lookup failed: ${res.status}`, res.status);
      const data = await res.json();
      return data.installations || [];
    },

    /** App Manifest flow: turn a temporary code into App credentials, once. */
    async convertManifest(code) {
      const res = await doFetch(`${API}/app-manifests/${code}/conversions`, {
        method: "POST",
        headers: { accept: "application/vnd.github+json", "user-agent": UA },
      });
      if (!res.ok) throw new GitHubError(`manifest conversion failed: ${res.status}`, res.status);
      return res.json();
    },
  };
}

export async function signJwt(header, claims, pem) {
  const key = await importPrivateKey(pem);
  const unsigned = `${b64url(JSON.stringify(header))}.${b64url(JSON.stringify(claims))}`;
  const sig = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    key,
    new TextEncoder().encode(unsigned),
  );
  return `${unsigned}.${b64urlBytes(new Uint8Array(sig))}`;
}

async function importPrivateKey(pem) {
  if (!pem || !pem.includes("BEGIN PRIVATE KEY")) {
    throw new GitHubError(
      "GITHUB_APP_PRIVATE_KEY must be PKCS#8 (BEGIN PRIVATE KEY); GitHub downloads " +
        "PKCS#1 — convert once with: openssl pkcs8 -topk8 -nocrypt -in app.pem",
      500,
    );
  }
  return crypto.subtle.importKey(
    "pkcs8",
    pemToDer(pem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
}

function pemToDer(pem) {
  const raw = atob(pem.replace(/-----[^-]+-----/g, "").replace(/\s+/g, ""));
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
  return bytes.buffer;
}

export function b64url(str) {
  return b64urlBytes(new TextEncoder().encode(str));
}

export function b64urlBytes(bytes) {
  let bin = "";
  for (const byte of bytes) bin += String.fromCharCode(byte);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

/** Drop expired entries, then the oldest, until the cache is under its cap. */
function evictTokens(nowMs) {
  for (const [id, entry] of tokenCache) {
    if (entry.expiresAt <= nowMs) tokenCache.delete(id);
  }
  while (tokenCache.size >= MAX_CACHED_TOKENS) {
    tokenCache.delete(tokenCache.keys().next().value);
  }
}
