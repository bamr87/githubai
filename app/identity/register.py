#!/usr/bin/env python3
"""Register the agent identity App from app/identity/manifest.json in one step.

    python3 app/identity/register.py                     # an App owned by your account
    python3 app/identity/register.py --org my-org        # an App owned by an organization
    python3 app/identity/register.py --name acme-claude --dry-run

GitHub's App Manifest flow: this script serves one page on 127.0.0.1, your
browser posts the manifest from it to GitHub, you confirm the App's name, and
GitHub redirects back here with a one-time code. The script exchanges the code
for the App's credentials (an unauthenticated call, valid for one hour) and
keeps only what an identity needs:

    ~/.config/githubai/<slug>.pem    the private key, mode 0600, never printed
    ~/.config/githubai/<slug>.json   id, slug, client id, owner and URLs (no secret)

The client secret and webhook secret GitHub also returns are discarded: the
identity App has no webhook and no OAuth flow. Then it prints the commands that
store the two Actions secrets the GitHubAI lanes read (AGENT_APP_CLIENT_ID and
AGENT_APP_PRIVATE_KEY) and the link that installs the App on your repositories.
It never sets a secret or installs anything itself.

Standard library only. Exit codes: 0 registered (or the dry run printed),
1 the flow failed or timed out, 2 usage.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import secrets
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.json"
DEFAULT_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "githubai"
DEFAULT_PORT = 8719
API = "https://api.github.com"
NAME_RX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,33}$")  # GitHub App names: 34 characters at most
KEEP = ("id", "slug", "name", "client_id", "html_url", "owner", "created_at")

Converter = Callable[[str], dict]


class FlowError(RuntimeError):
    """The registration could not finish; the message says why and what to do."""


def build_manifest(base: dict, name: str, port: int) -> dict:
    """The manifest with this run's name and local callback filled in."""
    if not NAME_RX.match(name):
        raise FlowError(f"App name {name!r}: use 1-34 letters, digits or hyphens, starting with a letter or digit")
    manifest = dict(base)
    manifest["name"] = name
    manifest["redirect_url"] = f"http://127.0.0.1:{port}/callback"
    manifest.pop("hook_attributes", None)  # an identity receives no events
    manifest["default_events"] = []
    manifest["public"] = False
    return manifest


def target_url(org: str | None, state: str) -> str:
    """Where the browser posts the manifest: the user's or an organization's new-App page."""
    q = urllib.parse.urlencode({"state": state})
    if org:
        return f"https://github.com/organizations/{urllib.parse.quote(org, safe='')}/settings/apps/new?{q}"
    return f"https://github.com/settings/apps/new?{q}"


def form_page(manifest: dict, target: str) -> str:
    """One page that posts the manifest to GitHub. Every value is HTML-escaped."""
    m = html.escape(json.dumps(manifest), quote=True)
    pretty = html.escape(json.dumps(manifest, indent=2))
    return f"""<!doctype html><meta charset="utf-8"><title>Register the agent identity App</title>
<body style="font-family:system-ui;max-width:46rem;margin:2rem auto;padding:0 1rem">
<h1>Register the agent identity App</h1>
<p>Submitting hands the manifest below to GitHub, which creates the App and sends a one-time code back to this
terminal. You can change the App's name on GitHub's page before confirming.</p>
<form method="post" action="{html.escape(target, quote=True)}">
<input type="hidden" name="manifest" value="{m}">
<button type="submit" style="font-size:1.1rem;padding:.5rem 1rem">Create the App on GitHub</button>
</form>
<pre style="background:#f6f8fa;padding:1rem;overflow:auto">{pretty}</pre></body>"""


def convert(code: str, opener=urllib.request.urlopen) -> dict:
    """Exchange the one-time manifest code for the App's credentials (no auth needed; the code is the proof)."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", code or ""):
        raise FlowError("GitHub returned a malformed manifest code")
    req = urllib.request.Request(f"{API}/app-manifests/{code}/conversions", method="POST", data=b"",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "githubai-identity"})
    try:
        with opener(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise FlowError(f"GitHub refused the manifest code (HTTP {e.code}); codes expire after an hour, run again") from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise FlowError(f"could not reach GitHub to finish the registration: {e}") from e


def save_credentials(app: dict, out_dir: Path, force: bool = False) -> tuple[Path, Path]:
    """Write the key (0600, created exclusively) and the non-secret metadata. Returns both paths."""
    slug, pem = app.get("slug"), app.get("pem")
    if not slug or not re.fullmatch(r"[a-z0-9-]+", slug) or not pem or "PRIVATE KEY" not in pem:
        raise FlowError("GitHub's answer had no usable slug or private key")
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o700)
    key_path, meta_path = out_dir / f"{slug}.pem", out_dir / f"{slug}.json"
    flags = os.O_WRONLY | os.O_CREAT | (os.O_TRUNC if force else os.O_EXCL)
    try:
        fd = os.open(key_path, flags, 0o600)
    except FileExistsError as e:
        raise FlowError(f"{key_path} already exists; pass --force to replace it") from e
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(pem if pem.endswith("\n") else pem + "\n")
    os.chmod(key_path, 0o600)
    meta = {k: app.get(k) for k in KEEP}
    if isinstance(meta.get("owner"), dict):
        meta["owner"] = {"login": meta["owner"].get("login"), "type": meta["owner"].get("type")}
    meta["bot_login"] = f"{slug}[bot]"
    meta["key_path"] = str(key_path)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return key_path, meta_path


def next_steps(app: dict, key_path: Path, scope: str | None) -> str:
    """What the maintainer does next, as commands. No secret value appears in it."""
    where = f" {scope}" if scope else " --repo <owner>/<repo>   # or --org <org> for every repository"
    slug = app["slug"]
    lines = [
        f"✓ Registered {app.get('name') or slug} (App id {app.get('id')}, client id {app.get('client_id')}).",
        f"  It acts on GitHub as {slug}[bot]. Private key: {key_path} (mode 0600).",
        "",
        "1. Install it on the repositories its agents may write to:",
        f"     {app.get('html_url') or 'https://github.com/apps/' + slug}/installations/new",
        "2. Store the two Actions secrets the GitHubAI lanes read:",
        f"     gh secret set AGENT_APP_CLIENT_ID --body '{app.get('client_id')}'{where}",
        f"     gh secret set AGENT_APP_PRIVATE_KEY{where} < '{key_path}'",
        "3. Act as it from a local session (docs: app/identity/README.md):",
        f"     python3 app/identity/agent_token.py --app {slug} --repo <owner>/<repo> -- gh auth status",
    ]
    return "\n".join(lines)


def serve(manifest: dict, target: str, state: str, port: int, converter: Converter,
          timeout: float = 600, on_ready: Callable[[str], None] | None = None) -> dict:
    """Serve the form on 127.0.0.1 and wait for GitHub's redirect. Returns the converted App."""
    result: dict = {}
    page = form_page(manifest, target)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # the code and state never reach a log
            pass

        def _send(self, status: int, body: str):
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):  # noqa: N802 (http.server's naming)
            url = urllib.parse.urlsplit(self.path)
            if url.path == "/":
                return self._send(200, page)
            if url.path != "/callback":
                return self._send(404, "not found")
            q = urllib.parse.parse_qs(url.query)
            if not secrets.compare_digest((q.get("state") or [""])[0], state):
                return self._send(400, "<p>State mismatch: this callback did not come from the page this run served.</p>")
            try:
                result["app"] = converter((q.get("code") or [""])[0])
            except FlowError as e:
                result["error"] = str(e)
                return self._send(502, f"<p>{html.escape(str(e))}</p>")
            self._send(200, "<h1>Registered.</h1><p>Return to the terminal for the next steps. You can close this tab.</p>")
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    server = HTTPServer(("127.0.0.1", port), Handler)
    address = f"http://127.0.0.1:{server.server_address[1]}/"
    if on_ready:
        on_ready(address)
    timer = threading.Timer(timeout, server.shutdown)
    timer.start()
    try:
        server.serve_forever()
    finally:
        timer.cancel()
        server.server_close()
    if "app" in result:
        return result["app"]
    raise FlowError(result.get("error") or f"no callback from GitHub within {int(timeout)} seconds")


def main(argv: list[str] | None = None, converter: Converter = convert, open_browser=webbrowser.open) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--name", help="the App's name (default: <your login or --org>-claude); GitHub lets you edit it")
    ap.add_argument("--org", help="register the App under this organization instead of your account")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"local callback port (default {DEFAULT_PORT})")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_DIR, help=f"where the key is kept (default {DEFAULT_DIR})")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--force", action="store_true", help="replace an existing key file for the same slug")
    ap.add_argument("--no-browser", action="store_true", help="print the local address instead of opening it")
    ap.add_argument("--dry-run", action="store_true", help="print the manifest and the target, start nothing")
    args = ap.parse_args(argv)

    owner = args.org or os.environ.get("GITHUB_USER") or os.environ.get("USER") or "my"
    name = args.name or f"{owner}-claude"[:34]
    try:
        manifest = build_manifest(json.loads(args.manifest.read_text(encoding="utf-8")), name, args.port)
    except (OSError, json.JSONDecodeError) as e:
        print(f"✗ cannot read {args.manifest}: {e}", file=sys.stderr)
        return 2
    except FlowError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2
    state = secrets.token_urlsafe(24)
    target = target_url(args.org, state)
    if args.dry_run:
        print(json.dumps(manifest, indent=2))
        print(f"\nwould post to {target.split('?')[0]} and wait on {manifest['redirect_url']}")
        return 0

    def ready(address: str):
        print(f"▸ Open {address} to register {name!r} (waiting up to 10 minutes; Ctrl-C to stop).")
        if not args.no_browser:
            open_browser(address)

    try:
        app = serve(manifest, target, state, args.port, converter, on_ready=ready)
        key_path, _ = save_credentials(app, args.out_dir.expanduser(), force=args.force)
    except FlowError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"✗ could not listen on 127.0.0.1:{args.port} ({e}); pass --port", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n✗ stopped before GitHub called back; nothing was registered here", file=sys.stderr)
        return 1
    print(next_steps(app, key_path, f"--org {args.org}" if args.org else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
