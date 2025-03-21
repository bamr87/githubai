from __future__ import annotations

import os, requests, argparse, yaml, re
from openai import OpenAI
from utils.openai_utils import call_openai_chat
from utils.github_api_utils import fetch_issue, create_github_issue
from utils.template_utils import load_template_from_path

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}


def load_template():
    path = ".github/ISSUE_TEMPLATE/README_update.md"
    yaml_config, template_body = load_template_from_path(path)
    return yaml_config, template_body

def fetch_file_contents(repo, filepath):
    res = requests.get(f"https://api.github.com/repos/{repo}/contents/{filepath}", headers=HEADERS)
    res.raise_for_status()
    import base64
    return base64.b64decode(res.json()['content']).decode('utf-8')

def call_openai(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    return call_openai_chat(messages)

def create_structured_issue(repo, title, body, parent):
    return create_github_issue(repo, title, body, parent_issue_number=parent, labels=["readme-update-detailed"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue-number", required=True)
    args = parser.parse_args()

    issue = fetch_issue(args.repo, args.issue_number)
    yaml_config, template_body = load_template()

    include_files = yaml_config.get('include_files', [])
    include_files_additional = yaml_config.get('include_files_additional', [])
    all_files = include_files + include_files_additional

    included_files_content = ""
    for file in all_files:
        included_files_content += f"\n\n--- {file} content ---\n"
        included_files_content += fetch_file_contents(args.repo, file)

    full_prompt = (
        f"{yaml_config['prompt']}\n\n"
        f"Original Request:\n{issue['body']}\n\n"
        f"Included Files:{included_files_content}\n\n"
        f"Structure:\n{template_body}"
    )

    ai_content = call_openai(full_prompt)
    new_issue = create_structured_issue(
        args.repo,
        title=yaml_config.get('title', '[README Update Detailed]: ') + issue['title'],
        body=ai_content,
        parent=args.issue_number
    )

    print(f"Created structured README update issue: {new_issue['html_url']}")

if __name__ == "__main__":
    main()