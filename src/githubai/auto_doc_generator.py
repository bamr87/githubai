import os
import openai
from github import Github
from git import Repo
import subprocess

openai.api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

repo_path = os.getcwd()
repo = Repo(repo_path)
head_commit = repo.head.commit
diff_data = head_commit.diff(None, create_patch=True)

commit_message = head_commit.message
diff_texts = []

for diff in diff_data:
    if diff.change_type != "D":  # Exclude deleted files
        try:
            diff_texts.append(diff.diff.decode("utf-8"))
        except Exception:
            continue

prompt = f"""
Given the following commit message and diff, generate:
1. A changelog entry suitable for CHANGELOG.md
2. A short documentation summary of what was changed or added

Commit Message:
{commit_message}

Diff:
{'\n\n'.join(diff_texts)}
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert software documenter."},
        {"role": "user", "content": prompt},
    ],
    temperature=0.5,
)

output = response["choices"][0]["message"]["content"]
print("\n--- AI Generated Output ---\n")
print(output)

# Optionally save to files
with open("CHANGELOG_AI.md", "a") as f:
    f.write(f"\n## {head_commit.hexsha[:7]}\n{output}\n")

# Push changes to 'feature-documentation' branch
feature_branch = "feature-documentation"

# Create a new branch based on main
subprocess.run(["git", "checkout", "-b", feature_branch], check=True)

# Stage the updated changelog
subprocess.run(["git", "add", "CHANGELOG_AI.md"], check=True)

# Commit with a message
subprocess.run(
    ["git", "commit", "-m", "Add AI-generated changelog and documentation summary"],
    check=True,
)

# Push the branch
subprocess.run(["git", "push", "-u", "origin", feature_branch], check=True)
