"""
Jira Integration for Orchestrator

Provides functions to extract Jira component and route to correct repository.
The harness delegates actual Jira fetching to skills (which use MCP).
"""

from typing import Dict, Optional


def get_issue_component(issue_key: str) -> Optional[str]:
    """
    Infer Jira component from issue key prefix for routing.

    The harness doesn't fetch full issue data - it just needs to know
    which repository to route to. The actual issue fetching happens in skills
    via MCP (mcp__atlassian__jira_get_issue).

    Args:
        issue_key: Jira issue key (e.g., 'SEMI-1413')

    Returns:
        Component name for routing, or None if unknown

    Examples:
        >>> get_issue_component('SEMI-1413')
        'Semi'
        >>> get_issue_component('RT-567')
        'Runtime'
    """
    # Infer component from issue key prefix for routing
    if issue_key.startswith('SEMI-'):
        return 'Semi'
    elif issue_key.startswith('RT-') or issue_key.startswith('RUN-'):
        return 'Runtime'
    elif issue_key.startswith('UI-'):
        return 'UI'
    elif issue_key.startswith('T2D-') or issue_key.startswith('TALK-'):
        return 'Talk2Data'
    elif issue_key.startswith('DR-') or issue_key.startswith('DATA-'):
        return 'Data Readiness'
    else:
        return None


def get_repository_for_issue(issue_key: str, component_mapping: Dict[str, str]) -> Optional[str]:
    """
    Get target repository name for an issue.

    Args:
        issue_key: Jira issue key
        component_mapping: Dict mapping component names to repository names
                          (from workspace.yaml jira.component_mapping)

    Returns:
        Repository name, or None if no mapping found

    Examples:
        >>> mapping = {'Semi': 'semi', 'Runtime': 'runtime'}
        >>> get_repository_for_issue('SEMI-1413', mapping)
        'semi'
    """
    component = get_issue_component(issue_key)
    if component and component in component_mapping:
        return component_mapping[component]
    return None


# Integration note:
# The harness's job is to route issues to the correct repository
# and prepare knowledge context. The actual Jira data fetching happens
# in the skills themselves via MCP:
#
# Example from /autonomous-implement skill:
#   const issue = await mcp__atlassian__jira_get_issue({
#     issueKey: issueKey,
#     fields: ['summary', 'description', 'issuetype', 'status']
#   })
#
# This separation keeps the harness lightweight and lets skills
# handle the full Jira integration with all available MCP tools.
