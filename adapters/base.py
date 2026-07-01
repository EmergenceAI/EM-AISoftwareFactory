"""
Base adapter interface for repository operations.

All repository adapters must implement this interface to enable
standardized orchestration across different repositories.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class RepositoryMetadata:
    """Metadata about a repository."""
    name: str
    display_name: str
    path: Path
    github_url: str
    primary_language: str
    build_system: str
    test_framework: str
    jira_component: str
    conventions: Dict[str, str]


class RepositoryAdapter(ABC):
    """
    Abstract interface for repository operations.

    Each repository implements this interface to provide standardized
    access to build, test, lint, and metadata operations.

    The adapter pattern allows the orchestrator to remain agnostic
    to repository-specific details while maintaining consistent operations.
    """

    def __init__(self, workspace_root: Path, config: Dict):
        """
        Initialize adapter with workspace configuration.

        Args:
            workspace_root: Root directory of the workspace
            config: Repository configuration from workspace.yaml
        """
        self.workspace_root = workspace_root
        self.config = config
        self.repo_path = workspace_root / config['path']

    @abstractmethod
    def get_metadata(self) -> RepositoryMetadata:
        """
        Return repository metadata.

        Returns:
            RepositoryMetadata with details about the repository
        """
        pass

    @abstractmethod
    def build(self, target: Optional[str] = None) -> bool:
        """
        Run build command for the repository.

        Args:
            target: Optional build target (e.g., 'wheel', 'dist')

        Returns:
            True if build succeeded, False otherwise
        """
        pass

    @abstractmethod
    def test(self, test_path: Optional[str] = None) -> bool:
        """
        Run test suite for the repository.

        Args:
            test_path: Optional specific test path/file to run

        Returns:
            True if tests passed, False otherwise
        """
        pass

    @abstractmethod
    def lint(self, files: Optional[List[str]] = None) -> bool:
        """
        Run linter on repository files.

        Args:
            files: Optional list of specific files to lint (None = all files)

        Returns:
            True if linting passed, False otherwise
        """
        pass

    @abstractmethod
    def format(self, files: Optional[List[str]] = None, check_only: bool = False) -> bool:
        """
        Run formatter on repository files.

        Args:
            files: Optional list of specific files to format (None = all files)
            check_only: If True, only check formatting without modifying files

        Returns:
            True if formatting is correct (or succeeded), False otherwise
        """
        pass

    @abstractmethod
    def get_architecture(self) -> str:
        """
        Return path to architecture documentation.

        Returns:
            Path to architecture.md relative to repo root
        """
        pass

    @abstractmethod
    def get_patterns(self) -> str:
        """
        Return path to coding patterns documentation.

        Returns:
            Path to patterns.md relative to repo root
        """
        pass

    @abstractmethod
    def get_conventions(self) -> Dict[str, str]:
        """
        Return coding conventions for this repository.

        Returns:
            Dictionary of convention name → convention value
            Examples: {'imports': 'absolute', 'typing': 'strict'}
        """
        pass

    @abstractmethod
    def create_branch(self, issue_key: str, issue_type: str, summary: str) -> str:
        """
        Create standardized branch name for Jira issue.

        Args:
            issue_key: Jira issue key (e.g., 'ABI-123')
            issue_type: Issue type (e.g., 'Story', 'Bug', 'Task')
            summary: Issue summary/title

        Returns:
            Created branch name
        """
        pass

    def install_dependencies(self) -> bool:
        """
        Install repository dependencies.

        Returns:
            True if installation succeeded, False otherwise
        """
        # Default implementation - can be overridden
        if self.config.get('build_system') == 'poetry':
            import subprocess
            result = subprocess.run(
                ['poetry', 'install'],
                cwd=self.repo_path,
                capture_output=True
            )
            return result.returncode == 0
        elif self.config.get('build_system') == 'pnpm':
            import subprocess
            result = subprocess.run(
                ['pnpm', 'install'],
                cwd=self.repo_path,
                capture_output=True
            )
            return result.returncode == 0
        return True

    def get_config_value(self, key: str, default=None):
        """
        Get configuration value with fallback.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
