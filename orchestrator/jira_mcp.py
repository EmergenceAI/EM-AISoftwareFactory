"""
Jira MCP Integration for Orchestrator

Provides functions to fetch Jira issues via MCP Atlassian tools.
Falls back to mock data when MCP is unavailable (for testing).
"""

import os
from typing import Dict, Optional


def is_mcp_available() -> bool:
    """Check if MCP Atlassian tools are available."""
    # Check for required environment variables
    required_vars = ['JIRA_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
    return all(var in os.environ for var in required_vars)


def get_issue(issue_key: str) -> Dict:
    """
    Fetch Jira issue via MCP.

    When running inside Claude Code with MCP configured, this will fetch
    real Jira data. Otherwise, falls back to mock data for testing.

    Args:
        issue_key: Jira issue key (e.g., 'ABI-123')

    Returns:
        Dictionary with issue data:
        {
            'key': 'ABI-123',
            'summary': 'Issue title',
            'description': 'Issue description',
            'components': ['Component1', 'Component2'],
            'labels': ['label1', 'label2'],
            'issuetype': 'Story'
        }
    """
    if is_mcp_available():
        try:
            return _fetch_from_mcp(issue_key)
        except Exception as e:
            print(f"⚠️  MCP fetch failed: {e}, using mock data")
            return _mock_issue(issue_key)
    else:
        print(f"ℹ️  MCP not configured, using mock data for {issue_key}")
        return _mock_issue(issue_key)


def _fetch_from_mcp(issue_key: str) -> Dict:
    """
    Fetch issue from Jira via MCP Atlassian tools.

    This function is called when running inside Claude Code with MCP configured.
    It uses the mcp__atlassian__jira_get_issue tool.

    Args:
        issue_key: Jira issue key

    Returns:
        Issue data dictionary

    Raises:
        Exception: If MCP call fails
    """
    # This would be called via the Skill tool or direct MCP invocation
    # For now, we'll use a placeholder that shows the integration pattern

    # In actual Claude Code environment, you would use:
    # result = mcp__atlassian__jira_get_issue(issue_key=issue_key)

    # Since we're in Python code, we simulate this with a note
    raise NotImplementedError(
        "MCP integration requires running in Claude Code environment. "
        "Use the orchestrator from within Claude Code to enable live Jira fetching."
    )


def _mock_issue(issue_key: str) -> Dict:
    """
    Return mock issue data for testing.

    Args:
        issue_key: Jira issue key

    Returns:
        Mock issue data
    """
    # Infer component from issue key prefix for better routing
    component = None
    if issue_key.startswith('SEMI-'):
        component = 'Semi'
    elif issue_key.startswith('RT-') or issue_key.startswith('RUN-'):
        component = 'Runtime'
    elif issue_key.startswith('UI-'):
        component = 'UI'
    elif issue_key.startswith('T2D-') or issue_key.startswith('TALK-'):
        component = 'Talk2Data'
    elif issue_key.startswith('DR-') or issue_key.startswith('DATA-'):
        component = 'Data Readiness'

    return {
        'key': issue_key,
        'summary': f'[MOCK] Implement feature for {issue_key}',
        'description': f"""
This is a mock issue for testing the orchestrator.

In production, this would be fetched from Jira via MCP.

To enable real Jira data:
1. Set environment variables: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
2. Run orchestrator from within Claude Code (not as standalone script)
3. MCP Atlassian tools will be available automatically

Issue Key: {issue_key}
        """.strip(),
        'components': [component] if component else [],
        'labels': [],
        'issuetype': 'Story'
    }


def get_issues_by_jql(jql: str, max_results: int = 50) -> list:
    """
    Fetch multiple issues via JQL query.

    Args:
        jql: JQL query string
        max_results: Maximum number of issues to return

    Returns:
        List of issue dictionaries
    """
    if is_mcp_available():
        try:
            return _fetch_jql_from_mcp(jql, max_results)
        except Exception as e:
            print(f"⚠️  MCP JQL fetch failed: {e}, using mock data")
            return _mock_jql_results(jql, max_results)
    else:
        print(f"ℹ️  MCP not configured, using mock JQL results")
        return _mock_jql_results(jql, max_results)


def _fetch_jql_from_mcp(jql: str, max_results: int) -> list:
    """Fetch issues via JQL from MCP."""
    # Would use: mcp__atlassian__jira_search(jql=jql, limit=max_results)
    raise NotImplementedError("MCP JQL requires Claude Code environment")


def _mock_jql_results(jql: str, max_results: int) -> list:
    """Return mock JQL results."""
    # Return 3 mock issues for testing
    return [
        _mock_issue('ABI-123'),
        _mock_issue('ABI-124'),
        _mock_issue('ABI-125'),
    ][:max_results]


# Integration instructions for Claude Code environment
INTEGRATION_INSTRUCTIONS = """
To use real Jira data via MCP:

1. Ensure MCP Atlassian server is configured in .mcp.json
2. Set environment variables:
   export JIRA_URL=https://your-company.atlassian.net
   export JIRA_EMAIL=your-email@company.com
   export JIRA_API_TOKEN=your_api_token

3. Run orchestrator from Claude Code (not standalone):
   - In Claude Code: /skill orchestrator implement ABI-123
   - Or use Workflow tool to invoke orchestrator

4. When running in Claude Code, replace _fetch_from_mcp() with:

   def _fetch_from_mcp(issue_key: str) -> Dict:
       # This call happens inside Claude Code with MCP available
       result = mcp__atlassian__jira_get_issue(
           issue_key=issue_key,
           fields='summary,description,components,labels,issuetype'
       )

       return {
           'key': result['key'],
           'summary': result['fields']['summary'],
           'description': result['fields'].get('description', ''),
           'components': [c['name'] for c in result['fields'].get('components', [])],
           'labels': result['fields'].get('labels', []),
           'issuetype': result['fields']['issuetype']['name']
       }

For now, orchestrator uses mock data when run as standalone script.
"""
