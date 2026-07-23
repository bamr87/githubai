#!/usr/bin/env python3
"""Resolve the effective GitHubAI configuration for a repository.

Merges three layers, later layers winning:

  1. profiles/_base.yml            (framework defaults)
  2. profiles/<repo.type>.yml      (repo-type standards)
  3. <repo>/.github/githubai.yml   (per-repo overrides; optional)

Maps merge recursively; lists and scalars are replaced. The consumer config
is read first only to learn `repo.type`, then re-applied on top of the
profile so its own overrides always win.

Outputs (GitHub Actions $GITHUB_OUTPUT format, or human-readable with
--print):

  config          merged config as single-line JSON
  type            resolved repo type
  model           claude.model override ("" = action default)
  max_turns       claude.max_turns
  <area>_enabled  "true"/"false" per automation area
  prompt_context  markdown block describing the repo's standards, injected
                  into every Claude prompt by the workflows
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only on bare runners
    sys.stderr.write(
        "load_config: PyYAML is required (pip install pyyaml)\n"
    )
    sys.exit(3)

AUTOMATION_AREAS = (
    "triage",
    "implement",
    "review",
    "auto_merge",
    "maintenance",
    "release",
)

OUTPUT_DELIMITER = "GHAI_EOF"


def deep_merge(base: dict, override: dict) -> dict:
    """Return base with override applied; maps recurse, everything else replaces."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise SystemExit(f"load_config: {path} must contain a YAML mapping")
    return data


def available_profiles(profiles_dir: Path) -> list[str]:
    return sorted(
        p.stem for p in profiles_dir.glob("*.yml") if not p.stem.startswith("_")
    )


def resolve(profiles_dir: Path, config_path: Path) -> tuple[dict, bool]:
    """Return (merged config, config_file_found)."""
    base = load_yaml(profiles_dir / "_base.yml")

    repo_config: dict = {}
    found = config_path.is_file()
    if found:
        repo_config = load_yaml(config_path)

    repo_type = str(
        (repo_config.get("repo") or {}).get("type")
        or (base.get("repo") or {}).get("type")
        or "base"
    )

    merged = base
    if repo_type != "base":
        profile_path = profiles_dir / f"{repo_type}.yml"
        if not profile_path.is_file():
            raise SystemExit(
                f"load_config: unknown repo.type '{repo_type}' — "
                f"available profiles: {', '.join(available_profiles(profiles_dir))}"
            )
        merged = deep_merge(merged, load_yaml(profile_path))
    merged = deep_merge(merged, repo_config)
    merged.setdefault("repo", {})["type"] = repo_type
    return merged, found


def build_prompt_context(config: dict, config_found: bool) -> str:
    """Render the standards block that workflows inject into Claude prompts."""
    repo = config.get("repo", {})
    profile = config.get("profile", {})
    standards = config.get("standards", {})
    automation = config.get("automation", {})
    labels = config.get("labels", {})

    lines: list[str] = ["## Repository standards (from GitHubAI config)", ""]
    lines.append(f"- Repo type: {repo.get('type', 'base')}")
    if repo.get("purpose"):
        lines.append(f"- Purpose: {repo['purpose']}")
    if repo.get("primary_language"):
        lines.append(f"- Primary language: {repo['primary_language']}")
    if not config_found:
        lines.append(
            "- Note: no .github/githubai.yml found; framework defaults apply."
        )
    lines.append("")

    guidance = str(profile.get("guidance", "")).strip()
    if guidance:
        lines.append(guidance)
        lines.append("")

    conventions = []
    if standards.get("commit_convention"):
        conventions.append(f"- Commit convention: {standards['commit_convention']}")
    if standards.get("branching"):
        conventions.append(f"- Branching: {standards['branching']}")
    if standards.get("test_command"):
        conventions.append(
            f"- Run tests with: `{standards['test_command']}` "
            "(a change is not done until this passes)"
        )
    if standards.get("lint_command"):
        conventions.append(f"- Run lint with: `{standards['lint_command']}`")
    if standards.get("required_files"):
        conventions.append(
            "- Required files: " + ", ".join(standards["required_files"])
        )
    if conventions:
        lines.append("### Conventions")
        lines.append("")
        lines.extend(conventions)
        lines.append("")

    docs_expectations = standards.get("docs_expectations") or []
    if docs_expectations:
        lines.append("### Documentation expectations")
        lines.append("")
        lines.extend(f"- {item}" for item in docs_expectations)
        lines.append("")

    focus = (automation.get("review") or {}).get("focus") or []
    if focus:
        lines.append("### Review focus for this repo type")
        lines.append("")
        lines.extend(f"- {item}" for item in focus)
        lines.append("")

    lines.append("### Automation posture")
    lines.append("")
    triage = automation.get("triage") or {}
    lines.append(
        "- Triage: "
        + ("enabled" if triage.get("enabled") else "disabled")
        + f"; dedupe={'on' if triage.get('dedupe') else 'off'}"
        + f", ask_clarifying={'on' if triage.get('ask_clarifying') else 'off'}"
        + f", auto_implement_labels={triage.get('auto_implement_labels') or []}"
    )
    implement = automation.get("implement") or {}
    lines.append(
        "- Implement: "
        + ("enabled" if implement.get("enabled") else "disabled")
        + f"; trigger_label={implement.get('trigger_label', 'claude:implement')}"
        + f", branch_prefix={implement.get('branch_prefix', 'claude/')}"
        + f", draft_pr={'yes' if implement.get('draft_pr') else 'no'}"
    )
    auto_merge = automation.get("auto_merge") or {}
    lines.append(
        "- Auto-merge: "
        + ("enabled" if auto_merge.get("enabled") else "disabled")
        + f"; trigger_label={auto_merge.get('trigger_label', 'claude:auto-merge')}"
        + f", max_risk={auto_merge.get('max_risk', 'low')}"
        + f", method={auto_merge.get('method', 'squash')}"
        + f", allowed_authors={auto_merge.get('allowed_authors') or []}"
        + f", allowed_paths={auto_merge.get('allowed_paths') or []}"
    )
    maintenance = automation.get("maintenance") or {}
    lines.append(
        "- Maintenance: "
        + ("enabled" if maintenance.get("enabled") else "disabled")
        + f"; tasks={maintenance.get('tasks') or []}"
        + f", max_issues_per_run={maintenance.get('max_issues_per_run', 3)}"
        + f", auto_fix_docs={'yes' if maintenance.get('auto_fix_docs') else 'no'}"
    )
    release = automation.get("release") or {}
    lines.append(
        "- Release: "
        + ("enabled" if release.get("enabled") else "disabled")
        + f"; draft={'yes' if release.get('draft') else 'no'}"
        + f", update_changelog={'yes' if release.get('update_changelog') else 'no'}"
    )
    lines.append("")

    taxonomy = labels.get("taxonomy") or []
    if taxonomy:
        lines.append("### Label taxonomy")
        lines.append("")
        lines.append(
            "Use only these labels (create nothing new without being asked):"
        )
        lines.extend(
            f"- `{entry['name']}` — {entry.get('description', '')}"
            for entry in taxonomy
            if isinstance(entry, dict) and entry.get("name")
        )
        lines.append("")

    text = "\n".join(lines).strip() + "\n"
    # The delimiter must never appear in the heredoc body.
    return text.replace(OUTPUT_DELIMITER, "GHAI-EOF")


def emit_outputs(config: dict, config_found: bool, out) -> None:
    claude = config.get("claude", {})
    automation = config.get("automation", {})

    def write(key: str, value: str) -> None:
        out.write(f"{key}={value}\n")

    write("config", json.dumps(config, separators=(",", ":"), sort_keys=True))
    write("type", str(config.get("repo", {}).get("type", "base")))
    write("model", str(claude.get("model", "") or ""))
    write("max_turns", str(claude.get("max_turns", 50)))
    for area in AUTOMATION_AREAS:
        enabled = bool((automation.get(area) or {}).get("enabled", False))
        write(f"{area}_enabled", "true" if enabled else "false")
    prompt_context = build_prompt_context(config, config_found)
    out.write(f"prompt_context<<{OUTPUT_DELIMITER}\n{prompt_context}{OUTPUT_DELIMITER}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=".github/githubai.yml",
        help="path to the consumer repo's config (default: .github/githubai.yml)",
    )
    parser.add_argument(
        "--profiles-dir",
        required=True,
        help="directory containing _base.yml and the repo-type profiles",
    )
    parser.add_argument(
        "--print",
        dest="human",
        action="store_true",
        help="pretty-print the merged config and prompt context to stdout",
    )
    args = parser.parse_args()

    profiles_dir = Path(args.profiles_dir)
    if not (profiles_dir / "_base.yml").is_file():
        raise SystemExit(f"load_config: no _base.yml in {profiles_dir}")

    config, found = resolve(profiles_dir, Path(args.config))

    if args.human:
        print(json.dumps(config, indent=2, sort_keys=True))
        print()
        print(build_prompt_context(config, found))
        return 0

    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as fh:
            emit_outputs(config, found, fh)
    else:
        emit_outputs(config, found, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
