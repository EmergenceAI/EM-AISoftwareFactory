---
name: jira-update
description: Update Jira issue with PR links, eval results, implementation notes, and status transitions
---

# Jira Update

Update Jira issues with implementation details including PR links, eval results, implementation summary, and status transitions.

## When to Use This Skill

Use this skill to:
- Link PR to Jira issue after implementation
- Record eval test results in Jira
- Add implementation notes and tech spec links
- Transition issue status (e.g., "To Do" → "In Review")
- Keep Jira in sync with implementation progress

## Usage

```bash
# Basic: Add PR link
/jira-update ABI-123 --pr-url https://github.com/org/repo/pull/789

# With eval results
/jira-update ABI-123 --pr-url https://github.com/org/repo/pull/789 --evals-passed 5 --evals-total 5

# With status transition
/jira-update ABI-123 --pr-url https://github.com/org/repo/pull/789 --status "In Review"

# Full update with all details
/jira-update ABI-123 \
  --pr-url https://github.com/org/repo/pull/789 \
  --evals-passed 5 \
  --evals-total 5 \
  --status "In Review" \
  --notes "Implemented with automated evals. All acceptance criteria met."
```

## Process

### Step 1: Fetch Issue Details

Get current issue information:

```javascript
const issue = await mcp__atlassian__jira_get_issue({
  issueKey: issueKey,
  fields: ['status', 'summary', 'customfield_*']
})
```

### Step 2: Build Update Comment

Create formatted comment with implementation details:

```markdown
## Implementation Complete ✓

**Pull Request:** [PR #{pr_number}]({pr_url})

**Eval Results:** {evals_passed}/{evals_total} passed ✓

**Implementation Notes:**
{notes}

**Files Changed:**
- {file1}
- {file2}

**Tech Spec:** [specs/features/{issue-key}.md](link)

---
*Updated automatically by autonomous-implement*
```

**Example:**
```markdown
## Implementation Complete ✓

**Pull Request:** [PR #789](https://github.com/EmergenceAI/em-talk2data/pull/789)

**Eval Results:** 5/5 passed ✓

**Implementation Notes:**
Implemented API rate limiting with Redis backend. All acceptance criteria validated through automated evals.

**Files Changed:**
- src/api/middleware/rate-limiter.ts
- src/config/redis.ts
- tests/evals/ABI-123/test_rate_limiting.py

**Tech Spec:** [specs/features/ABI-123.md](https://github.com/EmergenceAI/em-talk2data/blob/main/specs/features/ABI-123.md)

---
*Updated automatically by autonomous-implement*
```

### Step 3: Add Comment to Jira

Post the formatted comment:

```javascript
await mcp__atlassian__jira_add_comment({
  issueKey: issueKey,
  comment: formattedComment
})
```

### Step 4: Update Custom Fields (if available)

If custom fields exist, update them:

**PR URL field:**
```javascript
if (customFieldPRUrl) {
  await mcp__atlassian__jira_update_issue({
    issueKey: issueKey,
    fields: {
      [customFieldPRUrl]: pr_url
    }
  })
}
```

**Eval Results field:**
```javascript
if (customFieldEvalResults) {
  await mcp__atlassian__jira_update_issue({
    issueKey: issueKey,
    fields: {
      [customFieldEvalResults]: `${evals_passed}/${evals_total}`
    }
  })
}
```

### Step 5: Transition Status (if requested)

If `--status` provided, transition the issue:

```javascript
// Get available transitions
const transitions = await mcp__atlassian__jira_get_transitions({
  issueKey: issueKey
})

// Find matching transition
const transition = transitions.find(t => 
  t.name === requestedStatus || 
  t.to.name === requestedStatus
)

if (transition) {
  await mcp__atlassian__jira_transition_issue({
    issueKey: issueKey,
    transition: transition.id
  })
}
```

**Common transitions:**
- "To Do" → "In Progress"
- "In Progress" → "In Review"
- "In Review" → "Done"
- "In Review" → "To Do" (if changes needed)

### Step 6: Output Confirmation

Return summary of updates:

```markdown
Updated ABI-123: Add API rate limiting

✓ Added PR link: https://github.com/EmergenceAI/em-talk2data/pull/789
✓ Recorded eval results: 5/5 passed
✓ Added implementation notes
✓ Transitioned status: In Progress → In Review

View issue: https://company.atlassian.net/browse/ABI-123
```

## Output Schema

```json
{
  "issueKey": "ABI-123",
  "updated": true,
  "updates": {
    "comment": true,
    "prUrl": "https://github.com/EmergenceAI/em-talk2data/pull/789",
    "evalResults": "5/5",
    "status": "In Review"
  },
  "jiraUrl": "https://company.atlassian.net/browse/ABI-123"
}
```

## Arguments

### Required

**`issue-key`** - Jira issue key (e.g., "ABI-123")

### Optional

**`--pr-url`** - GitHub pull request URL
- Example: `https://github.com/org/repo/pull/789`
- Extracted PR number automatically

**`--pr-number`** - GitHub PR number (alternative to --pr-url)
- Example: `789`
- Constructs URL from current repo

**`--evals-passed`** - Number of eval tests that passed
- Example: `5`
- Used with `--evals-total`

**`--evals-total`** - Total number of eval tests
- Example: `5`
- Displays as "5/5 passed ✓"

**`--evals-failed`** - Number of eval tests that failed
- Example: `0`
- Displays failure summary if > 0

**`--status`** - Target status for transition
- Example: `"In Review"`, `"Done"`, `"In Progress"`
- Must match available transition in Jira

**`--notes`** - Implementation notes (markdown supported)
- Example: `"Implemented with Redis backend. All criteria met."`

**`--spec-url`** - Link to tech spec
- Example: `https://github.com/org/repo/blob/main/specs/features/ABI-123.md`

**`--files-changed`** - Comma-separated list of changed files
- Example: `"src/api/rate-limiter.ts,tests/test_rate_limit.py"`

## Eval Results Formatting

**All passed:**
```
✓ Eval Results: 5/5 passed

All acceptance criteria validated through automated tests.
```

**Some failed:**
```
⚠ Eval Results: 3/5 passed (2 failed)

Failed tests:
- test_rate_limit_performance: Expected < 10ms, got 15ms
- test_concurrent_users: Failed under load

Review failures and re-run evals after fixes.
```

**With details:**
```
✓ Eval Results: 5/5 passed

Functional Tests: 3/3 ✓
- test_rate_limiting_enforces_limit ✓
- test_rate_limit_headers ✓  
- test_429_status_code ✓

Performance Tests: 2/2 ✓
- test_rate_limit_latency ✓
- test_concurrent_requests ✓
```

## Status Transitions

**Common workflows:**

**Standard development flow:**
```
To Do → In Progress → In Review → Done
```

**If changes needed:**
```
In Review → In Progress → In Review
```

**If blocked:**
```
In Progress → Blocked → In Progress
```

The skill will:
1. Check available transitions for current status
2. Find transition matching requested status
3. Execute transition
4. Report success or error if transition not available

## Error Handling

**Issue not found:**
```
Error: Issue ABI-999 not found

Check:
- Issue key is correct
- You have access to the issue
- Issue is in the correct Jira project
```

**PR URL invalid:**
```
Error: Invalid PR URL format

Expected: https://github.com/org/repo/pull/{number}
Got: {provided_url}
```

**Status transition not available:**
```
Error: Cannot transition to "Done"

Available transitions from "To Do":
- In Progress
- Blocked
- Cancelled

Current status must be "In Review" to transition to "Done"
```

**Jira API error:**
```
Error: Failed to update issue ABI-123

Details: {error_message}

Check:
- JIRA_API_TOKEN is valid
- You have edit permissions on this issue
```

## Examples

### Example 1: Basic PR Link

```bash
/jira-update ABI-123 --pr-url https://github.com/EmergenceAI/em-talk2data/pull/789
```

**Result:**
```
Updated ABI-123: Add API rate limiting

✓ Added PR link: https://github.com/EmergenceAI/em-talk2data/pull/789

View issue: https://company.atlassian.net/browse/ABI-123
```

### Example 2: PR Link + Eval Results

```bash
/jira-update ABI-123 \
  --pr-url https://github.com/EmergenceAI/em-talk2data/pull/789 \
  --evals-passed 5 \
  --evals-total 5
```

**Result:**
```
Updated ABI-123: Add API rate limiting

✓ Added PR link
✓ Recorded eval results: 5/5 passed ✓

All acceptance criteria validated through automated tests.
```

### Example 3: Full Update with Status Transition

```bash
/jira-update ABI-123 \
  --pr-url https://github.com/EmergenceAI/em-talk2data/pull/789 \
  --evals-passed 5 \
  --evals-total 5 \
  --status "In Review" \
  --notes "Implemented API rate limiting with Redis. All evals passed."
```

**Result:**
```
Updated ABI-123: Add API rate limiting

✓ Added PR link
✓ Recorded eval results: 5/5 passed
✓ Added implementation notes  
✓ Transitioned status: In Progress → In Review

PR is ready for review. All acceptance criteria met.
```

### Example 4: Failed Evals

```bash
/jira-update ABI-123 \
  --pr-url https://github.com/EmergenceAI/em-talk2data/pull/789 \
  --evals-passed 3 \
  --evals-total 5 \
  --evals-failed 2 \
  --notes "Performance evals failed. Needs optimization."
```

**Result:**
```
Updated ABI-123: Add API rate limiting

✓ Added PR link
⚠ Recorded eval results: 3/5 passed (2 failed)

PR created with [NEEDS-REVIEW] label due to eval failures.
Manual review required before merge.
```

## Integration with Other Skills

**Used by `/autonomous-implement`:**
```javascript
// After creating PR
const pr = await skill('create-pr')
const evalResults = await runEvals(issue)

// Update Jira with results
await skill('jira-update', {
  issueKey: issue.key,
  prUrl: pr.url,
  evalsPassed: evalResults.passed,
  evalsTotal: evalResults.total,
  status: 'In Review'
})
```

**Manual workflow:**
```bash
# 1. Implement feature
/implement-plan specs/features/ABI-123.md

# 2. Create PR
/create-pr

# 3. Update Jira
/jira-update ABI-123 --pr-url https://github.com/org/repo/pull/789 --status "In Review"
```

## Configuration

**Required environment variables:**
```bash
JIRA_URL=https://company.atlassian.net
JIRA_EMAIL=user@company.com
JIRA_API_TOKEN=xxx
```

**Optional custom fields:**
- `customfield_xxxxx` for PR URL
- `customfield_yyyyy` for Eval Results

If custom fields are configured, the skill will populate them automatically.

## Success Criteria

- [x] Adds formatted comment with PR link and eval results
- [x] Updates custom fields if available
- [x] Transitions issue status if requested
- [x] Handles eval failures gracefully
- [x] Provides clear error messages
- [x] Returns structured output
- [x] Works with any Jira project

## Notes

**Comment formatting:**
- Uses markdown for rich formatting in Jira
- Includes clickable PR links
- Visual indicators (✓, ⚠, ✗) for status
- Auto-generated timestamp and attribution

**Status transitions:**
- Only transitions if target status is reachable
- Validates transition is available from current status
- Reports available transitions if requested one is invalid

**Performance:**
- Typical update time: 1-2 seconds
- Multiple API calls batched where possible
- Retries on transient failures
