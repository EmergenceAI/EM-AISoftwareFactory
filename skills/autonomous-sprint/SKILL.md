---
name: autonomous-sprint
description: Autonomously implement multiple Jira issues in parallel with eval-based validation
---

# Autonomous Sprint

Autonomously implement multiple Jira issues in parallel using the autonomous-sprint workflow.

## When to Use This Skill

Use this skill to:
- Implement an entire sprint of Jira issues autonomously
- Process multiple issues in parallel (8 concurrent by default)
- Execute complete development cycle for each issue with eval validation
- Automate: query Jira → create branches → implement → test → PR → update Jira

## Usage

```bash
# By Jira filter
/autonomous-sprint --jql "filter = 17150"
/autonomous-sprint --jql "filter = 'Agent Test'"

# By JQL query
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Connectors'"

# By project and sprint
/autonomous-sprint --project ABI --sprint "Sprint 23" --component "Talk2Data"

# Specific issues
/autonomous-sprint --jql "key IN (ABI-123, ABI-124, ABI-125)"

# Dry run (preview only, no changes)
/autonomous-sprint --jql "filter = 17150" --dry-run

# Control concurrency
/autonomous-sprint --jql "filter = 17150" --max-concurrent 4
/autonomous-sprint --jql "filter = 17150" --max-concurrent 16
```

## How It Works

This skill invokes the `autonomous-sprint` workflow which executes in three phases:

### Phase 1: Setup
- Query Jira with JQL
- Create standardized GitHub branches for each issue
- Update Jira issues with branch links

### Phase 2: Audit
- Check for existing implementations (PRs, commits)
- Filter out issues already completed
- Report what will be skipped

### Phase 3: Implement (Parallel)
- Spawn parallel agents (8 concurrent by default)
- Each agent runs `/autonomous-implement` for one issue
- Works in isolated git worktree (no conflicts)
- Creates PR if evals pass
- Updates Jira with results

## Parameters

**`--jql`** (string, required if no --project)
- JQL query for selecting issues
- Examples:
  - `"filter = 17150"`
  - `"filter = 'Agent Test'"`
  - `"project = ABI AND sprint = 'Sprint 23'"`
  - `"key IN (ABI-1, ABI-2, ABI-3)"`

**`--project`** (string, alternative to --jql)
- Jira project key
- Example: `ABI`

**`--sprint`** (string, used with --project)
- Sprint name
- Example: `"Sprint 23"`

**`--component`** (string, optional)
- Jira component filter
- Example: `"Talk2Data"`

**`--max-concurrent`** (number, default: 8)
- Maximum parallel agent executions
- Examples:
  - `4` for conservative/slower machines
  - `8` for balanced (default)
  - `16` for aggressive/powerful machines

**`--dry-run`** (boolean, default: false)
- Preview what would happen without making changes
- Shows which issues selected, which skipped
- No branches, PRs, or code changes made

**`--include-all`** (boolean, default: false)
- Include issues in any status
- By default only includes: "To Do", "In Progress"

## Example Output

### Successful Sprint (28/32 issues)

```
Starting autonomous sprint with JQL: filter = 17150

Phase: Setup
Querying Jira for issues...
Found 32 issues. Created 32 new branches.

Phase: Audit
Auditing issues for existing implementations...
Audit complete: 32 need implementation, 0 skipped

Phase: Implement
Starting parallel implementation of 32 issues (max 8 concurrent)...

==========================================================
AUTONOMOUS SPRINT COMPLETE
==========================================================

Total Issues: 32
  Implemented: 28 ✓
  Partial: 3 ⚠
  Failed: 1 ✗
  Skipped: 0

Eval Results: 156/160 passed
Total Duration: 18 minutes

✓ Successful Implementations:
  ABI-123: https://github.com/EmergenceAI/em-runtime/pull/789
    Evals: 5/5 passed
  ABI-124: https://github.com/EmergenceAI/em-runtime/pull/790
    Evals: 6/6 passed
  ... (26 more)

⚠ Partial Implementations (needs review):
  ABI-150: https://github.com/EmergenceAI/em-runtime/pull/817 [NEEDS-REVIEW]
    Evals: 4/6 passed
    Failed: 2 performance tests

Next Steps:
  1. Review PRs for successful implementations
  2. Address eval failures for partial implementations
  3. Investigate and retry failed implementations
```

### Dry Run Output

```
DRY RUN MODE: No changes will be made

Querying Jira for issues...
Found 32 issues. Would create 32 branches.

Issues:
- ABI-123: Add CSV connector
- ABI-124: Add Parquet connector
- ABI-125: Add PDF connector
... (29 more)

DRY RUN: Stopping before implementation

Would implement 32 issues
```

## Performance Expectations

### Timing Estimates (per issue)
- Research: 10-15 seconds
- Plan: 30-60 seconds
- Eval generation: 5-10 seconds
- Implementation: 2-5 minutes
- Eval execution: 10-30 seconds
- PR creation: 5-10 seconds
- Code review: 15-30 seconds
- Jira update: 2-5 seconds

**Total per issue:** 3-7 minutes

### Parallel Speedup

| Issues | Sequential | Parallel (8 agents) | Speedup |
|--------|-----------|---------------------|---------|
| 5 | 15-35 min | 3-7 min | 5x |
| 10 | 30-70 min | 4-9 min | 7.5x |
| 32 | 96-224 min | 12-28 min | **8x** |

## Prerequisites

**Environment Variables:**
```bash
export JIRA_URL=https://emergenceai.atlassian.net
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your_jira_api_token
export GITHUB_TOKEN=ghp_your_github_token
```

**Clean Working Tree:**
```bash
git status  # Should show: "working tree clean"
```

**System Resources (for 8 concurrent agents):**
- CPU: 8+ cores recommended
- RAM: 4-6 GB available
- Disk: 10+ GB free

## Best Practices

### Before Running

1. **Start with dry run:**
   ```bash
   /autonomous-sprint --jql "filter = 17150" --dry-run
   ```

2. **Test with small batch first:**
   ```bash
   /autonomous-sprint --jql "key IN (ABI-1, ABI-2, ABI-3)"
   ```

3. **Ensure acceptance criteria in Jira:**
   - Each issue should have testable acceptance criteria
   - Format: Functional, Performance, Quality criteria
   - Enables automated eval generation

### During Execution

1. **Monitor progress:**
   - Watch for phase transitions (Setup → Audit → Implement)
   - Check for error messages
   - Monitor system resources

2. **Don't interrupt:**
   - Let workflow complete
   - Agents work in isolated worktrees
   - Interrupting may leave partial work

### After Completion

1. **Review PRs:**
   ```bash
   gh pr list
   ```

2. **Check Jira updates:**
   - Verify PR links added
   - Check eval results recorded

3. **Merge successful PRs:**
   ```bash
   gh pr merge <number> --merge
   ```

## Troubleshooting

**"No issues found":**
- Check JQL syntax
- Verify filter exists and is accessible
- Ensure you have permissions to view issues

**Git conflicts:**
- Each agent works in isolated worktree
- Conflicts rare unless manual changes made
- Resolution: fix manually and retry issue

**Eval failures:**
- Review acceptance criteria in Jira
- Check PR description for failure details
- Fix manually or retry with `/autonomous-implement`

**Resource exhaustion:**
- Reduce concurrency: `--max-concurrent 4`
- Or process in batches:
  ```bash
  /autonomous-sprint --jql "key IN (ABI-1 to ABI-10)"
  # Wait for completion
  /autonomous-sprint --jql "key IN (ABI-11 to ABI-20)"
  ```

## Related Skills

- `/autonomous-implement` - Implement single issue
- `/jira-to-branches` - Just create branches
- `/eval-generator` - Generate tests from acceptance criteria
- `/jira-update` - Update Jira with results

## Notes

- Uses Claude Code Workflow orchestration
- Each agent runs in isolated git worktree
- Parallel execution via `pipeline()` pattern
- Automatic concurrency management
- Structured output with success/failure breakdown
- All PRs include eval results

## Success Criteria

- [x] Queries Jira correctly
- [x] Creates branches for all issues
- [x] Filters out completed work
- [x] Spawns parallel agents
- [x] Each agent implements autonomously
- [x] Creates PRs only when evals pass
- [x] Updates Jira with results
- [x] Returns structured summary
