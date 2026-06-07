# Autonomous Sprint Workflows

## Overview

Workflow scripts for autonomous implementation of Jira sprint issues using Claude Code's Workflow orchestration.

## Available Workflows

### `/autonomous-sprint` - Main Orchestrator

Autonomously implements multiple Jira issues in parallel with eval-based validation.

**Location:** `autonomous-sprint.js`

**Usage:**
```bash
# By JQL
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Talk2Data'"

# By project + sprint
/autonomous-sprint --project ABI --sprint "Sprint 23" --component "Talk2Data"

# Specific issues
/autonomous-sprint --jql "key IN (ABI-123, ABI-124, ABI-125)"

# Dry run (preview only)
/autonomous-sprint --project ABI --sprint "Sprint 23" --dry-run

# Control concurrency
/autonomous-sprint --project ABI --sprint "Sprint 23" --max-concurrent 4
```

**What It Does:**

1. **Setup Phase:**
   - Queries Jira with JQL
   - Creates GitHub branches for each issue
   - Updates Jira with branch links

2. **Audit Phase:**
   - Checks for existing implementations
   - Filters out issues with PRs or completed work
   - Reports what will be skipped

3. **Implement Phase:**
   - Spawns parallel agents (one per issue)
   - Each agent runs in isolated git worktree
   - Autonomous implementation with eval validation
   - Creates PRs only if evals pass
   - Updates Jira with results

**Output:**
```
AUTONOMOUS SPRINT COMPLETE
==========================================================

Total Issues: 10
  Implemented: 7 ✓
  Partial: 2 ⚠
  Failed: 1 ✗
  Skipped: 0 (already done)

Eval Results: 45/50 passed
Total Duration: 28 minutes

✓ Successful Implementations:
  ABI-123: https://github.com/org/repo/pull/789
    Evals: 5/5 passed
  ABI-124: https://github.com/org/repo/pull/790
    Evals: 8/8 passed
  ...

⚠ Partial Implementations (needs review):
  ABI-130: https://github.com/org/repo/pull/796 [NEEDS-REVIEW]
    Evals: 3/5 passed
    Failed: 2 tests

Next Steps:
  1. Review PRs for successful implementations
  2. Address eval failures for partial implementations
  3. Investigate and retry failed implementations
```

## Workflow Architecture

```
autonomous-sprint.js
│
├─ Phase 1: Setup
│  └─ /jira-to-branches
│     ├─ Query Jira (MCP)
│     ├─ Create branches (git)
│     └─ Update Jira (MCP)
│
├─ Phase 2: Audit
│  └─ Parallel /research-codebase
│     ├─ Check for existing PRs
│     ├─ Check for implementations
│     └─ Filter needs-work list
│
└─ Phase 3: Implement (Parallel Pipeline)
   └─ For each issue (in isolated worktree):
      ├─ /autonomous-implement
      │  ├─ Fetch Jira issue
      │  ├─ /research-codebase
      │  ├─ /create-plan
      │  ├─ /eval-generator
      │  ├─ /implement-plan
      │  ├─ Run evals (pytest)
      │  ├─ /create-pr (if evals pass)
      │  ├─ /code-review
      │  └─ /jira-update
      └─ Return results
```

## Configuration

### Environment Variables

```bash
# Jira (required)
JIRA_URL=https://company.atlassian.net
JIRA_EMAIL=user@company.com
JIRA_API_TOKEN=xxx

# GitHub (required)
GITHUB_TOKEN=ghp_xxx

# Workflow settings (optional)
MAX_CONCURRENT_AGENTS=8
EVAL_RETRY_LIMIT=3
EVAL_TIMEOUT=300
FORCE_PR_ON_EVAL_FAILURE=false
```

### Workflow Parameters

**`--jql`** (string)
- JQL query for selecting issues
- Example: `"project = ABI AND sprint = 'Sprint 23'"`

**`--project`** (string)
- Jira project key (alternative to --jql)
- Example: `ABI`

**`--sprint`** (string)
- Sprint name (used with --project)
- Example: `"Sprint 23"`

**`--component`** (string, optional)
- Jira component filter
- Example: `"Talk2Data"`

**`--max-concurrent`** (number, default: 8)
- Maximum parallel agent executions
- Example: `4` for slower machines or `16` for powerful servers

**`--dry-run`** (boolean, default: false)
- Preview what would be done without making changes
- Example: `--dry-run`

**`--include-all`** (boolean, default: false)
- Include issues in any status (not just To Do/In Progress)
- Example: `--include-all`

## Running Workflows

### From Repository

```bash
# Navigate to repository
cd ~/Documents/Development/em-talk2data

# Launch Claude with plugin
claude --plugin-dir .claude/plugins/em-software-factory

# Run workflow
/autonomous-sprint --project ABI --sprint "Sprint 23" --component "Talk2Data"
```

### Testing with Dry Run

```bash
# See what would happen without making changes
/autonomous-sprint --project ABI --sprint "Sprint 23" --dry-run

# Output shows:
# - Which issues would be selected
# - Which branches would be created
# - Which issues would be skipped
# - No actual changes made
```

### Controlling Concurrency

```bash
# Conservative (4 parallel agents)
/autonomous-sprint --project ABI --sprint "Sprint 23" --max-concurrent 4

# Aggressive (16 parallel agents - requires powerful machine)
/autonomous-sprint --project ABI --sprint "Sprint 23" --max-concurrent 16
```

## Workflow Output

### Success Case

All issues implemented successfully with passing evals:

```json
{
  "status": "success",
  "totalIssues": 5,
  "results": {
    "succeeded": 5,
    "partial": 0,
    "failed": 0,
    "skipped": 0
  },
  "evals": {
    "passed": 25,
    "total": 25,
    "rate": 100
  },
  "duration": {
    "totalSeconds": 1200,
    "totalMinutes": 20,
    "averagePerIssue": 240
  },
  "prs": [
    {
      "issueKey": "ABI-123",
      "prNumber": 789,
      "prUrl": "https://github.com/org/repo/pull/789",
      "status": "success"
    },
    ...
  ]
}
```

### Partial Success

Some issues succeeded, some had eval failures:

```json
{
  "status": "partial",
  "totalIssues": 5,
  "results": {
    "succeeded": 3,
    "partial": 2,
    "failed": 0,
    "skipped": 0
  },
  "evals": {
    "passed": 20,
    "total": 25,
    "rate": 80
  },
  "duration": {
    "totalSeconds": 1500,
    "totalMinutes": 25,
    "averagePerIssue": 300
  }
}
```

## Performance Characteristics

### Timing Estimates

**Per Issue (average):**
- Research: 10-15 seconds
- Plan creation: 30-60 seconds
- Eval generation: 5-10 seconds
- Implementation: 2-5 minutes
- Eval execution: 10-30 seconds
- PR creation: 5-10 seconds
- Code review: 15-30 seconds
- Jira update: 2-5 seconds

**Total per issue:** 3-7 minutes (depending on complexity)

**Parallel speedup:**
- 5 issues sequential: 15-35 minutes
- 5 issues parallel (5 agents): 3-7 minutes
- 10 issues parallel (8 agents): 4-9 minutes

### Resource Usage

**CPU:**
- Each agent is CPU-intensive during implementation
- Recommend max concurrent = CPU cores - 2

**Memory:**
- Each agent: ~200-500 MB
- 8 agents: ~2-4 GB total
- Monitor system resources

**Network:**
- Jira API calls (setup + per issue)
- GitHub API calls (per issue)
- Git push operations (per issue)

## Error Handling

### Common Errors

**No issues found:**
```
No issues found matching JQL query

Check:
- JQL syntax is correct
- Project key exists
- Sprint name is exact match
- You have access to the issues
```

**Git conflicts:**
```
Error: Git conflicts in issue ABI-123

Conflicts occur when:
- Another agent modified same files
- Manual changes in working tree

Resolution:
- Resolve conflicts manually
- Retry: /autonomous-implement ABI-123
```

**Eval failures:**
```
Warning: Evals failed for ABI-123 after 3 attempts

Options:
1. PR created with [NEEDS-REVIEW] label
2. Review eval failures manually
3. Fix and re-run evals
```

### Recovery Strategies

**Partial workflow failure:**
```bash
# Check which issues succeeded
git branch -r | grep "ABI-"

# Retry failed issues individually
/autonomous-implement ABI-125
/autonomous-implement ABI-126
```

**Resource exhaustion:**
```bash
# Reduce concurrency
/autonomous-sprint --project ABI --sprint "Sprint 23" --max-concurrent 2

# Or process in batches
/autonomous-sprint --jql "key IN (ABI-123, ABI-124, ABI-125)"
# Wait for completion, then:
/autonomous-sprint --jql "key IN (ABI-126, ABI-127, ABI-128)"
```

## Best Practices

### Before Running

1. **Clean working tree:**
   ```bash
   git status  # Should be clean
   git pull origin main
   ```

2. **Test with dry run:**
   ```bash
   /autonomous-sprint --project ABI --sprint "Sprint 23" --dry-run
   ```

3. **Start with small batch:**
   ```bash
   # Test with 2-3 issues first
   /autonomous-sprint --jql "key IN (ABI-123, ABI-124)"
   ```

### During Execution

1. **Monitor progress:**
   - Use `/workflows` command to see live status
   - Check system resources (CPU, memory)
   - Watch for error messages

2. **Don't interrupt:**
   - Let workflow complete
   - Interrupting may leave partial work
   - Use Ctrl+C only if necessary

### After Completion

1. **Review PRs:**
   - Check eval results
   - Review code changes
   - Merge approved PRs

2. **Address failures:**
   - Investigate partial implementations
   - Fix eval failures manually
   - Retry failed issues

3. **Update Jira:**
   - Verify Jira status transitions
   - Check PR links are correct
   - Update sprint board

## Troubleshooting

**Workflow won't start:**
- Check plugin is loaded: `claude --plugin-dir .claude/plugins/em-software-factory`
- Verify environment variables are set
- Ensure JQL syntax is valid

**Agents timing out:**
- Increase timeout in configuration
- Reduce concurrent agents
- Check network connectivity

**Evals failing consistently:**
- Review acceptance criteria in Jira
- Check if criteria are testable
- Verify test fixtures are correct

## Advanced Usage

### Custom JQL Patterns

**By milestone:**
```bash
/autonomous-sprint --jql "project = ABI AND labels = M1 AND status = 'To Do'"
```

**By priority:**
```bash
/autonomous-sprint --jql "project = ABI AND priority = Critical AND sprint = 'Sprint 23'"
```

**By assignee:**
```bash
/autonomous-sprint --jql "project = ABI AND assignee = currentUser() AND status = 'To Do'"
```

**Complex queries:**
```bash
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND (labels = M1 OR priority = Critical) AND status IN ('To Do', 'In Progress')"
```

## Integration with CI/CD

The workflow can be triggered from CI/CD pipelines:

```yaml
# .github/workflows/autonomous-sprint.yml
name: Autonomous Sprint

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9am

jobs:
  implement:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run autonomous sprint
        env:
          JIRA_URL: ${{ secrets.JIRA_URL }}
          JIRA_EMAIL: ${{ secrets.JIRA_EMAIL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          claude --plugin-dir .claude/plugins/em-software-factory << 'EOF'
          /autonomous-sprint --project ABI --sprint "Sprint 23"
          EOF
```

## Next Steps

1. Test with sample issues
2. Tune concurrency for your environment
3. Refine acceptance criteria format
4. Monitor success rates
5. Scale to full sprints
