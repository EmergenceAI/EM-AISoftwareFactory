"""
Repository adapter for em-runtime.

Python-based workflow orchestration engine using Poetry and pytest.
"""

from pathlib import Path
from typing import Dict, List, Optional
import subprocess

from .base import RepositoryAdapter, RepositoryMetadata


class RuntimeAdapter(RepositoryAdapter):
    """Adapter for em-runtime repository."""

    def get_metadata(self) -> RepositoryMetadata:
        """Return em-runtime metadata."""
        return RepositoryMetadata(
            name='runtime',
            display_name='EM Runtime',
            path=self.repo_path,
            github_url='https://github.com/EmergenceAI/em-runtime',
            primary_language='python',
            build_system='poetry',
            test_framework='pytest',
            jira_component='Runtime',
            conventions={
                'branch_prefix': 'feature/',
                'commit_format': 'conventional',
                'imports': 'absolute',
                'typing': 'strict',
                'docstrings': 'google',
                'test_naming': 'test_*'
            }
        )

    def build(self, target: Optional[str] = None) -> bool:
        """
        Run poetry build.

        Args:
            target: Build format ('wheel', 'sdist', or None for both)
        """
        cmd = ['poetry', 'build']
        if target:
            cmd.extend(['--format', target])

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Build failed: {result.stderr}")

        return result.returncode == 0

    def test(self, test_path: Optional[str] = None) -> bool:
        """
        Run pytest.

        Args:
            test_path: Specific test file/directory to run
        """
        cmd = ['poetry', 'run', 'pytest']

        if test_path:
            cmd.append(test_path)
        else:
            # Run with coverage
            cmd.extend(['--cov=src', '--cov-report=term-missing'])

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Tests failed:\n{result.stdout}")

        return result.returncode == 0

    def lint(self, files: Optional[List[str]] = None) -> bool:
        """
        Run ruff linter.

        Args:
            files: Specific files to lint (None = all)
        """
        cmd = ['poetry', 'run', 'ruff', 'check']

        if files:
            cmd.extend(files)
        else:
            cmd.append('.')

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Linting failed:\n{result.stdout}")

        return result.returncode == 0

    def format(self, files: Optional[List[str]] = None, check_only: bool = False) -> bool:
        """
        Run black formatter.

        Args:
            files: Specific files to format (None = all)
            check_only: Only check, don't modify files
        """
        cmd = ['poetry', 'run', 'black']

        if check_only:
            cmd.append('--check')

        if files:
            cmd.extend(files)
        else:
            cmd.append('.')

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    def get_architecture(self) -> str:
        """Return path to architecture documentation."""
        return 'docs/architecture.md'

    def get_patterns(self) -> str:
        """Return path to coding patterns documentation."""
        return 'docs/patterns.md'

    def get_conventions(self) -> Dict[str, str]:
        """Return coding conventions."""
        return {
            'imports': 'absolute',
            'typing': 'strict (mypy)',
            'docstrings': 'google style',
            'test_naming': 'test_* for functions, Test* for classes',
            'error_handling': 'explicit exceptions, no bare except',
            'async': 'asyncio for I/O, avoid threading'
        }

    def create_branch(self, issue_key: str, issue_type: str, summary: str) -> str:
        """
        Create standardized branch for em-runtime.

        Branch naming:
        - Story: feature/ABI-123-short-description
        - Bug: bugfix/ABI-123-short-description
        - Task: task/ABI-123-short-description
        """
        # Determine prefix based on issue type
        prefix_map = {
            'Story': 'feature',
            'Bug': 'bugfix',
            'Task': 'task',
            'Epic': 'epic'
        }
        prefix = prefix_map.get(issue_type, 'feature')

        # Slugify summary (lowercase, hyphens, max 50 chars)
        slug = summary.lower() \
            .replace(' ', '-') \
            .replace('_', '-') \
            [:50] \
            .strip('-')

        branch_name = f"{prefix}/{issue_key}-{slug}"

        # Create branch
        result = subprocess.run(
            ['git', 'checkout', '-b', branch_name],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Failed to create branch: {result.stderr}")
            return ""

        return branch_name
