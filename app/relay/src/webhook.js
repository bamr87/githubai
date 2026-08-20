/**
 * Webhook pipeline: verify → deduplicate → apply lifecycle → route → gate → dispatch.
 *
 * Every delivery produces exactly one activity row, including the ones that go
 * nowhere. "Why didn't Claude run on my issue?" is the question a hosted relay
 * has to answer, and it can only answer it if ignored deliveries are recorded
 * with their reason rather than dropped silently.
 */

import { OUTCOMES } from "./store.js";
import { evaluatePolicy, loadPolicy } from "./policy.js";
import { installationRecord, lifecycleFor, mapEvent } from "./routing.js";
import { verifyWebhookSignature } from "./session.js";
import { text } from "./http.js";

export const DEFAULT_RATE_LIMIT_PER_MINUTE = 60;

export async function handleWebhook(request, ctx) {
  const { env, store, github, now } = ctx;
  const body = await request.text();

  const signature = request.headers.get("x-hub-signature-256");
  if (!(await verifyWebhookSignature(env.WEBHOOK_SECRET, signature, body))) {
    return text("bad signature", 401);
  }

  const event = request.headers.get("x-github-event") || "";
  const deliveryId = request.headers.get("x-github-delivery") || "";
  if (event === "ping") return text("pong", 200);

  let payload;
  try {
    payload = JSON.parse(body);
  } catch {
    return text("bad payload", 400);
  }

  const nowIso = new Date(now()).toISOString();
  const installationId = payload?.installation?.id || 0;

  // An operator redelivering from the App's Advanced tab must not double-fire.
  if (!(await store.claimDelivery(deliveryId, nowIso))) {
    return text("duplicate delivery", 200);
  }

  const lifecycle = lifecycleFor(event, payload);
  if (lifecycle) {
    const detail = await applyLifecycle(ctx, lifecycle, payload, nowIso);
    await store.recordActivity({
      installationId,
      event,
      action: payload.action || "",
      outcome: OUTCOMES.LIFECYCLE,
      detail,
      now: nowIso,
    });
    return text(`lifecycle: ${lifecycle.kind}`, 200);
  }

  const repo = payload?.repository?.full_name || "";
  const decision = mapEvent(event, payload);

  if (!installationId || !repo) {
    // Nothing to attribute this to; record it so the gap is visible, not silent.
    await store.recordActivity({
      installationId,
      repo,
      event,
      action: payload?.action || "",
      outcome: OUTCOMES.IGNORED,
      detail: "delivery has no installation or repository",
      now: nowIso,
    });
    return text("no installation/repository in payload", 200);
  }

  const base = {
    installationId,
    repo,
    event,
    action: payload.action || "",
    subject: decision.subject || "",
    now: nowIso,
  };

  if (decision.ignored) {
    await store.recordActivity({ ...base, outcome: OUTCOMES.IGNORED, detail: decision.ignored });
    return text(`ignored: ${decision.ignored}`, 200);
  }

  const installation = await ensureInstallation(ctx, installationId, payload, nowIso);
  if (installation.suspendedAt) {
    await store.recordActivity({
      ...base,
      dispatchType: decision.type,
      outcome: OUTCOMES.SUSPENDED,
      detail: "installation is suspended",
    });
    return text("installation suspended", 200);
  }

  const policy = await loadPolicy(ctx, installation);
  const verdict = evaluatePolicy(policy.document, { repo, dispatchType: decision.type });
  if (!verdict.allowed) {
    await store.recordActivity({
      ...base,
      dispatchType: decision.type,
      outcome: OUTCOMES.SKIPPED_POLICY,
      detail: verdict.reason,
    });
    return text(`skipped by org policy: ${verdict.reason}`, 200);
  }

  const limit = Number(env.RATE_LIMIT_PER_MINUTE || DEFAULT_RATE_LIMIT_PER_MINUTE);
  const windowStart = Math.floor(now() / 60000);
  const rate = await store.bumpRate(installationId, windowStart, limit);
  if (!rate.allowed) {
    await store.recordActivity({
      ...base,
      dispatchType: decision.type,
      outcome: OUTCOMES.RATE_LIMITED,
      detail: `${rate.count} dispatches in this minute exceeds limit ${limit}`,
    });
    // 429 marks the delivery failed in the App's UI, which is the signal an
    // operator needs. GitHub does not auto-retry, so this cannot storm.
    return text("rate limited", 429);
  }

  try {
    await github.dispatch(installationId, repo, decision.type, decision.payload);
  } catch (err) {
    // Give up the delivery claim: a transient failure has to stay redeliverable
    // from the App's Advanced tab, and nothing was dispatched to duplicate.
    await store.releaseDelivery(deliveryId);
    await store.recordActivity({
      ...base,
      dispatchType: decision.type,
      outcome: OUTCOMES.ERROR,
      detail: String(err?.message || err).slice(0, 500),
    });
    return text("dispatch failed", 502);
  }

  await store.addRepos(installationId, [repo], nowIso);
  await store.recordActivity({
    ...base,
    dispatchType: decision.type,
    outcome: OUTCOMES.DISPATCHED,
    detail: policy.error ? `policy stale: ${policy.error}`.slice(0, 500) : "",
  });
  return text(`dispatched ${decision.type}`, 202);
}

async function applyLifecycle(ctx, lifecycle, payload, nowIso) {
  const { store } = ctx;
  const record = installationRecord(payload);

  switch (lifecycle.kind) {
    case "installed":
      if (!record) return "installation payload had no id";
      await store.upsertInstallation({ ...record, now: nowIso });
      await store.addRepos(record.id, lifecycle.repos, nowIso);
      return `installed on ${record.accountLogin} (${lifecycle.repos.length} repos)`;

    case "uninstalled":
      if (!record) return "installation payload had no id";
      await store.deleteInstallation(record.id);
      return `uninstalled from ${record.accountLogin}`;

    case "suspended":
      if (!record) return "installation payload had no id";
      await store.upsertInstallation({ ...record, suspendedAt: lifecycle.at, now: nowIso });
      return `suspended ${record.accountLogin}`;

    case "unsuspended":
      if (!record) return "installation payload had no id";
      await store.upsertInstallation({ ...record, suspendedAt: null, now: nowIso });
      return `unsuspended ${record.accountLogin}`;

    case "updated":
      if (record) await store.upsertInstallation({ ...record, now: nowIso });
      return `installation ${payload.action || "updated"}`;

    case "repos-changed": {
      if (!record) return "installation payload had no id";
      await store.upsertInstallation({ ...record, now: nowIso });
      await store.addRepos(record.id, lifecycle.added, nowIso);
      await store.removeRepos(record.id, lifecycle.removed);
      return `+${lifecycle.added.length} / -${lifecycle.removed.length} repos`;
    }

    case "plan-changed":
      if (!lifecycle.account) return "marketplace event had no account";
      await store.setPlan(lifecycle.account, lifecycle.plan, nowIso);
      return `${lifecycle.account} plan: ${lifecycle.plan}`;

    default:
      return lifecycle.kind;
  }
}

/**
 * Return the tenant record, seeding it from the delivery when absent — an App
 * installed before the relay (or after a database restore) must not go dark.
 */
async function ensureInstallation(ctx, installationId, payload, nowIso) {
  const existing = await ctx.store.getInstallation(installationId);
  if (existing) return existing;

  const owner = payload?.repository?.owner || {};
  const seeded = {
    id: installationId,
    accountLogin: owner.login || "",
    accountType: owner.type || "Organization",
    targetType: owner.type || "Organization",
    repositorySelection: "selected",
    suspendedAt: null,
  };
  await ctx.store.upsertInstallation({ ...seeded, now: nowIso });
  return { ...seeded, plan: "free", repos: [] };
}
