# Multi-Agent Autonomous System Design

## Vision

Enable autonomous, parallel implementation of Jira sprint tickets with eval-based acceptance criteria, automated PR creation, and minimal human intervention.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                          │
│  (/autonomous-sprint orchestrator - workflow-based)             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
  ┌──────────┐      ┌──────────────┐
  │  Phase 1 │      │   Phase 2    │
  │  Plan    │──────▶   Audit      │
  └──────────┘      └──────┬───────┘
                           │
                    ┌──────▼────────────────────────────┐
                    │       Phase 3: Work                │
                    │  Spawn N Parallel Agent Instances  │
                    └──────┬────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐      ┌─────────┐
   │ Agent 1 │        │ Agent 2 │ ...  │ Agent N │
   │ Issue A │        │ Issue B │      │ Issue N │
   └────┬────┘        └────┬────┘      └────┬────┘
        │                  │                 │
        ▼                  ▼                 ▼
   Phase 4: Implement → Eval → PR
        │                  │                 │
        ▼                  ▼                 ▼
   Phase 5: Review → Phase 6: Fix → Phase 7: Sync
```

## Phase Breakdown

### Phase 1: Sprint Branch Setup (`/sprint-branch-setup`)

**Input:**
- Jira project key (e.g., "ABI")
- Sprint name or ID
- GitHub repository

**Process:**
1. Query Jira for all active sprint issues (via MCP Atlassian)
2. For each issue:
   - Extract issue key, type, summary
   - Generate standardized branch name: `{type}/{issue-key}-{slug}`
     - Example: `feature/ABI-123-api-rate-limiting`
   - Create branch in GitHub (via `gh` CLI or GitHub API)
   - Update Jira issue with branch link (custom field or comment)
3. Return list of issues with branches

**Output:**
```json
[
  {
    "issueKey": "ABI-123",
    "summary": "API Rate Limiting",
    "branch": "feature/ABI-123-api-rate-limiting",
    "type": "Story",
    "status": "In Progress"
  },
  ...
]
```

**Dependencies:**
- MCP Atlassian (Jira)
- GitHub CLI (`gh`) or GitHub API via MCP
- Git repository access

---

### Phase 2: Codebase Audit (`/codebase-audit`)

**Input:**
- List of issues from Phase 1
- Repository path
- Optional: external audit findings 

**Process:**
1. For each issue:
   - Search for existing PRs mentioning issue key (via `gh pr list`)
   - Check if branch already has commits
   - Grep codebase for issue key references
   - Check if issue is already closed/resolved in Jira
2. Filter out issues that:
   - Already have merged PRs
   - Already have open PRs in review
   - Are marked as completed in Jira
3. Return filtered list of issues needing implementation

**Output:**
```json
{
  "needsWork": [
    {"issueKey": "ABI-123", "reason": "No PR exists"},
    {"issueKey": "ABI-125", "reason": "PR was rejected, needs rework"}
  ],
  "skipReasons": {
    "ABI-124": "Already has open PR #456",
    "ABI-126": "Already merged in PR #450"
  }
}
```

**Dependencies:**
- GitHub CLI (`gh`)
- Git repository
- MCP Atlassian (Jira status check)

---

### Phase 3: Worktree Orchestrator (`/worktree-orchestrator`)

**Input:**
- Filtered list of issues from Phase 2
- Max concurrent agents (default: CPU cores - 2)

**Process:**
1. For each issue:
   - Create isolated git worktree: `.claude/worktrees/{issue-key}`
   - Checkout the issue's branch in worktree
2. Spawn Claude agent instances (one per worktree)
   - Use Claude Code `--plugin-dir` for each agent
   - Pass issue key and worktree path as context
   - Configure agent to run Phase 4 (autonomous-implement)
3. Manage agent lifecycle:
   - Track agent status (running, completed, failed)
   - Monitor resource usage
   - Handle agent failures and retries

**Output:**
```json
{
  "agents": [
    {
      "agentId": "agent-abi-123",
      "issueKey": "ABI-123",
      "worktree": ".claude/worktrees/ABI-123",
      "status": "running",
      "pid": 12345
    },
    ...
  ]
}
```

**Implementation:**
- Use Claude Code Workflow tool for orchestration
- Each agent runs in isolated worktree (via `EnterWorktree`)
- Agent spawning uses `Agent` tool with isolation: 'worktree'

---

### Phase 4: Autonomous Implementation (`/autonomous-implement`)

**Input:**
- Jira issue key
- Worktree path
- Context files (CLAUDE.md, related docs)

**Process:**
1. **Read Issue:**
   - Fetch Jira issue details (description, acceptance criteria, comments)
   - Read linked context documents
   - Identify eval criteria from acceptance criteria

2. **Generate Tech Spec:**
   - Create implementation plan
   - Identify files to modify
   - Define eval test cases from acceptance criteria
   - Write spec to `specs/features/{issue-key}.md`

3. **Implement Solution:**
   - Execute implementation plan
   - Write code following spec
   - Create/update tests

4. **Run Evals:**
   - Execute eval tests defined in acceptance criteria
   - Validate implementation meets requirements
   - Retry on failures (max 3 attempts)

5. **Create PR (if evals pass):**
   - Commit changes with descriptive message
   - Push branch to GitHub
   - Create PR via `gh pr create`
   - Link PR to Jira issue
   - Add eval results to PR description

**Output:**
```json
{
  "issueKey": "ABI-123",
  "status": "success",
  "pr": {
    "number": 789,
    "url": "https://github.com/org/repo/pull/789",
    "title": "feat(ABI-123): Add API rate limiting"
  },
  "evalResults": {
    "passed": 5,
    "failed": 0,
    "total": 5
  }
}
```

**Eval Framework:**
- Acceptance criteria in Jira must include testable conditions
- Evals can be:
  - Unit tests
  - Integration tests
  - Performance benchmarks
  - API contract tests
  - Manual verification steps (converted to automated tests)

**Escalation:**
- If evals fail after 3 attempts → create PR with `[NEEDS-REVIEW]` label
- If unable to generate spec → escalate to human
- If critical errors → halt and notify

---

### Phase 5: PR Review Agent (`/pr-review-agent`)

**Input:**
- PR number or URL
- Repository

**Process:**
1. Fetch PR details via `gh pr view`
2. Run automated code review (use existing `/code-review` skill)
3. Generate review comments:
   - **Critical**: Bugs, security issues, breaking changes
   - **Warning**: Code smells, performance concerns
   - **Suggestion**: Style, readability improvements
4. Post inline comments to GitHub PR via `gh pr review`
5. Add overall verdict comment with summary

**Output:**
```json
{
  "pr": 789,
  "verdict": "APPROVED" | "REQUEST_CHANGES" | "COMMENT",
  "findings": {
    "critical": 0,
    "warning": 2,
    "suggestion": 5
  }
}
```

**Dependencies:**
- GitHub CLI (`gh pr review`)
- Existing `/code-review` skill

---

### Phase 6: PR Fix Agent (`/pr-fix-agent`)

**Input:**
- PR number
- Repository

**Process:**
1. Fetch all unresolved PR review comments via `gh pr view --json comments`
2. Filter comments by type:
   - Critical → must fix
   - Warning → should fix
   - Suggestion → optional fix
3. For each comment:
   - Understand the issue
   - Apply fix in code
   - Mark comment as resolved (if applicable)
4. Run evals again to ensure fixes don't break acceptance
5. Push updated branch
6. Post comment: "Applied fixes for review comments. Re-running evals..."

**Output:**
```json
{
  "pr": 789,
  "commentsAddressed": 7,
  "commentsRemaining": 0,
  "evalsPassed": true,
  "commitHash": "abc123"
}
```

**Dependencies:**
- GitHub CLI
- Worktree access
- Eval framework

---

### Phase 7: Jira Sync Agent (`/jira-sync-agent`)

**Input:**
- Issue key
- PR details
- Implementation summary
- Eval results

**Process:**
1. Update Jira issue:
   - Add comment with implementation summary
   - Add PR link
   - Update custom field: "PR URL"
   - Add eval results as comment
   - Update status (e.g., "In Review" if PR created)
2. Optionally attach implementation notes:
   - Tech spec location
   - Files changed
   - Test coverage

**Output:**
```json
{
  "issueKey": "ABI-123",
  "updated": true,
  "status": "In Review",
  "prLinked": true
}
```

**Dependencies:**
- MCP Atlassian (Jira)

---

## Orchestration Workflow

### Main Workflow: `/autonomous-sprint`

**Usage:**
```bash
/autonomous-sprint --project ABI --sprint "Sprint 23"
```

**Workflow Script:**
```javascript
export const meta = {
  name: 'autonomous-sprint',
  description: 'Autonomous multi-agent implementation of sprint issues',
  phases: [
    { title: 'Plan', detail: 'Setup branches for sprint issues' },
    { title: 'Audit', detail: 'Filter out completed work' },
    { title: 'Spawn', detail: 'Create agent worktrees' },
    { title: 'Implement', detail: 'Parallel autonomous implementation' },
    { title: 'Review', detail: 'Automated PR reviews' },
    { title: 'Fix', detail: 'Apply review feedback' },
    { title: 'Sync', detail: 'Update Jira status' }
  ]
}

// Phase 1: Plan
phase('Plan')
const issues = await agent('Run /sprint-branch-setup for project ABI sprint "Sprint 23"', {
  label: 'sprint-setup',
  schema: ISSUES_SCHEMA
})

// Phase 2: Audit
phase('Audit')
const filtered = await agent('Run /codebase-audit on issues', {
  label: 'audit',
  schema: FILTERED_ISSUES_SCHEMA
})

// Phase 3-7: Parallel Implementation
phase('Implement')
const results = await pipeline(
  filtered.needsWork,
  // Phase 3: Spawn worktree and Phase 4: Implement
  issue => agent(`Implement ${issue.issueKey} with evals`, {
    label: `implement-${issue.issueKey}`,
    isolation: 'worktree',
    schema: IMPLEMENTATION_RESULT_SCHEMA
  }),
  // Phase 5: Review
  result => result.pr ? agent(`Review PR ${result.pr.number}`, {
    label: `review-${result.issueKey}`,
    schema: REVIEW_RESULT_SCHEMA
  }) : null,
  // Phase 6: Fix (if needed)
  review => review && review.verdict === 'REQUEST_CHANGES' ? 
    agent(`Fix PR ${review.pr} based on comments`, {
      label: `fix-${review.pr}`,
      schema: FIX_RESULT_SCHEMA
    }) : review,
  // Phase 7: Sync
  finalResult => agent(`Update Jira ${finalResult.issueKey}`, {
    label: `sync-${finalResult.issueKey}`,
    schema: SYNC_RESULT_SCHEMA
  })
)

return {
  total: issues.length,
  implemented: results.filter(r => r.status === 'success').length,
  failed: results.filter(r => r.status === 'failed').length,
  results
}
```

---

## Eval Framework Design

### Acceptance Criteria Format in Jira

Jira issues must include structured acceptance criteria that can be converted to automated evals.

**Example:**

```markdown
## Acceptance Criteria

### Functional
- [ ] API rate limiting enforces 100 requests/minute per user
- [ ] Rate limit headers included in response (X-RateLimit-Remaining, X-RateLimit-Reset)
- [ ] 429 status code returned when limit exceeded

### Performance
- [ ] Rate limit check adds < 10ms latency to API calls
- [ ] System handles 1000 concurrent users without degradation

### Quality
- [ ] Unit test coverage ≥ 80%
- [ ] Integration tests validate rate limiting behavior
- [ ] No security vulnerabilities (passed Snyk scan)
```

### Eval Test Generation

The autonomous-implement agent converts acceptance criteria into executable tests:

**Functional Eval:**
```python
def test_rate_limiting_enforces_limit():
    # Make 101 requests as same user
    for i in range(101):
        response = api_client.get('/endpoint', user='test-user')
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
```

**Performance Eval:**
```python
def test_rate_limit_latency():
    start = time.time()
    response = api_client.get('/endpoint')
    latency = time.time() - start
    assert latency < 0.010  # < 10ms
```

### Eval Execution

Evals run in CI/CD pipeline and locally:

```bash
# Run all evals for issue
pytest tests/evals/ABI-123/ -v

# Performance evals
pytest tests/evals/ABI-123/performance/ --benchmark

# Integration evals
pytest tests/evals/ABI-123/integration/
```

### Eval Results Format

```json
{
  "issueKey": "ABI-123",
  "evalsPassed": true,
  "results": [
    {
      "name": "test_rate_limiting_enforces_limit",
      "status": "passed",
      "duration": "0.5s"
    },
    {
      "name": "test_rate_limit_latency",
      "status": "passed",
      "duration": "0.1s",
      "metric": "8.5ms"
    }
  ],
  "coverage": {
    "line": 85,
    "branch": 78
  }
}
```

---

## Configuration

### Environment Variables

```bash
# Jira
export JIRA_URL=https://company.atlassian.net
export JIRA_EMAIL=user@company.com
export JIRA_API_TOKEN=xxx
export JIRA_PROJECT_KEY=ABI

# GitHub
export GITHUB_TOKEN=ghp_xxx
export GITHUB_REPO=org/repo

# Multi-Agent Config
export MAX_CONCURRENT_AGENTS=8
export EVAL_RETRY_LIMIT=3
export AUTO_FIX_ENABLED=true
```

### Skills Configuration

Each skill will be in `skills/` directory:
- `skills/sprint-branch-setup/`
- `skills/codebase-audit/`
- `skills/worktree-orchestrator/`
- `skills/autonomous-implement/`
- `skills/pr-review-agent/`
- `skills/pr-fix-agent/`
- `skills/jira-sync-agent/`

### Workflow Configuration

Main orchestration workflow in `workflows/autonomous-sprint.js`

---

## Success Metrics

### System Performance
- Time to implement issue: < 30 minutes average
- Eval pass rate: ≥ 90% first attempt
- PR review findings: < 3 critical issues average
- Auto-fix success rate: ≥ 80%

### Quality Metrics
- Code coverage: ≥ 80% for implemented code
- Security scan pass rate: 100%
- Integration test pass rate: ≥ 95%

### Autonomy Metrics
- Human intervention rate: < 10% of issues
- Escalation reasons tracked
- Agent success rate by issue type

---

## Implementation Phases

### MVP (Phase 1-4 only)
1. Implement Phases 1-2 (Plan + Audit) as standalone skills
2. Implement Phase 4 (Autonomous Implement) with basic eval support
3. Manual PR review
4. Manual Jira updates

### Full Automation (All Phases)
1. Implement Phase 3 (Worktree Orchestrator)
2. Implement Phases 5-7 (Review, Fix, Sync)
3. End-to-end orchestration workflow
4. Monitoring and observability

### Advanced Features
1. Learning from past implementations
2. Smart retry strategies
3. Cross-issue dependency detection
4. Automatic spec improvement based on feedback

---

## Risk Mitigation

### Technical Risks
- **Agent failures**: Isolated worktrees prevent cross-contamination
- **Eval flakiness**: Retry logic + flakiness detection
- **Resource exhaustion**: Max concurrent agents limit
- **Code quality**: Automated review + eval gates

### Process Risks
- **Missing context**: Agents escalate when uncertain
- **Breaking changes**: Evals catch regressions
- **Security issues**: Automated security scans in eval
- **Human oversight**: Summary reports + escalation on failures

---

## Next Steps

1. ✅ Create this design document
2. Create skill: `/sprint-branch-setup`
3. Create skill: `/codebase-audit`
4. Create skill: `/autonomous-implement` (MVP)
5. Test MVP with 1-2 sample issues
6. Implement remaining skills (5-7)
7. Build orchestration workflow
8. Production testing with full sprint

---

## References

- ADO Multi-Agent Reference (adapted for Jira/GitHub)
- Claude Code Workflow Documentation
- Eval-Based Development Best Practices
