---
name: autonomous-implement
description: Autonomously implement Jira issue by composing existing skills with eval-based validation
---

# Autonomous Implement

Autonomously implement a Jira issue by composing existing skills: research → plan → generate evals → implement → validate → PR → update Jira.

## When to Use This Skill

Use this skill to:
- Fully implement a Jira issue autonomously
- Execute complete development cycle with eval validation
- Automate: spec → code → test → PR → Jira update
- Ensure acceptance criteria are met before PR creation

## Usage

```bash
# Implement single issue
/autonomous-implement ABI-123

# With repository knowledge context (from harness)
/autonomous-implement ABI-123 --context-file /tmp/knowledge_context.md

# With specific branch (if already created)
/autonomous-implement ABI-123 --branch story/ABI-123-api-rate-limiting

# Skip eval generation (use existing)
/autonomous-implement ABI-123 --skip-eval-gen

# Create PR even if evals fail (with warning label)
/autonomous-implement ABI-123 --force-pr

# Combined options
/autonomous-implement ABI-123 --context-file /tmp/context.md --branch feature/ABI-123

# With harness provenance tracking
/autonomous-implement ABI-123 --provenance-file .harness-results/provenance-events.jsonl
```

### Parameters

- `issue_key` (required): Jira issue key (e.g., 'ABI-123')
- `--context-file <path>`: Path to knowledge context file with repository architecture/patterns
- `--branch <name>`: Use existing branch instead of creating new one
- `--skip-eval-gen`: Skip evaluation generation step
- `--force-pr`: Create PR even if evaluations fail
- `--provenance-file <path>`: Path to JSONL file for appending structured progress events. Used by the harness to monitor live progress. If omitted, no events are written.

## Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Fetch Jira Issue                                         │
│    ↓                                                         │
│ 2. Create Branch from main/master (CRITICAL)                │
│    ↓                                                         │
│ 3. Research Codebase (/research-codebase)                   │
│    ↓                                                         │
│ 4. Create Plan (/create-plan)                               │
│    ↓                                                         │
│ 5. Generate Evals (/eval-generator)                         │
│    ↓                                                         │
│ 6. Implement (/implement-plan)                              │
│    ↓                                                         │
│ 7. Verify & Fix (/verify-and-fix) ← unified loop           │
│    ├─ Gate 1: Linter & static analysis                      │
│    ├─ Gate 2: Existing tests (no regressions)               │
│    ├─ Gate 3: New evals (acceptance criteria)               │
│    └─ Gate 4: Code review blockers check                    │
│    ├─ ALL PASS → Continue                                   │
│    └─ ANY FAIL → Fix → Retry (max 3 attempts)              │
│         ↓ (exhausted)                                        │
│         Create PR with [NEEDS-REVIEW] label                 │
│    ↓                                                         │
│ 8. Create PR (/create-pr)                                   │
│    ↓                                                         │
│ 9. Update Jira (/jira-update)                               │
└─────────────────────────────────────────────────────────────┘
```

## Knowledge Context Integration

When invoked by the **workspace harness**, this skill receives a knowledge context file containing:

### Context File Contents

```markdown
# Repository Knowledge Context

## Repository: runtime
**Language:** Python
**Build System:** poetry
**Test Framework:** pytest

## Architecture
[Repository architecture patterns and design decisions]

## Coding Patterns
[Common patterns used in this repository]

## Conventions
- Imports: absolute only
- Type hints: strict, all public APIs
- Docstrings: Google style

## Foundations Standards
### Air-Gapped Requirements (CRITICAL)
- NO cloud-specific APIs (GCP, AWS, Azure)
- Helm charts must deploy without cloud provider
...

### Definition of Done
1. 80% test coverage
2. gitleaks passes
3. Pacto contract valid
...
```

### Using Knowledge Context

If `--context-file` is provided:

1. **Read context file** at the start of implementation
2. **Extract key information**:
   - Repository architecture patterns
   - Coding conventions specific to this repo
   - Foundations requirements (air-gapped, DoD)
3. **Apply throughout implementation**:
   - Use architecture patterns in plan
   - Follow conventions in code
   - Validate against Foundations requirements
4. **Reference in commits/PRs**:
   - Mention compliance with standards
   - Note which patterns were followed

**Example:**
```bash
# When context file is provided:
/autonomous-implement ABI-123 --context-file /tmp/knowledge_context.md

# Skill reads context first, then proceeds with normal flow
# but uses repo-specific patterns and enforces standards
```

---

## Detailed Process

### Step 0: Load Knowledge Context (if provided)

If `--context-file` parameter is present:

```javascript
// Read knowledge context
const contextFile = args['context-file']
if (contextFile && fs.existsSync(contextFile)) {
  const context = fs.readFileSync(contextFile, 'utf-8')
  
  // Extract key sections
  const architecture = extractSection(context, 'Architecture')
  const patterns = extractSection(context, 'Coding Patterns')
  const conventions = extractSection(context, 'Conventions')
  const foundations = extractSection(context, 'Foundations Standards')
  
  // These will be referenced throughout implementation
  console.log('📚 Loaded repository knowledge context')
  console.log(`   Architecture: ${architecture.length} chars`)
  console.log(`   Patterns: ${patterns.length} chars`)
  console.log(`   Foundations: ${foundations.length} chars`)
}

// Parse provenance file path
const provenanceFile = args['provenance-file'] || null
```

---

### Provenance Helper (if --provenance-file provided)

Throughout this skill, append events to the provenance file after each major step.
Use the Write tool to append (read current content first, append new line, write back).
If the file does not exist yet, create it with the first event.

Event format — one JSON object per line, no trailing comma:

```json
{"event": "step_start", "step": "<name>", "timestamp": "<ISO8601>"}
{"event": "step_end", "step": "<name>", "success": true, "duration_ms": 12345, "output_preview": "<first 300 chars of output>"}
{"event": "gate", "gate": "<name>", "attempt": 1, "passed": true, "outputs": {}}
{"event": "fix_start", "attempt": 1, "timestamp": "<ISO8601>"}
{"event": "fix_end", "attempt": 1, "success": true, "duration_ms": 12345}
{"event": "run_complete", "outcome": "success", "pr_url": "https://...", "timestamp": "<ISO8601>"}
```

Steps to emit for: `fetch-issue`, `create-branch`, `research`, `plan`, `eval-gen`, `implement`,
each gate (`linter`, `tests`, `evals`, `code-review`), each fix attempt, and `create-pr`.

---

### Step 1: Fetch Jira Issue

> **Provenance:** If `--provenance-file` provided, append:
> `{"event": "step_start", "step": "fetch-issue", "timestamp": "<now ISO8601>"}`

Get issue details including acceptance criteria:

```javascript
const issue = await mcp__atlassian__jira_get_issue({
  issueKey: issueKey,
  fields: ['summary', 'description', 'issuetype', 'status', 'customfield_*']
})
```

Extract:
- Summary and description
- Acceptance criteria
- Linked issues/dependencies
- Current status
- Issue type (for branch naming)

> **Provenance:** Append:
> `{"event": "step_end", "step": "fetch-issue", "success": true, "duration_ms": <elapsed ms>, "output_preview": "<first 300 chars of issue summary/description>"}`

### Step 2: Create Branch from Main

> **Provenance:** If `--provenance-file` provided, append:
> `{"event": "step_start", "step": "create-branch", "timestamp": "<now ISO8601>"}`

**CRITICAL:** Always create new branch from main/master to avoid including unrelated changes.

**If --branch parameter NOT provided:**

```bash
# Fetch latest from remote
git fetch origin

# Switch to main branch (or master if main doesn't exist)
git checkout main || git checkout master

# Pull latest changes
git pull origin main || git pull origin master

# Create branch name from issue
# Format: {type}/{key}-{slug}
# Example: story/SEMI-1413-fix-wafer-processing
branchName=$(generate_branch_name issue)

# Create and checkout new branch from main
git checkout -b ${branchName}

# Verify we're on the new branch
git branch --show-current  # Should output: ${branchName}
```

**Branch naming convention:**

```javascript
function generateBranchName(issue) {
  const typeMap = {
    'Story': 'story',
    'Bug': 'bug', 
    'Task': 'task',
    'Epic': 'epic',
    'Sub-task': 'subtask'
  }
  
  const prefix = typeMap[issue.issuetype.name] || 'feature'
  const slug = issue.summary
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 50)
  
  return `${prefix}/${issue.key}-${slug}`
}
```

**If --branch parameter IS provided:**

```bash
# User specified existing branch, just checkout
git checkout ${providedBranchName}

# Verify we're on the correct branch
git branch --show-current
```

**Why this matters:**
- ✅ Clean branch from main = no unrelated changes in PR
- ✅ Predictable base for code review
- ✅ Avoids merge conflicts from stale branches
- ❌ Creating from current branch risks including WIP changes

> **Provenance:** Append:
> `{"event": "step_end", "step": "create-branch", "success": true, "duration_ms": <elapsed ms>, "output_preview": "<branch name created>"}`

### Step 3: Research Codebase

> **Provenance:** If `--provenance-file` provided, append:
> `{"event": "step_start", "step": "research", "timestamp": "<now ISO8601>"}`

Use existing `/research-codebase` skill to understand context:

```bash
/research-codebase "Research codebase for implementing ${issue.summary}. 
Find:
- Existing similar implementations
- Relevant files and patterns
- Dependencies and imports
- Test patterns and fixtures"
```

This provides:
- Existing code patterns to follow
- Files likely to change
- Test structure to match
- Potential conflicts or duplicates

> **Provenance:** Append:
> `{"event": "step_end", "step": "research", "success": true, "duration_ms": <elapsed ms>, "output_preview": "<first 300 chars of research output>"}`

### Step 4: Create Implementation Plan

> **Provenance:** If `--provenance-file` provided, append:
> `{"event": "step_start", "step": "plan", "timestamp": "<now ISO8601>"}`

Use existing `/create-plan` skill, **enriched with knowledge context if available**:

```bash
# If knowledge context loaded, inject into planning prompt:
/create-plan ${issueKey}

# Additional context for planner when knowledge available:
"Follow these repository-specific patterns:
${patterns}

Use this architecture approach:
${architecture}

Adhere to these conventions:
${conventions}

CRITICAL: Ensure air-gapped compatibility per Foundations standards:
${foundations}"
```

The plan should:
- Follow repository architecture patterns
- Use coding conventions specified in context
- Ensure Foundations requirements are met (air-gapped, test coverage, etc.)

Use existing `/create-plan` skill:

```bash
/create-plan ${issueKey}
```

Generates tech spec in `specs/features/${issueKey}.md`:
```markdown
# ABI-123: Add API Rate Limiting

## Overview
Implement API rate limiting using Redis...

## Files to Modify
- src/api/middleware/rate-limiter.ts (new)
- src/config/redis.ts (update)
- tests/api/test_rate_limiting.py (new)

## Implementation Steps
1. Set up Redis connection for rate limit storage
2. Create rate limiter middleware
3. Apply middleware to API routes
4. Add rate limit headers to responses
5. Implement test suite

## Dependencies
- redis npm package
- express-rate-limit middleware

## Testing Strategy
- Unit tests for rate limiter logic
- Integration tests for API endpoints
- Performance tests for latency
```

> **Provenance:** Append:
> `{"event": "step_end", "step": "plan", "success": true, "duration_ms": <elapsed ms>, "output_preview": "<first 300 chars of plan overview>"}`

### Step 5: Generate Evals from Acceptance Criteria

> **Provenance:** If `--provenance-file` provided, append:
> `{"event": "step_start", "step": "eval-gen", "timestamp": "<now ISO8601>"}`

Use `/eval-generator` to create validation tests:

```bash
/eval-generator ${issueKey}
```

Creates `tests/evals/${issueKey}/` with:
- `test_functional.py` - Functional acceptance tests
- `test_performance.py` - Performance benchmarks
- `test_quality.py` - Coverage and quality gates
- `conftest.py` - Test fixtures

> **Provenance:** Append:
> `{"event": "step_end", "step": "eval-gen", "success": true, "duration_ms": <elapsed ms>, "output_preview": "<first 300 chars listing generated eval files>"}`

### Step 6: Implement the Plan

> **Provenance:** If `--provenance-file` provided, append:
> `{"event": "step_start", "step": "implement", "timestamp": "<now ISO8601>"}`

Use existing `/implement-plan` skill:

```bash
/implement-plan specs/features/${issueKey}.md
```

Executes implementation:
- Creates/modifies files per spec
- Follows coding patterns from research
- Writes initial tests
- Updates documentation

> **Provenance:** Append:
> `{"event": "step_end", "step": "implement", "success": true, "duration_ms": <elapsed ms>, "output_preview": "<first 300 chars listing files created/modified>"}`

### Step 7: Verify & Fix

Invoke the `/verify-and-fix` skill. This runs all four verification gates in sequence, retrying with targeted fixes on each failure, up to 3 attempts:

```bash
/verify-and-fix ${issueKey}
```

The four gates (in order):
1. **Linter & static analysis** — auto-fix pass first, then manual edits for remaining errors
2. **Existing tests** — full suite excluding `tests/evals/`; no regressions allowed
3. **New evals** — acceptance-criteria tests in `tests/evals/${issueKey}/`
4. **Code review blockers** — parallel review agents; only blockers are fixed (nits ignored)

> **Provenance:** After each gate result, append:
> `{"event": "gate", "gate": "linter", "attempt": 1, "passed": true, "outputs": <gate JSON result>}`
>
> Use the actual gate name (`linter`, `tests`, `evals`, `code-review`) and current attempt number.
> Set `passed` to `true` if the gate passed, `false` if it failed. Include the gate's JSON result in `outputs`.

> **Provenance:** Before each fix invocation, append:
> `{"event": "fix_start", "attempt": 1, "timestamp": "<now ISO8601>"}`
>
> After each fix invocation completes, append:
> `{"event": "fix_end", "attempt": 1, "success": true, "duration_ms": <elapsed ms>}`
>
> Use the current attempt number (1-3). Set `success` to `true` if the fix resolved all remaining failures, `false` otherwise.

**On success** (all gates pass within 3 attempts): proceed to Step 8.

**On failure** (all 3 attempts exhausted with remaining failures):
- If `--force-pr` flag: create PR with `[NEEDS-REVIEW]` label and failure summary
- Otherwise: stop, report failures, ask human to intervene

See `/verify-and-fix` skill for full loop logic, fix strategies, and output schema.

### Step 8: Create Pull Request

> **Provenance:** If `--provenance-file` provided, append:
> `{"event": "step_start", "step": "create-pr", "timestamp": "<now ISO8601>"}`

If `/verify-and-fix` passes, use existing `/create-pr` skill:

```bash
/create-pr
```

PR description includes:
```markdown
## Summary
Implements API rate limiting with Redis backend

Closes ABI-123

## Implementation
- Added rate limiter middleware
- Configured Redis connection
- Applied rate limiting to all API endpoints
- Added rate limit headers to responses

## Verification Results
All gates passed after 2 attempts.

**Gate 1 — Linter:** ✅ No errors (auto-fixed 3 warnings on attempt 1)
**Gate 2 — Existing Tests:** ✅ 47/47 passing — no regressions
**Gate 3 — Evals (acceptance criteria):** ✅ 8/8 passed
  - ✓ Rate limiting enforces 100 req/min
  - ✓ Rate limit headers included
  - ✓ 429 status on limit exceeded
  - ✓ Rate limit resets correctly
  - ✓ Latency < 10ms
  - ✓ Handles 1000 concurrent users
  - ✓ Coverage 85% (target: 80%)
  - ✓ Security scan passed
**Gate 4 — Code Review:** ✅ Approve — no blockers

## Testing
\`\`\`bash
pytest tests/evals/ABI-123/ -v
\`\`\`
```

**If `/verify-and-fix` failed (and --force-pr used):**
- Add `[NEEDS-REVIEW]` label
- Include per-gate failure details in PR description
- List fixes applied across all attempts
- Request manual review for remaining failures

> **Provenance:** Append:
> `{"event": "step_end", "step": "create-pr", "success": true, "duration_ms": <elapsed ms>, "output_preview": "<PR URL and number>"}`

### Step 9: Update Jira

Use `/jira-update` to sync status:

```bash
/jira-update ${issueKey} \
  --pr-url ${prUrl} \
  --verification-passed ${verificationPassed} \
  --evals-passed ${evalsPassed} \
  --evals-total ${evalsTotal} \
  --status "In Review"
```

Adds comment to Jira:
```markdown
## Implementation Complete ✓

**Pull Request:** [PR #789](https://github.com/org/repo/pull/789)

**Verification Results (2 attempts):**
- ✅ Linter: No errors
- ✅ Existing Tests: 47/47
- ✅ Evals: 8/8 passed
- ✅ Code Review: Approve

All acceptance criteria validated through automated tests.

**Next Steps:**
- Merge after approval
```

> **Provenance:** After Step 9 completes (or after Step 8 if Step 9 is skipped), append the final event:
> `{"event": "run_complete", "outcome": "success", "pr_url": "<url or null>", "timestamp": "<now ISO8601>"}`
>
> Set `outcome` based on the run result:
> - `"success"` — all gates passed and PR was created
> - `"partial"` — gates failed but PR was still created (e.g. `--force-pr` used)
> - `"failed"` — no PR was created (gates failed without `--force-pr`, or a critical step errored)
>
> Set `pr_url` to the created PR URL, or `null` if no PR was created.

## Output

### Success Output

```markdown
✓ Successfully implemented ABI-123: Add API Rate Limiting

Timeline:
  ✓ Researched codebase (12s)
  ✓ Created implementation plan (45s)
  ✓ Generated evals (8s)
  ✓ Implemented solution (3m 24s)
  ✓ Verify & Fix — all gates passed on attempt 2/3 (1m 48s)
    ✓ Linter: No errors (auto-fixed 3 warnings on attempt 1)
    ✓ Existing tests: 47/47
    ✓ Evals: 8/8 passed
    ✓ Code review: Approve — no blockers
  ✓ Created PR #789 (5s)
  ✓ Updated Jira (3s)

Total time: 6 minutes 22 seconds

**Pull Request:** https://github.com/EmergenceAI/em-talk2data/pull/789
**Jira Issue:** https://company.atlassian.net/browse/ABI-123

Status: Ready for human review and merge
```

### Partial Success (Verification Failed)

```markdown
⚠ Partially implemented ABI-123: Add API Rate Limiting

Timeline:
  ✓ Researched codebase (12s)
  ✓ Created implementation plan (45s)
  ✓ Generated evals (8s)
  ✓ Implemented solution (3m 24s)
  ⚠ Verify & Fix — exhausted 3/3 attempts (4m 12s)
    ✓ Linter: No errors
    ✓ Existing tests: 47/47
    ⚠ Evals: 7/8 passed (1 failed)
    ✓ Code review: Approve — no blockers
  ✓ Created PR #789 with [NEEDS-REVIEW] label (5s)
  ✓ Updated Jira (3s)

Total time: 9 minutes 01 second

**Pull Request:** https://github.com/EmergenceAI/em-talk2data/pull/789
**Jira Issue:** https://company.atlassian.net/browse/ABI-123

**Remaining Failures:**
- Gate 3 (Evals): test_concurrent_users_performance — system degraded under 1000 users

Status: Needs human review to address remaining failures
```

### Failure (Cannot Proceed)

```markdown
✗ Failed to implement ABI-123: Add API Rate Limiting

Timeline:
  ✓ Researched codebase (12s)
  ✓ Created implementation plan (45s)
  ✓ Generated evals (8s)
  ✗ Implementation failed (error in middleware)

Error: Cannot import required Redis library

Recommendation:
1. Install missing dependency: npm install redis
2. Retry implementation: /autonomous-implement ABI-123

Or implement manually and run evals:
pytest tests/evals/ABI-123/ -v
```

## Output Schema

```json
{
  "issueKey": "ABI-123",
  "status": "success" | "partial" | "failed",
  "timeline": {
    "research": { "duration": 12, "status": "completed" },
    "plan": { "duration": 45, "status": "completed" },
    "evalGen": { "duration": 8, "status": "completed" },
    "implement": { "duration": 204, "status": "completed" },
    "verifyAndFix": {
      "duration": 108,
      "status": "completed",
      "passed": true,
      "attempts": 2,
      "gateResults": {
        "linter": { "passed": true, "autoFixed": 3, "remainingErrors": 0 },
        "existingTests": { "passed": true, "total": 47, "failures": [] },
        "evals": { "passed": 8, "failed": 0, "total": 8 },
        "codeReview": { "verdict": "Approve", "blockers": [] }
      }
    },
    "pr": {
      "duration": 5,
      "status": "completed",
      "number": 789,
      "url": "https://github.com/org/repo/pull/789"
    },
    "jiraUpdate": { "duration": 3, "status": "completed" }
  },
  "totalDuration": 385,
  "pr": {
    "number": 789,
    "url": "https://github.com/org/repo/pull/789",
    "status": "open"
  }
}
```

## Configuration

**Environment variables:**
```bash
# Jira
JIRA_URL=https://company.atlassian.net
JIRA_EMAIL=user@company.com
JIRA_API_TOKEN=xxx

# GitHub
GITHUB_TOKEN=ghp_xxx

# Verification loop settings (passed through to /verify-and-fix)
VERIFY_RETRY_LIMIT=3       # Max full-loop attempts (default: 3)
VERIFY_GATES=linter,tests,evals,review  # Gates to run (default: all)
EVAL_TIMEOUT=300           # Seconds before eval run times out (default: 300)
FORCE_PR_ON_EVAL_FAILURE=false  # Renamed from FORCE_PR_ON_EVAL_FAILURE; applies to any gate
```

**Skill-specific settings:**
```json
{
  "autonomous-implement": {
    "verifyRetryLimit": 3,
    "evalTimeout": 300,
    "forcePrOnFailure": false,
    "autoTransitionJira": true,
    "targetStatus": "In Review"
  }
}
```

## Error Handling

**Missing acceptance criteria:**
```
Warning: No acceptance criteria found for ABI-123

Proceeding without eval generation.
Implementation will be created but not validated.

Recommendation: Add acceptance criteria to Jira issue for validation.
```

**Implementation conflicts:**
```
Error: Git conflicts detected during implementation

Conflicts in:
- src/api/middleware/rate-limiter.ts

Recommendation:
1. Resolve conflicts manually
2. Retry: /autonomous-implement ABI-123
```

**Verification failures after max retries:**
```
Warning: /verify-and-fix exhausted 3 attempts with remaining failures

Failed gates (final attempt):
- Gate 3 (Evals): test_concurrent_users_performance — performance degradation
- (Gates 1, 2, 4 all passed)

Actions taken:
- Created PR #789 with [NEEDS-REVIEW] label
- Added per-gate failure details and all fixes applied to PR description
- Updated Jira with partial completion status

Next steps:
- Review performance issue manually
- Fix and re-run: /verify-and-fix ABI-123 --gates evals
- Update PR when passing
```

## Integration with Workflow

**Used by `/autonomous-sprint`:**
```javascript
// Parallel implementation of multiple issues
const results = await pipeline(
  issues,
  issue => agent(`Run /autonomous-implement ${issue.key}`, {
    label: `implement-${issue.key}`,
    isolation: 'worktree',
    schema: IMPLEMENTATION_RESULT_SCHEMA
  })
)
```

## Success Criteria

- [x] Composes existing skills correctly
- [x] Generates evals from acceptance criteria
- [x] Runs all 4 verification gates via `/verify-and-fix` before PR creation
- [x] Retries with targeted fixes on any gate failure (max 3 attempts)
- [x] Creates PR only when all gates pass (or with `[NEEDS-REVIEW]` label on failure)
- [x] Updates Jira with full verification context
- [x] Handles errors gracefully
- [x] Provides clear progress updates
- [x] Returns structured results

## Notes

**Autonomy level:**
- High autonomy: proceeds through all steps automatically
- Eval-gated: only creates PR if evals pass
- Escalation: alerts on failures after max retries

**Existing skills reused:**
- `/research-codebase` - Understanding context
- `/create-plan` - Tech spec generation
- `/implement-plan` - Code implementation
- `/verify-and-fix` - Comprehensive verification loop (linter + tests + evals + code review)
- `/create-pr` - PR creation

**New components:**
- `/eval-generator` - Test generation
- `/verify-and-fix` - Unified 4-gate retry loop (replaces inline eval-only retry + standalone code review step)
- `/jira-update` - Jira synchronization

**Performance:**
- Typical time: 3-8 minutes per issue
- Depends on complexity and codebase size
- Parallel execution via workflow for multiple issues
