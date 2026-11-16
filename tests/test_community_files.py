"""Community-health files must keep the shape the fleet standard requires.

SECURITY.md is UPS-REPO-14 in bamr87/bamr87 specs/REPOSITORY.md: supported
versions, a private way to report, and the response window.

The PR template is UPS-WORK-03 in specs/WORK.md: it carries the fleet
Definition of Done between the `fleet-dod` markers, byte-identical to the hub's
templates/community/.github/pull_request_template.md (the conformance workflow
compares the two). Repo-specific boxes go below `fleet-dod:end`, never inside.
"""

import re

SECURITY_HEADINGS = ("## Supported versions", "## Reporting a vulnerability", "## Response window")
SECURITY_SCOPE = ("claude-*.yml", "actions/load-config", "setup/install.sh", "app/relay/")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")

PR_TEMPLATE_SECTIONS = ("## What & why", "## How verified", "## Risk & compatibility")
DOD_START = "<!-- fleet-dod:start v1 -->"
DOD_END = "<!-- fleet-dod:end -->"
# The v1 boxes of the hub's reference template, in order; a new kit version bumps the marker and this list together.
DOD_BOXES = (
    "Title",
    "CI is green",
    "Tests",
    "Docs",
    "Agent instructions",
    "Decision recorded",
    "Backlog of record",
    "Clean diff",
)
BOX_RE = re.compile(r"^- \[ \] \*\*(.+?)\*\*")


def markdown_section(text, heading):
    """The body under `heading` up to the next heading of the same level, or "" when absent."""
    lines = text.splitlines()
    if heading not in lines:
        return ""
    body = []
    for line in lines[lines.index(heading) + 1:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def relative_links(text):
    return [target for target in LINK_RE.findall(text) if not re.match(r"^([a-z][a-z0-9+.-]*:|#)", target)]


def test_security_policy_has_the_required_sections(repo_root):
    path = repo_root / "SECURITY.md"
    assert path.is_file(), "SECURITY.md is missing at the repo root (UPS-REPO-14)"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    for heading in SECURITY_HEADINGS:
        assert heading in lines, f"SECURITY.md has no `{heading}` heading"
    assert "7 days" in markdown_section(text, "## Response window"), "SECURITY.md must state the 7-day window"
    assert "public issue" in markdown_section(text, "## Reporting a vulnerability"), (
        "SECURITY.md must steer reporters away from public issues"
    )


def test_security_policy_scope_names_the_shipped_surfaces(repo_root):
    text = (repo_root / "SECURITY.md").read_text(encoding="utf-8")
    scope = markdown_section(text, "## Scope")
    assert scope, "SECURITY.md has no `## Scope` section"
    for surface in SECURITY_SCOPE:
        assert surface in scope, f"SECURITY.md's scope does not name {surface}"
    links = relative_links(text)
    for target in ("app/DATA-HANDLING.md", "docs/security.md"):
        assert target in links, f"SECURITY.md does not link {target}"
    for target in links:
        assert (repo_root / target).exists(), f"SECURITY.md links {target}, which does not exist"


def test_security_model_sends_reporters_to_the_private_policy(repo_root):
    text = (repo_root / "docs" / "security.md").read_text(encoding="utf-8")
    reporting = markdown_section(text, "## Reporting")
    assert reporting, "docs/security.md has no `## Reporting` section"
    assert "../SECURITY.md" in relative_links(reporting), "docs/security.md's Reporting section must link SECURITY.md"
    assert "open an issue" not in reporting.lower(), "docs/security.md must not send vulnerability reports to issues"


def test_readme_links_the_security_policy(repo_root):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "SECURITY.md" in relative_links(readme), "README.md does not link SECURITY.md"


def test_pr_template_carries_the_fleet_definition_of_done(repo_root):
    text = (repo_root / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
    assert text.count("<!-- fleet-dod:start") == 1, "the PR template needs exactly one fleet-dod:start marker"
    assert text.count(DOD_END) == 1, f"the PR template needs exactly one `{DOD_END}` marker"
    lines = text.splitlines()
    assert DOD_START in lines, f"the PR template's block must open with `{DOD_START}` (the hub kit's version)"
    start, end = lines.index(DOD_START), lines.index(DOD_END)
    assert start < end, "fleet-dod:start must come before fleet-dod:end"
    block = lines[start + 1:end]
    boxes = [m.group(1) for m in map(BOX_RE.match, block) if m]
    assert tuple(boxes) == DOD_BOXES, f"the fleet-dod boxes must be the hub kit's, in order; found {boxes}"
    assert len(block) == len(DOD_BOXES), "only the kit's boxes go inside the block; add repo boxes below the end marker"


def test_pr_template_keeps_its_sections(repo_root):
    lines = (repo_root / ".github" / "pull_request_template.md").read_text(encoding="utf-8").splitlines()
    for heading in PR_TEMPLATE_SECTIONS:
        assert heading in lines, f"the PR template lost its `{heading}` section"
