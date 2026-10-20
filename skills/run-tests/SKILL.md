---
name: run-tests
description: Run the existing test suite (excluding evals/) and write a structured JSON result to --output
---

# Run Tests

Run the project's existing test suite on the current branch, excluding the `tests/evals/` directory (which is handled by `/run-evals`). Write a structured JSON result to `--output` for the harness.

## Usage

```bash
# Called by the harness
/run-tests --output .harness-results/tests.json

# Standalone
/run-tests
```

### Parameters

- `--output <path>`: File path to write the JSON result.

---

## Instructions

### Step 1: Discover test command

Check in this order:

```bash
# 1. Makefile
grep -E "^test:" Makefile   → make test

# 2. pyproject.toml (Python)
[tool.pytest.ini_options]   → uv run pytest   or   pytest

# 3. package.json (JS/TS)
"scripts": { "test": "..." } → npm test

# 4. go.mod (Go)
                             → go test ./...

# 5. Cargo.toml (Rust)
                             → cargo test

# 6. CI workflow
.github/workflows/*.yml      → extract test step command
```

### Step 2: Run tests, excluding evals

```bash
# Python — exclude evals directory
pytest --ignore=tests/evals/ -v \
  --json-report \
  --json-report-file=.harness-results/pytest-report.json \
  2>&1

# If --json-report plugin not installed, run without it and parse stdout
pytest --ignore=tests/evals/ -v 2>&1

# JS/TS
npm test -- --testPathIgnorePatterns=evals

# Go / Rust
go test ./...     # evals not applicable
```

### Step 3: Parse results

From pytest JSON report (if available):

```javascript
const report = JSON.parse(readFile('.harness-results/pytest-report.json'))
const passed = report.summary.passed
const failed = report.summary.failed
const total  = report.summary.total
const failures = report.tests
  .filter(t => t.outcome === 'failed')
  .map(t => ({
    nodeid:   t.nodeid,
    message:  t.call?.longrepr || t.longrepr || 'unknown error',
  }))
```

From stdout (fallback):

- Count lines matching `PASSED`, `FAILED`, `ERROR`
- Extract test names and error messages from failure blocks

### Step 4: Write JSON result to --output

```json
{
  "passed": true,
  "total": 47,
  "passed_count": 47,
  "failed_count": 0,
  "error_count": 0,
  "failures": [],
  "command": "pytest --ignore=tests/evals/ -v"
}
```

Failure example:

```json
{
  "passed": false,
  "total": 47,
  "passed_count": 45,
  "failed_count": 2,
  "error_count": 0,
  "failures": [
    {
      "nodeid": "tests/services/test_auth.py::test_token_expiry",
      "message": "AssertionError: expected 401, got 200"
    },
    {
      "nodeid": "tests/api/test_health.py::test_ready_endpoint",
      "message": "ConnectionRefusedError: [Errno 111] Connection refused"
    }
  ],
  "command": "pytest --ignore=tests/evals/ -v"
}
```

**`passed` is `true` only when `failed_count == 0 AND error_count == 0`.**

### Step 5: Print summary

```
🧪 Existing tests: pytest --ignore=tests/evals/
   Total: 47  |  Passed: 47  |  Failed: 0
   Result: ✅ PASS
```

---

## Output Schema

```json
{
  "passed": true | false,
  "total": 47,
  "passed_count": 47,
  "failed_count": 0,
  "error_count": 0,
  "failures": [
    { "nodeid": "...", "message": "..." }
  ],
  "command": "pytest ..."
}
```

## Exit Behaviour

- Exit 0 when `passed == true`.
- Exit 1 when `passed == false`.
- Always write the result file.
