from __future__ import annotations

import os
import requests
from openai import OpenAI
import argparse
import yaml
import re
from utils.openai_utils import call_openai_chat
from utils.github_api_utils import fetch_issue, create_github_issue
from utils.template_utils import load_template_from_path

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--parent-issue-number", required=True)
    parser.add_argument("--file-refs", nargs='*', default=[], help="Optional file references")
    return parser.parse_args()

def extract_template_name(issue_body):
    match = re.search(r'<!-- template:\s*(.+\.md)\s*-->', issue_body)
    if match:
        return match.group(1).strip()
    raise ValueError("Template name comment not found in issue body.")

def load_template(template_name):
    path = f".github/ISSUE_TEMPLATE/{template_name}"
    yaml_config, template_body = load_template_from_path(path)
    prompt = yaml_config.get('prompt','').strip()
    issue_title_prefix = yaml_config.get('title','[Structured]: ')
    return prompt, template_body, issue_title_prefix

def call_openai(prompt, parent_issue_content, template_body, file_contents=None):
    full_prompt = (
        f"{prompt}\n\n"
        f"Original Issue:\n{parent_issue_content}\n\n"
        f"Structure your response using the following template:\n\n"
        f"{template_body}\n\n"
        f"Fill out all sections completely."
    )

    if file_contents:
        file_content_str = '\n\n'.join([f"File: {path}\n{content}" for path, content in file_contents.items()])
        full_prompt += f"\n\nAdditional file contents:\n{file_content_str}"

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": full_prompt}
    ]
    return call_openai_chat(messages)

def create_sub_issue(repo, title, body, parent_issue_number, labels):
    return create_github_issue(repo, title, body, parent_issue_number, labels)

def main():
    args = parse_args()
    parent_issue = fetch_issue(args.repo, args.parent_issue_number)
    parent_body = parent_issue['body']

    template_name = extract_template_name(parent_body)
    prompt, template_body, issue_title_prefix = load_template(template_name)

    file_refs_content = {}
    for file_path in args.file_refs:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                file_refs_content[file_path] = f.read()

    ai_generated_body = call_openai(prompt, parent_body, template_body, file_refs_content)

    new_issue = create_sub_issue(
        args.repo,
        title=f"{issue_title_prefix}{parent_issue['title']}",
        body=ai_generated_body,
        parent_issue_number=args.parent_issue_number,
        labels=["ai-generated"]
    )

    print(f"Structured sub-issue created: {new_issue['html_url']}")

if __name__ == "__main__":
    main()