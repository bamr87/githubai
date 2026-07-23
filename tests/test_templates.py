"""Template stubs must stay consistent with the reusable workflows they call."""

import re

from conftest import load_yaml

PERMISSION_RANK = {"none": 0, "read": 1, "write": 2}


def stub_jobs_with_uses(path):
    data = load_yaml(path)
    for name, job in data.get("jobs", {}).items():
        if "uses" in job:
            yield name, job


def referenced_workflow(job, repo_root):
    match = re.fullmatch(r"bamr87/githubai/(\.github/workflows/[\w.-]+\.yml)@(\S+)", job["uses"])
    assert match, f"unexpected uses ref: {job['uses']}"
    return repo_root / match.group(1), match.group(2)


def test_stubs_exist_for_every_lane(template_stub_files):
    names = {p.name for p in template_stub_files}
    expected = {
        "claude.yml",
        "claude-triage.yml",
        "claude-implement.yml",
        "claude-review.yml",
        "claude-auto-merge.yml",
        "claude-maintenance.yml",
        "claude-release.yml",
        "claude-dispatch.yml",
    }
    assert expected <= names, f"missing stubs: {expected - names}"


def test_stubs_reference_real_workflows_at_main(template_stub_files, repo_root):
    for path in template_stub_files:
        for name, job in stub_jobs_with_uses(path):
            target, ref = referenced_workflow(job, repo_root)
            assert target.is_file(), f"{path.name}:{name} references missing workflow {target.name}"
            assert ref == "main", (
                f"{path.name}:{name} must ship @main (the installer's --ref handles pinning)"
            )
            assert job.get("secrets") == "inherit", f"{path.name}:{name} must pass secrets: inherit"


def test_called_workflows_declare_workflow_call(template_stub_files, repo_root):
    for path in template_stub_files:
        for name, job in stub_jobs_with_uses(path):
            target, _ = referenced_workflow(job, repo_root)
            data = load_yaml(target)
            triggers = data[True] if True in data else data.get("on")
            assert "workflow_call" in triggers, f"{target.name} is called but not callable"


def test_stub_permissions_cover_called_jobs(template_stub_files, repo_root):
    """A reusable workflow can't exceed its caller's grants - stubs must grant enough."""
    for path in template_stub_files:
        for name, job in stub_jobs_with_uses(path):
            target, _ = referenced_workflow(job, repo_root)
            caller_perms = job.get("permissions", {})
            for tname, tjob in load_yaml(target)["jobs"].items():
                for scope, level in (tjob.get("permissions") or {}).items():
                    granted = caller_perms.get(scope, "none")
                    assert PERMISSION_RANK[granted] >= PERMISSION_RANK[level], (
                        f"{path.name}:{name} grants {scope}={granted} but "
                        f"{target.name}:{tname} needs {level}"
                    )


def test_stub_inputs_exist_on_called_workflow(template_stub_files, repo_root):
    for path in template_stub_files:
        for name, job in stub_jobs_with_uses(path):
            target, _ = referenced_workflow(job, repo_root)
            data = load_yaml(target)
            triggers = data[True] if True in data else data.get("on")
            declared = set(((triggers.get("workflow_call") or {}).get("inputs") or {}))
            passed = set((job.get("with") or {}))
            unknown = passed - declared
            assert not unknown, f"{path.name}:{name} passes undeclared inputs {unknown} to {target.name}"


def test_starter_config_lists_valid_profiles(repo_root, profiles_dir):
    text = (repo_root / "template" / "githubai.yml").read_text(encoding="utf-8")
    for profile in sorted(p.stem for p in profiles_dir.glob("*.yml") if not p.stem.startswith("_")):
        assert profile in text, f"template/githubai.yml comment must mention profile '{profile}'"
    assert "GHAI_REPO_TYPE" in text, "installer substitution marker missing"
