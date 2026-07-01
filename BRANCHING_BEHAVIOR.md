# Branching Behavior in /autonomous-implement

## **Short Answer: YES, it creates a new branch automatically**

The `/autonomous-implement` skill **will create a new branch** in the identified repository when you run it.

---

## How Branch Creation Works

### **1. Automatic Branch Creation (Default)**

When you run:
```bash
/autonomous-implement SEMI-1413
```

The skill will:

1. ✅ **Fetch Jira issue** SEMI-1413
2. ✅ **Determine issue type** (Story, Bug, Task, etc.)
3. ✅ **Create branch** following naming convention:

```
{issue-type}/{issue-key}-{slug}

Examples:
- Story → story/SEMI-1413-fix-wafer-processing
- Bug → bug/SEMI-1413-memory-leak
- Task → task/SEMI-1413-update-docs
- Epic → epic/SEMI-1413-new-feature
```

**Branch naming uses:**
- Issue type prefix (story, bug, task, epic)
- Issue key (SEMI-1413)
- Slugified summary from Jira

---

### **2. Using Existing Branch (Optional)**

If you **already have a branch**, use the `--branch` parameter:

```bash
/autonomous-implement SEMI-1413 --branch feature/my-custom-branch
```

This will:
- ✅ Checkout your existing branch
- ❌ NOT create a new branch
- ✅ Implement changes on your specified branch

---

## Where Branch is Created

### **Orchestrator Flow:**

```
1. Orchestrator routes SEMI-1413 → semi repository
   Repository: /Users/malamunisamy/Documents/Development/em-semi

2. You run in Claude Code:
   cd /Users/malamunisamy/Documents/Development/em-semi
   /autonomous-implement SEMI-1413

3. Skill creates branch in em-semi:
   git checkout -b story/SEMI-1413-improve-wafer-yield
   
4. All changes happen in em-semi on that new branch

5. PR created from:
   Branch: story/SEMI-1413-improve-wafer-yield
   Target: main (or default branch)
```

---

## Branch Naming Convention

### **Standard Format:**

```
{type}/{key}-{slug}
```

### **Type Mapping:**

| Jira Issue Type | Branch Prefix |
|----------------|---------------|
| Story | `story/` |
| Bug | `bug/` |
| Task | `task/` |
| Epic | `epic/` |
| Sub-task | `subtask/` |
| Other | `feature/` |

### **Slug Generation:**

The slug is created from the Jira issue summary:

```
Summary: "Fix memory leak in wafer processing"
→ Slug: "fix-memory-leak-in-wafer-processing"
→ Branch: "bug/SEMI-1413-fix-memory-leak-in-wafer-processing"
```

**Rules:**
- Lowercase
- Spaces → hyphens
- Remove special characters
- Truncate to ~50 chars if too long

---

## Complete Example

### **Scenario: Implement SEMI-1413 in em-semi**

**Jira Issue:**
```
Key: SEMI-1413
Type: Story
Summary: Improve wafer yield prediction accuracy
Component: Semi
```

**Orchestrator Routes:**
```bash
$ python3 -m orchestrator implement SEMI-1413

🎯 Repository: semi (auto-routed)
✅ Knowledge context prepared
📝 To execute: cd em-semi && /autonomous-implement SEMI-1413
```

**In Claude Code:**
```bash
cd /Users/malamunisamy/Documents/Development/em-semi

# Current state
git branch
# * main

/autonomous-implement SEMI-1413

# Skill executes:
# 1. Fetch SEMI-1413 from Jira
# 2. Create branch: story/SEMI-1413-improve-wafer-yield-prediction
# 3. Research codebase
# 4. Create plan in specs/features/SEMI-1413.md
# 5. Generate evals in tests/evals/SEMI-1413/
# 6. Implement changes
# 7. Run evals
# 8. Create PR from story/SEMI-1413-improve-wafer-yield-prediction → main
# 9. Update Jira

# After execution
git branch
# * story/SEMI-1413-improve-wafer-yield-prediction
#   main
```

**Result:**
```
Repository: em-semi
Branch: story/SEMI-1413-improve-wafer-yield-prediction
PR: https://github.com/EmergenceAI/em-semi/pull/123
  Base: main
  Head: story/SEMI-1413-improve-wafer-yield-prediction
```

---

## Multi-Branch Scenario

### **If You Have Multiple Issues:**

```bash
# Issue 1
/autonomous-implement SEMI-1413
# Creates: story/SEMI-1413-improve-yield

# Issue 2
/autonomous-implement SEMI-1414
# Creates: bug/SEMI-1414-fix-sensor-data

# Issue 3
/autonomous-implement SEMI-1415
# Creates: task/SEMI-1415-update-calibration
```

**Each issue gets its own branch in em-semi!**

---

## Branch Isolation with Workflows

When using workflows (e.g., `/autonomous-sprint`), branches can be isolated:

```javascript
// In workflow
const results = await pipeline(
  issues,
  issue => agent(`/autonomous-implement ${issue.key}`, {
    isolation: 'worktree',  // Each gets separate worktree!
    schema: IMPLEMENTATION_SCHEMA
  })
)
```

**With `isolation: 'worktree'`:**
- ✅ Each issue implemented in **separate git worktree**
- ✅ Parallel execution without conflicts
- ✅ Each has its own branch
- ✅ Each creates its own PR

**Worktree example:**
```
em-semi/                              # Main worktree
.claude/worktrees/
  ├── SEMI-1413/                      # Worktree for SEMI-1413
  │   └── (branch: story/SEMI-1413-...)
  ├── SEMI-1414/                      # Worktree for SEMI-1414
  │   └── (branch: bug/SEMI-1414-...)
  └── SEMI-1415/                      # Worktree for SEMI-1415
      └── (branch: task/SEMI-1415-...)
```

---

## Checking Branch State

### **Before Running:**
```bash
cd /Users/malamunisamy/Documents/Development/em-semi
git status

# Output:
# On branch main
# nothing to commit, working tree clean
```

### **After Running:**
```bash
git status

# Output:
# On branch story/SEMI-1413-improve-wafer-yield-prediction
# Your branch is ahead of 'origin/main' by 3 commits
```

### **View All Branches:**
```bash
git branch -a

# Output:
# * story/SEMI-1413-improve-wafer-yield-prediction
#   main
#   remotes/origin/main
```

---

## Summary

### ✅ **What Happens Automatically:**

1. ✅ **Branch is created** in the identified repository (em-semi)
2. ✅ **Branch name follows convention** (type/key-slug)
3. ✅ **All changes happen on new branch**
4. ✅ **PR created from new branch → main**
5. ✅ **Jira updated with PR link**

### **What You Control:**

- ✅ **Repository selection** (via orchestrator routing or manual cd)
- ✅ **Branch name** (via `--branch` parameter if you want custom)
- ✅ **When to start** (you invoke the skill)

### **What You Don't Need to Do:**

- ❌ Manually create branch
- ❌ Remember naming convention
- ❌ Switch to branch
- ❌ Push branch to remote

**It's all automated!** 🎉

---

## Quick Reference

| Command | Branch Created | Where |
|---------|----------------|-------|
| `python3 -m orchestrator implement SEMI-1413` | No (just prepares) | N/A |
| `cd em-semi && /autonomous-implement SEMI-1413` | ✅ Yes | em-semi |
| `cd em-semi && /autonomous-implement SEMI-1413 --branch my-branch` | ❌ No (uses existing) | em-semi |
| `/autonomous-sprint --jql "..."` | ✅ Yes (one per issue) | Auto-routed repos |

**The orchestrator + skill combination handles everything automatically!**
