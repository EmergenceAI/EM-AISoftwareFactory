<!--
AUTO-GENERATED from runtime
Last sync: 2026-06-29 06:53:27 UTC
Source commit: 75b67ca25effe1e76ecbbef03d20bf8fe1d40b84
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# runtime Coding Conventions

## Code Style

### Python (from pyproject.toml)
```toml
[tool.black]
line-length = 120
extend-exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
  | em_runtime_governance/tests
  | em_runtime_assets/tests
  | em_runtime_utils/tests
  | em_runtime_common/tests
)/
'''

[tool.ruff]
line-length = 120
extend-exclude = [
    "packages/em_runtime_governance/tests",
    "packages/em_runtime_assets/tests",
    "packages/em_runtime_utils/tests",
    "packages/em_runtime_common/tests",
]

```

### TypeScript/JavaScript (from package.json)
```json
{
  "scripts": {
    "changeset": "changeset",
    "version": "changeset version",
    "release": "changeset publish"
  },
  "eslintConfig": null,
  "prettier": null
}
```

## Testing Conventions

- Test framework: pytest
- Test files: `tests/test_*.py`
