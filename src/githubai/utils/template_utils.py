import re
import yaml

def load_template_from_path(template_path: str):
    with open(template_path, 'r') as file:
        content = file.read()
    front_matter_match = re.search(r'^---(.*?)---', content, re.DOTALL)
    if not front_matter_match:
        raise ValueError("YAML front matter not found in template.")
    yaml_config = yaml.safe_load(front_matter_match.group(1))
    template_body = content[front_matter_match.end():].strip()
    return yaml_config, template_body
