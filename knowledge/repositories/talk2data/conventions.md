<!--
AUTO-GENERATED from talk2data
Last sync: 2026-06-29 06:53:28 UTC
Source commit: 64e783dd49b85dcad1398ac63be7e39c7c8ca8d8
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# talk2data Coding Conventions

## Code Style

### Python (from pyproject.toml)
```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.mypy]
explicit_package_bases = true

```

## Testing Conventions

- Test framework: pytest
- Test files: `tests/test_*.py`
