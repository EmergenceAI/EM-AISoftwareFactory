# Multi-Agent Autonomous System - Simplified Design (Composing Existing Skills)

## Key Insight: Reuse Existing Skills

Instead of building new skills from scratch, we **compose existing skills** with new orchestration layers.

### Existing Skills We Can Leverage

| Existing Skill | Phase | How We Use It |
|---------------|-------|---------------|
| `/research-codebase` | Phase 2 (Audit) | Research existing implementations, find PRs, check for duplicates |
| `/create-plan` | Phase 4 (Implement) | Generate tech spec from Jira issue |
| `/implement-plan` | Phase 4 (Implement) | Execute the implementation plan |
| `/code-review` | Phase 5 (Review) | Automated code review of PR |
| `/create-pr` | Phase 4 (Implement) | Create PR after implementation |

### What's New to Build

Only **3 new skills** + **1 orchestration workflow**:

1. **`/jira-to-branches`** - Query Jira with JQL → create GitHub branches
2. **`/autonomous-implement`** - Compose: research → plan → implement → eval → PR
3. **`/jira-update`** - Update Jira issue with PR links and status
4. **Workflow: `autonomous-sprint`** - Orchestrate all phases with parallel agents

---

## Simplified Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            /autonomous-sprint (Workflow)                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
  ┌──────────┐      ┌──────────────┐
  │  NEW:    │      │   EXISTING:  │
  │ /jira-to │──────▶  /research-  │
  │ -branches│      │   codebase   │
  └──────────┘      └──────┬───────┘
                           │
                    ┌──────▼────────────────────────────┐
                    │  NEW: /autonomous-implement        │
                    │  (composes existing skills)        │
                    └──────┬────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐      ┌─────────┐
   │ Agent 1 │        │ Agent 2 │ ...  │ Agent N │
   └────┬────┘        └────┬────┘      └────┬────┘
        │                  │                 │
        ├─ /create-plan (existing)
        ├─ /implement-plan (existing)
        ├─ Run evals (new)
        ├─ /create-pr (existing)
        ├─ /code-review (existing)
        └─ /jira-update (new)
```

---

## Phase 1: Query Jira & Create Branches

### New Skill: `/jira-to-branches`

**Usage:**
```bash
# Using JQL
/jira-to-branches --jql "project = ABI AND sprint = 'Sprint 23' AND status = 'To Do'"

# Or using project + sprint
/jira-to-branches --project ABI --sprint "Sprint 23"
```

**What it does:**
1. Execute JQL query via MCP Atlassian
2. For each issue:
   ```javascript
   const branchName = `${issueType}/${issueKey}-${slugify(summary)}`
   // Example: "story/ABI-123-api-rate-limiting"
   ```
3. Create GitHub branch: `git checkout -b ${branchName}`
4. Push branch: `git push -u origin ${branchName}`
5. Update Jira issue with branch link (comment or custom field)

**Output:**
```json
{
  "issues": [
    {
      "key": "ABI-123",
      "summary": "Add API rate limiting",
      "branch": "story/ABI-123-api-rate-limiting",
      "type": "Story"
    },
    ...
  ]
}
```

**Implementation:**
```markdown
---
name: jira-to-branches
description: Query Jira issues with JQL and create GitHub branches for each
---

# Process

1. **Parse arguments:**
   - If `--jql` provided: use directly
   - If `--project` and `--sprint`: construct JQL: 
     `project = {project} AND sprint = '{sprint}' AND status IN ('To Do', 'In Progress')`

2. **Query Jira:**
   - Use MCP tool: `mcp__atlassian__jira_search_issues` with JQL
   - Extract: issue key, summary, type, description, acceptance criteria

3. **For each issue:**
   - Generate branch name: `{type}/{key}-{slug}`
   - Check if branch exists: `git branch -r | grep {branchName}`
   - If not exists:
     - Create branch: `git checkout -b {branchName}`
     - Push to GitHub: `git push -u origin {branchName}`
   - Update Jira with branch link via comment

4. **Return** list of issues with branch names
```

---

## Phase 2: Audit (Using Existing `/research-codebase`)

Instead of new skill, use **existing `/research-codebase`** to check:

```bash
# For each issue, research if already implemented
/research-codebase "Search for existing PRs or code for ABI-123"
```

**Better: Automated audit via workflow**

The workflow can automate this:
```javascript
phase('Audit')
const auditResults = await parallel(
  issues.map(issue => () => 
    agent(`Use /research-codebase to check if ${issue.key} is already implemented`, {
      label: `audit-${issue.key}`,
      schema: AUDIT_SCHEMA
    })
  )
)

const needsWork = auditResults
  .filter(r => r.status === 'not-implemented')
  .map(r => r.issue)
```

---

## Phase 3-7: Autonomous Implementation (Composing Existing Skills)

### New Skill: `/autonomous-implement`

This skill **composes existing skills** in sequence:

**Usage:**
```bash
/autonomous-implement ABI-123
```

**What it does:**
```javascript
// 1. Fetch Jira issue
const issue = await jira.getIssue('ABI-123')

// 2. Use existing /create-plan skill
const plan = await skill('create-plan', issue.key)

// 3. Use existing /implement-plan skill
const implementation = await skill('implement-plan', plan)

// 4. Run evals (NEW - extract from acceptance criteria)
const evalResults = await runEvals(issue.acceptanceCriteria)

// 5. If evals pass, use existing /create-pr skill
if (evalResults.passed) {
  const pr = await skill('create-pr')
  
  // 6. Use existing /code-review skill
  const review = await skill('code-review')
  
  // 7. Update Jira (NEW skill)
  await skill('jira-update', {
    issueKey: issue.key,
    prUrl: pr.url,
    evalResults: evalResults
  })
}
```

**Implementation:**
```markdown
---
name: autonomous-implement
description: Autonomous implementation of Jira issue using existing skills + evals
---

# Process

1. **Fetch Jira Issue:**
   - Use MCP: `mcp__atlassian__jira_get_issue`
   - Extract description, acceptance criteria, linked issues

2. **Create Plan (existing skill):**
   - Invoke: `/create-plan {issue.key}`
   - Generates tech spec in `specs/features/{issue.key}.md`

3. **Generate Evals from Acceptance Criteria:**
   - Parse acceptance criteria from Jira
   - Convert to executable test cases
   - Write to `tests/evals/{issue.key}/`

4. **Implement (existing skill):**
   - Invoke: `/implement-plan specs/features/{issue.key}.md`
   - Executes the implementation

5. **Run Evals:**
   - Execute: `pytest tests/evals/{issue.key}/ -v --json-report`
   - Check if all evals pass

6. **If evals pass:**
   - Commit changes
   - Invoke: `/create-pr`
   - Get PR URL

7. **Code Review (existing skill):**
   - Invoke: `/code-review`
   - Post review to PR

8. **Update Jira:**
   - Invoke: `/jira-update` with PR details
```

---

## Phase 7: Update Jira

### New Skill: `/jira-update`

**Usage:**
```bash
/jira-update ABI-123 --pr-url https://github.com/org/repo/pull/789 --status "In Review"
```

**What it does:**
1. Add comment to Jira issue with PR link
2. Update custom field "PR URL" (if exists)
3. Add eval results as comment
4. Transition issue status (optional)

**Implementation:**
```markdown
---
name: jira-update
description: Update Jira issue with PR links, eval results, and status
---

# Process

1. **Add PR Link Comment:**
   ```
   mcp__atlassian__jira_add_comment(
     issueKey: "ABI-123",
     comment: "Pull Request created: [PR #789](https://github.com/org/repo/pull/789)"
   )
   ```

2. **Add Eval Results:**
   ```
   mcp__atlassian__jira_add_comment(
     issueKey: "ABI-123",
     comment: "Eval Results: 5/5 passed ✓"
   )
   ```

3. **Update Status (optional):**
   ```
   mcp__atlassian__jira_transition_issue(
     issueKey: "ABI-123",
     transition: "In Review"
   )
   ```
```

---

## Orchestration Workflow: `/autonomous-sprint`

**Usage:**
```bash
# Using JQL
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND status = 'To Do'"

# Using project + sprint
/autonomous-sprint --project ABI --sprint "Sprint 23"
```

**Workflow Script:**
```javascript
export const meta = {
  name: 'autonomous-sprint',
  description: 'Autonomous multi-agent implementation of sprint issues',
  phases: [
    { title: 'Setup', detail: 'Query Jira and create branches' },
    { title: 'Audit', detail: 'Check for existing implementations' },
    { title: 'Implement', detail: 'Parallel autonomous implementation' }
  ]
}

// Parse args
const jql = args.jql || `project = ${args.project} AND sprint = '${args.sprint}' AND status IN ('To Do', 'In Progress')`

// Phase 1: Setup branches
phase('Setup')
log(`Querying Jira with: ${jql}`)
const issues = await agent(`Run /jira-to-branches --jql "${jql}"`, {
  label: 'jira-setup',
  schema: ISSUES_SCHEMA
})

log(`Found ${issues.length} issues. Creating branches...`)

// Phase 2: Audit (filter out completed work)
phase('Audit')
const auditResults = await parallel(
  issues.map(issue => () =>
    agent(`Use /research-codebase to check if ${issue.key} has existing PR or implementation`, {
      label: `audit-${issue.key}`,
      schema: AUDIT_SCHEMA
    })
  )
)

const needsWork = issues.filter((issue, i) => 
  auditResults[i]?.status === 'needs-implementation'
)

log(`${needsWork.length} issues need implementation. Skipping ${issues.length - needsWork.length} already completed.`)

// Phase 3: Parallel Implementation
phase('Implement')
const results = await pipeline(
  needsWork,
  // Each agent runs /autonomous-implement in isolated worktree
  issue => agent(`Run /autonomous-implement ${issue.key}`, {
    label: `implement-${issue.key}`,
    isolation: 'worktree',  // Isolated git worktree per agent
    schema: IMPLEMENTATION_RESULT_SCHEMA
  })
)

// Summary
const succeeded = results.filter(r => r?.status === 'success')
const failed = results.filter(r => r?.status === 'failed')

log(`Implementation complete: ${succeeded.length} succeeded, ${failed.length} failed`)

return {
  total: issues.length,
  needsWork: needsWork.length,
  succeeded: succeeded.length,
  failed: failed.length,
  results: results.filter(Boolean)
}
```

---

## JQL Examples

**All sprint issues:**
```sql
project = ABI AND sprint = 'Sprint 23'
```

**Only unstarted issues:**
```sql
project = ABI AND sprint = 'Sprint 23' AND status = 'To Do'
```

**By labels:**
```sql
project = ABI AND labels = M1 AND status IN ('To Do', 'In Progress')
```

**By priority:**
```sql
project = ABI AND priority = Critical AND status = 'To Do'
```

**Specific issues:**
```sql
key IN (ABI-123, ABI-124, ABI-125)
```

---

## Eval Framework (NEW Component)

### Acceptance Criteria Format in Jira

```markdown
## Acceptance Criteria

### Functional
- [ ] API rate limiting enforces 100 requests/minute per user
- [ ] Rate limit headers included in response
- [ ] 429 status code returned when limit exceeded

### Performance
- [ ] Rate limit check adds < 10ms latency

### Quality
- [ ] Unit test coverage ≥ 80%
```

### Auto-Generated Evals

The `/autonomous-implement` skill parses acceptance criteria and generates:

**`tests/evals/ABI-123/test_functional.py`:**
```python
def test_rate_limiting_enforces_limit():
    """API rate limiting enforces 100 requests/minute per user"""
    # Make 101 requests
    for i in range(101):
        response = client.get('/api', user='test')
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429

def test_rate_limit_headers():
    """Rate limit headers included in response"""
    response = client.get('/api')
    assert 'X-RateLimit-Remaining' in response.headers
    assert 'X-RateLimit-Reset' in response.headers
```

**`tests/evals/ABI-123/test_performance.py`:**
```python
def test_rate_limit_latency():
    """Rate limit check adds < 10ms latency"""
    start = time.time()
    response = client.get('/api')
    latency = time.time() - start
    assert latency < 0.010  # < 10ms
```

### Running Evals

```bash
# Run all evals for an issue
pytest tests/evals/ABI-123/ -v --json-report

# Just functional evals
pytest tests/evals/ABI-123/test_functional.py

# With coverage
pytest tests/evals/ABI-123/ --cov=src --cov-report=term
```

---

## What to Build (Priority Order)

### MVP (1-2 Days)

1. ✅ **Skill: `/jira-to-branches`** (2-3 hours)
   - Query Jira with JQL
   - Create GitHub branches
   - Update Jira with branch links

2. ✅ **Skill: `/jira-update`** (1 hour)
   - Update Jira with PR links
   - Add comments with eval results

3. ✅ **Eval Generator** (3-4 hours)
   - Parse acceptance criteria from Jira
   - Generate pytest test files
   - Run evals and capture results

4. ✅ **Skill: `/autonomous-implement`** (4-5 hours)
   - Compose existing skills
   - Add eval execution
   - Handle eval failures

### Test MVP (1 Day)

5. **Test with 1-2 sample issues**
   - Create Jira issues with acceptance criteria
   - Run `/autonomous-implement`
   - Verify evals work
   - Check PR creation

### Full System (2-3 Days)

6. ✅ **Workflow: `/autonomous-sprint`** (1 day)
   - Implement workflow script
   - Add parallel agent orchestration
   - Test with 5-10 issues

7. ✅ **Monitoring & Observability** (1 day)
   - Track agent success/failure rates
   - Log eval results
   - Report generation

---

## Advantages of This Approach

✅ **Reuses existing skills** - Only 3 new skills needed  
✅ **JQL flexibility** - Users can filter issues however they want  
✅ **Composable** - Each skill is independently useful  
✅ **Testable** - Can test individual skills before orchestration  
✅ **Maintainable** - Changes to existing skills automatically benefit the system  

---

## Configuration

**`.env` or settings:**
```bash
# Jira
JIRA_URL=https://company.atlassian.net
JIRA_EMAIL=user@company.com
JIRA_API_TOKEN=xxx

# GitHub
GITHUB_TOKEN=ghp_xxx
GITHUB_REPO=org/repo

# Multi-Agent
MAX_CONCURRENT_AGENTS=8
EVAL_TIMEOUT=300  # 5 minutes
AUTO_CREATE_PR=true
```

---

## Next Steps

1. ✅ Review this simplified design
2. Build `/jira-to-branches` skill
3. Build eval generator
4. Build `/autonomous-implement` skill (composing existing)
5. Test with sample issues
6. Build orchestration workflow
7. Production test with full sprint

This approach is **much simpler** because we reuse existing skills instead of rebuilding from scratch!
