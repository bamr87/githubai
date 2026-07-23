"""Every repo-type profile must be well-formed and internally consistent."""

import pytest

from conftest import load_yaml

REQUIRED_BASE_SECTIONS = {"profile", "repo", "claude", "labels", "automation", "standards"}
AUTOMATION_AREAS = {"triage", "implement", "review", "auto_merge", "maintenance", "release"}


def profile_paths(profiles_dir):
    return sorted(p for p in profiles_dir.glob("*.yml"))


def test_base_profile_has_all_sections(profiles_dir):
    base = load_yaml(profiles_dir / "_base.yml")
    assert REQUIRED_BASE_SECTIONS <= set(base), (
        f"_base.yml missing sections: {REQUIRED_BASE_SECTIONS - set(base)}"
    )
    assert AUTOMATION_AREAS <= set(base["automation"])
    for area in AUTOMATION_AREAS:
        assert "enabled" in base["automation"][area], f"automation.{area} needs 'enabled'"


def test_base_taxonomy_is_well_formed(profiles_dir):
    base = load_yaml(profiles_dir / "_base.yml")
    taxonomy = base["labels"]["taxonomy"]
    assert taxonomy, "base taxonomy must not be empty"
    names = [entry["name"] for entry in taxonomy]
    assert len(names) == len(set(names)), "duplicate label names in taxonomy"
    for entry in taxonomy:
        assert set(entry) >= {"name", "color", "description"}, f"label entry incomplete: {entry}"
    for control in ("claude:implement", "claude:auto-merge", "claude:skip", "claude:needs-human", "claude:triaged"):
        assert control in names, f"control-plane label {control} missing from taxonomy"


def test_every_profile_parses_with_required_keys(profiles_dir):
    found = 0
    for path in profile_paths(profiles_dir):
        if path.stem.startswith("_"):
            continue
        found += 1
        data = load_yaml(path)
        profile = data.get("profile", {})
        assert profile.get("name") == path.stem, f"{path.name}: profile.name must match filename"
        assert profile.get("description"), f"{path.name}: profile.description required"
        assert str(profile.get("guidance", "")).strip(), f"{path.name}: profile.guidance required"
        assert (data.get("repo") or {}).get("type") == path.stem, (
            f"{path.name}: repo.type must match filename"
        )
    assert found >= 8, "expected the 8 documented repo-type profiles"


def test_profiles_only_use_known_top_level_keys(profiles_dir):
    base_keys = set(load_yaml(profiles_dir / "_base.yml")) | {"version"}
    for path in profile_paths(profiles_dir):
        data = load_yaml(path)
        unknown = set(data) - base_keys
        assert not unknown, f"{path.name} introduces top-level keys absent from _base.yml: {unknown}"


def test_profiles_documented_in_readme(profiles_dir):
    readme = (profiles_dir / "README.md").read_text(encoding="utf-8")
    for path in profile_paths(profiles_dir):
        if path.stem.startswith("_"):
            continue
        assert f"`{path.stem}`" in readme, f"profiles/README.md missing row for {path.stem}"


@pytest.mark.parametrize("risky", ["webapp", "github-action"])
def test_risky_profiles_do_not_widen_auto_merge_paths(profiles_dir, risky):
    data = load_yaml(profiles_dir / f"{risky}.yml")
    paths = ((data.get("automation") or {}).get("auto_merge") or {}).get("allowed_paths")
    if paths is not None:
        assert ".github/**" not in paths, (
            f"{risky} profile must not allow auto-merge across .github/** (workflow tampering surface)"
        )
