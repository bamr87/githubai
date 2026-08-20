"""GitHub App mode: manifest, relay, and org-policy consistency checks.

The relay's own behaviour is tested by its Node suite (`app/relay/test/`, run by
CI's `relay` job). What lives here is the cross-language contract: the relay and
the framework must agree about dispatch types, the config schema, and the
promises the docs make about permissions.
"""

import json
import re
import shutil
import subprocess

import pytest

from conftest import load_yaml

RELAY_MODULES = (
    "index.js",
    "webhook.js",
    "routing.js",
    "policy.js",
    "store.js",
    "session.js",
    "github.js",
    "dashboard.js",
    "http.js",
    "yaml.js",
)


@pytest.fixture(scope="session")
def relay_dir(repo_root):
    return repo_root / "app" / "relay"


@pytest.fixture(scope="session")
def manifest(repo_root):
    return json.loads((repo_root / "app" / "manifest.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def routing_source(relay_dir):
    return (relay_dir / "src" / "routing.js").read_text(encoding="utf-8")


def test_manifest_shape(manifest):
    assert manifest["name"] == "GitHubAI"
    assert manifest["hook_attributes"]["url"].endswith("/webhook")
    assert manifest["redirect_url"].endswith("/manifest/callback")
    assert manifest["setup_url"].endswith("/setup")
    for event in ("issues", "pull_request", "installation", "installation_repositories"):
        assert event in manifest["default_events"], f"manifest must subscribe to {event}"


def test_manifest_permissions_are_least_privilege(manifest):
    """The relay only fires repository_dispatch; it must never ask for write on
    anything else. `contents: write` is required by the dispatches endpoint."""
    perms = manifest["default_permissions"]
    assert perms["contents"] == "write", "repository_dispatch requires contents: write"
    assert perms["metadata"] == "read"
    write_scopes = {scope for scope, level in perms.items() if level == "write"}
    assert write_scopes == {"contents"}, f"unexpected write permissions: {write_scopes - {'contents'}}"


def test_every_subscribed_event_has_a_permission(manifest):
    required = {"issues": "issues", "pull_request": "pull_requests"}
    for event, scope in required.items():
        if event in manifest["default_events"]:
            assert scope in manifest["default_permissions"], (
                f"subscribing to '{event}' requires the '{scope}' permission"
            )


def test_relay_dispatch_types_match_dispatch_workflow(repo_root, routing_source):
    stub = load_yaml(repo_root / "template" / "workflows" / "claude-dispatch.yml")
    triggers = stub[True] if True in stub else stub.get("on")
    stub_types = set(triggers["repository_dispatch"]["types"])
    relay_types = set(re.findall(r"`\$\{DISPATCH_PREFIX\}-([a-z-]+)`", routing_source))
    relay_types = {f"githubai-{suffix}" for suffix in relay_types}

    # Maintenance is cron-driven; the relay never emits it, but the stub routes
    # it so a manual repository_dispatch still works.
    assert relay_types <= stub_types, f"relay emits unrouted types: {relay_types - stub_types}"
    for expected in ("githubai-triage", "githubai-implement", "githubai-review", "githubai-auto-merge"):
        assert expected in relay_types, f"relay must emit {expected}"


def test_relay_routing_mirrors_actions_mode_gating(routing_source):
    """repository_dispatch carries no issue/PR context, so the reusable
    workflows cannot re-check these gates - the relay has to apply them."""
    for gate in ("claude:skip", "draft", "fork", "Bot"):
        assert gate in routing_source, f"relay routing must handle the '{gate}' gate"
    for author in ("dependabot[bot]", "renovate[bot]"):
        assert author in routing_source, f"relay must know the trusted bot author {author}"


def test_relay_verifies_signatures_and_uses_app_auth(relay_dir):
    session = (relay_dir / "src" / "session.js").read_text(encoding="utf-8")
    github = (relay_dir / "src" / "github.js").read_text(encoding="utf-8")
    assert "x-hub-signature-256" in session or "verifyWebhookSignature" in session
    assert "timingSafeEqual" in session, "signature comparison must be constant-time"
    assert "access_tokens" in github, "relay must mint installation tokens"
    assert "BEGIN PRIVATE KEY" in github, "relay must demand PKCS#8 keys with a clear error"

    webhook = (relay_dir / "src" / "webhook.js").read_text(encoding="utf-8")
    verify_call = webhook.index("await verifyWebhookSignature(")
    assert verify_call < webhook.index("JSON.parse"), "verify the signature before parsing the body"
    assert verify_call < webhook.index("claimDelivery"), "verify before touching any state"


def test_relay_schema_has_nowhere_to_put_a_token(relay_dir):
    """app/DATA-HANDLING.md promises no credential is ever persisted. The
    strongest enforcement of that is a schema with no column to persist one."""
    schema = (relay_dir / "schema.sql").read_text(encoding="utf-8")
    statements = re.sub(r"--[^\n]*", "", schema).lower()
    for forbidden in ("token", "secret", "password", "pem", "key_"):
        assert forbidden not in statements, (
            f"relay schema declares something named '{forbidden}'; credentials must not be stored"
        )

    index = (relay_dir / "src" / "index.js").read_text(encoding="utf-8")
    assert "userToken" in index, "the OAuth flow should name the token it discards"


def test_relay_has_no_dependencies(relay_dir):
    package = json.loads((relay_dir / "package.json").read_text(encoding="utf-8"))
    assert package["type"] == "module"
    assert not package.get("dependencies"), "the relay must stay dependency-free"
    assert not package.get("devDependencies"), "the relay must stay dependency-free"
    assert package["scripts"]["test"].startswith("node --test")


def test_relay_modules_and_tests_exist(relay_dir):
    for module in RELAY_MODULES:
        assert (relay_dir / "src" / module).is_file(), f"missing relay module {module}"
    tests = {path.name for path in (relay_dir / "test").glob("*.test.js")}
    for expected in ("routing.test.js", "policy.test.js", "webhook.test.js", "index.test.js"):
        assert expected in tests, f"missing relay test {expected}"


def test_wrangler_config_matches_the_worker(relay_dir):
    config = (relay_dir / "wrangler.toml").read_text(encoding="utf-8")
    assert 'main = "src/index.js"' in config
    assert "[[d1_databases]]" in config and 'binding = "DB"' in config
    assert "[triggers]" in config and "crons" in config, "retention needs a cron trigger"


def test_schema_declares_every_table_the_store_uses(relay_dir):
    schema = (relay_dir / "schema.sql").read_text(encoding="utf-8")
    store = (relay_dir / "src" / "store.js").read_text(encoding="utf-8")
    tables = set(re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", schema))
    # `DO UPDATE SET` is not a table reference; skip it.
    used = set(re.findall(r"(?:INTO|FROM|UPDATE)\s+(?!SET\b)(\w+)", store))
    assert used <= tables, f"store.js queries undeclared tables: {used - tables}"


def test_org_policy_template_uses_the_repo_config_schema(repo_root, profiles_dir):
    """Org policy is the same schema repos already know, so operators learn one."""
    policy = load_yaml(repo_root / "template" / "githubai-org.yml")
    base = load_yaml(profiles_dir / "_base.yml")

    assert policy["version"] == base["version"]
    assert policy["org"]["enabled"] is True
    assert "include" in policy["org"]["repos"] and "exclude" in policy["org"]["repos"]
    for area in policy["automation"]:
        assert area in base["automation"], f"org policy names unknown automation area '{area}'"
        assert set(policy["automation"][area]) == {"enabled"}, (
            f"org policy may only gate '{area}' with `enabled`"
        )


def test_org_policy_areas_cover_every_relay_dispatch_type(repo_root, routing_source):
    policy = load_yaml(repo_root / "template" / "githubai-org.yml")
    areas = set(re.findall(r"\[DISPATCH_TYPES\.\w+\]: \"(\w+)\"", routing_source))
    assert areas, "could not read DISPATCH_AREA from routing.js"
    assert areas <= set(policy["automation"]), (
        f"org policy template cannot gate: {areas - set(policy['automation'])}"
    )


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_relay_yaml_parser_agrees_with_pyyaml(repo_root):
    """The relay parses org policy without PyYAML; a divergence would mean the
    same file means different things in app mode and in actions/load-config."""
    files = [
        "profiles/_base.yml",
        "profiles/library.yml",
        "profiles/webapp.yml",
        "template/githubai.yml",
        "template/githubai-org.yml",
        ".github/githubai.yml",
    ]
    script = (
        "const fs = require('node:fs');"
        "import('./app/relay/src/yaml.js').then((m) => {"
        "  const out = {};"
        f"  for (const f of {json.dumps(files)}) out[f] = m.parseYaml(fs.readFileSync(f, 'utf8'));"
        "  process.stdout.write(JSON.stringify(out));"
        "});"
    )
    result = subprocess.run(
        ["node", "-e", script],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    from_js = json.loads(result.stdout)
    for name in files:
        assert from_js[name] == load_yaml(repo_root / name), f"{name} parses differently in the relay"


def test_app_docs_exist_and_link_to_each_other(repo_root):
    app_dir = repo_root / "app"
    readme = (app_dir / "README.md").read_text(encoding="utf-8")
    for doc in ("OPERATIONS.md", "DATA-HANDLING.md", "MARKETPLACE.md"):
        assert (app_dir / doc).is_file(), f"missing app doc {doc}"
        assert doc in readme, f"app/README.md must link to {doc}"
