---
name: run-evals
description: Run acceptance-criteria eval tests for a Jira issue and write a structured JSON result to --output
---

# Run Evals

Run the acceptance-criteria eval tests generated for a specific Jira issue (`tests/evals/{issueKey}/`). Write a structured JSON result to `--output` for the harness.

## Usage

```bash
# Called by the harness
/run-evals ABI-123 --output .harness-results/evals.json

# Standalone
/run-evals ABI-123
```

### Parameters

- `issue_key` (required): Jira issue key — used to locate `tests/evals/{issueKey}/`
- `--output <path>`: File path to write the JSON result.

---

## Instructions

### Step 1: Locate eval directory

```bash
eval_dir = "tests/evals/${issueKey}"

if not exists(eval_dir):
    # Write "no evals found" result and exit 0 (not a failure)
    write_result({
        "passed": true,
        "skipped": true,
        "reason": f"No eval directory found at {eval_dir}",
        "total": 0,
        "passed_count": 0,
        "failed_count": 0,
        "failures": []
    })
    exit(0)
```

### Step 2: Run evals

```bash
pytest tests/evals/${issueKey}/ -v \
  --json-report \
  --json-report-file=.harness-results/eval-report.json \
  2>&1
```

If `--json-report` is not available:

```bash
pytest tests/evals/${issueKey}/ -v 2>&1
```

### Step 3: Parse results

Same parsing logic as `/run-tests` — use JSON report if available, fall back to stdout parsing.

**Critical rule:** eval tests represent acceptance criteria. Their text is the ground truth.

```javascript
const failures = report.tests
  .filter(t => t.outcome === 'failed')
  .map(t => ({
    nodeid:            t.nodeid,
    acceptance_criterion: extractCriterion(t.nodeid),  // infer from test name
    message:           t.call?.longrepr || 'unknown',
  }))
```

### Step 4: Write JSON result to --output

```json
{
  "passed": true,
  "skipped": false,
  "issue_key": "ABI-123",
  "eval_dir": "tests/evals/ABI-123",
  "total": 8,
  "passed_count": 8,
  "failed_count": 0,
  "failures": [],
  "command": "pytest tests/evals/ABI-123/ -v"
}
```

Failure example:

```json
{
  "passed": false,
  "skipped": false,
  "issue_key": "ABI-123",
  "eval_dir": "tests/evals/ABI-123",
  "total": 8,
  "passed_count": 6,
  "failed_count": 2,
  "failures": [
    {
      "nodeid": "tests/evals/ABI-123/test_functional.py::test_rate_limit_enforced",
      "acceptance_criterion": "Rate limiting enforces 100 req/min",
      "message": "AssertionError: got 200 OK, expected 429 Too Many Requests"
    },
    {
      "nodeid": "tests/evals/ABI-123/test_performance.py::test_latency_under_10ms",
      "acceptance_criterion": "Latency < 10ms",
      "message": "AssertionError: mean latency 18.4ms > 10ms threshold"
    }
  ],
  "command": "pytest tests/evals/ABI-123/ -v"
}
```

**`passed` is `true` only when `failed_count == 0`.**

### Step 5: Print summary

```
🎯 Evals: tests/evals/ABI-123/ (8 tests)
   Total: 8  |  Passed: 8  |  Failed: 0
   Result: ✅ PASS
```

---

## Output Schema

```json
{
  "passed": true | false,
  "skipped": false,
  "issue_key": "ABI-123",
  "eval_dir": "tests/evals/ABI-123",
  "total": 8,
  "passed_count": 8,
  "failed_count": 0,
  "failures": [
    {
      "nodeid": "...",
      "acceptance_criterion": "...",
      "message": "..."
    }
  ],
  "command": "pytest tests/evals/ABI-123/ -v"
}
```

## Invariant

**Never modify eval tests.** If an eval fails, the fix belongs in the implementation, not in the test file.

## Exit Behaviour

- Exit 0 when `passed == true` (including the `skipped == true` case).
- Exit 1 when `passed == false`.
- Always write the result file.
