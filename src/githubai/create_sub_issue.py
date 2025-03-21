from __future__ import annotations

import os
import requests
from openai import OpenAI
import argparse
import yaml
import re
from githubai.utils.openai_utils import call_openai_chat
from githubai.utils.github_api_utils import fetch_issue, create_github_issue
from githubai.utils.template_utils import load_template_from_path
from githubai.create_issue import main as create_issue_main

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def parse_args():
    """Parse arguments specifically for sub-issue creation."""
    parser = argparse.ArgumentParser(description="Create GitHub sub-issues with AI-generated content")
    parser.add_argument("--repo", required=True, help="GitHub repository in format 'owner/repo'")
    parser.add_argument("--parent-issue-number", required=True, help="Parent issue number")
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
    """Entry point for creating sub-issues. Delegates to the unified implementation."""
    args = parse_args()
    # Call the main function from create_issue.py with appropriate args
    import sys
    sys.argv = [
        sys.argv[0],
        "--repo", args.repo,
        "--parent-issue-number", args.parent_issue_number
    ]
    if args.file_refs:
        sys.argv.extend(["--file-refs"] + args.file_refs)

    create_issue_main()

if __name__ == "__main__":
    main()