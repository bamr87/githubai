"""Community-health files must keep the shape the fleet standard requires.

SECURITY.md is UPS-REPO-14 in bamr87/bamr87 specs/REPOSITORY.md: supported
versions, a private way to report, and the response window.
"""

import re

SECURITY_HEADINGS = ("## Supported versions", "## Reporting a vulnerability", "## Response window")
SECURITY_SCOPE = ("claude-*.yml", "actions/load-config", "setup/install.sh", "app/relay/")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


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
