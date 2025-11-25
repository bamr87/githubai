"""Docs services"""
import ast
import hashlib
import logging
from typing import Dict, List, Tuple, Optional, Any
from django.conf import settings
from git import Repo
from github import Github
from core.services.ai_service import AIService
from core.models import ChangelogEntry, DocumentationFile

logger = logging.getLogger('githubai')


class DocGenerationService:
    """Service for generating documentation - migrated from docgen.py"""

    def parse_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse Python file and extract comments and docstrings.
        Migrated from docgen.py::parse_python_file
        """
        with open(file_path, 'r') as file:
            file_content = file.read()

        tree = ast.parse(file_content)
        comments = []
        docstrings = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    name = getattr(node, 'name', '<module>')
                    docstrings.append((name, docstring))

        # Extract comments (simplified - actual implementation may vary)
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                comments.append(node.value.s)

        return {"comments": comments, "docstrings": docstrings}

    def generate_markdown_documentation(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate structured documentation in Markdown format.
        Migrated from docgen.py::generate_markdown_documentation
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

    def process_file(self, file_path: str) -> DocumentationFile:
        """Process a file and save to database"""
        parsed_data = self.parse_python_file(file_path)
        markdown = self.generate_markdown_documentation(parsed_data)

        # Generate content hash
        content_hash = hashlib.sha256(markdown.encode()).hexdigest()

        # Save or update in database
        doc_file, created = DocumentationFile.objects.update_or_create(
            file_path=file_path,
            defaults={
                'docstrings': dict(parsed_data['docstrings']),
                'comments': parsed_data['comments'],
                'markdown_content': markdown,
                'content_hash': content_hash,
            }
        )

        logger.info(f"{'Created' if created else 'Updated'} documentation for {file_path}")
        return doc_file


class ChangelogService:
    """Service for generating changelogs - migrated from auto_doc_generator.py"""

    def __init__(self) -> None:
        self.ai_service: AIService = AIService()

    def generate_from_commit(self, repo_path: Optional[str] = None) -> Optional[ChangelogEntry]:
        """
        Generate changelog from git commit.
        Migrated from auto_doc_generator.py
        """
        repo_path = repo_path or settings.BASE_DIR
        repo = Repo(repo_path)
        head_commit = repo.head.commit
        diff_data = head_commit.diff(None, create_patch=True)

        commit_message = head_commit.message
        diff_texts = []

        for diff in diff_data:
            if diff.change_type != "D":  # Exclude deleted files
                try:
                    diffContent = diff.diff
                    if diffContent is not None:
                        if isinstance(diffContent, bytes):
                            diff_texts.append(diffContent.decode("utf-8"))
                        else:
                            diff_texts.append(diffContent)
                except Exception:
                    continue

        # Generate AI prompt
        system_prompt = "You are an expert software documenter."
        user_prompt = (
            "Given the following commit message and diff, generate:\n"
            "1. A changelog entry suitable for CHANGELOG.md\n"
            "2. A short documentation summary of what was changed or added\n\n"
            f"Commit Message:\n{commit_message}\n\n"
            f"Diff:\n{chr(10).join(diff_texts)}"
        )

        response_content = self.ai_service.call_ai_chat(
            system_prompt,
            user_prompt,
            model="gpt-4",
            temperature=0.5
        )

        # Save to database
        entry = ChangelogEntry.objects.create(
            entry_type='commit',
            commit_sha=head_commit.hexsha,
            commit_message=commit_message,
            diff_summary="\n".join(diff_texts)[:5000],  # Truncate
            ai_generated_content=response_content
        )

        logger.info(f"Generated changelog for commit {head_commit.hexsha[:7]}")
        return entry

    def generate_from_pr(self, pr_number, repo_name=None):
        """Generate changelog from pull request"""
        repo_name = repo_name or f"{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}"

        g = Github(settings.GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))
        pr_files = pr.get_files()

        pr_diff_texts = []
        for pr_file in pr_files:
            if pr_file.status != "removed":
                if pr_file.patch:
                    pr_diff_texts.append(pr_file.patch)

        system_prompt = "You are an expert software documenter."
        user_prompt = (
            "Given the following pull request number and diff, generate:\n"
            "1. A changelog entry suitable for CHANGELOG.md\n"
            "2. A short documentation summary of what was changed or added\n\n"
            f"Pull Request Number:\n{pr_number}\n\n"
            f"Diff:\n{chr(10).join(pr_diff_texts)}"
        )

        response_content = self.ai_service.call_ai_chat(
            system_prompt,
            user_prompt,
            model="gpt-4",
            temperature=0.5
        )

        # Save to database
        entry = ChangelogEntry.objects.create(
            entry_type='pr',
            pr_number=pr_number,
            diff_summary="\n".join(pr_diff_texts)[:5000],
            ai_generated_content=response_content,
            file_path='CHANGELOG_AI_PR.md'
        )

        logger.info(f"Generated changelog for PR #{pr_number}")
        return entry
