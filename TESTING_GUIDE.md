# Multi-Agent Autonomous System - Testing Guide

## Quick Start Testing

Follow these steps to test the multi-agent system from simplest to most complex.

---

## Prerequisites

### 1. Environment Variables

```bash
# Check if variables are set
echo $JIRA_URL
echo $JIRA_EMAIL
echo $JIRA_API_TOKEN
echo $GITHUB_TOKEN

# If not set, add to your shell profile (~/.zshrc or ~/.bashrc)
export JIRA_URL=https://emergenceai.atlassian.net
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your_jira_api_token
export GITHUB_TOKEN=ghp_your_github_token

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

### 2. Install Plugin in Test Repository

```bash
# Go to a test repository (e.g., em-talk2data)
cd ~/Documents/Development/em-talk2data

# Install plugin as git submodule
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory

# Initialize submodule
git submodule update --init --recursive

# Commit
git add .gitmodules .claude/plugins/em-software-factory
git commit -m "Add EM Software Factory plugin"
```

### 3. Verify Plugin Installation

```bash
# Check plugin exists
ls -la .claude/plugins/em-software-factory/

# Should show:
# - skills/ directory
# - workflows/ directory
# - .claude-plugin/plugin.json
```

---

## Test 1: Verify Skills Load

**Goal:** Confirm the plugin and skills are accessible.

```bash
cd ~/Documents/Development/em-talk2data

# Launch Claude with plugin
claude --plugin-dir .claude/plugins/em-software-factory
```

**In Claude Code:**
```
What skills are available?
```

**Expected output:**
You should see the new skills listed:
- `/jira-to-branches`
- `/jira-update`
- `/eval-generator`
- `/autonomous-implement`
- `/autonomous-sprint` (workflow)

**✅ Pass:** Skills are listed  
**❌ Fail:** Skills not showing → Check plugin.json has `"skills": "./skills"`

---

## Test 2: Test Individual Skills

### Test 2a: `/jira-to-branches` (Dry Run)

**Goal:** Verify Jira connectivity and branch creation logic.

**Create a test issue in Jira first:**
1. Go to Jira
2. Create issue:
   - Project: ABI
   - Type: Story
   - Summary: "Test multi-agent system"
   - Component: Talk2Data (or your component)
   - Status: To Do

**In Claude Code:**
```bash
# Test with dry run (no actual changes)
/jira-to-branches --jql "project = ABI AND key = ABI-XXX"
```
*(Replace ABI-XXX with your test issue key)*

**Expected output:**
```
Found 1 issue:
- ABI-XXX: Test multi-agent system (Story)

Would create branch: story/ABI-XXX-test-multi-agent-system

✓ Jira query works
✓ Branch naming works
```

**If successful, create the actual branch:**
```bash
/jira-to-branches --jql "project = ABI AND key = ABI-XXX"
```

**Expected:**
- Branch created in GitHub
- Jira issue has comment with branch link

**✅ Pass:** Branch created, Jira updated  
**❌ Fail:** Check GitHub token permissions, Jira API access

---

### Test 2b: `/eval-generator`

**Goal:** Verify eval test generation from acceptance criteria.

**Add acceptance criteria to your test issue:**

In Jira issue description, add:
```markdown
## Acceptance Criteria

### Functional
- [ ] Function returns "Hello World"
- [ ] Function accepts name parameter
- [ ] Returns personalized greeting when name provided

### Quality
- [ ] Unit test coverage ≥ 80%
```

**In Claude Code:**
```bash
/eval-generator ABI-XXX
```

**Expected output:**
```
Generated eval tests for ABI-XXX: Test multi-agent system

Test Structure:
📁 tests/evals/ABI-XXX/
  ✓ test_functional.py (3 tests)
  ✓ test_quality.py (1 test)
  ✓ conftest.py (fixtures)
  ✓ README.md

Total: 4 tests generated
```

**Verify files created:**
```bash
ls -la tests/evals/ABI-XXX/
cat tests/evals/ABI-XXX/test_functional.py
```

**✅ Pass:** Test files created with correct structure  
**❌ Fail:** Check if acceptance criteria format is recognized

---

### Test 2c: `/jira-update`

**Goal:** Verify Jira update functionality.

```bash
/jira-update ABI-XXX --notes "Testing Jira update skill"
```

**Expected:**
- Comment added to Jira issue

**Check in Jira:**
- Go to ABI-XXX in Jira
- See comment with "Testing Jira update skill"

**✅ Pass:** Comment appears in Jira  
**❌ Fail:** Check Jira API token permissions

---

## Test 3: End-to-End Single Issue Test

**Goal:** Test complete autonomous implementation of one issue.

### Setup Test Issue

**Create new Jira issue with proper acceptance criteria:**

```
Project: ABI
Type: Story
Summary: Add hello world function
Component: Talk2Data
Status: To Do

Description:
Create a simple hello world function for testing autonomous implementation.

## Acceptance Criteria

### Functional
- [ ] Function hello_world() returns "Hello, World!"
- [ ] Function hello(name) returns "Hello, {name}!"

### Quality  
- [ ] Unit tests for both functions
- [ ] Test coverage ≥ 80%
```

### Run Autonomous Implementation

**In Claude Code:**
```bash
/autonomous-implement ABI-XXX
```
*(Replace with your actual issue key)*

**What to watch for:**

The skill will execute these steps (takes 3-7 minutes):
1. ✓ Fetch Jira issue
2. ✓ Research codebase (10-15s)
3. ✓ Create implementation plan (30-60s)
4. ✓ Generate eval tests (5-10s)
5. ✓ Implement solution (2-5 min)
6. ✓ Run evals (10-30s)
7. ✓ Create PR (if evals pass)
8. ✓ Code review
9. ✓ Update Jira

**Expected output:**
```
✓ Successfully implemented ABI-XXX: Add hello world function

Timeline:
  ✓ Researched codebase (12s)
  ✓ Created implementation plan (45s)
  ✓ Generated evals (8s)
  ✓ Implemented solution (2m 24s)
  ✓ Ran evals - 3/3 passed (12s)
  ✓ Created PR #789 (5s)
  ✓ Automated code review (18s)
  ✓ Updated Jira (3s)

Total time: 3 minutes 47 seconds

**Pull Request:** https://github.com/EmergenceAI/em-talk2data/pull/789
**Jira Issue:** https://emergenceai.atlassian.net/browse/ABI-XXX

Status: Ready for human review and merge
```

### Verify Results

**Check GitHub:**
1. Go to the PR URL
2. Verify:
   - ✓ Code was added (e.g., hello_world function)
   - ✓ Tests were created
   - ✓ PR description includes eval results
   - ✓ Code review comments posted

**Check Jira:**
1. Go to issue ABI-XXX
2. Verify:
   - ✓ Comment with PR link
   - ✓ Eval results recorded
   - ✓ Status changed to "In Review" (if configured)

**Check code locally:**
```bash
# Fetch the branch
git fetch origin

# Check out the PR branch
git checkout story/ABI-XXX-add-hello-world-function

# Look at the code
cat src/hello.py  # or wherever it was implemented

# Look at the tests
cat tests/evals/ABI-XXX/test_functional.py

# Run the tests
pytest tests/evals/ABI-XXX/ -v
```

**✅ Pass:** All verifications complete, PR created, tests pass  
**❌ Fail:** See Troubleshooting section below

---

## Test 4: Small Batch Test (2-3 Issues)

**Goal:** Test parallel execution with multiple issues.

### Setup

**Create 2-3 simple test issues in Jira:**

```
Issue 1: ABI-XX1
Summary: Add add(a, b) function
Acceptance Criteria:
- [ ] Function returns sum of two numbers
- [ ] Unit test coverage ≥ 80%

Issue 2: ABI-XX2
Summary: Add subtract(a, b) function
Acceptance Criteria:
- [ ] Function returns difference of two numbers
- [ ] Unit test coverage ≥ 80%

Issue 3: ABI-XX3
Summary: Add multiply(a, b) function
Acceptance Criteria:
- [ ] Function returns product of two numbers
- [ ] Unit test coverage ≥ 80%
```

### Run Workflow

**In Claude Code:**
```bash
/autonomous-sprint --jql "key IN (ABI-XX1, ABI-XX2, ABI-XX3)"
```

**Expected output:**
```
Starting autonomous sprint with JQL: key IN (ABI-XX1, ABI-XX2, ABI-XX3)

Phase: Setup
Querying Jira for issues...
Found 3 issues. Created 3 new branches.

Phase: Audit
Auditing issues for existing implementations...
Audit complete: 3 need implementation, 0 skipped

Phase: Implement
Starting parallel implementation of 3 issues (max 8 concurrent)...

[Progress bars showing 3 parallel agents working...]

==========================================================
AUTONOMOUS SPRINT COMPLETE
==========================================================

Total Issues: 3
  Implemented: 3 ✓
  Partial: 0 ⚠
  Failed: 0 ✗
  Skipped: 0

Eval Results: 9/9 passed
Total Duration: 4 minutes

✓ Successful Implementations:
  ABI-XX1: https://github.com/org/repo/pull/790
    Evals: 3/3 passed
  ABI-XX2: https://github.com/org/repo/pull/791
    Evals: 3/3 passed
  ABI-XX3: https://github.com/org/repo/pull/792
    Evals: 3/3 passed

Next Steps:
  1. Review PRs for successful implementations
  2. Merge approved PRs
```

### Verify

**Check that 3 PRs were created:**
```bash
gh pr list | grep ABI-XX
```

**Expected:**
- 3 PRs created
- All in parallel (total time ~4-5 min, not 9-12 min sequential)
- All with passing evals

**✅ Pass:** 3 PRs created in ~4-5 minutes with passing evals  
**❌ Fail:** Check concurrency settings, system resources

---

## Test 5: Dry Run (No Changes)

**Goal:** Preview what would happen without making changes.

```bash
/autonomous-sprint --project ABI --sprint "Sprint 23" --component "Talk2Data" --dry-run
```

**Expected output:**
```
DRY RUN MODE: No changes will be made

Querying Jira for issues...
Found 8 issues. Would create 8 branches.

Issues:
- ABI-123: Add API rate limiting
- ABI-124: Fix auth timeout
- ABI-125: Multi-agent system
- ... (5 more)

DRY RUN: Stopping before implementation

Would implement 8 issues
```

**✅ Pass:** Shows what would happen, no actual changes  
**❌ Fail:** Check JQL syntax

---

## Test 6: Full Sprint (When Ready)

**Goal:** Run on actual sprint with real issues.

### Before Running

1. **Clean working tree:**
   ```bash
   git status  # Should be clean
   git pull origin main
   ```

2. **Check system resources:**
   ```bash
   # CPU
   top

   # Memory
   free -h  # Linux
   vm_stat  # Mac
   ```

3. **Estimate time:**
   - Count issues in sprint
   - Estimate: `(issue_count / 8) * 5 minutes`
   - Example: 16 issues = (16/8) * 5 = 10 minutes

### Run

```bash
/autonomous-sprint --project ABI --sprint "Sprint 23" --component "Talk2Data"
```

### Monitor

**In another terminal:**
```bash
# Watch workflow progress
/workflows

# Watch git activity
watch -n 5 'git branch -a | grep ABI-'

# Watch system resources
top
```

### After Completion

**Review results:**
1. Check summary output
2. Review successful PRs
3. Investigate partial/failed implementations
4. Merge approved PRs

---

## Troubleshooting

### Plugin Not Loading

**Problem:** Skills don't appear

**Solution:**
```bash
# Verify plugin.json
cat .claude/plugins/em-software-factory/.claude-plugin/plugin.json | grep skills

# Should show: "skills": "./skills"

# Validate plugin
claude plugin validate .claude/plugins/em-software-factory
```

### Jira Connection Fails

**Problem:** "Failed to query Jira"

**Solution:**
```bash
# Test Jira credentials
curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" "$JIRA_URL/rest/api/2/myself"

# Should return your user info

# Check env vars are set
env | grep JIRA
```

### GitHub Token Issues

**Problem:** "Failed to create branch" or "Failed to create PR"

**Solution:**
```bash
# Test GitHub token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Check token has correct permissions:
# - repo (full control)
# - workflow

# Generate new token: https://github.com/settings/tokens
```

### Eval Tests Fail

**Problem:** Evals fail, PR marked [NEEDS-REVIEW]

**Solution:**
1. Check PR for failure details
2. Look at eval output in PR description
3. Fix manually or retry:
   ```bash
   # Check out branch
   git checkout story/ABI-XXX-feature
   
   # Run evals locally
   pytest tests/evals/ABI-XXX/ -v
   
   # Fix implementation
   # Re-run evals
   # Push fix
   ```

### Git Conflicts

**Problem:** "Git conflicts detected"

**Solution:**
```bash
# Pull latest main
git checkout main
git pull origin main

# Rebase branch
git checkout story/ABI-XXX-feature
git rebase main

# Resolve conflicts
# Continue: git rebase --continue
```

### Out of Memory

**Problem:** System slows down, agents fail

**Solution:**
```bash
# Reduce concurrent agents
/autonomous-sprint --project ABI --sprint "Sprint 23" --max-concurrent 4

# Or process in smaller batches
/autonomous-sprint --jql "key IN (ABI-1, ABI-2, ABI-3, ABI-4)"
# Wait for completion
/autonomous-sprint --jql "key IN (ABI-5, ABI-6, ABI-7, ABI-8)"
```

---

## Success Criteria Checklist

### Test 1: Skills Load
- [ ] Plugin installs successfully
- [ ] Skills appear in Claude Code
- [ ] No error messages

### Test 2: Individual Skills
- [ ] `/jira-to-branches` creates branch and updates Jira
- [ ] `/eval-generator` creates test files
- [ ] `/jira-update` adds comment to Jira

### Test 3: Single Issue
- [ ] `/autonomous-implement` completes successfully
- [ ] PR created with passing evals
- [ ] Jira updated with PR link
- [ ] Code review posted

### Test 4: Small Batch
- [ ] Multiple PRs created in parallel
- [ ] Total time < (count * avg) - shows parallelism
- [ ] All evals pass
- [ ] No git conflicts

### Test 5: Dry Run
- [ ] Shows preview without changes
- [ ] No branches created
- [ ] No PRs created

### Test 6: Full Sprint
- [ ] Completes without crashing
- [ ] Success rate ≥ 80%
- [ ] Partial/failed issues are manageable
- [ ] System resources acceptable

---

## Getting Help

**Check logs:**
```bash
# Claude Code logs
cat ~/.claude/logs/latest.log

# Workflow output
# Available in Claude Code session
```

**Debug mode:**
```bash
# Run with verbose output
CLAUDE_DEBUG=1 claude --plugin-dir .claude/plugins/em-software-factory
```

**Ask for help:**
- Review documentation: [MULTI_AGENT_COMPLETE.md](MULTI_AGENT_COMPLETE.md)
- Check skill docs: `skills/*/SKILL.md`
- Workflow guide: [workflows/README.md](workflows/README.md)

---

## Quick Reference

**Test single issue:**
```bash
/autonomous-implement ABI-XXX
```

**Test small batch:**
```bash
/autonomous-sprint --jql "key IN (ABI-1, ABI-2, ABI-3)"
```

**Test full sprint:**
```bash
/autonomous-sprint --project ABI --sprint "Sprint 23" --component "Talk2Data"
```

**Dry run:**
```bash
/autonomous-sprint --project ABI --sprint "Sprint 23" --dry-run
```

**Reduce concurrency:**
```bash
/autonomous-sprint --project ABI --sprint "Sprint 23" --max-concurrent 4
```

---

**Good luck testing! Start small and scale up.** 🚀
