/**
 * Org-level policy for the hosted relay.
 *
 * The policy document lives in the tenant's own `<account>/.github` repository
 * at `.github/githubai-org.yml`, so org policy is version-controlled, reviewed,
 * and owned by the customer — the relay only caches it. That keeps "config over
 * code" intact and means the hosted service stores no configuration a customer
 * cannot see and revert in their own repo.
 *
 * Two invariants make this safe to apply at the routing layer:
 *
 *   1. **Subtractive only.** Policy can stop the relay from dispatching; it can
 *      never make a repo do something its own `.github/githubai.yml` disables.
 *      Every dispatch still lands in the repo's workflows, which re-check their
 *      own config, labels, and permissions.
 *   2. **Last known good wins.** A missing file means "no restrictions". A file
 *      that fails to fetch or parse does NOT silently unlock what the previous
 *      version locked: the last successfully parsed document keeps applying and
 *      the error is surfaced in the activity log and dashboard.
 */

import { DISPATCH_AREA } from "./routing.js";
import { parseYaml } from "./yaml.js";

export const POLICY_REPO = ".github";
export const POLICY_PATH = ".github/githubai-org.yml";

export const DEFAULT_POLICY_TTL_SECONDS = 300;
/** Re-check sooner after a failure so a fixed file takes effect quickly. */
export const ERROR_POLICY_TTL_SECONDS = 60;

/** Fetch (or reuse cached) org policy for an installation. */
export async function loadPolicy(ctx, installation) {
  const { store, github, now } = ctx;
  const ttl = Number(ctx.ttlSeconds ?? DEFAULT_POLICY_TTL_SECONDS);
  const cached = await store.getPolicy(installation.id);
  const source = `${installation.accountLogin}/${POLICY_REPO}/${POLICY_PATH}`;

  if (cached) {
    const age = (now() - Date.parse(cached.fetchedAt)) / 1000;
    const limit = cached.error ? Math.min(ttl, ERROR_POLICY_TTL_SECONDS) : ttl;
    if (Number.isFinite(age) && age < limit) return { ...cached, cached: true };
  }

  let document = null;
  let error = "";
  try {
    const text = await github.readFile(
      installation.id,
      `${installation.accountLogin}/${POLICY_REPO}`,
      POLICY_PATH,
    );
    document = text === null ? null : normalizePolicy(parseYaml(text));
  } catch (err) {
    error = String(err?.message || err);
    // Keep enforcing the last document we understood rather than failing open.
    document = cached ? cached.document : null;
  }

  const entry = {
    source,
    document,
    error,
    fetchedAt: new Date(now()).toISOString(),
  };
  await store.setPolicy(installation.id, entry);
  return { ...entry, cached: false };
}

/** Reduce a parsed YAML document to the subset the relay acts on. */
export function normalizePolicy(raw) {
  if (raw === null || raw === undefined) return null;
  if (typeof raw !== "object" || Array.isArray(raw)) {
    throw new Error("org policy must be a YAML mapping");
  }
  const org = isMap(raw.org) ? raw.org : {};
  const repos = isMap(org.repos) ? org.repos : {};
  const automation = isMap(raw.automation) ? raw.automation : {};

  const areas = {};
  for (const area of new Set(Object.values(DISPATCH_AREA))) {
    const entry = automation[area];
    if (isMap(entry) && typeof entry.enabled === "boolean") areas[area] = entry.enabled;
    else if (typeof entry === "boolean") areas[area] = entry;
  }

  return {
    enabled: org.enabled === undefined ? true : Boolean(org.enabled),
    include: toGlobList(repos.include),
    exclude: toGlobList(repos.exclude),
    automation: areas,
  };
}

/**
 * Decide whether policy permits a dispatch.
 * Returns `{allowed: true}` or `{allowed: false, reason}`.
 */
export function evaluatePolicy(policy, { repo, dispatchType }) {
  if (!policy) return { allowed: true };

  if (policy.enabled === false) {
    return { allowed: false, reason: "org policy sets org.enabled: false" };
  }

  const name = repoName(repo);
  if (policy.include.length && !policy.include.some((g) => globMatch(g, repo, name))) {
    return { allowed: false, reason: `${repo} is not in org.repos.include` };
  }
  if (policy.exclude.some((g) => globMatch(g, repo, name))) {
    return { allowed: false, reason: `${repo} matches org.repos.exclude` };
  }

  const area = DISPATCH_AREA[dispatchType];
  if (area && policy.automation[area] === false) {
    return { allowed: false, reason: `org policy disables automation.${area}` };
  }
  return { allowed: true };
}

/** Glob with `*` and `?`, matched against both `owner/name` and bare `name`. */
export function globMatch(pattern, fullName, name) {
  const re = new RegExp(
    "^" +
      String(pattern)
        .replace(/[.+^${}()|[\]\\]/g, "\\$&")
        .replace(/\*/g, "[^]*")
        .replace(/\?/g, "[^]") +
      "$",
  );
  return re.test(fullName) || re.test(name);
}

function repoName(fullName) {
  const slash = String(fullName).indexOf("/");
  return slash === -1 ? String(fullName) : String(fullName).slice(slash + 1);
}

function toGlobList(value) {
  if (typeof value === "string") return [value];
  if (!Array.isArray(value)) return [];
  return value.filter((item) => typeof item === "string" && item !== "");
}

function isMap(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
