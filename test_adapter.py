#!/usr/bin/env python3
"""Quick test of runtime adapter."""

import sys
from pathlib import Path
import yaml

# Add adapters to path
sys.path.insert(0, str(Path(__file__).parent))

from adapters.runtime import RuntimeAdapter

# Load workspace config
with open('workspace.yaml') as f:
    workspace_config = yaml.safe_load(f)

workspace_root = Path(workspace_config['workspace']['root'])

# Find runtime config
runtime_config = next(
    r for r in workspace_config['repositories'] 
    if r['name'] == 'runtime'
)

# Create adapter
adapter = RuntimeAdapter(workspace_root, runtime_config)

# Test metadata
print("=" * 60)
print("RUNTIME ADAPTER TEST")
print("=" * 60)
print()

metadata = adapter.get_metadata()
print(f"Repository: {metadata.display_name}")
print(f"Path: {metadata.path}")
print(f"Language: {metadata.primary_language}")
print(f"Build System: {metadata.build_system}")
print(f"Test Framework: {metadata.test_framework}")
print()

# Test conventions
print("Conventions:")
conventions = adapter.get_conventions()
for key, value in conventions.items():
    print(f"  - {key}: {value}")
print()

# Test branch creation (dry run - we'll just generate the name)
print("Branch naming examples:")
examples = [
    ("ABI-123", "Story", "Add user authentication"),
    ("ABI-456", "Bug", "Fix memory leak in executor"),
    ("ABI-789", "Task", "Update dependencies")
]

for issue_key, issue_type, summary in examples:
    # Don't actually create branch, just show what it would be
    prefix_map = {'Story': 'feature', 'Bug': 'bugfix', 'Task': 'task'}
    prefix = prefix_map.get(issue_type, 'feature')
    slug = summary.lower().replace(' ', '-')[:50].strip('-')
    branch = f"{prefix}/{issue_key}-{slug}"
    print(f"  {issue_key} ({issue_type}): {branch}")

print()
print("=" * 60)
print("✅ Adapter test complete!")
print("=" * 60)
