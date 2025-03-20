import os, requests, argparse, yaml, re
from openai import OpenAI

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def fetch_issue(repo, number):
    res = requests.get(f"https://api.github.com/repos/{repo}/issues/{number}", headers=HEADERS)
    res.raise_for_status()
    return res.json()

def load_template():
    path = ".github/ISSUE_TEMPLATE/README_update_template.md"
    with open(path) as f:
        content = f.read()
    yaml_match = re.search(r'^---(.*?)---', content, re.DOTALL)
    yaml_content = yaml.safe_load(yaml_match.group(1))
    template_body = content[yaml_match.end():].strip()
    return yaml_content, template_body

def fetch_file_contents(repo, filepath):
    res = requests.get(f"https://api.github.com/repos/{repo}/contents/{filepath}", headers=HEADERS)
    res.raise_for_status()
    import base64
    return base64.b64decode(res.json()['content']).decode('utf-8')

def call_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2500
    )
    return response.choices[0].message.content.strip()

def create_structured_issue(repo, title, body, parent):
    res = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers=HEADERS,
        json={"title": title, "body": body+f"\n\n_Parent Issue: #{parent}_", "labels":["readme-update-detailed"]}
    )
    res.raise_for_status()
    return res.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue-number", required=True)
    args = parser.parse_args()

    issue = fetch_issue(args.repo, args.issue_number)
    yaml_config, template_body = load_template()

    included_files_content = ""
    for file in yaml_config.get('include_files', []):
        included_files_content += f"\n\n--- {file} content ---\n"
        included_files_content += fetch_file_contents(args.repo, file)

    full_prompt = f"{yaml_config['prompt']}\n\nOriginal Request:\n{issue['body']}\n\nIncluded Files:{included_files_content}\n\nStructure:\n{template_body}"

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