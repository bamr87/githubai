#!/usr/bin/env python3
"""seed.py — the AI-Seed planter and checker.

Single-file, stdlib-only (Python 3.10+), designed to be vendored: the planter
copies ITSELF into every target at .seed/tools/seed.py, so a planted repo can
verify itself in CI and plant the kernel onward (pollination).

Commands:
    plant <target>   stamp the AI-Seed kernel into a directory (additive-only;
                     idempotent and resumable — rerunning fills gaps, never
                     overwrites without --force; --update re-renders the
                     kernel-managed files from the current kernel + manifest)
    check <target>   structural gate: manifest, kill switch, Evolution Log,
                     guardrail markers in workflows, telemetry ledger, and —
                     when a kernel is present — kernel/installation parity
    status <target>  human summary: identity, gates, pause, recent ticks
    version          print the kernel version this copy carries

Design notes:
- The manifest (.seed/seed.yml) is a deliberately flat YAML subset (nested
  maps of scalar values, no lists) parsed by a small deterministic parser, so
  behavior is identical with or without PyYAML installed.
- File classes: USER-OWNED files (CONCEPT.md, CLAUDE.md, .seed/seed.yml,
  .seed/pause.yml, .seed/garden.yml) are written once and never touched again
  except with --force. KERNEL-MANAGED files (.github/workflows/seed-*.yml,
  .seed/telemetry/README.md, the vendored .seed/tools/seed.py) are re-rendered
  by --update and parity-checked by `check`.
- The planter never talks to GitHub: it writes files. Creating repos, setting
  secrets/variables, and branch protection are a human's acts, listed in the
  next-steps output.

Provenance: the plant/resume semantics follow year-of-ai's plant-lineage.rb,
the parity check follows the bamr87 hub's vendored-tool drift gate, and the
single-file stdlib posture follows bamr87/SCHEMA's schema_lint.py. See
docs/PATTERNS.md in bamr87/ai-seed.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import json
import re
import sys
from pathlib import Path

# Kept in sync with seed/VERSION by tests; the VERSION file wins when present.
KERNEL_VERSION = "0.5.0"

PLACEHOLDER_RE = re.compile(r"__SEED_[A-Z_]+__")

# Kernel-relative paths that stay user-owned after first write.
USER_OWNED = {
    "CONCEPT.md",
    "CLAUDE.md",
    ".seed/seed.yml",
    ".seed/pause.yml",
}

# Kernel-relative paths that are kernel-managed but only seeded when the
# corresponding flag is passed to `plant` (skip entirely otherwise).
SCHEMA_OPTIONAL = {"SCHEMA.md"}  # --schema

VENDORED_TOOL = ".seed/tools/seed.py"
LEDGER = ".seed/telemetry/evolution.jsonl"

DEFAULT_CRON = "17 4 * * 1"
DEFAULT_TEND_CRON = "47 */6 * * *"
DEFAULT_PLANTED_FROM = "bamr87/ai-seed"


# ---------------------------------------------------------------------------
# Minimal deterministic YAML-subset parser (nested maps of scalars, comments).
# ---------------------------------------------------------------------------

def parse_simple_yaml(text: str) -> dict:
    """Parse the flat YAML subset used by .seed/seed.yml and pause.yml.

    Supports nested maps and scalar values (quoted or bare), full-line and
    trailing ` #` comments. Lists and multi-line values are out of contract.
    Scalars are returned as strings ("true"/"false" stay strings on purpose —
    checks compare literally).
    """
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = raw.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, sep, val = line.strip().partition(":")
        if not sep:
            continue  # not key/value — out of contract, skip
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in {'"', "'"}:
            val = val[1:-1]
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else root
        # Inline flow lists are part of the manifest contract (policy.board /
        # policy.merge), so the parser understands them; block sequences are
        # still out of contract.
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            parent[key] = [i.strip().strip('"').strip("'")
                           for i in inner.split(",")] if inner else []
            continue
        if val == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = val
    return root


def dig(data: dict, *keys: str) -> str | list | dict | None:
    cur: object = data
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Kernel location and rendering.
# ---------------------------------------------------------------------------

def find_kernel(explicit: str | None) -> Path | None:
    """Locate seed/kernel: --kernel wins, else walk up from this file."""
    if explicit:
        p = Path(explicit).resolve()
        return p if (p / "CONCEPT.md").is_file() else None
    here = Path(__file__).resolve()
    for base in list(here.parents):
        cand = base / "seed" / "kernel"
        if (cand / "CONCEPT.md").is_file():
            return cand
    return None


def kernel_version(kernel: Path | None) -> str:
    if kernel is not None:
        vf = kernel.parent / "VERSION"
        if vf.is_file():
            return vf.read_text(encoding="utf-8").strip()
    return KERNEL_VERSION


def kernel_files(kernel: Path) -> list[str]:
    """Kernel-relative paths, sorted, excluding scratch."""
    out = []
    for p in sorted(kernel.rglob("*")):
        if p.is_file():
            out.append(p.relative_to(kernel).as_posix())
    return out


def render(text: str, tokens: dict[str, str], source: str) -> str:
    for k, v in tokens.items():
        text = text.replace(f"__SEED_{k}__", v)
    leftover = sorted(set(PLACEHOLDER_RE.findall(text)))
    if leftover:
        raise SystemExit(
            f"error: unresolved placeholder(s) {leftover} rendering {source} — "
            "the kernel and the planter disagree; update tools/seed.py or the template."
        )
    return text


def tokens_from_args(args: argparse.Namespace) -> dict[str, str]:
    repo = args.repo
    name = args.name or (repo.rsplit("/", 1)[-1] if repo else Path(args.target).resolve().name)
    if not repo:
        raise SystemExit("error: --repo owner/name is required for a fresh plant "
                         "(an existing .seed/seed.yml would provide it).")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*", repo):
        raise SystemExit(f"error: --repo must look like owner/name (got '{repo}').")
    return {
        "NAME": name,
        "REPO": repo,
        "DEFAULT_BRANCH": args.default_branch,
        "PLANTED": args.date or _dt.date.today().isoformat(),
        "KERNEL_VERSION": kernel_version(args.kernel_path),
        "PLANTED_FROM": args.planted_from,
        "GROW_CRON": args.cron,
        "TEND_CRON": args.tend_cron,
    }


def tokens_from_manifest(manifest: dict, kver: str) -> dict[str, str]:
    def need(*keys: str) -> str:
        v = dig(manifest, *keys)
        if not isinstance(v, str) or not v:
            raise SystemExit(f"error: .seed/seed.yml is missing {'.'.join(keys)} — cannot render.")
        return v
    return {
        "NAME": need("seed", "name"),
        "REPO": need("seed", "repo"),
        "DEFAULT_BRANCH": need("seed", "default_branch"),
        "PLANTED": need("seed", "planted"),
        "KERNEL_VERSION": kver,
        "PLANTED_FROM": need("seed", "planted_from"),
        "GROW_CRON": need("policy", "cadence", "grow_cron"),
        # Optional: repos planted before kernel v0.3.0 carry no tend_cron, so
        # a re-render must not hard-fail on them.
        "TEND_CRON": (dig(manifest, "policy", "cadence", "tend_cron")
                      if isinstance(dig(manifest, "policy", "cadence", "tend_cron"), str)
                      else DEFAULT_TEND_CRON),
    }


# ---------------------------------------------------------------------------
# plant
# ---------------------------------------------------------------------------

def cmd_plant(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    kernel = args.kernel_path
    if kernel is None:
        raise SystemExit("error: seed kernel not found — run from an ai-seed clone "
                         "(or a repo that vendors seed/kernel), or pass --kernel PATH.")
    kver = kernel_version(kernel)
    manifest_path = target / ".seed" / "seed.yml"
    if manifest_path.is_file():
        manifest = parse_simple_yaml(manifest_path.read_text(encoding="utf-8"))
        tokens = tokens_from_manifest(manifest, kver)
        if args.repo and args.repo != tokens["REPO"]:
            raise SystemExit(f"error: target is already planted as '{tokens['REPO']}' — "
                             "refusing to re-identify it (edit .seed/seed.yml deliberately instead).")
    else:
        tokens = tokens_from_args(args)

    planted, skipped, updated, drifted = [], [], [], []

    def write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    for rel in kernel_files(kernel):
        # Optional surfaces: skip unless the caller explicitly opts in.
        if rel in SCHEMA_OPTIONAL and not args.schema:
            continue
        rendered = render((kernel / rel).read_text(encoding="utf-8"), tokens, rel)
        dest = target / rel
        managed = rel not in USER_OWNED
        if not dest.exists():
            write(dest, rendered)
            planted.append(rel)
        elif dest.read_text(encoding="utf-8") == rendered:
            skipped.append(rel)
        elif args.force or (args.update and managed):
            write(dest, rendered)
            updated.append(rel)
        else:
            drifted.append(rel)

    # Vendor this tool itself (kernel-managed).
    self_src = Path(__file__).resolve().read_text(encoding="utf-8")
    vend = target / VENDORED_TOOL
    if not vend.exists():
        write(vend, self_src)
        planted.append(VENDORED_TOOL)
    elif vend.read_text(encoding="utf-8") == self_src:
        skipped.append(VENDORED_TOOL)
    elif args.force or args.update:
        write(vend, self_src)
        updated.append(VENDORED_TOOL)
    else:
        drifted.append(VENDORED_TOOL)

    # The ledger exists from day zero (append-only from the first tick).
    ledger = target / LEDGER
    if not ledger.exists():
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.touch()
        planted.append(LEDGER)

    # --update keeps the manifest's kernel_version honest (surgical line edit —
    # the manifest is user-owned, so only this one line may change).
    if args.update and manifest_path.is_file():
        txt = manifest_path.read_text(encoding="utf-8")
        new = re.sub(r"(?m)^(\s*kernel_version:\s*).*$", rf"\g<1>{kver}", txt)
        if new != txt:
            manifest_path.write_text(new, encoding="utf-8")
            updated.append(".seed/seed.yml (kernel_version)")

    # Optional garden layer.
    if args.garden:
        garden_src = kernel.parent / "garden"
        pairs = [
            (garden_src / "garden.yml", target / ".seed" / "garden.yml", False),
            (garden_src / "garden-orchestrate.yml",
             target / ".github" / "workflows" / "garden-orchestrate.yml", True),
        ]
        for src, dest, managed in pairs:
            rel = dest.relative_to(target).as_posix()
            rendered = render(src.read_text(encoding="utf-8"), tokens, src.name)
            if not dest.exists():
                write(dest, rendered)
                planted.append(rel)
            elif dest.read_text(encoding="utf-8") == rendered:
                skipped.append(rel)
            elif args.force or (args.update and managed):
                write(dest, rendered)
                updated.append(rel)
            else:
                drifted.append(rel)

    for rel in planted:
        print(f"  planted: {rel}")
    for rel in updated:
        print(f"  updated: {rel}")
    for rel in drifted:
        print(f"  drift:   {rel} (differs from kernel; kept — use --update for "
              f"kernel-managed files or --force to overwrite everything)")
    print(f"plant: {len(planted)} planted, {len(updated)} updated, "
          f"{len(skipped)} already current, {len(drifted)} kept with drift "
          f"(kernel v{kver}, target {target})")

    if planted and ".seed/seed.yml" in planted:
        print(f"""
Next steps (human-owned — the planter never does these):
  1. Fill in CONCEPT.md §1–§5 — germination reads it.
  2. Commit and push, then in GitHub for {tokens['REPO']}:
       secrets:   CLAUDE_CODE_OAUTH_TOKEN   (claude setup-token; primary auth)
                  ANTHROPIC_API_KEY          (optional metered fallback)
                  SEED_PAT                   (fine-grained PAT: contents, pull-requests, issues
                                              and actions all :write — without contents CI does not
                                              fire on seed PRs; without issues the tend lane cannot
                                              close resolved CI-failure issues or escalate a PR)
       variables: SEED_GROW_ENABLED=true     (only when ready — the variable is the consent)
                  SEED_EVOLVE_ENABLED=true   (only when ready — enables the issue lane)
                  SEED_TEND_ENABLED=true     (only when ready — lets the seed review CI, repair
                                              its own red PRs, and MERGE what is provably green;
                                              the bounds live in policy.merge)
       labels:    seed:request  seed:approved  seed:hold
                  (the issue lane's state machine: intake / consent / brake —
                   seed-evolve.yml never fires without seed:approved existing)
       branch protection on {tokens['DEFAULT_BRANCH']}: require PRs + the seed-verify check.
  3. Germinate: Actions -> seed-germinate -> Run workflow -> confirm: {tokens['NAME']}
  4. Review the draft PR. With SEED_TEND_ENABLED off, humans merge everything;
     with it on, the seed merges only its own provably-green work and leaves
     anything else — red, conflicted, human-authored, or labelled — for you.""")
    return 0


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def finish(self, label: str) -> int:
        for w in self.warnings:
            print(f"  warning: {w}")
        for e in self.errors:
            print(f"  ERROR:   {e}")
        print(f"check: {label} — {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return 1 if self.errors else 0


def _grow_workflow_markers() -> dict[str, str]:
    """Guardrail markers every installed seed-grow.yml must carry."""
    return {
        "SEED_GROW_ENABLED": "the default-OFF consent gate (vars.SEED_GROW_ENABLED)",
        "pause.yml": "the kill-switch check (.seed/pause.yml)",
        "concurrency": "the seed-write serializer (concurrency group)",
        "anthropics/claude-code-action@v1": "the pinned Claude Code action",
        "claude_code_oauth_token": "OAuth-first auth wiring",
        "--draft": "PR-only publish (draft pull request)",
    }


def _tend_workflow_markers() -> dict[str, str]:
    """Guardrail markers every installed seed-tend.yml must carry.

    The tend lane is the only one that merges, so its stops are load-bearing:
    a marker that silently disappears turns a bounded lane into an unbounded
    one. Each entry names the mechanism, not just the string.
    """
    return {
        "SEED_TEND_ENABLED": "the default-OFF consent gate (vars.SEED_TEND_ENABLED)",
        "pause.yml": "the kill-switch check (.seed/pause.yml)",
        "^\\.github/workflows/": "the never-auto-merge stop for PRs that edit CI",
        "no longer eligible on live state": "the re-verification against live state before merging",
        "max_repair_attempts": "the per-PR repair budget (an unfixable PR must reach a terminal state)",
        "ATTEMPT_MARKER": "the attempt ledger marker the budget is counted from",
        "compare/": "the diff guard that reads what the repair pass actually pushed",
    }


def cmd_check(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    r = Report()
    wf_dir = target / ".github" / "workflows"

    # Manifest.
    manifest_path = target / ".seed" / "seed.yml"
    manifest: dict = {}
    if not manifest_path.is_file():
        r.error(".seed/seed.yml missing — not a planted repo (run: seed.py plant).")
    else:
        manifest = parse_simple_yaml(manifest_path.read_text(encoding="utf-8"))
        if dig(manifest, "schema") != "seed-manifest/v1":
            r.error(".seed/seed.yml schema must be seed-manifest/v1.")
        for keys in (("seed", "name"), ("seed", "repo"), ("seed", "default_branch"),
                     ("policy", "models", "plan"), ("policy", "models", "build"),
                     ("policy", "models", "verify"), ("policy", "cadence", "grow_cron"),
                     ("gates", "grow"), ("auth", "primary")):
            if not isinstance(dig(manifest, *keys), str):
                r.error(f".seed/seed.yml missing required key: {'.'.join(keys)}")
        if dig(manifest, "auth", "primary") not in (None, "CLAUDE_CODE_OAUTH_TOKEN"):
            r.warn("auth.primary is not CLAUDE_CODE_OAUTH_TOKEN — the framework is OAuth-first by doctrine.")
        for key, want in (("pr_only", "true"), ("workflows_agent_writable", "false")):
            v = dig(manifest, "guardrails", key)
            if v != want:
                r.error(f"guardrails.{key} must be {want} (got {v!r}) — the constitution does not weaken.")
        # Merging is either forbidden outright (kernel < 0.3.0) or policy-gated
        # (kernel >= 0.3.0). Either is acceptable; a repo that gates merging
        # must keep the hard stops that make the gate meaningful.
        if dig(manifest, "guardrails", "never_merge") != "true":
            for key, want in (("merge_requires_green", "true"),
                              ("merge_human_authored", "false")):
                v = dig(manifest, "guardrails", key)
                if v != want:
                    r.error(f"guardrails.{key} must be {want} (got {v!r}) — a seed that may "
                            f"merge must never merge a red PR or a human's PR. Set "
                            f"guardrails.never_merge: true to forbid merging entirely instead.")
            if not dig(manifest, "guardrails", "merge_blocked_by_label"):
                r.error("guardrails.merge_blocked_by_label is unset — auto-merge needs a label "
                        "a human can apply to stop it (e.g. human-review).")
            # Escalation is only terminal if the label it applies is BOTH a
            # merge block label (so the PR stops being merged) and an ignore
            # label (so it stops counting against the board). Configure it as
            # neither and the lane politely labels a PR that it then repairs
            # again next tick — a guardrail that reads as one but is not.
            block_label = dig(manifest, "guardrails", "merge_blocked_by_label")
            if block_label:
                for keys, why in (
                    (("policy", "merge", "block_labels"),
                     "auto-merge would ignore the label the tend lane escalates with"),
                    (("policy", "board", "ignore_labels"),
                     "an escalated pull request would keep blocking growth forever"),
                ):
                    labels = dig(manifest, *keys)
                    if isinstance(labels, list) and block_label not in labels:
                        r.error(f"guardrails.merge_blocked_by_label ({block_label}) is missing from "
                                f"{'.'.join(keys)} — {why}.")
            if not dig(manifest, "policy", "board", "max_repair_attempts"):
                r.warn("policy.board.max_repair_attempts is unset — a pull request the repair "
                       "pass cannot fix is retried every tick forever and blocks the board.")
            if dig(manifest, "policy", "merge", "auto") == "true" \
                    and dig(manifest, "gates", "tend") is None:
                r.warn("policy.merge.auto is on but gates.tend is unset — nothing gates the lane "
                       "that performs merges.")

    # Kill switch.
    pause_path = target / ".seed" / "pause.yml"
    if not pause_path.is_file():
        r.error(".seed/pause.yml missing — every planted repo carries its kill switch.")
    else:
        pause = parse_simple_yaml(pause_path.read_text(encoding="utf-8"))
        if dig(pause, "paused") not in ("true", "false"):
            r.error(".seed/pause.yml must set paused: true|false.")
        elif dig(pause, "paused") == "true":
            r.warn("seed is PAUSED (.seed/pause.yml) — loops will refuse to run.")

    # Concept + Evolution Log.
    concept = target / "CONCEPT.md"
    if not concept.is_file():
        r.error("CONCEPT.md missing — the repo has no genome.")
    else:
        ctext = concept.read_text(encoding="utf-8")
        if "§8 Evolution Log" not in ctext:
            r.error("CONCEPT.md has no '§8 Evolution Log' section.")
        elif not re.search(r"(?m)^### G\d+-T\d+ ", ctext):
            r.error("CONCEPT.md §8 has no tick entries (### G<gen>-T<seq> — ...).")

    # Workflows: grow markers + verify + steward + forbidden commands.
    grow = wf_dir / "seed-grow.yml"
    if not grow.is_file():
        r.error(".github/workflows/seed-grow.yml missing — the repo cannot grow.")
    else:
        gtext = grow.read_text(encoding="utf-8")
        for marker, why in _grow_workflow_markers().items():
            if marker not in gtext:
                r.error(f"seed-grow.yml lost its guardrail marker '{marker}' ({why}).")
    tend = wf_dir / "seed-tend.yml"
    if tend.is_file():
        ttext = tend.read_text(encoding="utf-8")
        for marker, why in _tend_workflow_markers().items():
            if marker not in ttext:
                r.error(f"seed-tend.yml lost its guardrail marker '{marker}' ({why}).")
    elif dig(manifest, "policy", "merge", "auto") == "true":
        r.warn("policy.merge.auto is on but .github/workflows/seed-tend.yml is missing — "
               "nothing performs (or bounds) merging.")
    verify = wf_dir / "seed-verify.yml"
    if not verify.is_file():
        r.warn(".github/workflows/seed-verify.yml missing — nothing gates seed structure in CI.")
    elif ".seed/tools/seed.py" not in verify.read_text(encoding="utf-8"):
        r.warn("seed-verify.yml does not run the vendored checker (.seed/tools/seed.py).")
    steward = False
    if wf_dir.is_dir():
        for wf in sorted(wf_dir.glob("*.yml")):
            wtext = wf.read_text(encoding="utf-8")
            if "claude-code-action" in wtext and "issue_comment" in wtext:
                steward = True
            # Merging is confined to ONE lane. Growth, germination and the
            # issue lane must never merge, whatever the merge policy says.
            if re.search(r"(?m)^\s*[^#]*gh pr merge", wtext) and wf.name.startswith("seed-"):
                if dig(manifest, "guardrails", "never_merge") == "true":
                    r.error(f"{wf.name} merges, but guardrails.never_merge is true — "
                            f"remove the merge, or change the policy deliberately.")
                elif wf.name != "seed-tend.yml":
                    r.error(f"{wf.name} contains 'gh pr merge' — only the tend lane "
                            f"(seed-tend.yml) may merge; the grow, germinate and evolve "
                            f"lanes never do.")
    if not steward:
        r.warn("no steward found (no workflow wiring claude-code-action to issue_comment) — @claude mentions go unanswered.")

    # A gate the manifest declares must have a workflow that reads it, or the
    # consent surface is a dead promise (the kernel shipped SEED_EVOLVE_ENABLED
    # with no workflow honoring it until kernel v0.2.0).
    for gate_name in ("grow", "evolve"):
        var = dig(manifest, "gates", gate_name)
        if not isinstance(var, str) or not var:
            continue
        honored = any(
            var in wf.read_text(encoding="utf-8")
            for wf in sorted(wf_dir.glob("*.yml"))
        ) if wf_dir.is_dir() else False
        if not honored:
            r.warn(f"gates.{gate_name} declares {var} but no workflow reads it — "
                   f"that consent gate controls nothing (expected .github/workflows/seed-{gate_name}.yml).")

    # Vendored tool + version skew.
    vend = target / VENDORED_TOOL
    if not vend.is_file():
        r.error(f"{VENDORED_TOOL} missing — the repo cannot verify itself or plant onward.")
    else:
        m = re.search(r'(?m)^KERNEL_VERSION = "([^"]+)"', vend.read_text(encoding="utf-8"))
        want = dig(manifest, "seed", "kernel_version")
        if m and isinstance(want, str) and m.group(1) != want:
            r.warn(f"vendored seed.py is v{m.group(1)} but the manifest says kernel v{want} — replant with --update.")

    # Telemetry ledger.
    ledger = target / LEDGER
    if ledger.is_file():
        for i, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                r.error(f"{LEDGER}:{i} is not valid JSON — the ledger contract is broken.")
                continue
            if rec.get("schema") != "seed-telemetry/v1":
                r.warn(f"{LEDGER}:{i} has schema {rec.get('schema')!r} (expected seed-telemetry/v1).")
    else:
        r.warn(f"{LEDGER} missing — plant creates it empty; the first tick appends.")

    # Kernel parity (only where a kernel is present: the framework repo/forks).
    kernel = args.kernel_path
    if kernel is not None and manifest:
        strict = args.strict or dig(manifest, "kernel", "strict") == "true"
        try:
            tokens = tokens_from_manifest(manifest, kernel_version(kernel))
        except SystemExit:
            tokens = None
        if tokens:
            for rel in kernel_files(kernel):
                if rel in USER_OWNED:
                    continue
                dest = target / rel
                if not dest.exists():
                    continue  # absence is reported by the structural checks
                want = render((kernel / rel).read_text(encoding="utf-8"), tokens, rel)
                got = dest.read_text(encoding="utf-8")
                if want != got:
                    diff = sum(1 for _ in difflib.unified_diff(
                        want.splitlines(), got.splitlines(), lineterm=""))
                    msg = (f"{rel} drifts from the kernel (~{diff} diff lines) — "
                           f"re-render with: seed.py plant . --update")
                    (r.error if strict else r.warn)(msg)

    return r.finish(str(target))


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def cmd_status(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    manifest_path = target / ".seed" / "seed.yml"
    if not manifest_path.is_file():
        print(f"status: {target} is not planted (.seed/seed.yml missing).")
        return 1
    manifest = parse_simple_yaml(manifest_path.read_text(encoding="utf-8"))
    pause = {}
    if (target / ".seed" / "pause.yml").is_file():
        pause = parse_simple_yaml((target / ".seed" / "pause.yml").read_text(encoding="utf-8"))
    print(f"seed:    {dig(manifest, 'seed', 'name')} ({dig(manifest, 'seed', 'repo')})")
    print(f"kernel:  v{dig(manifest, 'seed', 'kernel_version')} planted {dig(manifest, 'seed', 'planted')} from {dig(manifest, 'seed', 'planted_from')}")
    print(f"models:  plan={dig(manifest, 'policy', 'models', 'plan')} build={dig(manifest, 'policy', 'models', 'build')} verify={dig(manifest, 'policy', 'models', 'verify')}")
    print(f"cadence: {dig(manifest, 'policy', 'cadence', 'grow_cron')} (cron, UTC)")
    gates = dig(manifest, "gates") or {}
    shown = " ".join(f"{k}={v}" for k, v in gates.items()) if isinstance(gates, dict) else "?"
    print(f"gates:   {shown} (repo variables; unset = idle)")
    print(f"board:   clear_before_grow={dig(manifest, 'policy', 'board', 'clear_before_grow')} "
          f"| auto-merge={dig(manifest, 'policy', 'merge', 'auto')} "
          f"(blocked by {dig(manifest, 'guardrails', 'merge_blocked_by_label')})")
    print(f"paused:  {dig(pause, 'paused') or 'unknown'}"
          + (f" ({dig(pause, 'reason')})" if dig(pause, "reason") else ""))
    concept = target / "CONCEPT.md"
    if concept.is_file():
        ticks = re.findall(r"(?m)^### (G\d+-T\d+ — .+)$", concept.read_text(encoding="utf-8"))
        print(f"ticks:   {len(ticks)} logged")
        for t in ticks[-3:]:
            print(f"  {t}")
    ledger = target / LEDGER
    if ledger.is_file():
        lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
        print(f"ledger:  {len(lines)} tick record(s)")
        for ln in lines[-3:]:
            try:
                rec = json.loads(ln)
                print(f"  run {rec.get('run_id')} {rec.get('tick')} -> {rec.get('conclusion')} "
                      f"(files={rec.get('changed_files')}, cost={rec.get('cost_usd')})")
            except json.JSONDecodeError:
                print(f"  (unparseable line: {ln[:60]}…)")
    return 0


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="seed.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plant", help="stamp the AI-Seed kernel into a directory")
    p.add_argument("target")
    p.add_argument("--repo", help="owner/name identity for a fresh plant")
    p.add_argument("--name", help="seed name (default: repo basename)")
    p.add_argument("--default-branch", default="main")
    p.add_argument("--cron", default=DEFAULT_CRON, help=f"grow schedule, UTC (default: '{DEFAULT_CRON}')")
    p.add_argument("--tend-cron", default=DEFAULT_TEND_CRON,
                   help=f"tend schedule, UTC (default: '{DEFAULT_TEND_CRON}')")
    p.add_argument("--date", help="plant date YYYY-MM-DD (default: today; for reproducible tests)")
    p.add_argument("--planted-from", default=DEFAULT_PLANTED_FROM)
    p.add_argument("--kernel", help="explicit path to seed/kernel")
    p.add_argument("--update", action="store_true",
                   help="re-render kernel-managed files from the current kernel + manifest")
    p.add_argument("--force", action="store_true",
                   help="overwrite EVERYTHING from the kernel, user-owned files included (destructive)")
    p.add_argument("--garden", action="store_true", help="also install the garden hub layer")
    p.add_argument("--schema", action="store_true",
                   help="seed SCHEMA.md (Pyramid Schema) — kernel-managed, refreshed by --update")
    p.set_defaults(func=cmd_plant)

    c = sub.add_parser("check", help="structural gate for a planted repo")
    c.add_argument("target")
    c.add_argument("--kernel", help="explicit path to seed/kernel (for parity)")
    c.add_argument("--strict", action="store_true", help="treat kernel parity drift as an error")
    c.set_defaults(func=cmd_check)

    s = sub.add_parser("status", help="human summary of a planted repo")
    s.add_argument("target")
    s.set_defaults(func=cmd_status)

    v = sub.add_parser("version", help="print the kernel version this copy carries")
    v.set_defaults(func=None)

    args = ap.parse_args(argv)
    if args.cmd == "version":
        print(kernel_version(find_kernel(None)))
        return 0
    args.kernel_path = find_kernel(getattr(args, "kernel", None))
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # e.g. `seed.py status | head` — not an error
        sys.exit(0)
