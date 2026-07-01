#!/usr/bin/env python3
"""
Orchestrator CLI - Workspace-level orchestration for multi-repository workflows.

This CLI routes Jira issues to repositories, loads repository-specific knowledge,
and delegates to /autonomous-implement skill for execution.

Usage:
    python -m orchestrator.cli implement ABI-123
    python -m orchestrator.cli implement ABI-123 --repo runtime
    python -m orchestrator.cli sprint --jql "sprint in openSprints()"
"""

import sys
import argparse
from pathlib import Path
import yaml
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.router import Router
from orchestrator.executor import Executor
from orchestrator.knowledge import KnowledgeEngine
from orchestrator import jira_mcp


def load_workspace_config() -> dict:
    """Load workspace.yaml configuration."""
    workspace_file = Path(__file__).parent.parent / 'workspace.yaml'

    if not workspace_file.exists():
        print(f"❌ Error: workspace.yaml not found at {workspace_file}")
        print("   Create workspace.yaml with repository configuration first.")
        sys.exit(1)

    with open(workspace_file) as f:
        return yaml.safe_load(f)


def get_jira_issue(issue_key: str) -> dict:
    """
    Fetch Jira issue details via MCP Atlassian tools.

    Delegates to jira_mcp module which handles:
    - Real Jira fetching when MCP is available
    - Mock data fallback for testing/development

    Args:
        issue_key: Jira issue key (e.g., 'ABI-123')

    Returns:
        Issue data dictionary
    """
    return jira_mcp.get_issue(issue_key)


def cmd_implement(args):
    """Implement a single Jira issue with workspace-level orchestration."""

    print(f"\n{'='*60}")
    print(f"AI Software Factory - Workspace Orchestrator")
    print(f"{'='*60}\n")

    # Load configuration
    workspace_config = load_workspace_config()
    factory_root = Path(__file__).parent.parent

    # Fetch Jira issue
    print(f"📋 Fetching issue: {args.issue_key}")
    issue = get_jira_issue(args.issue_key)
    print(f"   Summary: {issue['summary']}\n")

    # Route to repository (unless explicitly specified)
    if args.repo:
        repository = args.repo
        print(f"🎯 Repository: {repository} (explicit)")
    else:
        router = Router(workspace_config)
        repository = router.route_issue(issue)
        print(f"🎯 Repository: {repository} (auto-routed)")

    print()

    # Initialize executor
    executor = Executor(factory_root, workspace_config)

    # Execute in repository
    result = executor.execute_single_repo(
        issue_key=args.issue_key,
        repository=repository
    )

    # Print summary
    print(result.summary() if hasattr(result, 'summary') else str(result))

    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


def cmd_multi_repo(args):
    """Implement issue across multiple repositories."""

    print(f"\n{'='*60}")
    print(f"AI Software Factory - Multi-Repo Orchestrator")
    print(f"{'='*60}\n")

    # Load configuration
    workspace_config = load_workspace_config()
    factory_root = Path(__file__).parent.parent

    # Fetch Jira issue
    print(f"📋 Fetching issue: {args.issue_key}")
    issue = get_jira_issue(args.issue_key)
    print(f"   Summary: {issue['summary']}\n")

    # Determine affected repositories
    if args.repos:
        repositories = args.repos.split(',')
        print(f"🎯 Repositories: {', '.join(repositories)} (explicit)")
    else:
        router = Router(workspace_config)
        repositories = router.get_affected_repositories(issue)
        print(f"🎯 Repositories: {', '.join(repositories)} (auto-detected)")

    print()

    # Initialize executor
    executor = Executor(factory_root, workspace_config)

    # Execute across repositories
    result = executor.execute_multi_repo(
        issue_key=args.issue_key,
        repositories=repositories
    )

    # Print summary
    print(result.summary())

    # Exit with appropriate code
    sys.exit(0 if result.overall_success else 1)


def cmd_sprint(args):
    """Execute multiple issues from a sprint (delegates to /autonomous-sprint)."""

    print(f"\n{'='*60}")
    print(f"AI Software Factory - Sprint Orchestrator")
    print(f"{'='*60}\n")

    print("🔄 Delegating to /autonomous-sprint skill...")
    print(f"   JQL: {args.jql}\n")

    # TODO: This should invoke /autonomous-sprint skill with JQL
    # For now, just show what would happen

    print("⚠️  Sprint orchestration via CLI not yet implemented.")
    print("   Use /autonomous-sprint skill directly instead:")
    print(f"   /autonomous-sprint --jql \"{args.jql}\"")

    sys.exit(1)


def cmd_knowledge(args):
    """Display repository knowledge."""

    workspace_config = load_workspace_config()
    factory_root = Path(__file__).parent.parent

    # Initialize knowledge engine
    knowledge_root = factory_root / 'knowledge'
    knowledge_engine = KnowledgeEngine(str(knowledge_root))

    if args.list:
        # List available repositories
        repos = workspace_config.get('repositories', [])
        print(f"\n{'='*60}")
        print("Available Repositories")
        print(f"{'='*60}\n")
        for repo in repos:
            print(f"  - {repo['name']}: {repo.get('display_name', repo['name'])}")
        print()
        return

    if not args.repo:
        print("❌ Error: --repo required (or use --list to see available repos)")
        sys.exit(1)

    # Load knowledge for repository
    print(f"\n{'='*60}")
    print(f"Repository Knowledge: {args.repo}")
    print(f"{'='*60}\n")

    knowledge = knowledge_engine.get_repository_knowledge(args.repo)

    for category, content in knowledge.items():
        print(f"\n## {category.upper()}")
        print(f"{'-'*60}")
        if content:
            # Show first 500 chars
            preview = content[:500] + ('...' if len(content) > 500 else '')
            print(preview)
        else:
            print("(No content available)")

    print()


def cmd_test(args):
    """Test orchestrator components without execution."""

    print(f"\n{'='*60}")
    print(f"Orchestrator Component Test")
    print(f"{'='*60}\n")

    workspace_config = load_workspace_config()
    factory_root = Path(__file__).parent.parent

    # Test router
    print("Testing Router...")
    router = Router(workspace_config)
    test_issue = get_jira_issue(args.issue_key)
    repo = router.route_issue(test_issue)
    print(f"  ✅ Routed {args.issue_key} → {repo}\n")

    # Test knowledge engine
    print("Testing Knowledge Engine...")
    knowledge_root = factory_root / 'knowledge'
    knowledge_engine = KnowledgeEngine(str(knowledge_root))
    knowledge = knowledge_engine.get_repository_knowledge(repo)
    print(f"  ✅ Loaded knowledge for {repo}:")
    for category in knowledge.keys():
        length = len(knowledge[category])
        print(f"     - {category}: {length} chars")
    print()

    # Test foundations
    print("Testing Foundations Standards...")
    foundations = knowledge_engine.get_foundations_guidance('standards')
    if foundations:
        print(f"  ✅ Loaded foundations standards: {len(foundations.get('standards', ''))} chars")
    else:
        print(f"  ⚠️  No foundations standards found")
    print()

    print("✅ All component tests passed!\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AI Software Factory - Workspace-level orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Implement single issue (auto-route to repository)
  python -m orchestrator.cli implement ABI-123

  # Implement in specific repository
  python -m orchestrator.cli implement ABI-123 --repo runtime

  # Implement across multiple repositories
  python -m orchestrator.cli multi-repo SDK-456 --repos sdk,runtime,runtime-ui

  # Execute sprint (delegates to /autonomous-sprint)
  python -m orchestrator.cli sprint --jql "sprint in openSprints()"

  # View repository knowledge
  python -m orchestrator.cli knowledge --repo runtime
  python -m orchestrator.cli knowledge --list

  # Test orchestrator components
  python -m orchestrator.cli test ABI-123
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # implement command
    implement = subparsers.add_parser(
        'implement',
        help='Implement single Jira issue in one repository'
    )
    implement.add_argument('issue_key', help='Jira issue key (e.g., ABI-123)')
    implement.add_argument(
        '--repo',
        help='Explicit repository name (default: auto-route)'
    )
    implement.set_defaults(func=cmd_implement)

    # multi-repo command
    multi = subparsers.add_parser(
        'multi-repo',
        help='Implement issue across multiple repositories'
    )
    multi.add_argument('issue_key', help='Jira issue key')
    multi.add_argument(
        '--repos',
        help='Comma-separated repository names (default: auto-detect)'
    )
    multi.set_defaults(func=cmd_multi_repo)

    # sprint command
    sprint = subparsers.add_parser(
        'sprint',
        help='Execute multiple issues from sprint'
    )
    sprint.add_argument(
        '--jql',
        required=True,
        help='JQL query for issues'
    )
    sprint.set_defaults(func=cmd_sprint)

    # knowledge command
    knowledge = subparsers.add_parser(
        'knowledge',
        help='View repository knowledge'
    )
    knowledge.add_argument('--repo', help='Repository name')
    knowledge.add_argument('--list', action='store_true', help='List all repositories')
    knowledge.set_defaults(func=cmd_knowledge)

    # test command
    test = subparsers.add_parser(
        'test',
        help='Test orchestrator components'
    )
    test.add_argument('issue_key', help='Jira issue key for testing')
    test.set_defaults(func=cmd_test)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
