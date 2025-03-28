import pytest
from src.githubai.docgen import parse_python_file, generate_markdown_documentation

def test_parse_python_file(mocker):
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="""
    '''
    Module docstring
    '''
    # Comment 1
    def foo():
        '''
        Function docstring
        '''
        # Comment 2
        pass
    """))

    result = parse_python_file("dummy_path")
    assert result["comments"] == ["Comment 1", "Comment 2"]
    assert result["docstrings"] == [("foo", "Function docstring")]

def test_generate_markdown_documentation():
    parsed_data = {
        "comments": ["Comment 1", "Comment 2"],
        "docstrings": [("foo", "Function docstring")]
    }

    result = generate_markdown_documentation(parsed_data)
    expected_output = """# Documentation

## Docstrings
### foo
Function docstring

## Comments
- Comment 1
- Comment 2
"""
    assert result == expected_output
