"""
Orchestrator: Workspace-level orchestration for multi-repository workflows.

This package provides:
- Knowledge Engine: Loads repository-specific architecture/patterns
- Router: Routes Jira issues to correct repository
- Executor: Delegates to /autonomous-implement skill with knowledge context
- Multi-repo coordination: Handles cross-repository dependencies

The harness is a THIN layer that enhances existing skills with:
- Repository-specific knowledge injection
- Multi-repository routing and coordination
- Foundations standards enforcement
"""

from .knowledge import KnowledgeEngine
from .router import Router
from .planner import Planner
from .executor import Executor, TaskResult, ExecutionResult
from .reporter import Reporter
from .sync import sync_knowledge_if_needed, force_sync_all

__all__ = [
    'KnowledgeEngine',
    'Router',
    'Planner',
    'Executor',
    'TaskResult',
    'ExecutionResult',
    'Reporter',
    'sync_knowledge_if_needed',
    'force_sync_all',
]

__version__ = '0.1.0'


def ensure_knowledge_fresh(verbose: bool = False):
    """
    Ensure knowledge packs are up-to-date before harness runs.

    This is called automatically by harness entry points.
    Only re-extracts if source documentation has changed.

    Args:
        verbose: Print sync status messages
    """
    sync_knowledge_if_needed(verbose=verbose)
