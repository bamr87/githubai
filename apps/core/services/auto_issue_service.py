"""Auto Issue Service - automatically generate GitHub issues from repo analysis"""
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from django.conf import settings
from core.models import Issue
from core.services.github_service import GitHubService
from core.services.ai_service import AIService

logger = logging.getLogger('githubai')


class AutoIssueService:
    """Service for automatically creating GitHub issues from repo analysis"""

    CHORE_TYPES = {
        'code_quality': 'Analyze code for quality issues, complexity, and best practices',
        'todo_scan': 'Find TODO/FIXME/HACK comments in code that need attention',
        'documentation': 'Identify missing or outdated documentation',
        'dependencies': 'Check for outdated dependencies and security issues',
        'test_coverage': 'Analyze test coverage and suggest missing tests',
        'general_review': 'Perform a general repository health check',
    }

    def __init__(self) -> None:
        self.github_service: GitHubService = GitHubService()
        self.ai_service: AIService = AIService()

    def analyze_repo_and_create_issue(
        self,
        repo: str,
        chore_type: str = 'general_review',
        context_files: Optional[List[str]] = None,
        auto_submit: bool = True,
    ) -> Issue:
        """
        Analyze repository and automatically create a GitHub issue.

        Args:
            repo: Repository in format owner/repo (defaults to bamr87/githubai)
            chore_type: Type of analysis to perform (see CHORE_TYPES)
            context_files: Optional list of files to analyze
            auto_submit: If True, creates GitHub issue; if False, only returns analysis

        Returns:
            Issue instance with analysis results
        """
        repo = repo or getattr(settings, "DEFAULT_REPO", "bamr87/githubai")

        if chore_type not in self.CHORE_TYPES:
            raise ValueError(
                f"Invalid chore_type. Must be one of: {', '.join(self.CHORE_TYPES.keys())}"
            )

        logger.info(f"Starting auto-issue analysis: {chore_type} for {repo}")

        # Get repo analysis
        analysis_data = self._perform_analysis(repo, chore_type, context_files)

        # Generate AI-refined issue content
        issue_content = self._generate_issue_content(
            chore_type, analysis_data, repo
        )

        if not auto_submit:
            logger.info("Auto-submit disabled, returning analysis only")
            return issue_content

        # Create GitHub issue
        title = self._generate_title(chore_type, analysis_data)
        labels = self._get_labels_for_chore(chore_type)

        github_issue = self.github_service.create_github_issue(
            repo=repo,
            title=title,
            body=issue_content,
            labels=labels,
        )

        # Save to database
        issue = Issue.objects.create(
            github_repo=repo,
            github_issue_number=github_issue['number'],
            title=title,
            body=issue_content,
            issue_type='other',
            labels=labels,
            ai_generated=True,
            ai_prompt_used=f"Auto-issue: {chore_type}",
            ai_response=issue_content,
            html_url=github_issue.get('html_url'),
        )

        logger.info(
            f"Created auto-issue #{issue.github_issue_number}: {title}"
        )
        return issue

    def _perform_analysis(
        self, repo: str, chore_type: str, context_files: Optional[List[str]] = None
    ) -> Dict:
        """Perform repository analysis based on chore type"""

        analysis = {
            'repo': repo,
            'chore_type': chore_type,
            'findings': [],
            'file_contents': {},
        }

        # Determine which files to analyze
        if context_files:
            files_to_check = context_files
        else:
            files_to_check = self._get_default_files_for_chore(chore_type)

        # Fetch and analyze files
        for file_path in files_to_check:
            try:
                content = self.github_service.fetch_file_contents(repo, file_path)
                analysis['file_contents'][file_path] = content

                # Perform specific analysis based on chore type
                if chore_type == 'todo_scan':
                    todos = self._scan_for_todos(content, file_path)
                    analysis['findings'].extend(todos)
                elif chore_type == 'code_quality':
                    quality_issues = self._analyze_code_quality(content, file_path)
                    analysis['findings'].extend(quality_issues)
                elif chore_type == 'documentation':
                    doc_gaps = self._check_documentation(content, file_path)
                    analysis['findings'].extend(doc_gaps)

            except Exception as e:
                logger.warning(f"Could not analyze file {file_path}: {e}")
                analysis['findings'].append({
                    'file': file_path,
                    'type': 'error',
                    'message': f"Could not fetch or analyze: {str(e)}"
                })

        return analysis

    def _generate_issue_content(
        self, chore_type: str, analysis_data: Dict, repo: str
    ) -> str:
        """Use AI to generate well-formatted issue content from analysis"""

        system_prompt = (
            "You are a software engineering assistant that creates detailed GitHub issues "
            "for repository maintenance and improvements. Based on the analysis data provided, "
            "generate a clear, actionable GitHub issue in Markdown format. Include:\n"
            "- A summary of findings\n"
            "- Specific recommendations with file references\n"
            "- Prioritized action items\n"
            "- Expected benefits of addressing these items\n\n"
            "Format the issue professionally with proper Markdown sections."
        )

        findings_text = "\n".join([
            f"- {finding.get('file', 'N/A')}: {finding.get('message', finding)}"
            for finding in analysis_data.get('findings', [])
        ])

        files_analyzed = ", ".join(analysis_data.get('file_contents', {}).keys())

        user_prompt = (
            f"Repository: {repo}\n"
            f"Analysis Type: {chore_type} - {self.CHORE_TYPES[chore_type]}\n"
            f"Files Analyzed: {files_analyzed or 'Default project files'}\n\n"
            f"Findings:\n{findings_text or 'General repository review'}\n\n"
            f"Please create a comprehensive GitHub issue that addresses these findings "
            f"and provides actionable recommendations for the development team."
        )

        issue_body = self.ai_service.call_ai_chat(system_prompt, user_prompt)
        return issue_body

    def _generate_title(self, chore_type: str, analysis_data: Dict) -> str:
        """Generate issue title based on chore type and findings"""
        finding_count = len(analysis_data.get('findings', []))

        title_map = {
            'code_quality': f"[Auto] Code Quality Review - {finding_count} items found",
            'todo_scan': f"[Auto] TODO/FIXME Comments - {finding_count} items to address",
            'documentation': f"[Auto] Documentation Gaps - {finding_count} areas need attention",
            'dependencies': "[Auto] Dependency Update & Security Check",
            'test_coverage': "[Auto] Test Coverage Analysis",
            'general_review': "[Auto] Repository Health Check",
        }

        return title_map.get(chore_type, f"[Auto] Repository Maintenance: {chore_type}")

    def _get_labels_for_chore(self, chore_type: str) -> List[str]:
        """Get appropriate labels for chore type"""
        base_labels = ['auto-generated', 'maintenance']

        chore_labels = {
            'code_quality': ['code-quality', 'refactor'],
            'todo_scan': ['technical-debt'],
            'documentation': ['documentation'],
            'dependencies': ['dependencies', 'security'],
            'test_coverage': ['testing'],
            'general_review': ['health-check'],
        }

        return base_labels + chore_labels.get(chore_type, [])

    def _get_default_files_for_chore(self, chore_type: str) -> List[str]:
        """Get default files to check for each chore type"""
        common_files = ['README.md', 'requirements-dev.txt', 'pyproject.toml']

        chore_files = {
            'code_quality': ['apps/core/services/issue_service.py', 'apps/core/views.py'],
            'todo_scan': ['apps/core/services/issue_service.py', 'apps/core/services/ai_service.py'],
            'documentation': ['README.md', 'docs/DJANGO_IMPLEMENTATION.md'],
            'dependencies': ['requirements-dev.txt', 'pyproject.toml'],
            'test_coverage': ['tests/test_issues_service.py', 'pytest.ini'],
            'general_review': common_files,
        }

        return chore_files.get(chore_type, common_files)

    def _scan_for_todos(self, content: str, file_path: str) -> List[Dict]:
        """Scan file content for TODO/FIXME/HACK comments"""
        findings = []
        todo_pattern = re.compile(
            r'#\s*(TODO|FIXME|HACK|XXX|NOTE|BUG)[\s:]*(.+?)$',
            re.IGNORECASE | re.MULTILINE
        )

        for match in todo_pattern.finditer(content):
            findings.append({
                'file': file_path,
                'type': match.group(1).upper(),
                'message': match.group(2).strip(),
            })

        return findings

    def _analyze_code_quality(self, content: str, file_path: str) -> List[Dict]:
        """Analyze code for quality issues"""
        findings = []

        # Check for long lines
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                findings.append({
                    'file': file_path,
                    'line': i,
                    'type': 'line_length',
                    'message': f'Line {i} exceeds 120 characters ({len(line)} chars)',
                })

        # Check for missing docstrings in Python files
        if file_path.endswith('.py'):
            if 'def ' in content or 'class ' in content:
                if '"""' not in content and "'''" not in content:
                    findings.append({
                        'file': file_path,
                        'type': 'documentation',
                        'message': 'File contains functions/classes but no docstrings',
                    })

        return findings[:5]  # Limit findings

    def _check_documentation(self, content: str, file_path: str) -> List[Dict]:
        """Check for documentation gaps"""
        findings = []

        if file_path.endswith('.md'):
            # Check for common sections in README
            if file_path == 'README.md':
                required_sections = ['Installation', 'Usage', 'Contributing', 'License']
                for section in required_sections:
                    if section.lower() not in content.lower():
                        findings.append({
                            'file': file_path,
                            'type': 'missing_section',
                            'message': f'Missing "{section}" section',
                        })

        return findings

    @classmethod
    def list_chore_types(cls) -> Dict[str, str]:
        """Return available chore types"""
        return cls.CHORE_TYPES
