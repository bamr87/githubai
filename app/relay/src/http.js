/** Response helpers with the relay's standard security headers. */

const BASE_HEADERS = {
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
  "x-frame-options": "DENY",
  "cache-control": "no-store",
};

export function text(body, status = 200, headers = {}) {
  return new Response(body, {
    status,
    headers: { ...BASE_HEADERS, "content-type": "text/plain; charset=utf-8", ...headers },
  });
}

export function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { ...BASE_HEADERS, "content-type": "application/json; charset=utf-8", ...headers },
  });
}

/**
 * HTML with a strict CSP. The dashboard ships one inline <style> block and no
 * scripts at all, so a style nonce is the entire allowance — nothing loads from
 * a third party and no script can execute even if markup escaping ever slipped.
 */
export function html(body, { status = 200, nonce = "", formAction = "'self'", headers = {} } = {}) {
  const csp = [
    "default-src 'none'",
    `style-src 'nonce-${nonce}'`,
    "img-src 'self' data:",
    // Only the App Manifest page overrides this, to post the manifest to GitHub.
    `form-action ${formAction}`,
    "base-uri 'none'",
    "frame-ancestors 'none'",
  ].join("; ");
  return new Response(body, {
    status,
    headers: {
      ...BASE_HEADERS,
      "content-type": "text/html; charset=utf-8",
      "content-security-policy": csp,
      ...headers,
    },
  });
}

/**
 * `extra` may be a plain object, a Headers, or an array of [name, value] pairs.
 * The array form exists because a response can carry several Set-Cookie headers
 * and comma-folding them into one is not reliably parsed.
 */
export function redirect(location, extra = {}) {
  const headers = new Headers({ ...BASE_HEADERS, location });
  const pairs = Array.isArray(extra)
    ? extra
    : extra instanceof Headers
      ? [...extra]
      : Object.entries(extra);
  for (const [name, value] of pairs) headers.append(name, value);
  return new Response(null, { status: 302, headers });
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function randomNonce() {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}
