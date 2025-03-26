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

def extract_file_paths_from_frontmatter(yaml_config: dict) -> list:
    """
    Extract file paths from the template frontmatter.

    Args:
        yaml_config (dict): The YAML configuration loaded from the template frontmatter.

    Returns:
        list: A list of file paths included in the template frontmatter.
    """
    return yaml_config.get('include_files', [])
