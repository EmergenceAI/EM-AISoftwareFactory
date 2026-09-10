---
name: run-linter
description: Run linter and static analysis on changed files; write structured JSON result to --output file
---

# Run Linter

Run linter and static analysis on the current branch's changed files. Write a structured JSON result to the path specified by `--output` so the harness can read pass/fail deterministically.

## Usage

```bash
# Called by the harness — always provide --output
/run-linter --output .harness-results/linter.json

# Standalone (omit --output to just print results)
/run-linter
```

### Parameters

- `--output <path>`: File path to write the JSON result. Required when called by the harness.

---

## Instructions

### Step 1: Detect project type and linter command

Check `Makefile`, `pyproject.toml`, `package.json`, `.github/workflows/` in that order.

```bash
# Python — check for make target first
if Makefile has "check" or "lint" target:
    make check   # or make lint
else:
    ruff check .
    black --check .
    isort --check-only .

# JavaScript / TypeScript
npm run lint
# or: eslint src/ --max-warnings=0

# Go
golangci-lint run

# Catch-all
make lint   # if defined
```

### Step 2: Auto-fix pass (Python only)

Before recording failures, attempt auto-fix:

```bash
ruff check --fix .
black .
isort .
```

Re-run the linter after auto-fix to measure what remains.

### Step 3: Collect results

Parse linter output:

```
errors  = lines matching ERROR or error-level diagnostics
warnings = lines matching WARNING (allowed — do not block)
auto_fixed = count of issues resolved by the auto-fix pass
remaining_errors = count of errors after auto-fix
```

### Step 4: Write JSON result to --output

Write the result file **before** printing anything to stdout.

```json
{
  "passed": true,
  "tool": "ruff + black + isort",
  "auto_fixed": 3,
  "remaining_errors": 0,
  "remaining_warnings": 2,
  "errors": [],
  "warnings": [
    "src/foo.py:12: line too long (121 > 120)"
  ]
}
```

**`passed` is `true` only when `remaining_errors == 0`.** Warnings do not block.

Failure example:

```json
{
  "passed": false,
  "tool": "ruff + black + isort",
  "auto_fixed": 2,
  "remaining_errors": 1,
  "remaining_warnings": 0,
  "errors": [
    "src/api/handler.py:42: F401 'os' imported but unused"
  ],
  "warnings": []
}
```

### Step 5: Print summary to stdout

```
🔍 Linter: ruff + black + isort
   Auto-fixed: 3 issues
   Errors: 0  |  Warnings: 2
   Result: ✅ PASS
```

---

## Output Schema

```json
{
  "passed": true | false,
  "tool": "string — linter(s) used",
  "auto_fixed": 0,
  "remaining_errors": 0,
  "remaining_warnings": 0,
  "errors": ["file:line: code message", ...],
  "warnings": ["file:line: code message", ...]
}
```

## Exit Behaviour

- Exit 0 when `passed == true` (harness reads exit code as secondary signal).
- Exit 1 when `passed == false`.
- Always write the result file even on failure.
