---
name: fix-failures
description: Read gate failure context from --failures-file and apply targeted fixes per gate type
---

# Fix Failures

Read gate failure context written by the harness and apply targeted fixes — one fix strategy per failed gate type. Write a fix summary to `.harness-results/fix-{attempt}.json` so the harness can log what was changed.

## Usage

```bash
# Called by the harness after a gate loop attempt fails
/fix-failures --failures-file .harness-results/failures-1.json

# Called with explicit attempt number
/fix-failures --failures-file .harness-results/failures-2.json --attempt 2
```

### Parameters

- `--failures-file <path>` (required): Path to the failures JSON written by the harness. Contains an array of `{ gate, outputs }` objects.
- `--attempt <n>`: Attempt number (default: 1). Used to name the fix summary file.

---

## Failures File Format

```json
[
  {
    "gate": "linter",
    "outputs": {
      "passed": false,
      "errors": ["src/foo.py:42: F401 'os' imported but unused"],
      "auto_fixed": 2,
      "remaining_errors": 1
    }
  },
  {
    "gate": "evals",
    "outputs": {
      "passed": false,
      "failures": [
        {
          "nodeid": "tests/evals/ABI-123/test_functional.py::test_rate_limit_enforced",
          "acceptance_criterion": "Rate limiting enforces 100 req/min",
          "message": "AssertionError: got 200 OK, expected 429"
        }
      ]
    }
  }
]
```

---

## Instructions

### Step 1: Read failures file

```bash
failures = JSON.parse(readFile(args['failures-file']))
```

### Step 2: Apply fixes in gate order

Process each failed gate in this order, regardless of the order they appear in the file:

**Order: linter → tests → evals → code-review**

#### Fix: linter

1. Read each error — note file path and line number.
2. Run auto-fix first:
   ```bash
   ruff check --fix .
   black .
   isort .
   ```
3. For errors that remain after auto-fix: read the file at the specified line, understand the issue, apply a targeted edit.
4. Record each fix in `fixes_applied`.

#### Fix: tests

1. For each failing test:
   a. Read the test file to understand what it expects.
   b. Read the implementation file(s) the test exercises.
   c. Determine: is the test correct and the implementation wrong, or did the implementation intentionally change behaviour?
   d. Fix the implementation. Do NOT delete tests.
   e. If the implementation intentionally changed behaviour (and it was approved in the plan), update the test assertion and add a comment explaining why.
2. Record each fix.

#### Fix: evals

1. For each failing eval:
   a. Read the eval test to extract the acceptance criterion.
   b. Read the implementation code that should satisfy it.
   c. Fix the implementation. **Never edit eval test files.**
   d. Record what was changed and why.
2. Do NOT modify eval tests under any circumstance.

#### Fix: code-review

1. For each blocker:
   a. Read `file` + `line` from the blocker object.
   b. Read the code at that location.
   c. Apply the fix described in `description`.
   d. Ignore suggestions — only fix blockers.
2. Record each fix.

### Step 3: Write fix summary

Write to `.harness-results/fix-{attempt}.json`:

```json
{
  "attempt": 1,
  "gates_addressed": ["linter", "evals"],
  "fixes_applied": [
    {
      "gate": "linter",
      "file": "src/foo.py",
      "line": 42,
      "description": "Removed unused 'os' import"
    },
    {
      "gate": "evals",
      "file": "src/api/rate_limiter.py",
      "description": "Fixed rate limit check to use per-minute window instead of per-second"
    }
  ],
  "files_modified": ["src/foo.py", "src/api/rate_limiter.py"],
  "skipped": [],
  "notes": "Linter auto-fix resolved 2 of 3 issues; 1 required manual edit."
}
```

### Step 4: Print summary

```
🔧 Fix attempt 1
   Gates addressed: linter, evals
   Fixes applied: 2
     - src/foo.py:42 — removed unused import [linter]
     - src/api/rate_limiter.py — fixed rate limit window [evals]
   Files modified: 2
```

---

## Output Schema

```json
{
  "attempt": 1,
  "gates_addressed": ["linter", "evals"],
  "fixes_applied": [
    {
      "gate": "linter | tests | evals | code-review",
      "file": "src/...",
      "line": 42,
      "description": "what was changed and why"
    }
  ],
  "files_modified": ["src/..."],
  "skipped": ["tests/evals/ABI-123/test_functional.py"],
  "notes": "optional free-text"
}
```

---

## Invariants

- **Never modify eval test files** — they encode acceptance criteria.
- **Never delete tests** — fix the implementation instead.
- **Fix blockers only** from the code-review gate — do not address suggestions.
- **Auto-fix before manual edit** for the linter gate.
- If a fix cannot be determined (e.g., a performance issue requires architectural input), log it in `skipped` and note the reason. The harness will surface it in the failure summary.
