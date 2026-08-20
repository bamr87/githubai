/**
 * Multi-tenant state for the hosted relay.
 *
 * Two interchangeable implementations behind one interface: `d1Store` for
 * Cloudflare D1 in production, `memoryStore` for tests and `wrangler dev`
 * without a database. Keeping every SQL statement in this file means the rest
 * of the relay is storage-agnostic and fully testable off-platform.
 *
 * Schema: schema.sql. Scope of what is stored: app/DATA-HANDLING.md.
 */

const ACTIVITY_RETENTION_DAYS = 30;

/** Outcomes recorded in the activity log; the dashboard groups by these. */
export const OUTCOMES = {
  DISPATCHED: "dispatched",
  IGNORED: "ignored",
  SKIPPED_POLICY: "skipped-policy",
  SUSPENDED: "suspended",
  RATE_LIMITED: "rate-limited",
  DUPLICATE: "duplicate",
  ERROR: "error",
  LIFECYCLE: "lifecycle",
};

/**
 * Shared fallback used when no D1 binding is bound (`wrangler dev` without a
 * database, and tests). Module-level so state survives across requests within
 * an isolate — a per-request store would silently disable deduplication,
 * rate limiting, and policy caching.
 */
let fallbackStore = null;

export function createStore(env) {
  if (env && env.DB && typeof env.DB.prepare === "function") return d1Store(env.DB);
  if (!fallbackStore) fallbackStore = memoryStore();
  return fallbackStore;
}

/** Test seam: drop the shared in-memory state. */
export function resetFallbackStore() {
  fallbackStore = null;
}

export function d1Store(db) {
  const run = (sql, ...params) => db.prepare(sql).bind(...params).run();
  const first = (sql, ...params) => db.prepare(sql).bind(...params).first();
  const all = async (sql, ...params) => (await db.prepare(sql).bind(...params).all()).results || [];

  return {
    kind: "d1",

    async claimDelivery(deliveryId, now) {
      if (!deliveryId) return true;
      try {
        await run("INSERT INTO deliveries (delivery_id, received_at) VALUES (?, ?)", deliveryId, now);
        return true;
      } catch (err) {
        // Only a key conflict means "already handled". Any other failure - a D1
        // outage, say - must surface as a 500 so GitHub records a failed
        // delivery; swallowing it here would silently drop every event.
        if (/UNIQUE|PRIMARY KEY|constraint/i.test(String(err?.message || err))) return false;
        throw err;
      }
    },

    async releaseDelivery(deliveryId) {
      if (!deliveryId) return;
      await run("DELETE FROM deliveries WHERE delivery_id = ?", deliveryId);
    },

    async upsertInstallation(rec) {
      await run(
        `INSERT INTO installations
           (id, account_login, account_type, target_type, repository_selection, suspended_at, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
         ON CONFLICT(id) DO UPDATE SET
           account_login = excluded.account_login,
           account_type = excluded.account_type,
           target_type = excluded.target_type,
           repository_selection = excluded.repository_selection,
           suspended_at = excluded.suspended_at,
           updated_at = excluded.updated_at`,
        rec.id,
        rec.accountLogin,
        rec.accountType || "Organization",
        rec.targetType || "Organization",
        rec.repositorySelection || "selected",
        rec.suspendedAt || null,
        rec.now,
        rec.now,
      );
    },

    async deleteInstallation(id) {
      await run("DELETE FROM installation_repos WHERE installation_id = ?", id);
      await run("DELETE FROM policy_cache WHERE installation_id = ?", id);
      await run("DELETE FROM rate_limits WHERE installation_id = ?", id);
      await run("DELETE FROM installations WHERE id = ?", id);
    },

    async setSuspended(id, suspendedAt, now) {
      await run(
        "UPDATE installations SET suspended_at = ?, updated_at = ? WHERE id = ?",
        suspendedAt,
        now,
        id,
      );
    },

    async setPlan(accountLogin, plan, now) {
      await run(
        "UPDATE installations SET plan = ?, updated_at = ? WHERE account_login = ?",
        plan,
        now,
        accountLogin,
      );
    },

    async addRepos(id, fullNames, now) {
      for (const fullName of fullNames) {
        await run(
          "INSERT OR IGNORE INTO installation_repos (installation_id, full_name, added_at) VALUES (?, ?, ?)",
          id,
          fullName,
          now,
        );
      }
    },

    async removeRepos(id, fullNames) {
      for (const fullName of fullNames) {
        await run(
          "DELETE FROM installation_repos WHERE installation_id = ? AND full_name = ?",
          id,
          fullName,
        );
      }
    },

    async getInstallation(id) {
      const row = await first("SELECT * FROM installations WHERE id = ?", id);
      if (!row) return null;
      const repos = await all(
        "SELECT full_name FROM installation_repos WHERE installation_id = ? ORDER BY full_name",
        id,
      );
      return toInstallation(row, repos.map((r) => r.full_name));
    },

    async listInstallations(ids) {
      if (!ids.length) return [];
      const placeholders = ids.map(() => "?").join(",");
      const rows = await all(
        `SELECT * FROM installations WHERE id IN (${placeholders}) ORDER BY account_login`,
        ...ids,
      );
      const repos = await all(
        `SELECT installation_id, full_name FROM installation_repos
          WHERE installation_id IN (${placeholders}) ORDER BY full_name`,
        ...ids,
      );
      return rows.map((row) =>
        toInstallation(
          row,
          repos.filter((r) => r.installation_id === row.id).map((r) => r.full_name),
        ),
      );
    },

    async recordActivity(rec) {
      await run(
        `INSERT INTO activity
           (installation_id, repo_full_name, event, action, dispatch_type, subject, outcome, detail, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        rec.installationId || 0,
        rec.repo || "",
        rec.event || "",
        rec.action || "",
        rec.dispatchType || "",
        rec.subject || "",
        rec.outcome,
        rec.detail || "",
        rec.now,
      );
    },

    async listActivity(ids, limit) {
      if (!ids.length) return [];
      const placeholders = ids.map(() => "?").join(",");
      const rows = await all(
        `SELECT * FROM activity WHERE installation_id IN (${placeholders})
          ORDER BY id DESC LIMIT ?`,
        ...ids,
        limit,
      );
      return rows.map(toActivity);
    },

    async bumpRate(id, windowStart, limit) {
      const row = await first(
        `INSERT INTO rate_limits (installation_id, window_start, count) VALUES (?, ?, 1)
         ON CONFLICT(installation_id) DO UPDATE SET
           count = CASE WHEN rate_limits.window_start = excluded.window_start THEN rate_limits.count + 1 ELSE 1 END,
           window_start = excluded.window_start
         RETURNING count`,
        id,
        windowStart,
      );
      const count = row ? row.count : 1;
      return { count, allowed: count <= limit };
    },

    async getPolicy(id) {
      const row = await first("SELECT * FROM policy_cache WHERE installation_id = ?", id);
      return row ? toPolicy(row) : null;
    },

    async setPolicy(id, entry) {
      await run(
        `INSERT INTO policy_cache (installation_id, source, document, error, fetched_at)
         VALUES (?, ?, ?, ?, ?)
         ON CONFLICT(installation_id) DO UPDATE SET
           source = excluded.source, document = excluded.document,
           error = excluded.error, fetched_at = excluded.fetched_at`,
        id,
        entry.source || "",
        JSON.stringify(entry.document ?? null),
        entry.error || "",
        entry.fetchedAt,
      );
    },

    async prune(cutoffIso) {
      await run("DELETE FROM activity WHERE created_at < ?", cutoffIso);
      await run("DELETE FROM deliveries WHERE received_at < ?", cutoffIso);
    },

    async health() {
      const row = await first(
        "SELECT (SELECT COUNT(*) FROM installations) AS installations, (SELECT COUNT(*) FROM activity) AS activity",
      );
      return { installations: row?.installations ?? 0, activity: row?.activity ?? 0 };
    },
  };
}

export function memoryStore() {
  const installations = new Map();
  const repos = new Map();
  const deliveries = new Map();
  const policies = new Map();
  const rates = new Map();
  const plans = new Map();
  let activity = [];
  let seq = 0;

  const reposOf = (id) => Array.from(repos.get(id) || []).sort();

  return {
    kind: "memory",

    async claimDelivery(deliveryId, now) {
      if (!deliveryId) return true;
      if (deliveries.has(deliveryId)) return false;
      deliveries.set(deliveryId, now);
      return true;
    },

    async releaseDelivery(deliveryId) {
      deliveries.delete(deliveryId);
    },

    async upsertInstallation(rec) {
      const existing = installations.get(rec.id);
      installations.set(rec.id, {
        id: rec.id,
        accountLogin: rec.accountLogin,
        accountType: rec.accountType || "Organization",
        targetType: rec.targetType || "Organization",
        repositorySelection: rec.repositorySelection || "selected",
        plan: plans.get(rec.accountLogin) || existing?.plan || "free",
        suspendedAt: rec.suspendedAt || null,
        createdAt: existing?.createdAt || rec.now,
        updatedAt: rec.now,
      });
    },

    async deleteInstallation(id) {
      installations.delete(id);
      repos.delete(id);
      policies.delete(id);
      rates.delete(id);
    },

    async setSuspended(id, suspendedAt, now) {
      const rec = installations.get(id);
      if (rec) installations.set(id, { ...rec, suspendedAt, updatedAt: now });
    },

    async setPlan(accountLogin, plan, now) {
      plans.set(accountLogin, plan);
      for (const [id, rec] of installations) {
        if (rec.accountLogin === accountLogin) {
          installations.set(id, { ...rec, plan, updatedAt: now });
        }
      }
    },

    async addRepos(id, fullNames) {
      if (!repos.has(id)) repos.set(id, new Set());
      for (const fullName of fullNames) repos.get(id).add(fullName);
    },

    async removeRepos(id, fullNames) {
      const set = repos.get(id);
      if (set) for (const fullName of fullNames) set.delete(fullName);
    },

    async getInstallation(id) {
      const rec = installations.get(id);
      return rec ? { ...rec, repos: reposOf(id) } : null;
    },

    async listInstallations(ids) {
      return ids
        .map((id) => installations.get(id))
        .filter(Boolean)
        .map((rec) => ({ ...rec, repos: reposOf(rec.id) }))
        .sort((a, b) => a.accountLogin.localeCompare(b.accountLogin));
    },

    async recordActivity(rec) {
      activity.unshift({
        id: ++seq,
        installationId: rec.installationId || 0,
        repo: rec.repo || "",
        event: rec.event || "",
        action: rec.action || "",
        dispatchType: rec.dispatchType || "",
        subject: rec.subject || "",
        outcome: rec.outcome,
        detail: rec.detail || "",
        createdAt: rec.now,
      });
    },

    async listActivity(ids, limit) {
      const wanted = new Set(ids);
      return activity.filter((row) => wanted.has(row.installationId)).slice(0, limit);
    },

    async bumpRate(id, windowStart, limit) {
      const current = rates.get(id);
      const count = current && current.windowStart === windowStart ? current.count + 1 : 1;
      rates.set(id, { windowStart, count });
      return { count, allowed: count <= limit };
    },

    async getPolicy(id) {
      return policies.get(id) || null;
    },

    async setPolicy(id, entry) {
      policies.set(id, {
        source: entry.source || "",
        document: entry.document ?? null,
        error: entry.error || "",
        fetchedAt: entry.fetchedAt,
      });
    },

    async prune(cutoffIso) {
      activity = activity.filter((row) => row.createdAt >= cutoffIso);
      for (const [id, at] of deliveries) if (at < cutoffIso) deliveries.delete(id);
    },

    async health() {
      return { installations: installations.size, activity: activity.length };
    },
  };
}

export function retentionCutoff(nowMs, days = ACTIVITY_RETENTION_DAYS) {
  return new Date(nowMs - days * 86400000).toISOString();
}

function toInstallation(row, repoNames) {
  return {
    id: row.id,
    accountLogin: row.account_login,
    accountType: row.account_type,
    targetType: row.target_type,
    repositorySelection: row.repository_selection,
    plan: row.plan,
    suspendedAt: row.suspended_at,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    repos: repoNames,
  };
}

function toActivity(row) {
  return {
    id: row.id,
    installationId: row.installation_id,
    repo: row.repo_full_name,
    event: row.event,
    action: row.action,
    dispatchType: row.dispatch_type,
    subject: row.subject,
    outcome: row.outcome,
    detail: row.detail,
    createdAt: row.created_at,
  };
}

function toPolicy(row) {
  let document = null;
  try {
    document = JSON.parse(row.document);
  } catch {
    document = null;
  }
  return { source: row.source, document, error: row.error, fetchedAt: row.fetched_at };
}
