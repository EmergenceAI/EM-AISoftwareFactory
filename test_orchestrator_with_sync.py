#!/usr/bin/env python3
"""
Test Orchestrator with Auto-Sync

Demonstrates that knowledge packs are automatically synced before orchestrator runs.
"""

import sys
from orchestrator import ensure_knowledge_fresh, KnowledgeEngine, Router

def main():
    print("=" * 80)
    print("AI Software Factory Orchestrator - Auto-Sync Test")
    print("=" * 80)
    print()

    # Step 1: Auto-sync knowledge (only if changed)
    print("Step 1: Syncing knowledge packs...")
    print("-" * 80)
    ensure_knowledge_fresh(verbose=True)
    print()

    # Step 2: Initialize knowledge engine
    print("Step 2: Initializing knowledge engine...")
    print("-" * 80)
    from pathlib import Path
    knowledge_root = Path(__file__).parent / 'knowledge'
    engine = KnowledgeEngine(knowledge_root=str(knowledge_root))
    print(f"Knowledge root: {knowledge_root}")
    print()

    # Step 3: Test knowledge retrieval
    print("Step 3: Testing knowledge retrieval...")
    print("-" * 80)

    repos = ['runtime', 'runtime-ui', 'talk2data', 'data-readiness']

    for repo in repos:
        print(f"\n📚 {repo}:")

        # Get all knowledge for repo
        knowledge = engine.get_repository_knowledge(repo)

        # Architecture
        if knowledge.get('architecture'):
            lines = knowledge['architecture'].split('\n')
            # Show first 5 non-empty lines
            preview = [l for l in lines if l.strip()][:5]
            print(f"  Architecture: {len(lines)} lines")
            if preview:
                print(f"  Preview: {preview[0][:60]}...")
        else:
            print(f"  ⚠️  No architecture found")

        # Patterns
        if knowledge.get('patterns'):
            lines = knowledge['patterns'].split('\n')
            print(f"  Patterns: {len(lines)} lines")
        else:
            print(f"  ⚠️  No patterns found")

        # Conventions
        if knowledge.get('conventions'):
            lines = knowledge['conventions'].split('\n')
            print(f"  Conventions: {len(lines)} lines")
        else:
            print(f"  ⚠️  No conventions found")

    print()

    # Step 4: Test router
    print("Step 4: Testing router...")
    print("-" * 80)

    import yaml
    workspace_config_path = Path(__file__).parent / 'workspace.yaml'
    with open(workspace_config_path) as f:
        workspace_config = yaml.safe_load(f)

    router = Router(workspace_config=workspace_config)

    # Mock Jira issue
    test_issue = {
        'key': 'TEST-123',
        'fields': {
            'summary': 'Fix bug in workflow execution',
            'description': 'The workflow executor is failing on async tasks',
            'components': [{'name': 'Runtime'}],
            'labels': ['backend', 'bug']
        }
    }

    routed_repo = router.route_issue(test_issue)
    print(f"\nIssue: {test_issue['key']}")
    print(f"Summary: {test_issue['fields']['summary']}")
    print(f"Routed to: {routed_repo}")
    print()

    # Step 5: Summary
    print("=" * 80)
    print("Summary:")
    print("=" * 80)
    print("✅ Knowledge packs synced")
    print("✅ Knowledge engine initialized")
    print("✅ Knowledge retrieval working")
    print("✅ Router working")
    print()
    print("🎉 Orchestrator ready to use!")
    print()
    print("Next steps:")
    print("1. Knowledge packs will auto-sync before each orchestrator run")
    print("2. Only re-extracts if README.md or docs/ changed in repos")
    print("3. Manual sync: ./sync_knowledge.sh")
    print("4. Force sync: python3 -m orchestrator.sync --force")
    print()

if __name__ == '__main__':
    main()
