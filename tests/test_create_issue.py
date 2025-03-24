import pytest
from src.githubai.create_issue import (
    fetch_file_contents,
    extract_template_name,
    load_template,
    generate_prompt,
    call_openai_with_prompt,
    create_readme_update_issue,
    create_sub_issue_from_template,
    run_create_issue,
    parse_args_for_sub_issue,
    main
)

def test_fetch_file_contents(mocker):
    mock_get = mocker.patch('requests.get')
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'content': 'dGVzdCBjb250ZW50'}
    mock_get.return_value = mock_response

    result = fetch_file_contents('repo', 'path/to/file')
    assert result == 'test content'

def test_extract_template_name():
    issue_body = "<!-- template: test_template.md -->"
    result = extract_template_name(issue_body)
    assert result == 'test_template.md'

def test_load_template(mocker):
    mock_load_template_from_path = mocker.patch('src.githubai.create_issue.load_template_from_path')
    mock_load_template_from_path.return_value = ({'prompt': 'Test prompt'}, 'Template body')

    yaml_config, template_body, prompt, issue_title_prefix = load_template('test_template.md')
    assert yaml_config == {'prompt': 'Test prompt'}
    assert template_body == 'Template body'
    assert prompt == 'Test prompt'
    assert issue_title_prefix == '[Structured]: '

def test_generate_prompt():
    prompt_text = "Test prompt"
    issue_content = "Issue content"
    template_body = "Template body"
    file_contents = {'file1': 'content1', 'file2': 'content2'}

    result = generate_prompt(prompt_text, issue_content, template_body, file_contents)
    assert "Test prompt" in result
    assert "Issue content" in result
    assert "Template body" in result
    assert "content1" in result
    assert "content2" in result

def test_call_openai_with_prompt(mocker):
    mock_call_openai_chat = mocker.patch('src.githubai.create_issue.call_openai_chat')
    mock_call_openai_chat.return_value = 'AI response'

    result = call_openai_with_prompt('Test prompt')
    assert result == 'AI response'

def test_create_readme_update_issue(mocker):
    mock_fetch_issue = mocker.patch('src.githubai.create_issue.fetch_issue')
    mock_load_template_from_path = mocker.patch('src.githubai.create_issue.load_template_from_path')
    mock_fetch_file_contents = mocker.patch('src.githubai.create_issue.fetch_file_contents')
    mock_call_openai_with_prompt = mocker.patch('src.githubai.create_issue.call_openai_with_prompt')
    mock_create_github_issue = mocker.patch('src.githubai.create_issue.create_github_issue')

    mock_fetch_issue.return_value = {'body': 'Issue body', 'title': 'Issue title'}
    mock_load_template_from_path.return_value = ({'prompt': 'Test prompt', 'include_files': []}, 'Template body')
    mock_fetch_file_contents.return_value = 'File content'
    mock_call_openai_with_prompt.return_value = 'AI response'
    mock_create_github_issue.return_value = {'html_url': 'http://example.com'}

    result = create_readme_update_issue('repo', 1)
    assert result == 'http://example.com'

def test_create_sub_issue_from_template(mocker):
    mock_fetch_issue = mocker.patch('src.githubai.create_issue.fetch_issue')
    mock_load_template = mocker.patch('src.githubai.create_issue.load_template')
    mock_generate_prompt = mocker.patch('src.githubai.create_issue.generate_prompt')
    mock_call_openai_with_prompt = mocker.patch('src.githubai.create_issue.call_openai_with_prompt')
    mock_create_github_issue = mocker.patch('src.githubai.create_issue.create_github_issue')

    mock_fetch_issue.return_value = {'body': 'Issue body', 'title': 'Issue title'}
    mock_load_template.return_value = ({'prompt': 'Test prompt'}, 'Template body', 'Test prompt', '[Structured]: ')
    mock_generate_prompt.return_value = 'Generated prompt'
    mock_call_openai_with_prompt.return_value = 'AI response'
    mock_create_github_issue.return_value = {'html_url': 'http://example.com'}

    result = create_sub_issue_from_template('repo', 1)
    assert result == 'http://example.com'

def test_run_create_issue(mocker):
    mock_create_sub_issue_from_template = mocker.patch('src.githubai.create_issue.create_sub_issue_from_template')
    mock_create_sub_issue_from_template.return_value = {'html_url': 'http://example.com'}

    result = run_create_issue('repo', 'Title', 'Body', 1, ['label'])
    assert result == 'http://example.com'

def test_parse_args_for_sub_issue(mocker):
    mocker.patch('sys.argv', ['create_issue', '--repo', 'repo', '--parent-issue-number', '1'])
    args = parse_args_for_sub_issue()
    assert args.repo == 'repo'
    assert args.parent_issue_number == '1'

def test_main(mocker):
    mock_parse_args_for_sub_issue = mocker.patch('src.githubai.create_issue.parse_args_for_sub_issue')
    mock_run_create_issue = mocker.patch('src.githubai.create_issue.run_create_issue')

    mock_parse_args_for_sub_issue.return_value = mocker.Mock(repo='repo', parent_issue_number='1', file_refs=[])
    mock_run_create_issue.return_value = 'http://example.com'

    main()
    mock_run_create_issue.assert_called_once_with(
        repo='repo',
        parent_issue_number='1',
        title='Sub-issue created by AI',
        body='This is a sub-issue created by AI based on the parent issue.',
        labels=['ai-generated'],
        file_refs=[]
    )
