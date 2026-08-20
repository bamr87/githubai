# Seed telemetry ledger

`evolution.jsonl` is the append-only record of this repo's autonomous growth: one JSON line per grow tick, schema `seed-telemetry/v1`, appended deterministically by the `seed-grow.yml` workflow (never by a model pass).

```json
{"schema":"seed-telemetry/v1","run_id":"123456","repo":"__SEED_REPO__","tick":"G1-T1","conclusion":"published","passes":{"plan":"success","build":"success","verify":"success","fallback":"skipped"},"changed_files":7,"cost_usd":1.42,"num_turns":38,"started":"2026-01-01T04:17:00Z","ended":"2026-01-01T04:29:00Z"}
```

Contract rules: lines are never edited or deleted (corrections append); `cost_usd` / `num_turns` come from the Claude Code execution output when parseable and are `null` otherwise — never fabricated; the ledger rides each grow PR, so it merges together with the content it describes and the default branch stays protected.
