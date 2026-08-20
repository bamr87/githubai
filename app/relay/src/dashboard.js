/**
 * Read-only activity dashboard.
 *
 * Scope note: GitHubAI's PRD puts "a web UI beyond GitHub" out of scope, and
 * that still holds — this is not a place to read code, file issues, or talk to
 * Claude. It answers exactly one question a webhook relay owes its operators:
 * what did the router do with my org's events, and why. Everything actionable
 * still happens in GitHub.
 *
 * No scripts, no external assets, one nonce'd stylesheet (see http.js CSP).
 */

import { escapeHtml } from "./http.js";

const OUTCOME_LABELS = {
  dispatched: "dispatched",
  ignored: "ignored",
  "skipped-policy": "org policy",
  suspended: "suspended",
  "rate-limited": "rate limited",
  duplicate: "duplicate",
  error: "error",
  lifecycle: "lifecycle",
};

export function renderPage({ title, nonce, body, login = "" }) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)}</title>
<style nonce="${escapeHtml(nonce)}">${STYLE}</style>
</head>
<body>
<header class="bar">
  <span class="brand">GitHubAI<span class="dim"> relay</span></span>
  ${login ? `<span class="dim">${escapeHtml(login)} · <a href="/logout">sign out</a></span>` : ""}
</header>
<main>
${body}
</main>
<footer class="dim">
  Routing telemetry only. Claude runs in your repositories' own Actions, with your own token.
  <a href="https://github.com/bamr87/githubai">Docs</a>
</footer>
</body>
</html>
`;
}

export function renderLanding({ nonce, installUrl, signedOutReason = "" }) {
  const body = `
<h1>GitHubAI relay</h1>
<p>This service routes GitHub App events into each repository's own GitHubAI workflows. It never runs Claude, never reads your code, and never holds your tokens.</p>
${signedOutReason ? `<p class="notice">${escapeHtml(signedOutReason)}</p>` : ""}
<p class="actions">
  <a class="button" href="/login">Sign in with GitHub</a>
  ${installUrl ? `<a class="button ghost" href="${escapeHtml(installUrl)}">Install the app</a>` : ""}
</p>
<h2>What you can see here</h2>
<ul>
  <li>Which installations you administer, and which repositories they cover.</li>
  <li>Every webhook the relay handled: what it dispatched, ignored, or blocked — and why.</li>
  <li>Whether your org policy file parsed, and when it was last read.</li>
</ul>`;
  return renderPage({ title: "GitHubAI relay", nonce, body });
}

export function renderDashboard({ nonce, login, installations, activity, policies }) {
  const body = `
<h1>Activity</h1>
${installationsSection(installations, policies)}
${activitySection(activity, installations)}`;
  return renderPage({ title: "GitHubAI relay — activity", nonce, body, login });
}

function installationsSection(installations, policies) {
  if (!installations.length) {
    return `<p class="notice">No GitHubAI installations found for your account. <a href="/login">Re-authorize</a> after installing the app.</p>`;
  }
  const rows = installations
    .map((inst) => {
      const policy = policies.get(inst.id);
      return `<tr>
  <td><strong>${escapeHtml(inst.accountLogin)}</strong><div class="dim">${escapeHtml(inst.targetType)} · id ${escapeHtml(inst.id)}</div></td>
  <td>${inst.repositorySelection === "all" ? "all repositories" : `${inst.repos.length} selected`}
      <div class="dim">${escapeHtml(inst.repos.slice(0, 4).join(", "))}${inst.repos.length > 4 ? ` +${inst.repos.length - 4} more` : ""}</div></td>
  <td>${escapeHtml(inst.plan || "free")}</td>
  <td>${inst.suspendedAt ? `<span class="pill warn">suspended</span>` : `<span class="pill ok">active</span>`}</td>
  <td>${policyCell(policy)}</td>
</tr>`;
    })
    .join("\n");
  return `<section>
<h2>Installations</h2>
<table>
<thead><tr><th>Account</th><th>Repositories</th><th>Plan</th><th>Status</th><th>Org policy</th></tr></thead>
<tbody>
${rows}
</tbody>
</table>
</section>`;
}

function policyCell(policy) {
  if (!policy) return `<span class="dim">not read yet</span>`;
  if (policy.error) {
    return `<span class="pill warn">error</span><div class="dim">${escapeHtml(policy.error.slice(0, 160))}</div>
      <div class="dim">last good document still applies</div>`;
  }
  if (!policy.document) {
    // GitHub returns 404 both for "no such file" and "repo not in this
    // installation", so the empty case has to name the second possibility.
    return `<span class="dim">none — no policy file, or the <code>.github</code> repository is not part of this installation</span>`;
  }
  const areas = Object.entries(policy.document.automation || {})
    .filter(([, enabled]) => enabled === false)
    .map(([area]) => area);
  const bits = [];
  if (policy.document.enabled === false) bits.push("routing disabled");
  if (areas.length) bits.push(`off: ${areas.join(", ")}`);
  if (policy.document.include?.length) bits.push(`include ${policy.document.include.join(", ")}`);
  if (policy.document.exclude?.length) bits.push(`exclude ${policy.document.exclude.join(", ")}`);
  return `<span class="pill ok">loaded</span><div class="dim">${escapeHtml(bits.join(" · ") || "no restrictions")}</div>`;
}

function activitySection(activity, installations) {
  if (!activity.length) {
    return `<section><h2>Recent deliveries</h2><p class="notice">No deliveries recorded yet. Open an issue in a covered repository to see routing here.</p></section>`;
  }
  const accounts = new Map(installations.map((inst) => [inst.id, inst.accountLogin]));
  const rows = activity
    .map(
      (row) => `<tr>
  <td class="mono dim">${escapeHtml(row.createdAt)}</td>
  <td>${escapeHtml(row.repo || accounts.get(row.installationId) || "—")}${row.subject ? ` <span class="dim">${escapeHtml(row.subject)}</span>` : ""}</td>
  <td class="mono">${escapeHtml(row.event)}${row.action ? `.${escapeHtml(row.action)}` : ""}</td>
  <td class="mono">${escapeHtml(row.dispatchType || "—")}</td>
  <td><span class="pill ${outcomeClass(row.outcome)}">${escapeHtml(OUTCOME_LABELS[row.outcome] || row.outcome)}</span></td>
  <td class="dim">${escapeHtml(row.detail || "")}</td>
</tr>`,
    )
    .join("\n");
  return `<section>
<h2>Recent deliveries</h2>
<table>
<thead><tr><th>When (UTC)</th><th>Repository</th><th>Event</th><th>Dispatch</th><th>Outcome</th><th>Detail</th></tr></thead>
<tbody>
${rows}
</tbody>
</table>
</section>`;
}

function outcomeClass(outcome) {
  if (outcome === "dispatched") return "ok";
  if (outcome === "error") return "bad";
  if (outcome === "rate-limited" || outcome === "skipped-policy" || outcome === "suspended") return "warn";
  return "";
}

const STYLE = `
:root {
  color-scheme: light dark;
  --bg: #ffffff; --fg: #1f2328; --dim: #59636e; --line: #d1d9e0;
  --panel: #f6f8fa; --ok: #1a7f37; --warn: #9a6700; --bad: #cf222e; --link: #0969da;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117; --fg: #e6edf3; --dim: #9198a1; --line: #30363d;
    --panel: #151b23; --ok: #3fb950; --warn: #d29922; --bad: #f85149; --link: #4493f8;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}
a { color: var(--link); }
main { max-width: 1100px; margin: 0 auto; padding: 24px 20px 48px; }
.bar {
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
  padding: 12px 20px; border-bottom: 1px solid var(--line); background: var(--panel);
}
.brand { font-weight: 600; }
h1 { font-size: 22px; margin: 8px 0 16px; }
h2 { font-size: 16px; margin: 28px 0 10px; }
section { margin-bottom: 8px; }
table { width: 100%; border-collapse: collapse; display: block; overflow-x: auto; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-size: 12px; text-transform: uppercase; letter-spacing: .04em; color: var(--dim); font-weight: 600; }
.dim { color: var(--dim); font-size: 12px; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
.pill {
  display: inline-block; padding: 1px 8px; border-radius: 999px;
  border: 1px solid var(--line); font-size: 12px;
}
.pill.ok { color: var(--ok); border-color: var(--ok); }
.pill.warn { color: var(--warn); border-color: var(--warn); }
.pill.bad { color: var(--bad); border-color: var(--bad); }
.notice { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; }
.actions { display: flex; gap: 10px; flex-wrap: wrap; margin: 18px 0; }
.button {
  display: inline-block; padding: 7px 14px; border-radius: 6px; text-decoration: none;
  background: var(--link); color: #fff; font-weight: 500;
}
.button.ghost { background: transparent; color: var(--link); border: 1px solid var(--line); }
footer { max-width: 1100px; margin: 0 auto; padding: 0 20px 32px; }
ul { padding-left: 20px; }
`;
