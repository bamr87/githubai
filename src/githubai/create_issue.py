from __future__ import annotations

import os
import requests
import argparse
import re
import base64
import openai
from utils.github_api_utils import fetch_issue, create_github_issue
from utils.template_utils import load_template_from_path
from utils.openai_utils import call_openai_chat

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def fetch_file_contents(repo, filepath):
    """Fetch file contents from GitHub repository."""
    res = requests.get(f"https://api.github.com/repos/{repo}/contents/{filepath}", headers=HEADERS)
    res.raise_for_status()
    return base64.b64decode(res.json()['content']).decode('utf-8')

def extract_template_name(issue_body):
    """Extract template name from issue body."""
    match = re.search(r'<!-- template:\s*(.+\.md)\s*-->', issue_body)
    if match:
        return match.group(1).strip()
    raise ValueError("Template name comment not found in issue body.")

def load_template(template_name):
    """Load template from repository."""
    path = f".github/ISSUE_TEMPLATE/{template_name}"
    yaml_config, template_body = load_template_from_path(path)
    prompt = yaml_config.get('prompt', '').strip()
    issue_title_prefix = yaml_config.get('title', '[Structured]: ')
    return yaml_config, template_body, prompt, issue_title_prefix

def generate_prompt(prompt_text, issue_content, template_body, file_contents=None):
    """Generate a prompt for OpenAI with all necessary context."""
    full_prompt = (
        f"{prompt_text}\n\n"
        f"Original Issue:\n{issue_content}\n\n"
        f"Structure your response using the following template:\n\n"
        f"{template_body}\n\n"
        f"Fill out all sections completely."
    )

    if file_contents:
        if isinstance(file_contents, dict):
            file_content_str = '\n\n'.join([f"File: {path}\n{content}" for path, content in file_contents.items()])
            full_prompt += f"\n\nAdditional file contents:\n{file_content_str}"
        else:
            full_prompt += f"\n\nAdditional file contents:\n{file_contents}"

    return full_prompt

def call_openai_with_prompt(prompt):
    """Call OpenAI with a formatted prompt."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    return call_openai_chat(messages)

def create_readme_update_issue(repo, issue_number):
    """Create a README update issue based on a parent issue."""
    issue = fetch_issue(repo, issue_number)
    yaml_config, template_body = load_template_from_path(".github/ISSUE_TEMPLATE/README_update.md")

    # Collect all files to include
    include_files = yaml_config.get('include_files', [])
    # Look for additional files in the issue body
    include_files_additional_match = re.search(r'include_files_additional:(.*?)##', issue['body'], re.DOTALL)
    include_files_additional = []
    if include_files_additional_match:
        files_section = include_files_additional_match.group(1).strip()
        for line in files_section.split('\n'):
            file_match = re.match(r'\s*-\s*(.*?)\s*$', line)
            if file_match:
                include_files_additional.append(file_match.group(1).strip())

    all_files = include_files + include_files_additional

    # Fetch content of all files
    included_files_content = ""
    for file in all_files:
        try:
            included_files_content += f"\n\n--- {file} content ---\n"
            included_files_content += fetch_file_contents(repo, file)
        except Exception as e:
            included_files_content += f"\n\nError fetching {file}: {str(e)}\n"

    full_prompt = (
        f"{yaml_config['prompt']}\n\n"
        f"Original Request:\n{issue['body']}\n\n"
        f"Included Files:{included_files_content}\n\n"
        f"Structure:\n{template_body}"
    )

    ai_content = call_openai_with_prompt(full_prompt)
    new_issue = create_github_issue(
        repo,
        title=yaml_config.get('title', '[README Update Detailed]: ') + issue['title'],
        body=ai_content,
        parent_issue_number=issue_number,
        labels=["readme-update-detailed"]
    )

    return new_issue

def create_sub_issue_from_template(repo, parent_issue_number, file_refs=None):
    """Create a sub-issue based on a parent issue using a template."""
    parent_issue = fetch_issue(repo, parent_issue_number)
    parent_body = parent_issue['body']

    # Extract template information
    template_name = extract_template_name(parent_body)
    yaml_config, template_body, prompt, issue_title_prefix = load_template(template_name)

    # Process file references if provided
    file_refs_content = {}
    if file_refs:
        for file_path in file_refs:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    file_refs_content[file_path] = f.read()

    # Generate prompt and call OpenAI
    full_prompt = generate_prompt(prompt, parent_body, template_body, file_refs_content)
    ai_generated_body = call_openai_with_prompt(full_prompt)

    # Create the issue
    new_issue = create_github_issue(
        repo,
        title=f"{issue_title_prefix}{parent_issue['title']}",
        body=ai_generated_body,
        parent_issue_number=parent_issue_number,
        labels=["ai-generated"]
    )

    return new_issue

def run_create_issue(repo, title, body, parent_issue_number, labels):
    """Unified function to create either a README update or sub-issue."""
    if issue_number:
        new_issue = create_readme_update_issue(repo, issue_number)
    elif parent_issue_number:
        new_issue = create_sub_issue_from_template(repo, parent_issue_number, file_refs)
    else:
        raise ValueError("Either issue_number or parent_issue_number must be provided")

    return new_issue['html_url']

def parse_args_for_sub_issue():
    """Parse arguments specifically for sub-issue creation."""
    parser = argparse.ArgumentParser(description="Create GitHub sub-issues with AI-generated content")
    parser.add_argument("--repo", required=True, help="GitHub repository in format 'owner/repo'")
    parser.add_argument("--parent-issue-number", required=True, help="Parent issue number")
    parser.add_argument("--file-refs", nargs='*', default=[], help="Optional file references")
    return parser.parse_args()

def main():
    """Main entry point for the script."""
    # Determine if this is being called as a sub-issue creator
    import sys
    script_name = os.path.basename(sys.argv[0])

    if 'create_issue' in script_name:
        args = parse_args_for_sub_issue()
        url = run_create_issue(
            repo=args.repo,
            parent_issue_number=args.parent_issue_number,
            title="Sub-issue created by AI",
            body="This is a sub-issue created by AI based on the parent issue.",
            labels=["ai-generated"]
        )
    else:
        # Standard argument parsing for the main script
        parser = argparse.ArgumentParser(description="Create GitHub issues with AI-generated content")
        parser.add_argument("--repo", required=True, help="GitHub repository in format 'owner/repo'")
        parser.add_argument("--issue-number", help="Issue number for README updates")
        parser.add_argument("--parent-issue-number", help="Parent issue number for creating sub-issues")
        parser.add_argument("--file-refs", nargs='*', default=[], help="Optional file references")
        args = parser.parse_args()

        if not args.issue_number and not args.parent_issue_number:
            parser.error("Either --issue-number or --parent-issue-number must be specified")

        url = run_create_issue(
            repo=args.repo,
            title="Sub-issue created by AI",
            body="This is a sub-issue created by AI based on the parent issue.",
            parent_issue_number=args.parent_issue_number,
            labels=["ai-generated"]
        )

    print(f"Created issue: {url}")

if __name__ == "__main__":
    main()