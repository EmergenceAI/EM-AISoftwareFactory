---
name: run-code-review
description: Run a focused code review for blockers only and write a structured JSON result to --output
---

# Run Code Review

Run a focused parallel code review on the current branch diff, extracting only **blockers** (bugs, security issues, linter errors, failing tests). Write a structured JSON result to `--output` for the harness.

This is a harness-optimised variant of `/code-review`. Suggestions and nits are collected but do not affect the `passed` verdict.

## Usage

```bash
# Called by the harness
/run-code-review --output .harness-results/code-review.json

# Standalone (prints full review, no output file)
/run-code-review
```

### Parameters

- `--output <path>`: File path to write the JSON result.

---

## Instructions

### Step 1: Determine diff scope

```bash
# On a feature branch — review all changes vs main
git diff main...HEAD

# On main — review staged changes
git diff --staged

# Fallback — latest commit
git show HEAD
```

### Step 2: Assess diff size and launch parallel agents

**Small diff** (≤100 lines / ≤3 files): launch agents 1–4 only.
**Medium/large diff** (>100 lines or >3 files): launch all agents.

Launch in a single parallel call:

- **Agent 1 — Test & Linter Runner**: run tests and linter for changed files; report failures
- **Agent 2 — Code Reviewer**: up to 5 issues ranked by impact; focus on bugs and incorrect logic
- **Agent 3 — Security Reviewer**: injection, auth, secrets, error-handling leaks
- **Agent 4 — Quality Reviewer**: complexity, dead code, architectural pattern violations
- **Agent 5 — Performance Reviewer** *(large diff only)*: N+1, blocking ops, memory leaks
- **Agent 6 — Dependency Reviewer** *(large diff only)*: new deps, API contract breaks, deployment safety

### Step 3: Triage findings into blockers vs suggestions

**Blockers** (anything that must be fixed before merge):
- Bugs or logic errors that fail in production
- Security vulnerabilities with a realistic exploit path
- Linter errors (not warnings)
- Failing tests surfaced by Agent 1
- Clear architectural violations from the project style guide

**Suggestions**: everything else (style, minor performance, nice-to-haves).

### Step 4: Write JSON result to --output

```json
{
  "passed": true,
  "verdict": "Approve",
  "blockers": [],
  "suggestions": [
    {
      "severity": "MED",
      "category": "quality",
      "title": "Redundant null check",
      "file": "src/api/handler.py",
      "line": 88,
      "description": "Variable is never null at this point — check is dead code."
    }
  ],
  "agents_run": ["test-runner", "code-reviewer", "security-reviewer", "quality-reviewer"],
  "diff_stats": { "files_changed": 3, "lines_added": 87, "lines_removed": 12 }
}
```

Failure example:

```json
{
  "passed": false,
  "verdict": "Needs Work",
  "blockers": [
    {
      "severity": "HIGH",
      "category": "security",
      "title": "SQL injection via unsanitised input",
      "file": "src/db/queries.py",
      "line": 34,
      "description": "user_id is interpolated directly into the SQL string. Use parameterised queries."
    },
    {
      "severity": "HIGH",
      "category": "correctness",
      "title": "Off-by-one in pagination",
      "file": "src/api/list.py",
      "line": 71,
      "description": "offset = page * limit should be offset = (page - 1) * limit; page 1 skips first item."
    }
  ],
  "suggestions": [],
  "agents_run": ["test-runner", "code-reviewer", "security-reviewer", "quality-reviewer"],
  "diff_stats": { "files_changed": 5, "lines_added": 210, "lines_removed": 45 }
}
```

**`passed` is `true` only when `blockers` is empty.**

### Step 5: Print summary

```
🔎 Code review (4 agents)
   Blockers: 0  |  Suggestions: 1
   Verdict: ✅ Approve
```

---

## Output Schema

```json
{
  "passed": true | false,
  "verdict": "Approve | Needs Work",
  "blockers": [
    {
      "severity": "HIGH | MED | LOW",
      "category": "security | correctness | performance | quality",
      "title": "...",
      "file": "src/...",
      "line": 42,
      "description": "..."
    }
  ],
  "suggestions": [ ... ],
  "agents_run": ["..."],
  "diff_stats": { "files_changed": 0, "lines_added": 0, "lines_removed": 0 }
}
```

## Calibration

- **Only blockers affect `passed`** — suggestions are recorded but don't gate the loop.
- Calibrate severity as a senior engineer would: internal tooling, controlled inputs, and low-blast-radius code get lower severity than user-facing authentication or payment flows.
- Do not include nits or style preferences in blockers.

## Exit Behaviour

- Exit 0 when `passed == true`.
- Exit 1 when `passed == false`.
- Always write the result file.
