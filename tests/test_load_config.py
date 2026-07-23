"""Unit tests for the load-config merge and output semantics."""

import io

import pytest
import yaml

import load_config


def write_config(tmp_path, data):
    path = tmp_path / "githubai.yml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_defaults_when_config_missing(profiles_dir, tmp_path):
    merged, found = load_config.resolve(profiles_dir, tmp_path / "missing.yml")
    assert not found
    assert merged["repo"]["type"] == "base"
    assert merged["automation"]["triage"]["enabled"] is True
    assert merged["automation"]["auto_merge"]["enabled"] is False, "auto-merge must be opt-in"


def test_profile_layer_applies(profiles_dir, tmp_path):
    path = write_config(tmp_path, {"repo": {"type": "docs"}})
    merged, found = load_config.resolve(profiles_dir, path)
    assert found
    assert merged["repo"]["type"] == "docs"
    # docs profile enables auto_merge and narrows focus
    assert merged["automation"]["auto_merge"]["enabled"] is True
    assert "broken or missing links" in " ".join(merged["automation"]["review"]["focus"])
    # base values survive where the profile is silent
    assert merged["automation"]["implement"]["trigger_label"] == "claude:implement"


def test_repo_config_wins_over_profile(profiles_dir, tmp_path):
    path = write_config(
        tmp_path,
        {
            "repo": {"type": "docs", "purpose": "test purpose"},
            "automation": {"auto_merge": {"enabled": False}},
            "claude": {"max_turns": 7},
        },
    )
    merged, _ = load_config.resolve(profiles_dir, path)
    assert merged["automation"]["auto_merge"]["enabled"] is False
    assert merged["claude"]["max_turns"] == 7
    assert merged["repo"]["purpose"] == "test purpose"
    # deep merge: sibling keys from base survive the override
    assert merged["automation"]["auto_merge"]["method"] == "squash"


def test_lists_replace_not_concatenate(profiles_dir, tmp_path):
    path = write_config(
        tmp_path,
        {"repo": {"type": "library"}, "automation": {"auto_merge": {"allowed_paths": ["only/this/**"]}}},
    )
    merged, _ = load_config.resolve(profiles_dir, path)
    assert merged["automation"]["auto_merge"]["allowed_paths"] == ["only/this/**"]


def test_unknown_type_fails_listing_profiles(profiles_dir, tmp_path):
    path = write_config(tmp_path, {"repo": {"type": "spaceship"}})
    with pytest.raises(SystemExit) as exc:
        load_config.resolve(profiles_dir, path)
    message = str(exc.value)
    assert "spaceship" in message and "library" in message


def test_outputs_format_and_flags(profiles_dir, tmp_path):
    path = write_config(tmp_path, {"repo": {"type": "library"}, "claude": {"model": "claude-opus-4-8"}})
    merged, found = load_config.resolve(profiles_dir, path)
    buf = io.StringIO()
    load_config.emit_outputs(merged, found, buf)
    out = buf.getvalue()
    lines = dict(
        line.split("=", 1) for line in out.splitlines() if "=" in line and "<<" not in line and line != "GHAI_EOF"
    )
    assert lines["type"] == "library"
    assert lines["model"] == "claude-opus-4-8"
    assert lines["triage_enabled"] == "true"
    assert lines["auto_merge_enabled"] == "false"
    assert f"prompt_context<<{load_config.OUTPUT_DELIMITER}" in out
    assert out.rstrip().endswith(load_config.OUTPUT_DELIMITER)


def test_prompt_context_contains_the_contract(profiles_dir, tmp_path):
    path = write_config(tmp_path, {"repo": {"type": "webapp", "purpose": "checkout service UI"}})
    merged, found = load_config.resolve(profiles_dir, path)
    context = load_config.build_prompt_context(merged, found)
    for expected in (
        "Repo type: webapp",
        "checkout service UI",
        "### Review focus",
        "### Automation posture",
        "### Label taxonomy",
        "migrations",  # webapp guidance mentions migration safety
    ):
        assert expected.lower() in context.lower(), f"prompt context missing: {expected}"
    assert load_config.OUTPUT_DELIMITER not in context, "context must never contain the heredoc delimiter"


def test_missing_config_noted_in_context(profiles_dir, tmp_path):
    merged, found = load_config.resolve(profiles_dir, tmp_path / "missing.yml")
    context = load_config.build_prompt_context(merged, found)
    assert "no .github/githubai.yml found" in context
