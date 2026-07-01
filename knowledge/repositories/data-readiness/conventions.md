<!--
AUTO-GENERATED from data-readiness
Last sync: 2026-06-29 06:53:28 UTC
Source commit: 20b4b407771b7e789c7e79bd35f38514e6a9ca44
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# data-readiness Coding Conventions

## Code Style

### Python (from pyproject.toml)
```toml
[tool.ruff]
line-length = 120
target-version = "py312"
extend-exclude = ["alembic"]

```

## Testing Conventions

- Test framework: pytest
- Test files: `tests/test_*.py`
