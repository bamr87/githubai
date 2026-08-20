"""Tests for the AI-Seed planter/checker CLI (tools/seed.py) and the kernel.

These pin the framework's public contract: planting is additive-only and
idempotent, `check` enforces the constitution, kernel-managed vs user-owned
file semantics hold, and this repo's own plant (self-hosting) stays green
under strict parity.
"""

import re
from pathlib import Path

import pytest
import yaml

from tools.seed import (
    KERNEL_VERSION,
    SCHEMA_OPTIONAL,
    main,
    parse_simple_yaml,
)

REPO_ROOT = Path(__file__).parent.parent
KERNEL_DIR = REPO_ROOT / "seed" / "kernel"


def plant(target: Path, *extra: str) -> int:
    return main(["plant", str(target), "--repo", "bamr87/test-seed",
                 "--date", "2026-01-01", *extra])


class TestSimpleYamlParser:
    def test_nested_maps_scalars_comments(self):
        data = parse_simple_yaml(
            "# full-line comment\n"
            "schema: seed-manifest/v1\n"
            "policy:\n"
            "  cadence:\n"
            '    grow_cron: "17 4 * * 1"  # inline comment\n'
            "  models:\n"
            "    plan: claude-haiku-4-5\n"
            "kernel:\n"
            "  strict: false\n"
        )
        assert data["schema"] == "seed-manifest/v1"
        assert data["policy"]["cadence"]["grow_cron"] == "17 4 * * 1"
        assert data["policy"]["models"]["plan"] == "claude-haiku-4-5"
        assert data["kernel"]["strict"] == "false"

    def test_matches_pyyaml_on_the_kernel_manifest(self):
        # The mini-parser and PyYAML must agree on the real manifest subset.
        text = (REPO_ROOT / ".seed" / "seed.yml").read_text()
        mini = parse_simple_yaml(text)
        full = yaml.safe_load(text)

        def normalize(v):
            if isinstance(v, dict):
                return {k: normalize(x) for k, x in v.items()}
            if isinstance(v, list):  # inline flow lists (policy.board / policy.merge)
                return [normalize(x) for x in v]
            return str(v).lower() if isinstance(v, bool) else str(v)

        assert mini == normalize(full)


class TestPlant:
    def test_fresh_plant_then_check_green(self, tmp_path):
        assert plant(tmp_path) == 0
        for rel in (
            "CONCEPT.md", "CLAUDE.md",
            ".seed/seed.yml", ".seed/pause.yml",
            ".seed/tools/seed.py", ".seed/telemetry/evolution.jsonl",
            ".github/workflows/seed-germinate.yml",
            ".github/workflows/seed-grow.yml",
            ".github/workflows/seed-steward.yml",
            ".github/workflows/seed-verify.yml",
        ):
            assert (tmp_path / rel).exists(), f"plant did not create {rel}"
        assert "__SEED_" not in (tmp_path / ".seed" / "seed.yml").read_text()
        assert main(["check", str(tmp_path)]) == 0

    def test_plant_is_idempotent(self, tmp_path, capsys):
        plant(tmp_path)
        capsys.readouterr()
        assert plant(tmp_path) == 0
        out = capsys.readouterr().out
        assert "0 planted, 0 updated" in out

    def test_plant_refuses_to_reidentify(self, tmp_path):
        plant(tmp_path)
        with pytest.raises(SystemExit):
            main(["plant", str(tmp_path), "--repo", "someone/else"])

    def test_fresh_plant_requires_repo(self, tmp_path):
        with pytest.raises(SystemExit):
            main(["plant", str(tmp_path)])

    def test_rendered_workflows_are_valid_yaml(self, tmp_path):
        plant(tmp_path, "--garden")
        wf_dir = tmp_path / ".github" / "workflows"
        files = sorted(wf_dir.glob("*.yml"))
        assert len(files) == 7  # 6 kernel + garden-orchestrate
        for wf in files:
            yaml.safe_load(wf.read_text())

    def test_update_repairs_managed_but_keeps_user_owned(self, tmp_path, capsys):
        plant(tmp_path)
        grow = tmp_path / ".github" / "workflows" / "seed-grow.yml"
        grow.write_text(grow.read_text().replace("--draft", "--fill"))
        concept = tmp_path / "CONCEPT.md"
        concept.write_text(concept.read_text() + "\nHuman-owned addition.\n")
        capsys.readouterr()
        assert plant(tmp_path, "--update") == 0
        assert "--draft" in grow.read_text(), "--update must repair kernel-managed drift"
        assert "Human-owned addition." in concept.read_text(), \
            "--update must never touch user-owned files"


class TestCheck:
    def test_guardrail_weakening_is_an_error(self, tmp_path, capsys):
        plant(tmp_path)
        manifest = tmp_path / ".seed" / "seed.yml"
        manifest.write_text(manifest.read_text().replace(
            "pr_only: true", "pr_only: false"))
        assert main(["check", str(tmp_path)]) == 1
        assert "pr_only" in capsys.readouterr().out

    def test_merge_hard_stops_cannot_be_weakened(self, tmp_path, capsys):
        """A seed allowed to merge must keep the stops that make it safe."""
        plant(tmp_path)
        manifest = tmp_path / ".seed" / "seed.yml"
        manifest.write_text(manifest.read_text().replace(
            "merge_requires_green: true", "merge_requires_green: false"))
        assert main(["check", str(tmp_path)]) == 1
        out = capsys.readouterr().out
        assert "merge_requires_green" in out and "never merge a red PR" in out

    def test_only_the_tend_lane_may_merge(self, tmp_path, capsys):
        """Growth must never merge, even when the merge policy is on."""
        plant(tmp_path)
        grow = tmp_path / ".github" / "workflows" / "seed-grow.yml"
        grow.write_text(grow.read_text() + "\n# gh pr merge 1 --squash\n".replace("# ", "          "))
        assert main(["check", str(tmp_path)]) == 1
        assert "only the tend lane" in capsys.readouterr().out

    def test_lost_draft_marker_is_an_error(self, tmp_path, capsys):
        plant(tmp_path)
        grow = tmp_path / ".github" / "workflows" / "seed-grow.yml"
        grow.write_text(grow.read_text().replace("--draft", "--fill"))
        assert main(["check", str(tmp_path)]) == 1
        assert "--draft" in capsys.readouterr().out

    def test_declared_gate_with_no_workflow_is_flagged(self, tmp_path, capsys):
        """A consent gate the manifest declares must control something.

        Kernel v0.1.0 shipped gates.evolve: SEED_EVOLVE_ENABLED with no
        workflow reading it — a dead promise on every planted repo. The
        checker now warns when any declared gate is unhonored.
        """
        plant(tmp_path)
        (tmp_path / ".github" / "workflows" / "seed-evolve.yml").unlink()
        assert main(["check", str(tmp_path)]) == 0  # warning, not an error
        out = capsys.readouterr().out
        assert "SEED_EVOLVE_ENABLED" in out and "no workflow reads it" in out

    def test_missing_kill_switch_is_an_error(self, tmp_path):
        plant(tmp_path)
        (tmp_path / ".seed" / "pause.yml").unlink()
        assert main(["check", str(tmp_path)]) == 1

    def test_strict_parity_flags_any_managed_drift(self, tmp_path, capsys):
        plant(tmp_path)
        grow = tmp_path / ".github" / "workflows" / "seed-grow.yml"
        # A benign-looking edit that keeps every guardrail marker intact.
        grow.write_text(grow.read_text().replace("--max-turns 40", "--max-turns 41"))
        assert main(["check", str(tmp_path)]) == 0, "non-strict drift is a warning"
        assert main(["check", str(tmp_path), "--strict"]) == 1
        assert "drifts from the kernel" in capsys.readouterr().out


class TestSelfHosting:
    """ai-seed is planted with its own kernel — and must stay green."""

    def test_self_check_is_green_under_strict_parity(self):
        assert main(["check", str(REPO_ROOT)]) == 0

    def test_every_declared_gate_is_honored_here(self):
        """ai-seed runs every lane it advertises — no dead gates in the flagship."""
        manifest = parse_simple_yaml((REPO_ROOT / ".seed" / "seed.yml").read_text())
        installed = "\n".join(
            wf.read_text() for wf in (REPO_ROOT / ".github" / "workflows").glob("*.yml")
        )
        for gate_name, var in (manifest.get("gates") or {}).items():
            assert var in installed, f"gates.{gate_name} ({var}) is declared but no workflow reads it"

    def test_manifest_is_strict(self):
        manifest = parse_simple_yaml((REPO_ROOT / ".seed" / "seed.yml").read_text())
        assert manifest["kernel"]["strict"] == "true"

    def test_vendored_tool_is_identical_to_canonical(self):
        canonical = (REPO_ROOT / "tools" / "seed.py").read_text()
        vendored = (REPO_ROOT / ".seed" / "tools" / "seed.py").read_text()
        assert canonical == vendored, \
            "re-vendor with: python3 tools/seed.py plant . --update"

    def test_kernel_version_is_synchronized(self):
        assert (REPO_ROOT / "seed" / "VERSION").read_text().strip() == KERNEL_VERSION, \
            "bump KERNEL_VERSION in tools/seed.py together with seed/VERSION"

    def test_evolution_log_has_ticks(self):
        text = (REPO_ROOT / "CONCEPT.md").read_text()
        assert re.search(r"(?m)^### G\d+-T\d+ ", text)


class TestSchemaFlag:
    def test_fresh_plant_without_schema_flag_does_not_create_schema_md(self, tmp_path):
        plant(tmp_path)
        assert not (tmp_path / "SCHEMA.md").exists(), \
            "plant without --schema must not create SCHEMA.md"

    def test_fresh_plant_with_schema_flag_creates_schema_md(self, tmp_path, capsys):
        assert plant(tmp_path, "--schema") == 0
        assert (tmp_path / "SCHEMA.md").exists(), "plant --schema must create SCHEMA.md"
        out = capsys.readouterr().out
        assert "SCHEMA.md" in out, "planted SCHEMA.md must appear in plant output"
        content = (tmp_path / "SCHEMA.md").read_text()
        assert "__SEED_" not in content, "SCHEMA.md must have no unresolved placeholders"
        assert "bamr87/test-seed" in content, "SCHEMA.md must contain the repo name"

    def test_schema_update_rerenders_from_kernel(self, tmp_path, capsys):
        plant(tmp_path, "--schema")
        schema = tmp_path / "SCHEMA.md"
        original = schema.read_text()
        schema.write_text(original + "\nDrifted line.\n")
        capsys.readouterr()
        assert plant(tmp_path, "--schema", "--update") == 0
        assert schema.read_text() == original, \
            "--schema --update must re-render SCHEMA.md to match the kernel template"
        out = capsys.readouterr().out
        assert "SCHEMA.md" in out

    def test_schema_check_passes_after_schema_plant(self, tmp_path):
        plant(tmp_path, "--schema")
        assert main(["check", str(tmp_path)]) == 0

    def test_schema_optional_constant_names_schema_md(self):
        assert "SCHEMA.md" in SCHEMA_OPTIONAL


class TestKernelTemplates:
    def test_kernel_workflows_keep_core_guardrail_text(self):
        grow = (KERNEL_DIR / ".github" / "workflows" / "seed-grow.yml").read_text()
        for marker in ("SEED_GROW_ENABLED", "pause.yml", "concurrency",
                       "anthropics/claude-code-action@v1",
                       "claude_code_oauth_token", "--draft",
                       "persist-credentials: false"):
            assert marker in grow, f"kernel seed-grow.yml lost '{marker}'"
        germinate = (KERNEL_DIR / ".github" / "workflows" / "seed-germinate.yml").read_text()
        assert "confirm" in germinate and "pause.yml" in germinate

    def test_only_the_tend_lane_merges(self):
        """Merging is confined to one auditable lane (kernel v0.3.0)."""
        for wf in (KERNEL_DIR / ".github" / "workflows").glob("*.yml"):
            if wf.name == "seed-tend.yml":
                continue
            assert "gh pr merge" not in wf.read_text(), \
                f"{wf.name} merges — only seed-tend.yml may"

    def test_tend_lane_keeps_its_hard_stops(self):
        tend = (KERNEL_DIR / ".github" / "workflows" / "seed-tend.yml").read_text()
        for marker in ("SEED_TEND_ENABLED", "pause.yml", "block_labels",
                       "no longer eligible on live state", "startswith(\"seed/\")",
                       "human-review"):
            assert marker in tend, f"kernel seed-tend.yml lost '{marker}'"

    def test_grow_is_gated_on_a_clear_board(self):
        grow = (KERNEL_DIR / ".github" / "workflows" / "seed-grow.yml").read_text()
        assert "seed-tend.yml" in grow, "grow must tend before it grows"
        assert "needs.board.outputs.clear" in grow, \
            "grow must be gated on the post-tend board survey"

    def test_templates_only_use_known_placeholders(self):
        known = {"__SEED_NAME__", "__SEED_REPO__", "__SEED_DEFAULT_BRANCH__",
                 "__SEED_PLANTED__", "__SEED_KERNEL_VERSION__",
                 "__SEED_PLANTED_FROM__", "__SEED_GROW_CRON__",
                 "__SEED_TEND_CRON__"}
        for path in list(KERNEL_DIR.rglob("*")) + list((KERNEL_DIR.parent / "garden").rglob("*")):
            if path.is_file():
                found = set(re.findall(r"__SEED_[A-Z_]+__", path.read_text()))
                unknown = found - known
                assert not unknown, f"{path} uses unknown placeholder(s): {unknown}"
