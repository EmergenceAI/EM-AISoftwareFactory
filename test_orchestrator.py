#!/usr/bin/env python3
"""
Test the orchestrator end-to-end.

This script demonstrates:
1. Loading workspace configuration
2. Creating knowledge engine, router, planner
3. Generating task graph from mock Jira issue
4. Displaying the result
"""

import sys
from pathlib import Path
import yaml
import json

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import KnowledgeEngine, Router, Planner

# Load workspace config
print("Loading workspace configuration...")
with open('workspace.yaml') as f:
    workspace_config = yaml.safe_load(f)

workspace_root = Path(workspace_config['workspace']['root'])
factory_root = Path(__file__).parent

print(f"Workspace root: {workspace_root}")
print(f"Factory root: {factory_root}")
print()

# Initialize components
print("Initializing orchestrator components...")
knowledge_engine = KnowledgeEngine(factory_root / 'knowledge')
router = Router(workspace_config)
planner = Planner(knowledge_engine, router, workspace_config)
print("✅ Components initialized")
print()

# Mock Jira issue
mock_issue = {
    'key': 'ABI-123',
    'type': 'Story',
    'summary': 'Add user authentication to Runtime API',
    'description': '''
    Implement JWT-based authentication for the Runtime API.

    Requirements:
    - Add authentication middleware
    - Support JWT tokens
    - Add login/logout endpoints
    - Include tests
    ''',
    'components': ['Runtime'],
    'acceptanceCriteria': '''
    - User can login with email/password
    - JWT token is returned on successful login
    - Protected endpoints require valid token
    - Token expires after 24 hours
    '''
}

print("=" * 60)
print("ORCHESTRATOR TEST")
print("=" * 60)
print()

print("Mock Jira Issue:")
print(f"  Key: {mock_issue['key']}")
print(f"  Type: {mock_issue['type']}")
print(f"  Summary: {mock_issue['summary']}")
print(f"  Components: {mock_issue['components']}")
print()

# Step 1: Route issue
print("Step 1: Routing issue to repository...")
repo = router.route_issue(mock_issue)
print(f"  → Routed to: {repo}")
print()

# Step 2: Load knowledge
print("Step 2: Loading knowledge pack...")
knowledge = knowledge_engine.get_repository_knowledge(repo)
print(f"  → Architecture: {len(knowledge['architecture'])} chars")
print(f"  → Patterns: {len(knowledge['patterns'])} chars")
print(f"  → Conventions: {len(knowledge['conventions'])} chars")
print()

# Step 3: Generate task graph
print("Step 3: Generating task graph...")
task_graph = planner.create_task_graph(mock_issue)
print(f"  → Tasks: {len(task_graph.tasks)}")
print(f"  → Dependencies: {len(task_graph.dependencies)}")
print()

# Display task graph
print("Task Graph Details:")
print(f"  Issue: {task_graph.issue_key}")
print()

for i, task in enumerate(task_graph.tasks, 1):
    print(f"  Task {i}: {task.repository}")
    print(f"    Issue: {task.issue_key}")
    print(f"    Type: {task.issue_type}")
    print(f"    Adapter: {task.adapter_class}")
    print(f"    Steps: {len(task.steps)}")

    for j, step in enumerate(task.steps, 1):
        print(f"      {j}. {step.phase} → {step.prompt_template}")

    print()

if task_graph.dependencies:
    print("  Dependencies:")
    for dep in task_graph.dependencies:
        print(f"    {dep.before} → {dep.after} ({dep.reason})")
    print()

print("=" * 60)
print("✅ Orchestrator test complete!")
print("=" * 60)
print()
print("Next steps:")
print("  1. The orchestrator successfully generated a task graph")
print("  2. Knowledge was loaded from the knowledge pack")
print("  3. Steps were generated based on issue type")
print("  4. Ready to integrate with Claude Code for execution")
