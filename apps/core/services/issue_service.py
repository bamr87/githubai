"""Issues service layer - migrated from create_issue.py"""
import re
import logging
from django.conf import settings
from core.models import Issue, IssueTemplate, IssueFileReference
from core.services.github_service import GitHubService
from core.services.ai_service import AIService

logger = logging.getLogger('githubai')


class IssueService:
    """Service for managing GitHub issues with AI generation"""

    def __init__(self):
        self.github_service = GitHubService()
        self.ai_service = AIService()

    def create_sub_issue_from_template(self, repo, parent_issue_number, file_refs=None):
        """
        Create a sub-issue based on a parent issue using a template.
        Migrated from create_issue.py::create_sub_issue_from_template
        """
        # Fetch parent issue from GitHub
        parent_github_issue = self.github_service.fetch_issue(repo, parent_issue_number)
        parent_body = parent_github_issue['body']

        # Extract template information
        template_name = self._extract_template_name(parent_body)
        template = IssueTemplate.objects.get(name=template_name, is_active=True)

        # Process file references
        file_refs_content = {}
        if file_refs:
            for file_path in file_refs:
                try:
                    content = self.github_service.fetch_file_contents(repo, file_path)
                    file_refs_content[file_path] = content
                except Exception as e:
                    logger.warning(f"Could not fetch file {file_path}: {e}")

        # Extract file paths from issue body and template
        issue_file_paths = re.findall(
            r"include_files_additional:\s*-\s*(.*?)\s*$",
            parent_body,
            re.MULTILINE
        )
        for file_path in issue_file_paths + template.include_files:
            if file_path not in file_refs_content:
                try:
                    content = self.github_service.fetch_file_contents(repo, file_path)
                    file_refs_content[file_path] = content
                except Exception as e:
                    logger.warning(f"Could not fetch file {file_path}: {e}")

        # Generate AI content
        system_instructions = f"{template.prompt}\n\n{template.template_body}"
        user_instructions = parent_body

        if file_refs_content:
            file_content_str = "\n\n".join([
                f"File: {path}\n{content}"
                for path, content in file_refs_content.items()
            ])
            user_instructions += f"\n\nIncluded Files:\n{file_content_str}"

        ai_generated_body = self.ai_service.call_ai_chat(
            system_instructions,
            user_instructions
        )

        # Create GitHub issue
        new_title = f"{template.title_prefix}{parent_github_issue['title']}"
        github_issue = self.github_service.create_github_issue(
            repo=repo,
            title=new_title,
            body=ai_generated_body,
            parent_issue_number=parent_issue_number,
            labels=['ai-generated'] + template.labels
        )

        # Save to database
        parent_issue, _ = Issue.objects.get_or_create(
            github_repo=repo,
            github_issue_number=parent_issue_number,
            defaults={
                'title': parent_github_issue['title'],
                'body': parent_body,
                'html_url': parent_github_issue.get('html_url'),
            }
        )

        issue = Issue.objects.create(
            github_repo=repo,
            github_issue_number=github_issue['number'],
            title=new_title,
            body=ai_generated_body,
            issue_type='sub_issue',
            labels=['ai-generated'] + template.labels,
            parent_issue=parent_issue,
            template=template,
            ai_generated=True,
            ai_prompt_used=system_instructions,
            ai_response=ai_generated_body,
            html_url=github_issue['html_url']
        )

        # Save file references
        for file_path, content in file_refs_content.items():
            IssueFileReference.objects.create(
                issue=issue,
                file_path=file_path,
                content=content
            )

        logger.info(f"Created sub-issue #{issue.github_issue_number} from parent #{parent_issue_number}")
        return issue

    def create_readme_update_issue(self, repo, issue_number, additional_files=None):
        """
        Create a README update issue.
        Migrated from create_issue.py::create_readme_update_issue
        """
        # Fetch parent issue
        github_issue = self.github_service.fetch_issue(repo, issue_number)

        # Load README update template
        try:
            template = IssueTemplate.objects.get(name='README_update.md', is_active=True)
        except IssueTemplate.DoesNotExist:
            raise ValueError("README update template not found")

        # Collect files
        all_files = template.include_files + (additional_files or [])
        included_files_content = ""

        for file in all_files:
            try:
                included_files_content += f"\n\n--- {file} content ---\n"
                included_files_content += self.github_service.fetch_file_contents(repo, file)
            except Exception as e:
                included_files_content += f"\n\nError fetching {file}: {str(e)}\n"

        # Generate AI content
        system_instructions = f"{template.prompt}\n\n{template.template_body}"
        user_instructions = f"{github_issue['body']}\n\nIncluded Files:{included_files_content}"

        ai_content = self.ai_service.call_ai_chat(
            system_instructions,
            user_instructions
        )

        # Create GitHub issue
        new_title = f"{template.title_prefix}{github_issue['title']}"
        github_new_issue = self.github_service.create_github_issue(
            repo=repo,
            title=new_title,
            body=ai_content,
            parent_issue_number=issue_number,
            labels=['readme-update-detailed']
        )

        # Save to database
        parent_issue, _ = Issue.objects.get_or_create(
            github_repo=repo,
            github_issue_number=issue_number,
            defaults={
                'title': github_issue['title'],
                'body': github_issue['body'],
                'html_url': github_issue.get('html_url'),
            }
        )

        issue = Issue.objects.create(
            github_repo=repo,
            github_issue_number=github_new_issue['number'],
            title=new_title,
            body=ai_content,
            issue_type='readme',
            labels=['readme-update-detailed'],
            parent_issue=parent_issue,
            template=template,
            ai_generated=True,
            ai_prompt_used=system_instructions,
            ai_response=ai_content,
            html_url=github_new_issue['html_url']
        )

        logger.info(f"Created README update issue #{issue.github_issue_number}")
        return issue

    def create_issue_from_feedback(
        self,
        feedback_type,
        summary,
        description,
        repo=None,
        context_files=None,
    ):
        """Create a GitHub issue from raw user feedback using AI.

        Args:
            feedback_type: "bug" or "feature" (mapped to Issue.issue_type)
            summary: Short user-provided summary used as base title
            description: Detailed feedback text from the user
            repo: Optional repo string (defaults to bamr87/githubai)
            context_files: Optional list of repo file paths to include as context
        """

        repo = repo or getattr(settings, "DEFAULT_REPO", "bamr87/githubai")
        context_files = context_files or []

        file_refs_content = {}
        for file_path in context_files:
            try:
                content = self.github_service.fetch_file_contents(repo, file_path)
                file_refs_content[file_path] = content
            except Exception as e:
                logger.warning(f"Could not fetch context file {file_path}: {e}")

        context_block = ""
        if file_refs_content:
            context_block = "\n\nRepo Context Files:\n" + "\n\n".join(
                [f"File: {path}\n{content}" for path, content in file_refs_content.items()]
            )

        system_instructions = (
            "You are an assistant that converts raw user feedback about a GitHub "
            "project into a well-structured GitHub issue. "
            "Return GitHub-flavored Markdown with clear sections such as Summary, "
            "Details, Steps to Reproduce (for bugs), Expected vs Actual, or "
            "Motivation and Acceptance Criteria (for features). Do not include "
            "front-matter or YAML, only the Markdown body."
        )

        user_instructions = (
            f"Feedback type: {feedback_type}\n"
            f"Short summary: {summary}\n\n"
            f"Detailed feedback:\n{description}\n"
            f"{context_block}"
        )

        ai_generated_body = self.ai_service.call_ai_chat(
            system_instructions,
            user_instructions,
        )

        issue_type = "bug" if feedback_type == "bug" else "feature"
        labels = ["ai-generated", issue_type]

        github_issue = self.github_service.create_github_issue(
            repo=repo,
            title=summary,
            body=ai_generated_body,
            parent_issue_number=None,
            labels=labels,
        )

        issue = Issue.objects.create(
            github_repo=repo,
            github_issue_number=github_issue["number"],
            title=summary,
            body=ai_generated_body,
            issue_type=issue_type,
            labels=labels,
            ai_generated=True,
            ai_prompt_used=system_instructions,
            ai_response=ai_generated_body,
            html_url=github_issue.get("html_url"),
        )

        for file_path, content in file_refs_content.items():
            IssueFileReference.objects.create(
                issue=issue,
                file_path=file_path,
                content=content,
            )

        logger.info(
            "Created feedback-based issue #%s (%s) in %s",
            issue.github_issue_number,
            issue_type,
            repo,
        )
        return issue

    def _extract_template_name(self, issue_body):
        """Extract template name from issue body comment"""
        match = re.search(r"<!-- template:\s*(.+\.md)\s*-->", issue_body)
        if match:
            return match.group(1).strip()
        raise ValueError("Template name comment not found in issue body.")
