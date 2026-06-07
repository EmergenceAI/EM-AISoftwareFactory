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

# With specific branch (if already created)
/autonomous-implement ABI-123 --branch story/ABI-123-api-rate-limiting

# Skip eval generation (use existing)
/autonomous-implement ABI-123 --skip-eval-gen

# Create PR even if evals fail (with warning label)
/autonomous-implement ABI-123 --force-pr
```

## Process Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Fetch Jira Issue                                     │
│    ↓                                                     │
│ 2. Research Codebase (existing /research-codebase)      │
│    ↓                                                     │
│ 3. Create Plan (existing /create-plan)                  │
│    ↓                                                     │
│ 4. Generate Evals (/eval-generator)                     │
│    ↓                                                     │
│ 5. Implement (existing /implement-plan)                 │
│    ↓                                                     │
│ 6. Run Evals (pytest)                                   │
│    ├─ PASS → Continue                                   │
│    └─ FAIL → Retry (max 3 attempts)                     │
│         ↓                                                │
│ 7. Create PR (existing /create-pr)                      │
│    ↓                                                     │
│ 8. Code Review (existing /code-review)                  │
│    ↓                                                     │
│ 9. Update Jira (/jira-update)                           │
└─────────────────────────────────────────────────────────┘
```

## Detailed Process

### Step 1: Fetch Jira Issue

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

### Step 2: Research Codebase

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

### Step 3: Create Implementation Plan

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

### Step 4: Generate Evals from Acceptance Criteria

Use `/eval-generator` to create validation tests:

```bash
/eval-generator ${issueKey}
```

Creates `tests/evals/${issueKey}/` with:
- `test_functional.py` - Functional acceptance tests
- `test_performance.py` - Performance benchmarks
- `test_quality.py` - Coverage and quality gates
- `conftest.py` - Test fixtures

### Step 5: Implement the Plan

Use existing `/implement-plan` skill:

```bash
/implement-plan specs/features/${issueKey}.md
```

Executes implementation:
- Creates/modifies files per spec
- Follows coding patterns from research
- Writes initial tests
- Updates documentation

### Step 6: Run Evals

Execute generated eval tests:

```bash
pytest tests/evals/${issueKey}/ -v --json-report --json-report-file=eval-results.json
```

**Parse results:**
```javascript
const evalResults = JSON.parse(readFile('eval-results.json'))

const summary = {
  total: evalResults.summary.total,
  passed: evalResults.summary.passed,
  failed: evalResults.summary.failed,
  duration: evalResults.summary.duration
}
```

**If evals fail:**
- Analyze failure reasons
- Attempt fixes (max 3 attempts)
- If still failing after 3 attempts:
  - Option A: Create PR with `[NEEDS-REVIEW]` label
  - Option B: Escalate to human

**Retry logic:**
```javascript
let attempt = 1
const maxAttempts = 3

while (attempt <= maxAttempts) {
  const results = await runEvals(issueKey)
  
  if (results.passed === results.total) {
    // All passed!
    break
  }
  
  if (attempt < maxAttempts) {
    // Analyze failures and fix
    await analyzeFai lures(results.failures)
    await applyFixes(results.failures)
    attempt++
  } else {
    // Max attempts reached
    throw new Error(`Evals failed after ${maxAttempts} attempts`)
  }
}
```

### Step 7: Create Pull Request

If evals pass, use existing `/create-pr` skill:

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

## Eval Results
✓ All acceptance criteria validated

**Functional Tests:** 4/4 passed
- ✓ Rate limiting enforces 100 req/min
- ✓ Rate limit headers included
- ✓ 429 status on limit exceeded
- ✓ Rate limit resets correctly

**Performance Tests:** 2/2 passed
- ✓ Latency < 10ms
- ✓ Handles 1000 concurrent users

**Quality Tests:** 2/2 passed
- ✓ Coverage 85% (target: 80%)
- ✓ Security scan passed

Total: 8/8 tests passed ✓

## Testing
\`\`\`bash
pytest tests/evals/ABI-123/ -v
\`\`\`
```

**If evals failed (and --force-pr used):**
- Add `[NEEDS-REVIEW]` label
- Include failure details in PR description
- Request manual review

### Step 8: Automated Code Review

Run existing `/code-review` skill on the PR:

```bash
/code-review
```

Posts review comments:
- Critical issues (bugs, security)
- Warnings (code smells, performance)
- Suggestions (style, readability)

### Step 9: Update Jira

Use `/jira-update` to sync status:

```bash
/jira-update ${issueKey} \
  --pr-url ${prUrl} \
  --evals-passed ${evalsPassed} \
  --evals-total ${evalsTotal} \
  --status "In Review"
```

Adds comment to Jira:
```markdown
## Implementation Complete ✓

**Pull Request:** [PR #789](https://github.com/org/repo/pull/789)

**Eval Results:** 8/8 passed ✓

All acceptance criteria validated through automated tests.

**Next Steps:**
- Code review in progress
- Merge after approval
```

## Output

### Success Output

```markdown
✓ Successfully implemented ABI-123: Add API Rate Limiting

Timeline:
  ✓ Researched codebase (12s)
  ✓ Created implementation plan (45s)
  ✓ Generated evals (8s)
  ✓ Implemented solution (3m 24s)
  ✓ Ran evals - 8/8 passed (15s)
  ✓ Created PR #789 (5s)
  ✓ Automated code review (22s)
  ✓ Updated Jira (3s)

Total time: 4 minutes 34 seconds

**Pull Request:** https://github.com/EmergenceAI/em-talk2data/pull/789
**Jira Issue:** https://company.atlassian.net/browse/ABI-123

Status: Ready for human review and merge
```

### Partial Success (Evals Failed)

```markdown
⚠ Partially implemented ABI-123: Add API Rate Limiting

Timeline:
  ✓ Researched codebase (12s)
  ✓ Created implementation plan (45s)
  ✓ Generated evals (8s)
  ✓ Implemented solution (3m 24s)
  ⚠ Ran evals - 6/8 passed (2 failed) (15s)
  ⚠ Retried fixes - 7/8 passed (1 failed) (1m 30s)
  ⚠ Max retry attempts reached
  ✓ Created PR #789 with [NEEDS-REVIEW] label (5s)
  ✓ Updated Jira (3s)

Total time: 6 minutes 22 seconds

**Pull Request:** https://github.com/EmergenceAI/em-talk2data/pull/789
**Jira Issue:** https://company.atlassian.net/browse/ABI-123

**Failed Evals:**
- test_concurrent_users_performance: System degraded under 1000 users

Status: Needs human review to address eval failures
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
    "evals": { 
      "duration": 15, 
      "status": "completed",
      "passed": 8,
      "failed": 0,
      "total": 8
    },
    "pr": { 
      "duration": 5, 
      "status": "completed",
      "number": 789,
      "url": "https://github.com/org/repo/pull/789"
    },
    "review": { "duration": 22, "status": "completed" },
    "jiraUpdate": { "duration": 3, "status": "completed" }
  },
  "totalDuration": 274,
  "pr": {
    "number": 789,
    "url": "https://github.com/org/repo/pull/789",
    "status": "open"
  },
  "evalResults": {
    "passed": 8,
    "failed": 0,
    "total": 8,
    "categories": {
      "functional": { "passed": 4, "total": 4 },
      "performance": { "passed": 2, "total": 2 },
      "quality": { "passed": 2, "total": 2 }
    }
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

# Eval settings
EVAL_RETRY_LIMIT=3
EVAL_TIMEOUT=300  # 5 minutes
FORCE_PR_ON_EVAL_FAILURE=false
```

**Skill-specific settings:**
```json
{
  "autonomous-implement": {
    "maxRetries": 3,
    "evalTimeout": 300,
    "forcePrOnFailure": false,
    "skipCodeReview": false,
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

**Eval failures after max retries:**
```
Warning: Evals failed after 3 attempts

Failed tests:
- test_concurrent_users_performance (performance degradation)

Actions taken:
- Created PR #789 with [NEEDS-REVIEW] label
- Added failure details to PR description
- Updated Jira with partial completion status

Next steps:
- Review performance issue manually
- Fix and re-run evals
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
- [x] Generates and validates evals
- [x] Retries on eval failures
- [x] Creates PR only when evals pass (or with warning)
- [x] Updates Jira with full context
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
- `/create-pr` - PR creation
- `/code-review` - Automated review

**New components:**
- `/eval-generator` - Test generation
- Eval execution - pytest runner
- `/jira-update` - Jira synchronization
- Retry logic - Automated fix attempts

**Performance:**
- Typical time: 3-8 minutes per issue
- Depends on complexity and codebase size
- Parallel execution via workflow for multiple issues
