import ast
import inspect

def parse_python_file(file_path):
    """
    Parse a Python file and extract comments and docstrings.

    Args:
        file_path (str): Path to the Python file.

    Returns:
        dict: A dictionary containing the extracted comments and docstrings.
    """
    with open(file_path, "r") as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    comments = []
    docstrings = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef) or isinstance(node, ast.Module):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings.append((node.name, docstring))

    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
            comments.append(node.value.s)

    return {"comments": comments, "docstrings": docstrings}

def generate_markdown_documentation(parsed_data):
    """
    Generate structured documentation in Markdown format.

    Args:
        parsed_data (dict): A dictionary containing the extracted comments and docstrings.

    Returns:
        str: The generated documentation in Markdown format.
    """
    markdown = "# Documentation\n\n"

    markdown += "## Docstrings\n"
    for name, docstring in parsed_data["docstrings"]:
        markdown += f"### {name}\n"
        markdown += f"{docstring}\n\n"

    markdown += "## Comments\n"
    for comment in parsed_data["comments"]:
        markdown += f"- {comment}\n"

    return markdown

def main(file_path):
    """
    Main function to parse a Python file and generate documentation.

    Args:
        file_path (str): Path to the Python file.
    """
    parsed_data = parse_python_file(file_path)
    documentation = generate_markdown_documentation(parsed_data)
    print(documentation)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate documentation from Python file.")
    parser.add_argument("file_path", help="Path to the Python file.")
    args = parser.parse_args()

    main(args.file_path)
