"""
Router - Determines which repository an issue should be implemented in.

Uses multiple strategies:
1. Jira component mapping (primary)
2. Issue description analysis (fallback)
3. Labels (fallback)
4. Default to 'runtime'
"""

from typing import Dict, List, Optional
import re


class Router:
    """Routes Jira issues to repositories."""

    def __init__(self, workspace_config: Dict):
        """
        Initialize router with workspace configuration.

        Args:
            workspace_config: Loaded workspace.yaml configuration
        """
        self.workspace_config = workspace_config
        self.component_mapping = self._build_component_mapping()

    def route_issue(self, jira_issue: Dict) -> str:
        """
        Determine which repository should handle this issue.

        Strategy:
        1. Check Jira component field → component_mapping
        2. Analyze description for repository mentions
        3. Check labels for repo: prefix
        4. Default to 'runtime'

        Args:
            jira_issue: Jira issue dict with fields like:
                - key: Issue key (e.g., 'ABI-123')
                - components: List of component names
                - description: Issue description
                - labels: List of labels

        Returns:
            Repository name (e.g., 'runtime', 'runtime-ui')
        """
        # Strategy 1: Component mapping
        repo = self._route_by_component(jira_issue)
        if repo:
            return repo

        # Strategy 2: Description analysis
        repo = self._route_by_description(jira_issue)
        if repo:
            return repo

        # Strategy 3: Label prefix (repo:runtime)
        repo = self._route_by_labels(jira_issue)
        if repo:
            return repo

        # Default: runtime
        return 'runtime'

    def route_batch(self, jira_issues: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Route multiple issues and group by repository.

        Args:
            jira_issues: List of Jira issue dicts

        Returns:
            Dictionary mapping repository name → list of issues
            Example:
            {
                'runtime': [issue1, issue2],
                'runtime-ui': [issue3],
                'talk2data': [issue4, issue5]
            }
        """
        issues_by_repo: Dict[str, List[Dict]] = {}

        for issue in jira_issues:
            repo = self.route_issue(issue)

            if repo not in issues_by_repo:
                issues_by_repo[repo] = []

            issues_by_repo[repo].append(issue)

        return issues_by_repo

    def get_affected_repositories(self, jira_issue: Dict) -> List[str]:
        """
        Determine all repositories affected by this issue.

        Some issues may touch multiple repositories (e.g., SDK + Runtime).

        Args:
            jira_issue: Jira issue dict

        Returns:
            List of repository names
        """
        affected = []

        # Check components (may have multiple)
        components = jira_issue.get('components', [])
        for component in components:
            repo = self.component_mapping.get(component)
            if repo and repo not in affected:
                affected.append(repo)

        # Check description for explicit mentions
        description = jira_issue.get('description', '')
        for repo_name in self._get_all_repo_names():
            if repo_name in description.lower() or repo_name.replace('-', ' ') in description.lower():
                if repo_name not in affected:
                    affected.append(repo_name)

        # Default to single repo if nothing found
        if not affected:
            affected.append(self.route_issue(jira_issue))

        return affected

    # Private methods

    def _build_component_mapping(self) -> Dict[str, str]:
        """Build component name → repository name mapping from workspace config."""
        mapping = {}

        # Get component mapping from workspace config
        jira_config = self.workspace_config.get('jira', {})
        component_map = jira_config.get('component_mapping', {})

        for component_name, repo_name in component_map.items():
            mapping[component_name] = repo_name

        return mapping

    def _route_by_component(self, jira_issue: Dict) -> Optional[str]:
        """Route based on Jira component field."""
        components = jira_issue.get('components', [])

        if not components:
            return None

        # Use first component that maps to a repository
        for component in components:
            repo = self.component_mapping.get(component)
            if repo:
                return repo

        return None

    def _route_by_description(self, jira_issue: Dict) -> Optional[str]:
        """Route based on description analysis."""
        description = jira_issue.get('description', '').lower()

        if not description:
            return None

        # Check for explicit repository mentions
        repo_keywords = {
            'runtime': ['runtime', 'executor', 'workflow engine'],
            'runtime-ui': ['ui', 'frontend', 'react', 'interface'],
            'talk2data': ['talk2data', 'talk to data', 't2d', 'query'],
            'connectors': ['connector', 'integration', 'data source'],
            'sdk': ['sdk', 'core library', 'shared'],
            'data-readiness': ['data readiness', 'data quality', 'readiness']
        }

        # Count mentions per repository
        mentions = {}
        for repo, keywords in repo_keywords.items():
            count = sum(1 for keyword in keywords if keyword in description)
            if count > 0:
                mentions[repo] = count

        # Return repository with most mentions
        if mentions:
            return max(mentions, key=mentions.get)

        return None

    def _route_by_labels(self, jira_issue: Dict) -> Optional[str]:
        """Route based on labels with 'repo:' prefix."""
        labels = jira_issue.get('labels', [])

        if not labels:
            return None

        # Look for labels like 'repo:runtime', 'repo:ui'
        for label in labels:
            if label.startswith('repo:'):
                repo_name = label[5:]  # Strip 'repo:' prefix
                # Validate it's a known repository
                if repo_name in self._get_all_repo_names():
                    return repo_name

        return None

    def _get_all_repo_names(self) -> List[str]:
        """Get all repository names from workspace config."""
        repos = self.workspace_config.get('repositories', [])
        return [repo['name'] for repo in repos]


# Convenience function
def route_issue(workspace_config: Dict, jira_issue: Dict) -> str:
    """
    Convenience function to route a single issue.

    Args:
        workspace_config: Loaded workspace.yaml
        jira_issue: Jira issue dict

    Returns:
        Repository name
    """
    router = Router(workspace_config)
    return router.route_issue(jira_issue)
