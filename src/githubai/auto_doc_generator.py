import os
import openai
from github import Github
from git import Repo
from utils.openai_utils import call_openai_chat

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

# Generate OpenAI prompt
prompt = (
    "Given the following commit message and diff, generate:\n"
    "1. A changelog entry suitable for CHANGELOG.md\n"
    "2. A short documentation summary of what was changed or added\n\n"
    f"Commit Message:\n{commit_message}\n\n"
    f"Diff:\n{chr(10).join(diff_texts)}"
)

# Use call_openai_chat to get the response
messages = [
    {"role": "system", "content": "You are an expert software documenter."},
    {"role": "user", "content": prompt},
]
response_content = call_openai_chat(messages, model="gpt-4", temperature=0.5)

if response_content:
    print("\n--- AI Generated Output ---\n")
    print(response_content)

    # Save to changelog file
    with open("CHANGELOG_AI.md", "a") as f:
        f.write(f"\n## {head_commit.hexsha[:7]}\n{response_content}\n")
