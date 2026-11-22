#!/usr/bin/env python3
"""Act as the agent identity App from a local shell or Claude Code session.

    python3 app/identity/agent_token.py --app acme-claude --repo acme/web -- gh pr create --draft --fill
    python3 app/identity/agent_token.py --app acme-claude --repo acme/web -- claude     # a session that writes as the bot
    python3 app/identity/agent_token.py --app acme-claude --repo acme/web whoami         # the identity, no token
    eval "$(python3 app/identity/agent_token.py --app acme-claude --repo acme/web env)" # exports, for your own shell

It signs a short JWT with the App's private key (`openssl`, so no Python
dependency), finds the App's installation on the repository's owner, mints a
one-hour installation token, and runs the command with:

    GH_TOKEN                          the installation token (gh, and git through `gh auth setup-git`)
    GIT_AUTHOR_NAME / _EMAIL          <slug>[bot] and its noreply address, so GitHub credits the bot
    GIT_COMMITTER_NAME / _EMAIL       the same
    AGENT_LOGIN                       <slug>[bot]

The default mode runs the command and never prints the token. `env` prints
export lines for `eval` and is the only mode whose output contains it.

The App comes from --app <slug> (the metadata app/identity/register.py saved),
or --app-id and --key, or AGENT_APP_CLIENT_ID and AGENT_APP_PRIVATE_KEY_FILE.
Exit codes: the command's own exit code; 2 for usage or a failure before it ran.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
DEFAULT_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "githubai"
REPO_RX = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class IdentityError(RuntimeError):
    """Minting failed; the message says why and what to check."""


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def app_jwt(app_id: str, key_path: Path, now: int | None = None, openssl: str = "openssl") -> str:
    """An RS256 JWT for the App, valid for nine minutes (GitHub allows ten), backdated a minute for clock skew."""
    if not shutil.which(openssl):
        raise IdentityError("openssl is not on PATH; it signs the App's JWT")
    now = int(time.time()) if now is None else now
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = b64url(json.dumps({"iat": now - 60, "exp": now + 540, "iss": str(app_id)}, separators=(",", ":")).encode())
    signing_input = f"{header}.{payload}".encode("ascii")
    r = subprocess.run([openssl, "dgst", "-sha256", "-sign", str(key_path)], input=signing_input,
                       capture_output=True, check=False)
    if r.returncode != 0 or not r.stdout:
        raise IdentityError(f"openssl could not sign with {key_path}: {r.stderr.decode(errors='replace').strip()[:200]}")
    return f"{header}.{payload}.{b64url(r.stdout)}"


def http(method: str, path: str, token: str, body: dict | None = None, opener=urllib.request.urlopen) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}/{path.lstrip('/')}", data=data, method=method, headers={
        "Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "githubai-identity"})
    try:
        with opener(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        raise IdentityError(f"GitHub answered {e.code} to {method} /{path.split('?')[0]}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise IdentityError(f"could not reach GitHub: {e}") from e


def mint(app_id: str, key_path: Path, repo: str, opener=urllib.request.urlopen, jwt_fn=app_jwt) -> dict:
    """The installation token for `repo`, scoped to that one repository, and who it acts as."""
    if not REPO_RX.match(repo):
        raise IdentityError(f"--repo must be owner/name, not {repo!r}")
    jwt = jwt_fn(app_id, key_path)
    slug = (http("GET", "app", jwt, opener=opener) or {}).get("slug")
    if not slug:
        raise IdentityError("GitHub did not say which App this key belongs to")
    try:
        inst = http("GET", f"repos/{repo}/installation", jwt, opener=opener)
    except IdentityError as e:
        raise IdentityError(f"{slug} is not installed on {repo} ({e}); install it from "
                            f"https://github.com/apps/{slug}/installations/new") from e
    name = repo.split("/", 1)[1]
    tok = http("POST", f"app/installations/{inst['id']}/access_tokens", jwt, {"repositories": [name]}, opener=opener)
    login = f"{slug}[bot]"
    user = http("GET", f"users/{urllib.parse.quote(login, safe='')}", tok["token"], opener=opener) or {}
    if not user.get("id"):
        raise IdentityError(f"GitHub has no user for {login}")
    return {"token": tok["token"], "expires_at": tok.get("expires_at"), "slug": slug, "login": login,
            "id": user["id"], "email": f"{user['id']}+{login}@users.noreply.github.com"}


def child_env(ident: dict, base: dict | None = None) -> dict:
    env = dict(os.environ if base is None else base)
    env.update({"GH_TOKEN": ident["token"], "AGENT_LOGIN": ident["login"],
                "GIT_AUTHOR_NAME": ident["login"], "GIT_AUTHOR_EMAIL": ident["email"],
                "GIT_COMMITTER_NAME": ident["login"], "GIT_COMMITTER_EMAIL": ident["email"]})
    env.pop("GITHUB_TOKEN", None)  # gh prefers GH_TOKEN, but a stray GITHUB_TOKEN must not win elsewhere
    return env


def resolve_app(args) -> tuple[str, Path]:
    """The App id (or client id) and its key, from --app's saved metadata, flags or the environment."""
    if args.app:
        meta_path = Path(args.config_dir).expanduser() / f"{args.app}.json"
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise IdentityError(f"no saved App {args.app!r} at {meta_path} (run app/identity/register.py)") from e
        return str(meta.get("client_id") or meta["id"]), Path(meta["key_path"])
    app_id = args.app_id or os.environ.get("AGENT_APP_CLIENT_ID")
    key = args.key or os.environ.get("AGENT_APP_PRIVATE_KEY_FILE")
    if not app_id or not key:
        raise IdentityError("name the App: --app <slug>, or --app-id and --key, or AGENT_APP_CLIENT_ID and "
                            "AGENT_APP_PRIVATE_KEY_FILE")
    return str(app_id), Path(key)


def main(argv: list[str] | None = None, opener=urllib.request.urlopen, jwt_fn=app_jwt, runner=subprocess.call) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    command: list[str] = []
    if "--" in argv:
        i = argv.index("--")
        argv, command = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mode", nargs="?", choices=("run", "env", "whoami"), default="run")
    ap.add_argument("--app", help="the App's slug, as app/identity/register.py saved it")
    ap.add_argument("--app-id", help="the App's client id (or numeric id)")
    ap.add_argument("--key", help="path to the App's private key")
    ap.add_argument("--repo", required=True, help="owner/name the token is scoped to")
    ap.add_argument("--config-dir", default=str(DEFAULT_DIR))
    args = ap.parse_args(argv)
    if args.mode == "run" and not command:
        ap.error("run needs a command after --, e.g. -- gh auth status")
    try:
        app_id, key = resolve_app(args)
        ident = mint(app_id, key, args.repo, opener=opener, jwt_fn=jwt_fn)
    except IdentityError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2
    if args.mode == "whoami":
        print(json.dumps({k: ident[k] for k in ("login", "id", "email", "slug", "expires_at")}, indent=2))
        return 0
    if args.mode == "env":
        for k, v in child_env(ident, base={}).items():
            print(f"export {k}={json.dumps(v)}")
        return 0
    print(f"▸ running as {ident['login']} on {args.repo} (token expires {ident.get('expires_at') or 'in an hour'})",
          file=sys.stderr)
    return runner(command, env=child_env(ident))


if __name__ == "__main__":
    sys.exit(main())
