-- GitHubAI hosted relay — D1 schema.
--
-- Apply (idempotent):
--   wrangler d1 execute githubai --remote --file=schema.sql
--
-- What this database deliberately does NOT hold: repository code, issue or PR
-- bodies, Claude Code OAuth tokens, GitHub user tokens, or any model traffic.
-- It holds installation metadata, cached org policy (which lives canonically
-- in the org's own .github repo), and routing telemetry. See app/DATA-HANDLING.md.

CREATE TABLE IF NOT EXISTS installations (
  id                    INTEGER PRIMARY KEY,
  account_login         TEXT    NOT NULL,
  account_type          TEXT    NOT NULL DEFAULT 'Organization',
  target_type           TEXT    NOT NULL DEFAULT 'Organization',
  repository_selection  TEXT    NOT NULL DEFAULT 'selected',
  plan                  TEXT    NOT NULL DEFAULT 'free',
  suspended_at          TEXT,
  created_at            TEXT    NOT NULL,
  updated_at            TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS installations_account ON installations (account_login);

CREATE TABLE IF NOT EXISTS installation_repos (
  installation_id  INTEGER NOT NULL,
  full_name        TEXT    NOT NULL,
  added_at         TEXT    NOT NULL,
  PRIMARY KEY (installation_id, full_name)
);

-- Webhook idempotency: an operator redelivering a webhook must not double-fire
-- repository_dispatch. Rows are pruned with the activity log.
CREATE TABLE IF NOT EXISTS deliveries (
  delivery_id  TEXT PRIMARY KEY,
  received_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  installation_id  INTEGER NOT NULL,
  repo_full_name   TEXT    NOT NULL DEFAULT '',
  event            TEXT    NOT NULL,
  action           TEXT    NOT NULL DEFAULT '',
  dispatch_type    TEXT    NOT NULL DEFAULT '',
  subject          TEXT    NOT NULL DEFAULT '',
  outcome          TEXT    NOT NULL,
  detail           TEXT    NOT NULL DEFAULT '',
  created_at       TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS activity_installation ON activity (installation_id, id DESC);
CREATE INDEX IF NOT EXISTS activity_created ON activity (created_at);

-- Cache of the org policy document fetched from <account>/.github. The source
-- of truth is always that repository; this is a TTL cache, never an edit target.
CREATE TABLE IF NOT EXISTS policy_cache (
  installation_id  INTEGER PRIMARY KEY,
  source           TEXT    NOT NULL,
  document         TEXT    NOT NULL,
  error            TEXT    NOT NULL DEFAULT '',
  fetched_at       TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS rate_limits (
  installation_id  INTEGER PRIMARY KEY,
  window_start     INTEGER NOT NULL,
  count            INTEGER NOT NULL
);
