"""Installer must stay in sync with the taxonomy and template stubs."""

import re
import subprocess

from conftest import load_yaml


def installer_text(repo_root):
    return (repo_root / "setup" / "install.sh").read_text(encoding="utf-8")


def test_installer_bash_syntax(repo_root):
    subprocess.run(["bash", "-n", str(repo_root / "setup" / "install.sh")], check=True)


def parse_installer_labels(text):
    match = re.search(r"LABELS='([^']+)'", text)
    assert match, "LABELS block not found in install.sh"
    labels = {}
    for line in match.group(1).strip().splitlines():
        name, color, desc = line.split("|", 2)
        labels[name] = (color, desc)
    return labels


def test_installer_labels_match_taxonomy(repo_root, profiles_dir):
    """CLAUDE.md sync duty: _base.yml taxonomy and install.sh LABELS move together."""
    taxonomy = {
        entry["name"]: entry["color"]
        for entry in load_yaml(profiles_dir / "_base.yml")["labels"]["taxonomy"]
    }
    installer = {name: color for name, (color, _) in parse_installer_labels(installer_text(repo_root)).items()}
    assert installer == taxonomy, (
        "install.sh LABELS out of sync with profiles/_base.yml labels.taxonomy "
        f"(only-in-installer: {set(installer) - set(taxonomy)}, "
        f"only-in-taxonomy: {set(taxonomy) - set(installer)}, "
        f"color-mismatches: { {k for k in installer.keys() & taxonomy.keys() if installer[k] != taxonomy[k]} })"
    )


def test_installer_workflow_list_matches_stubs(repo_root):
    text = installer_text(repo_root)
    match = re.search(r'WORKFLOWS="([^"]+)"', text)
    assert match
    listed = set(match.group(1).split())
    stub_names = {p.stem for p in (repo_root / "template" / "workflows").glob("*.yml")}
    # claude-dispatch is installed only with --app and is referenced separately.
    assert listed == stub_names - {"claude-dispatch"}, (
        f"installer WORKFLOWS out of sync with template/workflows: {listed ^ (stub_names - {'claude-dispatch'})}"
    )
    assert "claude-dispatch" in text, "installer must handle the --app dispatch stub"


def test_installer_valid_profiles_match_profiles_dir(repo_root, profiles_dir):
    text = installer_text(repo_root)
    match = re.search(r'VALID_PROFILES="([^"]+)"', text)
    assert match
    listed = set(match.group(1).split())
    actual = {p.stem for p in profiles_dir.glob("*.yml") if not p.stem.startswith("_")}
    assert listed == actual, f"installer VALID_PROFILES out of sync: {listed ^ actual}"


def test_installer_mentions_oauth_first_setup(repo_root):
    text = installer_text(repo_root)
    assert "claude setup-token" in text
    assert "CLAUDE_CODE_OAUTH_TOKEN" in text
    assert "github.com/apps/claude" in text
