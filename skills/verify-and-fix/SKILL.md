---
name: verify-and-fix
description: Run all verification gates (linter, existing tests, evals, code review) in a retry loop until everything passes or max attempts is reached
---

# Verify and Fix

Run a comprehensive, ordered verification loop that checks linter/static analysis, existing tests, new acceptance-criteria evals, and code review blockers — retrying with targeted fixes on each failure until all gates pass or the attempt limit is reached.

This is a **reusable primitive**. It is invoked by `/autonomous-implement` after implementation, but can also be called standalone at any point during development.

## When to Use This Skill

- After implementing a feature to verify everything is green before opening a PR
- As a standalone check on a work-in-progress branch
- From other skills that need a verified-clean state before proceeding (e.g., `/autonomous-sprint`, `/autonomous-implement`)

## Usage

```bash
# Full loop — all 4 gates, max 3 attempts
/verify-and-fix ABI-123

# Run only specific gates
/verify-and-fix ABI-123 --gates linter,tests

# Override retry limit
/verify-and-fix ABI-123 --max-attempts 5

# Skip eval gate (no evals generated yet)
/verify-and-fix ABI-123 --skip-evals
```

### Parameters

- `issue_key` (required): Jira issue key — used to locate eval tests at `tests/evals/{issueKey}/`
- `--gates <list>`: Comma-separated subset of gates to run: `linter`, `tests`, `evals`, `review`. Default: all four.
- `--max-attempts <n>`: Override retry limit. Default: `VERIFY_RETRY_LIMIT` env var (default 3).
- `--skip-evals`: Skip Gate 3 (eval tests). Implies only gates 1, 2, 4 run.

---

## Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│ attempt = 1 (max 3)                                         │
│                                                              │
│  Gate 1: Linter & Static Analysis                           │
│    ↓ PASS                                                    │
│  Gate 2: Existing Tests (full suite, no regressions)        │
│    ↓ PASS                                                    │
│  Gate 3: New Evals (tests/evals/{issueKey}/)                │
│    ↓ PASS                                                    │
│  Gate 4: Code Review Blockers Check                         │
│    ↓ PASS                                                    │
│  ALL PASS → return { passed: true, attempts: N }            │
│                                                              │
│  ANY FAIL → applyTargetedFixes(failures) → attempt++       │
│    └─ attempt > maxAttempts → return { passed: false, ... } │
└─────────────────────────────────────────────────────────────┘
```

**Gate order rationale:** Linter errors are cheapest to fix and can cause test failures (import errors, syntax errors). Regressions in existing tests must be resolved before running new evals to avoid false positives. Code review is the most expensive gate (spawns parallel agents), so it runs last — only when the fast gates are already green.

---

## Detailed Gate Specs

### Gate 1: Linter & Static Analysis

**What to run** (check project config first — `Makefile`, `pyproject.toml`, `package.json`, `.github/workflows/`):

```bash
# Python projects
make check        # if Makefile target exists
# or directly:
ruff check .
black --check .
isort --check-only .

# TypeScript/JavaScript projects
npm run lint
# or: eslint src/

# Go projects
golangci-lint run

# General
make lint         # if defined
```

**Auto-fix pass** (run before declaring failure):

```bash
# Python
ruff check --fix .
black .
isort .

# JS/TS
npm run lint -- --fix
eslint src/ --fix
```

**Gate passes when:** Zero linter errors (warnings are allowed but logged).

**Gate fails when:** Any linter error remains after the auto-fix pass.

---

### Gate 2: Existing Tests

**What to run:** The full existing test suite, excluding the new evals directory (`tests/evals/`).

```bash
# Python projects
make test                               # if Makefile target exists
pytest --ignore=tests/evals/ -v        # or directly
uv run pytest --ignore=tests/evals/ -v # if using uv

# JavaScript/TypeScript
npm test
npm run test:unit

# Go
go test ./...
```

**Gate passes when:** All pre-existing tests pass. New tests added as part of the implementation may fail here — treat them as implementation failures (fix the code, not the test).

**Gate fails when:** Any test that existed before this branch's changes is now failing (regression), OR any new test added during implementation is failing.

**Fix strategy:**
1. Read the failing test file and the implementation file it tests.
2. Determine: is the test correct and the implementation wrong, or did the implementation intentionally change behavior?
3. If regression: fix the implementation to restore correct behavior.
4. If intentional behavior change: update the test to match the new contract AND add a comment explaining why.
5. Do NOT delete tests to make them pass.

---

### Gate 3: New Evals (Acceptance Criteria Tests)

**What to run:** Only the evals generated for this issue.

```bash
pytest tests/evals/${issueKey}/ -v \
  --json-report \
  --json-report-file=.verify-and-fix-eval-results.json
```

**Gate passes when:** All eval tests pass (100%).

**Gate fails when:** Any eval test fails.

**Fix strategy:**
1. Read the failing eval test to understand which acceptance criterion it validates.
2. Read the implementation code that should satisfy the criterion.
3. Fix the implementation. Do NOT modify eval tests — they represent the acceptance criteria.
4. Re-run only the failing evals to confirm the fix before moving on.

**Parse results:**
```javascript
const results = JSON.parse(readFile('.verify-and-fix-eval-results.json'))
const summary = {
  total: results.summary.total,
  passed: results.summary.passed,
  failed: results.summary.failed,
  failedTests: results.tests.filter(t => t.outcome === 'failed').map(t => t.nodeid)
}
```

---

### Gate 4: Code Review Blockers Check

**What to run:** The `/code-review` skill scoped to the current branch diff. Extract only **Blockers** — suggestions and nits are ignored in the loop.

```bash
/code-review
```

Read the review output and filter for the `### Blockers` section. If the verdict is `Approve` or the Blockers section is empty, the gate passes.

**Gate passes when:** Verdict is `Approve` (no blockers), OR the Blockers section lists zero items.

**Gate fails when:** One or more blockers are listed (bugs, security issues, linter errors the code review agent found that Gate 1 missed, failing tests the review agent flagged).

**Fix strategy:**
1. Read each blocker: file path, line reference, and description.
2. Locate the file and line.
3. Apply the fix described in the blocker.
4. Do NOT address suggestions or nits — those go in the PR description for the human reviewer.

---

## Retry Loop — Full Logic

```javascript
const maxAttempts = parseInt(process.env.VERIFY_RETRY_LIMIT || '3')
const gates = parseGatesParam(args['gates']) || ['linter', 'tests', 'evals', 'review']

let attempt = 1
let allGateResults = []
const fixLog = []

while (attempt <= maxAttempts) {
  console.log(`\n🔄 Verification attempt ${attempt}/${maxAttempts}`)
  
  const gateResults = {}
  let failed = false
  
  // Run gates in order — stop at first failure to avoid noisy output
  // but still collect all failures before fixing
  
  if (gates.includes('linter')) {
    gateResults.linter = await runLinterGate()
    if (!gateResults.linter.passed) failed = true
  }
  
  if (gates.includes('tests')) {
    gateResults.existingTests = await runExistingTestsGate()
    if (!gateResults.existingTests.passed) failed = true
  }
  
  if (gates.includes('evals') && !args['skip-evals']) {
    gateResults.evals = await runEvalsGate(issueKey)
    if (!gateResults.evals.passed) failed = true
  }
  
  if (gates.includes('review')) {
    gateResults.codeReview = await runCodeReviewGate()
    if (!gateResults.codeReview.passed) failed = true
  }
  
  allGateResults.push({ attempt, ...gateResults })
  
  if (!failed) {
    return {
      passed: true,
      attempts: attempt,
      gateResults,
      fixesApplied: fixLog
    }
  }
  
  if (attempt < maxAttempts) {
    const fixes = await applyTargetedFixes(gateResults)
    fixLog.push(...fixes)
    attempt++
  } else {
    // Max attempts reached
    return {
      passed: false,
      attempts: attempt,
      gateResults,
      fixesApplied: fixLog,
      remainingFailures: collectFailures(gateResults)
    }
  }
}
```

---

## Fix Application — Targeted Per Gate

When one or more gates fail, apply fixes in gate order before retrying:

```javascript
async function applyTargetedFixes(gateResults) {
  const fixes = []

  if (gateResults.linter && !gateResults.linter.passed) {
    // 1. Run auto-fix commands
    // 2. For remaining errors: read error message, locate file:line, edit
    fixes.push(...await fixLinterErrors(gateResults.linter.errors))
  }

  if (gateResults.existingTests && !gateResults.existingTests.passed) {
    // 1. Read failing test + implementation
    // 2. Fix implementation (or update test if intentional change)
    fixes.push(...await fixTestFailures(gateResults.existingTests.failures))
  }

  if (gateResults.evals && !gateResults.evals.passed) {
    // 1. Map failing eval → acceptance criterion
    // 2. Fix implementation (never edit eval tests)
    fixes.push(...await fixEvalFailures(gateResults.evals.failedTests))
  }

  if (gateResults.codeReview && !gateResults.codeReview.passed) {
    // 1. Read each blocker's file:line
    // 2. Apply fix (ignore suggestions/nits)
    fixes.push(...await fixCodeReviewBlockers(gateResults.codeReview.blockers))
  }

  return fixes
}
```

---

## Output

### All Gates Pass

```markdown
✅ Verification passed on attempt 2/3

Gate Results:
  ✅ Linter: No errors (auto-fixed 3 warnings on attempt 1)
  ✅ Existing Tests: 47/47 passing
  ✅ Evals: 8/8 passing (tests/evals/ABI-123/)
  ✅ Code Review: Approve — no blockers

Fixes Applied (attempt 1):
  - Auto-fixed: ruff --fix removed 3 unused import warnings
  - Fixed: src/api/rate_limiter.py:42 — removed unreachable branch flagged by ruff

Ready to create PR.
```

### Max Attempts Reached

```markdown
⚠️ Verification failed after 3/3 attempts

Gate Results (final attempt):
  ✅ Linter: No errors
  ✅ Existing Tests: 47/47 passing
  ⚠️ Evals: 6/8 passing (2 failed)
    - test_concurrent_users_performance: latency exceeded threshold
    - test_rate_limit_reset: reset timer off by 1s
  ✅ Code Review: Approve — no blockers

Fixes Applied:
  - Attempt 1: Fixed linter errors (3 auto-fixed)
  - Attempt 2: Fixed test_rate_limit_reset — corrected timer math
  - Attempt 3: Adjusted connection pool size for throughput — test still fails

Remaining Failures:
  - test_concurrent_users_performance: needs architecture review

Recommendation: Create PR with [NEEDS-REVIEW] label. Human review needed for performance issue.
```

---

## Output Schema

```json
{
  "passed": true,
  "attempts": 2,
  "gateResults": {
    "linter": {
      "passed": true,
      "autoFixed": 3,
      "remainingErrors": 0
    },
    "existingTests": {
      "passed": true,
      "total": 47,
      "failures": []
    },
    "evals": {
      "passed": 8,
      "failed": 0,
      "total": 8,
      "failedTests": []
    },
    "codeReview": {
      "verdict": "Approve",
      "blockers": [],
      "suggestions": 2
    }
  },
  "fixesApplied": [
    "auto-fix: ruff removed 3 unused import warnings",
    "edit: src/api/rate_limiter.py:42 — removed unreachable branch"
  ]
}
```

---

## Configuration

```bash
VERIFY_RETRY_LIMIT=3       # Max full-loop attempts (default: 3)
VERIFY_GATES=linter,tests,evals,review  # Which gates to run (default: all)
EVAL_TIMEOUT=300           # Seconds before eval run times out (default: 300)
```

---

## Invariants

- **Never modify eval tests** to make them pass. Evals represent acceptance criteria.
- **Never delete existing tests** to remove failures. Fix the code instead.
- **Never skip blockers** from code review. Fix blockers; ignore suggestions and nits.
- **Auto-fix is always attempted first** for linter gate before manual edits.
- **Gate order is fixed**: linter → tests → evals → review. This order is not configurable.

---

## Integration with Other Skills

**Called by `/autonomous-implement`** after Step 6 (Implement):
```bash
/verify-and-fix ${issueKey}
# returns: { passed, attempts, gateResults, fixesApplied }
# if passed → proceed to /create-pr
# if !passed → create PR with [NEEDS-REVIEW] label, flag remaining failures
```

**Can also be called standalone** during development:
```bash
# After making changes, before committing
/verify-and-fix ABI-123

# Check only linter and tests (fast feedback)
/verify-and-fix ABI-123 --gates linter,tests

# Full verification before opening PR manually
/verify-and-fix ABI-123 --max-attempts 5
```
