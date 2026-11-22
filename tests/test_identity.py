"""The agent identity App (app/identity/): least privilege, an exact no-op without it, and no token leaks.

Covers the manifest, the agent-identity action, every lane's wiring, the session
handoff workflow, and both scripts end to end: registration against a local
callback with a fake GitHub, and token minting against a fake GitHub with a real
openssl-signed JWT (skipped where openssl is missing).
"""

import base64
import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import threading
import urllib.error
import urllib.request

import pytest

from conftest import REPO_ROOT, load_yaml

IDENTITY = REPO_ROOT / "app" / "identity"
LANES = sorted(p.name for p in (REPO_ROOT / ".github" / "workflows").glob("claude*.yml"))
TOKEN_EXPR = "${{ steps.agent-token.outputs.token }}"


def load_module(name):
    spec = importlib.util.spec_from_file_location(f"identity_{name}", IDENTITY / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


register = load_module("register")
agent_token = load_module("agent_token")


# --------------------------------------------------------------------------- #
# The manifest: an identity, not a service
# --------------------------------------------------------------------------- #
def test_manifest_is_a_private_identity_with_least_privilege():
    m = json.loads((IDENTITY / "manifest.json").read_text(encoding="utf-8"))
    assert m["public"] is False, "the identity App belongs to one owner"
    assert "hook_attributes" not in m and m["default_events"] == [], "an identity receives no webhooks"
    perms = m["default_permissions"]
    for scope in ("contents", "pull_requests", "issues"):
        assert perms[scope] == "write", f"the agent writes {scope}"
    assert perms["metadata"] == "read"
    allowed = {"contents", "pull_requests", "issues", "workflows", "actions", "checks", "metadata"}
    assert set(perms) <= allowed, f"permissions beyond what the lanes use: {set(perms) - allowed}"
    for never in ("administration", "secrets", "members", "organization_administration", "environments"):
        assert never not in perms


# --------------------------------------------------------------------------- #
# The composite action
# --------------------------------------------------------------------------- #
def test_identity_action_defaults_match_claude_code_action():
    action = load_yaml(REPO_ROOT / "actions" / "agent-identity" / "action.yml")
    assert "${{" not in action["description"], "an expression in a manifest description breaks the action"
    assert {"mode", "login", "user-id", "email", "bot-id", "bot-name"} <= set(action["outputs"])
    script = action["runs"]["steps"][0]["run"]
    # Without the App the lane must commit exactly as claude-code-action's defaults do.
    assert "bot_id=41898282" in script and 'bot_name="claude[bot]"' in script
    uses = [line.strip() for line in script.splitlines() if "$APP_TOKEN" in line]
    assert all(u.startswith(('if [[ -n "$APP_TOKEN" ]]', 'user_id="$(GH_TOKEN="$APP_TOKEN" gh api')) for u in uses), (
        f"the token is only tested and handed to gh, never printed: {uses}")


# --------------------------------------------------------------------------- #
# Every lane writes as the identity when it exists, and as before when it does not
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", LANES)
def test_lane_writes_as_the_identity(name):
    path = REPO_ROOT / ".github" / "workflows" / name
    data = load_yaml(path)
    on = data.get(True, data.get("on"))
    secrets = on["workflow_call"]["secrets"]
    for key in ("AGENT_APP_CLIENT_ID", "AGENT_APP_PRIVATE_KEY"):
        assert key in secrets and secrets[key]["required"] is False, f"{name}: {key} must be optional"
    for job_name, job in data["jobs"].items():
        steps = job["steps"]
        assert "HAS_AGENT_APP" in (job.get("env") or {}), f"{name}:{job_name} needs HAS_AGENT_APP"
        by_id = {s.get("id"): (i, s) for i, s in enumerate(steps) if s.get("id")}
        i_tok, tok = by_id["agent-token"]
        assert tok["uses"] == "actions/create-github-app-token@v3" and tok["if"] == "env.HAS_AGENT_APP == 'true'"
        i_who, who = by_id["identity"]
        assert who["uses"] == "./.githubai-framework/actions/agent-identity" and i_who > i_tok
        removal = next(i for i, s in enumerate(steps) if "rm -rf .githubai-framework" in str(s.get("run", "")))
        assert i_who < removal, f"{name}: resolve the identity before the framework checkout is removed"
        for step in steps:
            if str(step.get("uses", "")).startswith("anthropics/claude-code-action"):
                w = step["with"]
                assert w["github_token"] == TOKEN_EXPR, f"{name}: claude-code-action must get the identity token"
                assert w["bot_id"] == "${{ steps.identity.outputs.bot-id }}"
                assert w["bot_name"] == "${{ steps.identity.outputs.bot-name }}"
            gh = (step.get("env") or {}).get("GH_TOKEN")
            if gh is not None:
                assert gh == "${{ steps.agent-token.outputs.token || github.token }}", (
                    f"{name}: a gh step must write as the identity when it exists")


# --------------------------------------------------------------------------- #
# The session handoff
# --------------------------------------------------------------------------- #
def test_handoff_opens_prs_only_for_people_and_never_parses_messages():
    path = REPO_ROOT / ".github" / "workflows" / "agent-handoff.yml"
    data = load_yaml(path)
    on = data.get(True, data.get("on"))
    assert on["push"]["branches"] == ["claude/**"]
    assert set(on["workflow_call"]["secrets"]) == {"AGENT_APP_CLIENT_ID", "AGENT_APP_PRIVATE_KEY"}
    job = data["jobs"]["handoff"]
    cond = " ".join(job["if"].split())
    assert "!endsWith(github.actor, '[bot]')" in cond, "a bot's push opens its own pull request"
    assert "vars.AGENT_HANDOFF_ENABLED != 'false'" in cond, "every loop has a kill switch"
    assert job["permissions"] == {"contents": "read"}, "the job token reads; the App token writes"
    run = next(s for s in job["steps"] if s.get("name") == "Open the pull request as the agent")["run"]
    assert "${{" not in run, "nothing is interpolated into the script"
    assert "--body-file" in run and "--add-reviewer" in run and "gh pr list" in run


def test_handoff_stub_and_installer():
    stub = load_yaml(REPO_ROOT / "template" / "workflows" / "agent-handoff.yml")
    assert stub["jobs"]["handoff"]["secrets"] == "inherit"
    text = (REPO_ROOT / "setup" / "install.sh").read_text(encoding="utf-8")
    assert "agent-handoff" in text and "app/identity/register.py" in text


# --------------------------------------------------------------------------- #
# register.py
# --------------------------------------------------------------------------- #
BASE = json.loads((IDENTITY / "manifest.json").read_text(encoding="utf-8"))


def test_build_manifest_fills_the_run_and_refuses_bad_names():
    m = register.build_manifest(dict(BASE, hook_attributes={"url": "x"}), "acme-claude", 9000)
    assert m["name"] == "acme-claude" and m["redirect_url"] == "http://127.0.0.1:9000/callback"
    assert m["public"] is False and "hook_attributes" not in m and m["default_events"] == []
    for bad in ("", "-x", "has space", "x" * 35, "evil<script>"):
        with pytest.raises(register.FlowError):
            register.build_manifest(BASE, bad, 9000)


def test_target_and_form_escape_everything():
    assert register.target_url(None, "s1").startswith("https://github.com/settings/apps/new?state=s1")
    assert register.target_url("my org", "s1").startswith("https://github.com/organizations/my%20org/settings/apps/new")
    page = register.form_page(dict(BASE, description='"><script>alert(1)</script>'), "https://github.com/x?a=1&b=2")
    assert "<script>alert" not in page and "&lt;script&gt;" in page and "a=1&amp;b=2" in page


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def json_opener(routes, calls):
    """A urlopen stand-in: routes maps 'METHOD /path' to a JSON-able answer or an int status."""
    def opener(req, timeout=30):
        path = req.full_url.split("api.github.com", 1)[1].split("?")[0]
        key = f"{req.get_method()} {path}"
        calls.append((key, req.headers.get("Authorization"), req.data))
        ans = routes.get(key, 404)
        if isinstance(ans, int):
            raise urllib.error.HTTPError(req.full_url, ans, "x", {}, io.BytesIO(b"{}"))
        return FakeResp(json.dumps(ans).encode())
    return opener


APP = {"id": 7, "slug": "acme-claude", "name": "acme-claude", "client_id": "Iv23abc", "html_url": "https://github.com/apps/acme-claude",
       "owner": {"login": "acme", "type": "Organization", "id": 1}, "pem": "-----BEGIN RSA PRIVATE KEY-----\nAAA\n-----END RSA PRIVATE KEY-----",
       "client_secret": "cs-secret", "webhook_secret": "wh-secret"}


def test_convert_validates_the_code_and_reports_refusals():
    calls = []
    got = register.convert("abc123", opener=json_opener({"POST /app-manifests/abc123/conversions": APP}, calls))
    assert got["slug"] == "acme-claude" and calls[0][1] is None, "the conversion is unauthenticated"
    with pytest.raises(register.FlowError, match="malformed"):
        register.convert("../x", opener=json_opener({}, []))
    with pytest.raises(register.FlowError, match="HTTP 404"):
        register.convert("gone", opener=json_opener({}, []))


def test_save_credentials_keeps_the_key_private_and_drops_the_secrets(tmp_path):
    key, meta = register.save_credentials(APP, tmp_path / "cfg")
    assert stat.S_IMODE(os.stat(key).st_mode) == 0o600
    saved = json.loads(meta.read_text())
    text = meta.read_text()
    assert "PRIVATE KEY" not in text and "cs-secret" not in text and "wh-secret" not in text
    assert saved["bot_login"] == "acme-claude[bot]" and saved["client_id"] == "Iv23abc"
    assert saved["owner"] == {"login": "acme", "type": "Organization"}
    with pytest.raises(register.FlowError, match="already exists"):
        register.save_credentials(APP, tmp_path / "cfg")
    register.save_credentials(APP, tmp_path / "cfg", force=True)
    steps = register.next_steps(APP, key, "--org acme")
    assert "PRIVATE KEY" not in steps and "cs-secret" not in steps
    assert "gh secret set AGENT_APP_CLIENT_ID --body 'Iv23abc' --org acme" in steps
    assert "https://github.com/apps/acme-claude/installations/new" in steps


def test_serve_checks_state_and_returns_the_converted_app():
    manifest = register.build_manifest(BASE, "acme-claude", 0)
    ready = threading.Event()
    box = {}

    def on_ready(address):
        box["address"] = address
        ready.set()

    def run():
        box["app"] = register.serve(manifest, "https://github.com/settings/apps/new?state=s", "good-state", 0,
                                    converter=lambda code: dict(APP, code=code), timeout=20, on_ready=on_ready)

    t = threading.Thread(target=run)
    t.start()
    assert ready.wait(10)
    base = box["address"]
    page = urllib.request.urlopen(base, timeout=5).read().decode()
    assert "Create the App on GitHub" in page and "acme-claude" in page
    with pytest.raises(urllib.error.HTTPError) as bad:
        urllib.request.urlopen(base + "callback?code=c1&state=wrong", timeout=5)
    assert bad.value.code == 400
    ok = urllib.request.urlopen(base + "callback?code=c1&state=good-state", timeout=5).read().decode()
    assert "Registered" in ok
    t.join(10)
    assert box["app"]["code"] == "c1"


def test_dry_run_starts_nothing(capsys):
    assert register.main(["--dry-run", "--name", "acme-claude"], converter=None, open_browser=None) == 0
    assert '"name": "acme-claude"' in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# agent_token.py
# --------------------------------------------------------------------------- #
needs_openssl = pytest.mark.skipif(not shutil.which("openssl"), reason="openssl not installed")


@pytest.fixture(scope="module")
def keypair(tmp_path_factory):
    if not shutil.which("openssl"):
        pytest.skip("openssl not installed")
    d = tmp_path_factory.mktemp("keys")
    key, pub = d / "app.pem", d / "pub.pem"
    subprocess.run(["openssl", "genrsa", "-out", str(key), "2048"], check=True, capture_output=True)
    subprocess.run(["openssl", "rsa", "-in", str(key), "-pubout", "-out", str(pub)], check=True, capture_output=True)
    return key, pub


def unb64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


@needs_openssl
def test_app_jwt_is_a_verifiable_rs256_token(keypair, tmp_path):
    key, pub = keypair
    jwt = agent_token.app_jwt("Iv23abc", key, now=1_000_000)
    header, payload, sig = jwt.split(".")
    assert json.loads(unb64(header)) == {"alg": "RS256", "typ": "JWT"}
    claims = json.loads(unb64(payload))
    assert claims == {"iat": 999_940, "exp": 1_000_540, "iss": "Iv23abc"}
    assert claims["exp"] - claims["iat"] <= 600, "GitHub refuses a JWT that lives over ten minutes"
    sig_file = tmp_path / "sig"
    sig_file.write_bytes(unb64(sig))
    v = subprocess.run(["openssl", "dgst", "-sha256", "-verify", str(pub), "-signature", str(sig_file)],
                       input=f"{header}.{payload}".encode(), capture_output=True)
    assert v.returncode == 0, v.stderr


ROUTES = {
    "GET /app": {"slug": "acme-claude"},
    "GET /repos/acme/web/installation": {"id": 42},
    "POST /app/installations/42/access_tokens": {"token": "ghs_secret_token", "expires_at": "2026-11-22T17:00:00Z"},
    "GET /users/acme-claude%5Bbot%5D": {"id": 555, "login": "acme-claude[bot]"},
}


def fake_jwt(app_id, key_path):
    return "jwt-for-" + app_id


def test_mint_scopes_the_token_and_names_the_bot():
    calls = []
    ident = agent_token.mint("Iv23abc", "k.pem", "acme/web", opener=json_opener(ROUTES, calls), jwt_fn=fake_jwt)
    assert ident == {"token": "ghs_secret_token", "expires_at": "2026-11-22T17:00:00Z", "slug": "acme-claude",
                     "login": "acme-claude[bot]", "id": 555, "email": "555+acme-claude[bot]@users.noreply.github.com"}
    post = next(c for c in calls if c[0].startswith("POST"))
    assert json.loads(post[2]) == {"repositories": ["web"]}, "the token is scoped to the one repository"
    assert all(c[1] == "Bearer jwt-for-Iv23abc" for c in calls[:3])


def test_mint_explains_a_missing_installation():
    routes = {k: v for k, v in ROUTES.items() if "installation" not in k}
    with pytest.raises(agent_token.IdentityError, match="installations/new"):
        agent_token.mint("Iv23abc", "k.pem", "acme/web", opener=json_opener(routes, []), jwt_fn=fake_jwt)
    with pytest.raises(agent_token.IdentityError, match="owner/name"):
        agent_token.mint("Iv23abc", "k.pem", "not a repo", opener=json_opener(ROUTES, []), jwt_fn=fake_jwt)


def test_run_mode_hands_the_token_to_the_command_and_never_prints_it(capsys):
    seen = {}

    def runner(cmd, env):
        seen.update(cmd=cmd, env=env)
        return 3

    rc = agent_token.main(["--app-id", "Iv23abc", "--key", "k.pem", "--repo", "acme/web", "--", "gh", "auth", "status"],
                          opener=json_opener(ROUTES, []), jwt_fn=fake_jwt, runner=runner)
    assert rc == 3, "the command's own exit code"
    env = seen["env"]
    assert seen["cmd"] == ["gh", "auth", "status"] and env["GH_TOKEN"] == "ghs_secret_token"
    assert env["GIT_AUTHOR_NAME"] == env["GIT_COMMITTER_NAME"] == "acme-claude[bot]"
    assert env["GIT_AUTHOR_EMAIL"] == "555+acme-claude[bot]@users.noreply.github.com"
    assert "GITHUB_TOKEN" not in env
    out = capsys.readouterr()
    assert "ghs_secret_token" not in out.out + out.err


def test_whoami_omits_the_token_and_env_prints_exports(capsys):
    args = ["--app-id", "Iv23abc", "--key", "k.pem", "--repo", "acme/web"]
    assert agent_token.main(args + ["whoami"], opener=json_opener(ROUTES, []), jwt_fn=fake_jwt) == 0
    who = capsys.readouterr().out
    assert "ghs_secret_token" not in who and '"login": "acme-claude[bot]"' in who
    assert agent_token.main(args + ["env"], opener=json_opener(ROUTES, []), jwt_fn=fake_jwt) == 0
    assert 'export GH_TOKEN="ghs_secret_token"' in capsys.readouterr().out


def test_saved_app_metadata_is_resolved(tmp_path):
    key, _ = register.save_credentials(APP, tmp_path)
    ns = type("A", (), {"app": "acme-claude", "config_dir": str(tmp_path), "app_id": None, "key": None})()
    assert agent_token.resolve_app(ns) == ("Iv23abc", key)
