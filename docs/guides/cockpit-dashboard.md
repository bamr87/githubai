# Multi-Repo DevOps Cockpit (Fleet Dashboard)

## Overview

The **DevOps Cockpit** evolves GitHubAI from a single-repo, action-oriented tool
into a **multi-repo, observation-oriented** dashboard: a single place to register
many GitHub repositories, continuously ingest signals from each, store time-series
metrics, surface them on a fleet dashboard, and let AI distill what needs attention.

It is implemented as an additive `dashboard` Django app and a `/fleet` page in the
React frontend. Nothing in the existing single-repo workflow changes.

## Architecture

The cockpit follows a **Repository registry → Signal ingestion → Metrics store →
Dashboards → AI orchestration** spine:

| Layer | Component |
|-------|-----------|
| Registry | `Organization`, `Repository`, `RepoConnection` models |
| Ingestion | `MetricsCollectorService` + Celery tasks (`ingest_repository_metrics`, `ingest_all_tracked_repositories`) |
| Metrics store | `RepoMetricSnapshot` (time-series, with a 0–100 `health_score`) |
| Dashboards | `/api/dashboard/fleet/...` endpoints + the React `/fleet` page |
| AI orchestration | `FleetDigestService` + `RepoDigest` model + digest tasks |

### Data model

- **`Organization`** — a GitHub org/owner that groups repositories.
- **`Repository`** — a first-class, registered repo (replaces the loose
  `github_repo` string elsewhere). Carries metadata (language, stars, archived)
  and an `is_tracked` watchlist flag.
- **`RepoConnection`** — references the credential used to access a repo
  (environment variable name or GitHub App installation id). **Never stores raw
  secrets.**
- **`RepoMetricSnapshot`** — a point-in-time capture of signals (open/stale PRs,
  open issues, CI success rate, security alerts, last release) plus a raw `data`
  JSON blob. Exposes a computed `health_score`.
- **`RepoDigest`** — an AI (or rule-based) "what needs attention" summary, scoped
  to a single repo or the whole fleet, with a severity level.

### Health score

`health_score` is a 0–100 heuristic:

```
100 − (1 − ci_success_rate) × 40 − min(security_alerts × 10, 30) − min(stale_prs × 3, 30)
```

## Getting started

### 1. Register repositories

```bash
# Register and add to the ingestion watchlist
python manage.py register_repo --repo owner/repo

# Register without tracking (no scheduled ingestion)
python manage.py register_repo --repo owner/repo --no-track
```

Or via the API (requires authentication):

```bash
curl -X POST http://localhost:8000/api/dashboard/repositories/register/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "owner/repo", "is_tracked": true}'
```

### 2. Ingest metrics

```bash
# One repo
python manage.py ingest_metrics --repo owner/repo

# All tracked repos
python manage.py ingest_metrics
```

For continuous ingestion, schedule `ingest_all_tracked_repositories` with Celery
Beat. Collectors degrade gracefully: a single failing GitHub endpoint records zero
for that signal rather than aborting the whole snapshot.

### 3. View the fleet dashboard

Run the frontend (`npm run dev` in `frontend/`) and open `/fleet`. The page shows:

- **Aggregate KPIs** — repositories, open PRs, stale PRs, open issues, failing CI,
  security alerts across the whole fleet.
- **Repository health grid** — one row per repo with a health bar, PR/issue counts,
  CI success rate, security alert count, and last release.
- **Attention lists** — failing CI, open security alerts, and stale PRs across repos.
- **Fleet digest** — click *Generate Digest* for an AI-distilled briefing.

### 4. Generate an AI digest

```bash
# Fleet-wide
python manage.py fleet_digest --fleet

# Single repo
python manage.py fleet_digest --repo owner/repo

# Deterministic rule-based summary (no AI provider needed)
python manage.py fleet_digest --fleet --no-ai
```

The digest service reuses the multi-provider `AIService`. When no provider is
configured (or the call fails), it falls back to a deterministic rule-based
summary so the cockpit remains useful without AI.

## REST API

All routes are under `/api/dashboard/`. Read endpoints are public; write/
orchestration actions require authentication.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/repositories/` | List registered repositories |
| POST | `/repositories/register/` | Register a repo (auth) |
| GET | `/repositories/{id}/snapshots/` | Snapshot history for a repo |
| POST | `/repositories/{id}/collect/` | Collect a snapshot now (auth) |
| POST | `/repositories/{id}/track/` · `/untrack/` | Toggle the watchlist (auth) |
| GET | `/snapshots/` | List metric snapshots |
| GET | `/digests/` | List AI digests |
| GET | `/fleet/overview/` | Aggregate KPIs + per-repo health grid |
| GET | `/fleet/attention/` | Cross-cutting "needs attention" lists |
| POST | `/fleet/digest/` | Generate a fleet digest (auth) |

## Security

- `RepoConnection` stores only **references** to credentials (env var names /
  installation ids), never raw tokens.
- All write and orchestration endpoints are authentication-gated; read-only fleet
  views are public so the dashboard can render without a session.
- A GitHub App (per-installation tokens, higher rate limits, webhooks, per-repo
  scoping) is the recommended credential source at multi-repo scale.

## Roadmap

This is the foundational slice (Phases 0–1 plus API/AI entry points). Future
phases build on it: webhook-driven ingestion, DORA metrics and trend charts,
per-repo deep-dive pages, a conversational "fleet copilot", an agent framework
(monitor/linter/security/release agents), linting aggregation, and a general
alerting engine. See `PRD.md` for the full north-star.
