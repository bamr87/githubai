import os
import requests

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def fetch_issue(repo, issue_number):
    res = requests.get(f"https://api.github.com/repos/{repo}/issues/{issue_number}", headers=HEADERS)
    res.raise_for_status()
    return res.json()

def create_github_issue(repo, title, body, parent_issue_number=None, labels=None):
    labels = labels or []
    if parent_issue_number:
        body += f"\n\n_Parent Issue: #{parent_issue_number}_"
    data = {
        "title": title,
        "body": body,
        "labels": labels
    }
    res = requests.post(f"https://api.github.com/repos/{repo}/issues", headers=HEADERS, json=data)
    res.raise_for_status()
    return res.json()