#!/usr/bin/env bash
# GitHubAI installer - wires Claude Code automation into the current repo.
#
# Usage (from the root of the target repository):
#   curl -fsSL https://raw.githubusercontent.com/bamr87/githubai/main/setup/install.sh | bash
#   curl -fsSL .../install.sh | bash -s -- --profile library --ref v1 --labels
#
# Flags:
#   --profile NAME   repo type: library|webapp|service|cli|github-action|docs|data|template
#                    (auto-detected when omitted)
#   --ref REF        framework ref to pin the installed stubs to (default: main)
#   --source O/R     framework repo to install from (default: bamr87/githubai)
#   --app            also install the GitHub App dispatch workflow (app mode)
#   --labels         create the GitHubAI label taxonomy via `gh` (needs gh auth)
#   --force          overwrite files that already exist
#   --dry-run        print what would happen without writing anything
#
# The installer only writes files and (optionally) labels. It never edits
# existing code and it prints the manual steps (secret + GitHub App) at the
# end - it cannot and does not handle credentials itself.

set -euo pipefail

SOURCE_REPO="bamr87/githubai"
REF="main"
PROFILE=""
FORCE=0
DRY_RUN=0
WITH_LABELS=0
WITH_APP=0

WORKFLOWS="claude claude-triage claude-implement claude-review claude-auto-merge claude-maintenance claude-release"

# Keep in sync with labels.taxonomy in profiles/_base.yml - tests/test_installer.py
# enforces the match. Format: name|color|description
LABELS='type:bug|d73a4a|Something is broken
type:feature|a2eeef|New capability or enhancement
type:docs|0075ca|Documentation only
type:chore|cfd3d7|Maintenance, refactoring, dependencies
type:question|d876e3|Question or discussion, no code change expected
priority:high|b60205|Urgent - address before other work
priority:medium|fbca04|Normal queue
priority:low|c2e0c6|Nice to have
size:xs|ededed|Trivial change (minutes)
size:s|ededed|Small change (under an hour)
size:m|ededed|Medium change (hours)
size:l|ededed|Large change (days)
claude:triaged|5319e7|Claude has triaged this issue
claude:implement|5319e7|Approved for Claude to implement - applying this label starts work
claude:in-progress|5319e7|Claude is working on this
claude:needs-human|e11d21|Claude determined a human decision is required
claude:auto-merge|0e8a16|Eligible for automated safety check and auto-merge
claude:skip|ededed|Exclude this item from Claude automation'

log() { printf '%s\n' "$*"; }
err() { printf 'githubai: %s\n' "$*" >&2; }
die() { err "$*"; exit 1; }

usage() { sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="${2:-}"; shift 2 ;;
    --ref) REF="${2:-}"; shift 2 ;;
    --source) SOURCE_REPO="${2:-}"; shift 2 ;;
    --app) WITH_APP=1; shift ;;
    --labels) WITH_LABELS=1; shift ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown flag: $1 (see --help)" ;;
  esac
done

git rev-parse --show-toplevel >/dev/null 2>&1 || die "run this from inside a git repository"
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

RAW_BASE="https://raw.githubusercontent.com/${SOURCE_REPO}/${REF}"

detect_profile() {
  if [ -f action.yml ] || [ -f action.yaml ]; then
    echo "github-action"; return
  fi
  if [ -f mkdocs.yml ] || [ -f docusaurus.config.js ] || [ -f docusaurus.config.ts ] || [ -d _posts ]; then
    echo "docs"; return
  fi
  if [ -n "$(find . -maxdepth 2 -name '*.ipynb' -print -quit 2>/dev/null)" ] || [ -f dvc.yaml ]; then
    echo "data"; return
  fi
  if [ -f package.json ]; then
    if grep -q '"bin"' package.json; then echo "cli"; return; fi
    if grep -Eq '"(react|next|vue|svelte|@angular/core)"' package.json; then echo "webapp"; return; fi
    if grep -Eq '"(express|fastify|koa|hapi)"' package.json; then echo "service"; return; fi
    echo "library"; return
  fi
  if [ -f pyproject.toml ] || [ -f setup.py ]; then
    if grep -q 'console_scripts\|\[project.scripts\]' pyproject.toml setup.py 2>/dev/null; then echo "cli"; return; fi
    if grep -Eq 'django|flask|fastapi' pyproject.toml setup.py 2>/dev/null; then echo "webapp"; return; fi
    echo "library"; return
  fi
  if [ -f go.mod ]; then
    if [ -d cmd ]; then echo "cli"; return; fi
    echo "library"; return
  fi
  if [ -f Cargo.toml ]; then
    if [ -d src/bin ] || grep -q '^\[\[bin\]\]' Cargo.toml; then echo "cli"; return; fi
    echo "library"; return
  fi
  echo "library"
}

VALID_PROFILES="library webapp service cli github-action docs data template"
if [ -z "$PROFILE" ]; then
  PROFILE="$(detect_profile)"
  log "Detected repo type: ${PROFILE} (override with --profile)"
else
  case " $VALID_PROFILES " in
    *" $PROFILE "*) ;;
    *) die "unknown profile '$PROFILE' - valid: $VALID_PROFILES" ;;
  esac
fi

fetch() {
  # fetch <path-in-framework-repo> -> stdout
  curl -fsSL "${RAW_BASE}/$1" || die "failed to download ${RAW_BASE}/$1"
}

install_file() {
  # install_file <source-path-in-repo> <dest-path> [transform-function]
  local src="$1" dest="$2" transform="${3:-cat}"
  if [ -e "$dest" ] && [ "$FORCE" -ne 1 ]; then
    log "skip   $dest (exists; use --force to overwrite)"
    return
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    log "would  $dest (from $src)"
    return
  fi
  mkdir -p "$(dirname "$dest")"
  fetch "$src" | "$transform" > "$dest"
  log "wrote  $dest"
}

pin_ref() {
  # Rewrite @main workflow refs to the pinned --ref in installed stubs.
  if [ "$REF" = "main" ]; then cat; else sed "s#${SOURCE_REPO}/\\(.*\\)@main#${SOURCE_REPO}/\\1@${REF}#"; fi
}

set_type() {
  sed "s/GHAI_REPO_TYPE/${PROFILE}/"
}

log "Installing GitHubAI (${SOURCE_REPO}@${REF}) with profile '${PROFILE}'..."

for wf in $WORKFLOWS; do
  install_file "template/workflows/${wf}.yml" ".github/workflows/${wf}.yml" "pin_ref"
done
if [ "$WITH_APP" -eq 1 ]; then
  install_file "template/workflows/claude-dispatch.yml" ".github/workflows/claude-dispatch.yml" "pin_ref"
fi
install_file "template/githubai.yml" ".github/githubai.yml" "set_type"
install_file "template/CLAUDE.md" "CLAUDE.md"

if [ "$WITH_LABELS" -eq 1 ]; then
  if [ "$DRY_RUN" -ne 1 ]; then
    command -v gh >/dev/null 2>&1 || die "--labels needs the GitHub CLI (gh) authenticated for this repo"
  fi
  log "Creating label taxonomy..."
  printf '%s\n' "$LABELS" | while IFS='|' read -r name color desc; do
    [ -n "$name" ] || continue
    if [ "$DRY_RUN" -eq 1 ]; then
      log "would  label '$name'"
    elif gh label create "$name" --color "$color" --description "$desc" --force >/dev/null; then
      log "label  $name"
    else
      err "could not create label $name"
    fi
  done
fi

cat <<'NEXT'

GitHubAI installed. Three manual steps remain:

1. Claude Code OAuth token (the default auth for every workflow):
     claude setup-token           # prints a token; then:
     gh secret set CLAUDE_CODE_OAUTH_TOKEN
   (Organizations can set it once as an org secret instead. ANTHROPIC_API_KEY
   works as a fallback secret if you cannot use OAuth.)

2. Install the Claude GitHub App on this repo (required by claude-code-action
   for branch/PR operations): https://github.com/apps/claude

3. Review .github/githubai.yml - set repo.purpose (Claude reads it in every
   run), confirm the detected repo type, and decide whether to enable
   automation.auto_merge (read docs/security.md in the framework repo first;
   it requires branch protection with required checks).

Then open an issue - Claude triages it within a minute or two. Mention
@claude anywhere for interactive help.
NEXT
