import subprocess
import re
import sys
from pathlib import Path


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def get_latest_tag():
    try:
        return run("git describe --tags $(git rev-list --tags --max-count=1)").lstrip(
            "v"
        )
    except subprocess.CalledProcessError:
        return None


def read_version():
    return Path("VERSION").read_text().strip()


def write_version(version):
    Path("VERSION").write_text(version)
    init_file = Path("src/githubai/__init__.py")
    init_content = init_file.read_text()
    init_content = re.sub(
        r'__version__ = ".*"', f'__version__ = "{version}"', init_content
    )
    init_file.write_text(init_content)


def determine_bump(commit_msg):
    if "[major]" in commit_msg:
        return "major"
    elif "[minor]" in commit_msg:
        return "minor"
    else:
        return "patch"


def bump_version(current_version, bump_type):
    major, minor, patch = map(int, current_version.split("."))
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def main():
    commit_msg = run("git log -1 --pretty=%B")
    bump_type = determine_bump(commit_msg)

    latest_tag = get_latest_tag()
    current_version = read_version()

    if latest_tag and current_version != latest_tag:
        print(
            "Version conflict detected. Updating local version to match the latest tag."
        )
        current_version = latest_tag
        write_version(current_version)

    new_version = bump_version(current_version, bump_type)
    write_version(new_version)

    run("git config --global user.name 'github-actions[bot]'")
    run("git config --global user.email 'github-actions[bot]@users.noreply.github.com'")
    run("git add .")
    run(f'git commit -m "Bump version to {new_version}"')
    run("git push")
    run(f"git tag v{new_version}")
    run(f"git push origin v{new_version}")


if __name__ == "__main__":
    main()
