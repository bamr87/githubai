from __future__ import annotations

import os
import requests
from openai import OpenAI
import argparse
import yaml
import re

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--parent-issue-number", required=True)
    return parser.parse_args()

def fetch_issue(repo, issue_number):
    res = requests.get(f"https://api.github.com/repos/{repo}/issues/{issue_number}", headers=HEADERS)
    res.raise_for_status()
    return res.json()

def extract_template_name(issue_body):
    match = re.search(r'<!-- template:\s*(.+\.md)\s*-->', issue_body)
    if match:
        return match.group(1).strip()
    raise ValueError("Template name comment not found in issue body.")

def load_template(template_name):
    path = f".github/ISSUE_TEMPLATE/{template_name}"
    with open(path, 'r') as file:
        content = file.read()
    front_matter_match = re.search(r'^---(.*?)---', content, re.DOTALL)
    if not front_matter_match:
        raise ValueError("YAML front matter not found in template.")

    yaml_content = yaml.safe_load(front_matter_match.group(1))
    prompt = yaml_content.get('prompt', '').strip()
    template_body = content[front_matter_match.end():].strip()
    issue_title_prefix = yaml_content.get('title', '[Structured]: ')

    return prompt, template_body, issue_title_prefix

def call_openai(prompt, parent_issue_content, template_body):
    full_prompt = (
        f"{prompt}\n\n"
        f"Original Issue:\n{parent_issue_content}\n\n"
        f"Structure your response using the following template:\n\n"
        f"{template_body}\n\n"
        f"Fill out all sections completely."
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.2,
        max_tokens=2500
    )

    return response.choices[0].message.content.strip()

def create_sub_issue(repo, title, body, parent_issue_number, labels):
    data = {
        "title": title,
        "body": body + f"\n\n_Parent Issue: #{parent_issue_number}_",
        "labels": labels
    }
    res = requests.post(f"https://api.github.com/repos/{repo}/issues", headers=HEADERS, json=data)
    res.raise_for_status()
    return res.json()

def main():
    args = parse_args()
    parent_issue = fetch_issue(args.repo, args.parent_issue_number)
    parent_body = parent_issue['body']

    template_name = extract_template_name(parent_body)
    prompt, template_body, issue_title_prefix = load_template(template_name)

    ai_generated_body = call_openai(prompt, parent_body, template_body)

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