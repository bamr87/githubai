/**
 * Webhook → dispatch mapping. Pure functions, no I/O, so the routing contract
 * is fully unit-testable.
 *
 * The rule this file exists to enforce: **app mode must gate exactly like
 * Actions mode**. A reusable workflow reached via `repository_dispatch` cannot
 * re-check `github.event.issue.labels` (there is no issue in the event), so the
 * `claude:skip` opt-out, the bot-author exclusion, and the fork/draft rules are
 * applied here instead. Routing that is laxer than the direct-event path would
 * be a silent privilege escalation for app-mode tenants.
 */

export const DISPATCH_PREFIX = "githubai";

export const DISPATCH_TYPES = {
  triage: `${DISPATCH_PREFIX}-triage`,
  implement: `${DISPATCH_PREFIX}-implement`,
  review: `${DISPATCH_PREFIX}-review`,
  autoMerge: `${DISPATCH_PREFIX}-auto-merge`,
  maintenance: `${DISPATCH_PREFIX}-maintenance`,
};

/** Areas in githubai.yml `automation:` that gate each dispatch type. */
export const DISPATCH_AREA = {
  [DISPATCH_TYPES.triage]: "triage",
  [DISPATCH_TYPES.implement]: "implement",
  [DISPATCH_TYPES.review]: "review",
  [DISPATCH_TYPES.autoMerge]: "auto_merge",
  [DISPATCH_TYPES.maintenance]: "maintenance",
};

export const SKIP_LABEL = "claude:skip";
export const IMPLEMENT_LABEL = "claude:implement";
export const REVIEW_LABEL = "claude:review";
export const AUTO_MERGE_LABEL = "claude:auto-merge";

/** PR authors whose PRs enter the auto-merge lane without a maintainer label. */
export const AUTO_MERGE_AUTHORS = ["dependabot[bot]", "renovate[bot]"];

/**
 * Map a webhook to a dispatch decision.
 *
 * Returns `{type, payload, subject}` to dispatch, or `{ignored: reason}`.
 * Never returns null, so every delivery produces an auditable activity row.
 */
export function mapEvent(event, payload) {
  const action = payload?.action || "";

  if (event === "issues") return mapIssue(action, payload);
  if (event === "pull_request") return mapPullRequest(action, payload);
  return ignored(`event '${event}' is not routed`);
}

function mapIssue(action, payload) {
  const issue = payload.issue || {};
  const number = issue.number;
  if (!number) return ignored("issue payload has no number");
  const labels = labelNames(issue.labels);
  const subject = `#${number}`;

  if (labels.includes(SKIP_LABEL)) return ignored(`${SKIP_LABEL} label present`, subject);

  if (action === "opened" || action === "reopened") {
    // Mirrors claude-triage.yml: bot-authored issues (including Claude's own
    // maintenance issues) arrive pre-labeled and are not re-triaged.
    if (issue.user && issue.user.type === "Bot") return ignored("issue authored by a bot", subject);
    return dispatch(DISPATCH_TYPES.triage, { issue_number: String(number) }, subject);
  }

  if (action === "labeled" && payload.label?.name === IMPLEMENT_LABEL) {
    return dispatch(DISPATCH_TYPES.implement, { issue_number: String(number) }, subject);
  }

  return ignored(`issues.${action || "?"} is not routed`, subject);
}

function mapPullRequest(action, payload) {
  const pr = payload.pull_request || {};
  const number = pr.number;
  if (!number) return ignored("pull_request payload has no number");
  const subject = `#${number}`;
  const labels = labelNames(pr.labels);

  if (labels.includes(SKIP_LABEL)) return ignored(`${SKIP_LABEL} label present`, subject);

  // Fork PRs never get secrets in Actions mode; do not route them here either.
  const sameRepo = pr.head?.repo?.full_name && pr.head.repo.full_name === payload.repository?.full_name;
  if (!sameRepo) return ignored("pull request is from a fork", subject);

  if (action === "opened" || action === "ready_for_review") {
    if (pr.draft) return ignored("pull request is a draft", subject);
    const trustedBot = action === "opened" && AUTO_MERGE_AUTHORS.includes(pr.user?.login);
    return trustedBot
      ? dispatch(DISPATCH_TYPES.autoMerge, { pr_number: String(number) }, subject)
      : dispatch(DISPATCH_TYPES.review, { pr_number: String(number) }, subject);
  }

  if (action === "labeled") {
    const name = payload.label?.name;
    if (name === AUTO_MERGE_LABEL) {
      return dispatch(DISPATCH_TYPES.autoMerge, { pr_number: String(number) }, subject);
    }
    if (name === REVIEW_LABEL) {
      return dispatch(DISPATCH_TYPES.review, { pr_number: String(number) }, subject);
    }
  }

  return ignored(`pull_request.${action || "?"} is not routed`, subject);
}

/**
 * Installation lifecycle: what a delivery means for the tenant record.
 * Returns `{kind, ...}` or null when the event carries no lifecycle meaning.
 */
export function lifecycleFor(event, payload) {
  const installation = payload?.installation;

  if (event === "installation") {
    const action = payload.action;
    if (action === "created") {
      return {
        kind: "installed",
        repos: (payload.repositories || []).map((repo) => repo.full_name).filter(Boolean),
      };
    }
    if (action === "deleted") return { kind: "uninstalled" };
    if (action === "suspend") return { kind: "suspended", at: installation?.suspended_at || nowIso() };
    if (action === "unsuspend") return { kind: "unsuspended" };
    return { kind: "updated" };
  }

  if (event === "installation_repositories") {
    return {
      kind: "repos-changed",
      added: (payload.repositories_added || []).map((repo) => repo.full_name).filter(Boolean),
      removed: (payload.repositories_removed || []).map((repo) => repo.full_name).filter(Boolean),
    };
  }

  if (event === "marketplace_purchase") {
    const purchase = payload.marketplace_purchase || {};
    const cancelled = payload.action === "cancelled";
    return {
      kind: "plan-changed",
      account: purchase.account?.login || "",
      plan: cancelled ? "free" : slug(purchase.plan?.name) || "free",
    };
  }

  return null;
}

/** Describe an installation payload as a tenant record. */
export function installationRecord(payload) {
  const installation = payload?.installation;
  if (!installation?.id) return null;
  return {
    id: installation.id,
    accountLogin: installation.account?.login || "",
    accountType: installation.account?.type || "Organization",
    targetType: installation.target_type || installation.account?.type || "Organization",
    repositorySelection: installation.repository_selection || "selected",
    suspendedAt: installation.suspended_at || null,
  };
}

function dispatch(type, payload, subject) {
  return { type, payload, subject };
}

function ignored(reason, subject = "") {
  return { ignored: reason, subject };
}

function labelNames(labels) {
  return Array.isArray(labels) ? labels.map((label) => label?.name).filter(Boolean) : [];
}

function slug(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function nowIso() {
  return new Date().toISOString();
}
