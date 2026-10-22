"""The generated reference in docs/reference/ must match the files it is generated from."""

import subprocess
import sys


def test_generated_reference_is_fresh(repo_root):
    """Changing a workflow input, permission or label means rerunning tools/gen_reference.py."""
    result = subprocess.run(
        [sys.executable, str(repo_root / "tools" / "gen_reference.py"), "--check"],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_generated_reference_covers_every_claude_workflow(repo_root, claude_workflow_files):
    reference = (repo_root / "docs" / "reference" / "workflows.md").read_text(encoding="utf-8")
    for path in claude_workflow_files:
        assert f"## `{path.name}`" in reference, f"docs/reference/workflows.md has no section for {path.name}"


def test_docs_index_is_fresh(repo_root):
    """docs/README.md is generated from each document's summary line (tools/docs_index.py)."""
    result = subprocess.run(
        [sys.executable, str(repo_root / "tools" / "docs_index.py"), "--check", "--root", str(repo_root)],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert result.returncode == 0, result.stderr or result.stdout
