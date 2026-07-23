"""GitHub App scaffolding consistency checks."""

import json
import re

from conftest import load_yaml


def test_manifest_shape(repo_root):
    manifest = json.loads((repo_root / "app" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "GitHubAI"
    perms = manifest["default_permissions"]
    assert perms["contents"] == "write" and perms["issues"] == "write" and perms["pull_requests"] == "write"
    assert "issues" in manifest["default_events"] and "pull_request" in manifest["default_events"]
    assert manifest["hook_attributes"]["url"].endswith("/webhook")


def test_relay_dispatch_types_match_dispatch_workflow(repo_root):
    worker = (repo_root / "app" / "relay" / "worker.js").read_text(encoding="utf-8")
    stub = load_yaml(repo_root / "template" / "workflows" / "claude-dispatch.yml")
    triggers = stub[True] if True in stub else stub.get("on")
    stub_types = set(triggers["repository_dispatch"]["types"])
    worker_types = {
        f"githubai-{suffix}" for suffix in re.findall(r"DISPATCH_PREFIX\}-([a-z-]+)`", worker)
    }
    # Maintenance is cron-driven; the relay never emits it, but the stub routes it for manual dispatches.
    assert worker_types <= stub_types, f"relay emits unrouted types: {worker_types - stub_types}"
    for expected in ("githubai-triage", "githubai-implement", "githubai-review", "githubai-auto-merge"):
        assert expected in worker_types, f"relay must emit {expected}"


def test_relay_verifies_signatures_and_uses_app_auth(repo_root):
    worker = (repo_root / "app" / "relay" / "worker.js").read_text(encoding="utf-8")
    assert "x-hub-signature-256" in worker
    assert "timingSafeEqual" in worker
    assert "access_tokens" in worker, "relay must mint installation tokens"
    assert "BEGIN PRIVATE KEY" in worker, "relay must demand PKCS#8 keys with a clear error"
