"""Convention tests for the framework workflows.

These encode the promises the README makes: OAuth-first auth everywhere,
least-privilege permissions, reusability via workflow_call, and injection
hygiene around untrusted issue/PR content.
"""

import re

from conftest import load_yaml

OAUTH_EXPR = "${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}"
FALLBACK_EXPR = "${{ secrets.CLAUDE_CODE_OAUTH_TOKEN == '' && secrets.ANTHROPIC_API_KEY || '' }}"

# Automation workflows (everything claude-* except the interactive claude.yml)
AUTOMATION = {
    "claude-triage.yml",
    "claude-implement.yml",
    "claude-review.yml",
    "claude-auto-merge.yml",
    "claude-maintenance.yml",
    "claude-release.yml",
}


def claude_action_steps(workflow: dict):
    for job in workflow.get("jobs", {}).values():
        for step in job.get("steps", []) or []:
            if str(step.get("uses", "")).startswith("anthropics/claude-code-action"):
                yield step


def test_expected_workflow_files_exist(workflow_files):
    names = {p.name for p in workflow_files}
    assert AUTOMATION | {"claude.yml", "ci.yml", "markdown-oneline.yml"} <= names


def test_all_workflows_parse(workflow_files):
    for path in workflow_files:
        data = load_yaml(path)
        assert isinstance(data, dict) and "jobs" in data, f"{path.name} did not parse to a workflow"


def test_claude_action_pinned_to_v1(claude_workflow_files):
    for path in claude_workflow_files:
        for step in claude_action_steps(load_yaml(path)):
            assert step["uses"] == "anthropics/claude-code-action@v1", (
                f"{path.name}: claude-code-action must be pinned @v1"
            )


def test_oauth_first_auth_everywhere(claude_workflow_files):
    """The core product promise: OAuth token default, API key only as fallback."""
    for path in claude_workflow_files:
        steps = list(claude_action_steps(load_yaml(path)))
        assert steps, f"{path.name} has no claude-code-action step"
        for step in steps:
            with_block = step.get("with", {})
            assert with_block.get("claude_code_oauth_token") == OAUTH_EXPR, (
                f"{path.name}: claude_code_oauth_token must be the OAuth secret"
            )
            assert with_block.get("anthropic_api_key") == FALLBACK_EXPR, (
                f"{path.name}: anthropic_api_key must be the empty-OAuth fallback expression"
            )


def test_automation_workflows_are_reusable(claude_workflow_files):
    for path in claude_workflow_files:
        triggers = load_yaml(path)[True] if True in load_yaml(path) else load_yaml(path).get("on")
        assert isinstance(triggers, dict), f"{path.name}: expected mapping triggers"
        assert "workflow_call" in triggers, f"{path.name} must declare workflow_call"
        secrets = (triggers.get("workflow_call") or {}).get("secrets") or {}
        assert {"CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY"} <= set(secrets), (
            f"{path.name}: workflow_call must declare both auth secrets"
        )


def test_jobs_have_timeouts_and_permissions(claude_workflow_files):
    for path in claude_workflow_files:
        data = load_yaml(path)
        for name, job in data["jobs"].items():
            assert "timeout-minutes" in job, f"{path.name}:{name} needs timeout-minutes"
            assert "permissions" in job, f"{path.name}:{name} needs explicit permissions"
            assert job["permissions"].get("id-token") == "write", (
                f"{path.name}:{name} needs id-token: write for claude-code-action"
            )


def test_automation_workflows_have_concurrency(workflow_files):
    for path in workflow_files:
        if path.name in AUTOMATION:
            assert "concurrency" in load_yaml(path), f"{path.name} needs a concurrency group"


def test_no_untrusted_body_interpolation(workflow_files):
    """Issue/PR titles and bodies are attacker-controlled; only numbers/logins may be interpolated."""
    banned = re.compile(
        r"\$\{\{\s*(github\.event\.(issue|pull_request|comment|review)\.(body|title)|"
        r"github\.event\.review\.body)"
    )
    for path in workflow_files:
        text = path.read_text(encoding="utf-8")
        assert not banned.search(text), f"{path.name} interpolates untrusted content"


def test_automation_prompts_mark_content_as_data(workflow_files):
    for path in workflow_files:
        if path.name not in AUTOMATION:
            continue
        text = path.read_text(encoding="utf-8").lower()
        assert "not" in text and "instructions" in text, (
            f"{path.name}: prompt must state that repo content is data, not instructions"
        )


def test_triage_and_auto_merge_evaluator_are_read_only(repo_root):
    """Tool allowlists back the security docs: no Edit/Write in triage or the merge evaluator."""
    for name in ("claude-triage.yml", "claude-auto-merge.yml"):
        data = load_yaml(repo_root / ".github" / "workflows" / name)
        for step in claude_action_steps(data):
            args = step.get("with", {}).get("claude_args", "")
            match = re.search(r'--allowedTools\s+"([^"]+)"', args)
            assert match, f"{name}: claude_args must set an explicit --allowedTools"
            tools = match.group(1)
            for banned in ("Edit", "Write", "Bash(git push"):
                assert banned not in tools, f"{name}: {banned} must not be allowed"


def test_auto_merge_uses_structured_output_and_auto_flag(repo_root):
    text = (repo_root / ".github" / "workflows" / "claude-auto-merge.yml").read_text(encoding="utf-8")
    assert "--json-schema" in text, "auto-merge must demand a structured verdict"
    assert "--auto" in text, "auto-merge must defer to branch protection via gh pr merge --auto"
    assert "structured_output" in text
