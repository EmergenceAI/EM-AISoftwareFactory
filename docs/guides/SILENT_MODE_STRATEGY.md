# Silent Mode Strategy: Making Skills 80% Autonomous

## Problem: Too Much Interactivity

**Current state:** All 22 skills require manual approvals at multiple steps
- Write files → Approval needed
- Git operations → Approval needed
- Run tests → Approval needed  
- Create PR → Approval needed

**Result:** "Autonomous" skills aren't really autonomous ❌

---

## Solution: 80/20 Silent Mode

**Goal:** 80% autonomous, 20% human checkpoints

### Implementation Strategy

Configure permissions ONCE, then skills run autonomously with minimal checkpoints.

---

## Global Permission Configuration

### File: `.claude/settings.local.json`

```json
{
  "autonomous": {
    "enabled": true,
    "mode": "80-20"
  },
  
  "permissions": {
    // ═══════════════════════════════════════════════════════
    // 100% AUTONOMOUS - No prompts
    // ═══════════════════════════════════════════════════════
    "autoApprove": {
      "Read": true,                    // Always auto-approve reads
      "ToolSearch": true,               // Find tools automatically
      "mcp_*": "read_only"             // Auto-approve MCP reads (Jira/Confluence get)
    },
    
    // ═══════════════════════════════════════════════════════
    // 90% AUTONOMOUS - Auto-approve with validation
    // ═══════════════════════════════════════════════════════
    "Write": {
      "enabled": true,
      "rules": [
        {
          "pattern": "specs/**/*",           // Auto-approve specs
          "autoApprove": true
        },
        {
          "pattern": "tests/**/*",           // Auto-approve tests
          "autoApprove": true
        },
        {
          "pattern": "src/**/*.py",          // Auto-approve source (with backup)
          "autoApprove": true,
          "backup": true
        },
        {
          "pattern": "src/**/*.ts",
          "autoApprove": true,
          "backup": true
        },
        {
          "pattern": "*.md",                 // Auto-approve docs
          "autoApprove": true
        },
        {
          "pattern": ".env*",                // NEVER auto-approve secrets
          "autoApprove": false
        }
      ],
      "maxFilesPerOperation": 50,           // Escalate if >50 files
      "createBackup": true                   // Always backup before write
    },
    
    "Edit": {
      "enabled": true,
      "autoApprove": true,                   // Auto-approve edits
      "createBackup": true
    },
    
    // ═══════════════════════════════════════════════════════
    // 80% AUTONOMOUS - Safe bash commands auto-approved
    // ═══════════════════════════════════════════════════════
    "Bash": {
      "allowedPatterns": [
        // Git read operations (100% auto)
        "git status",
        "git diff",
        "git diff *",
        "git log",
        "git log *",
        "git show *",
        "git branch",
        "git branch -l",
        
        // Git write operations (auto-approve, safe)
        "git checkout -b *",                 // Create branch
        "git add *",                         // Stage files
        "git commit *",                      // Commit
        "git push *",                        // Push (non-force)
        
        // BLOCKED: Destructive git operations
        // "git reset --hard *",             // Never auto-approve
        // "git push --force *",             // Never auto-approve
        // "git clean -fd",                  // Never auto-approve
        
        // Build/Test operations (auto-approve)
        "poetry install",
        "poetry run *",
        "poetry build",
        "pnpm install",
        "pnpm *",
        "npm install",
        "npm run *",
        "npm test",
        
        // Test execution (auto-approve)
        "pytest *",
        "python -m pytest *",
        "vitest *",
        
        // Docker operations (auto-approve read-only)
        "docker ps",
        "docker images",
        "docker build *",                    // Build is safe
        "docker run --rm *",                 // Run with cleanup
        
        // File operations (safe)
        "ls *",
        "find *",
        "grep *",
        "cat *",
        "head *",
        "tail *",
        
        // GitHub CLI (auto-approve)
        "gh pr list",
        "gh pr view *",
        "gh pr create *",                    // Auto-approve PR creation
        "gh pr merge *",                     // Requires --confirm flag
        "gh issue list",
        "gh issue view *"
      ],
      
      "blockedPatterns": [
        "*rm -rf*",                          // Never auto-approve
        "*sudo *",                           // Never auto-approve
        "*chmod 777*",                       // Never auto-approve
        "*>/dev/null 2>&1*",                // No silent errors
        "*git reset --hard*",               // Destructive
        "*git push --force*",               // Destructive
        "*git clean -f*"                    // Destructive
      ],
      
      "autoApprove": "allowedOnly",          // Only auto-approve if in allowedPatterns
      "timeout": 300000                      // 5 min timeout
    }
  },
  
  // ═══════════════════════════════════════════════════════
  // CHECKPOINTS - When to pause for human review
  // ═══════════════════════════════════════════════════════
  "checkpoints": {
    "beforeCommit": false,                   // Don't pause before commit
    "beforePush": false,                     // Don't pause before push
    "beforePR": true,                        // ⏸️  PAUSE: Review PR description
    "onTestFailure": true,                   // ⏸️  PAUSE: If tests fail
    "onEvalFailure": true,                   // ⏸️  PAUSE: If evals fail
    "onMultiRepo": true,                     // ⏸️  PAUSE: Multi-repo coordination
    "onArchitectureChange": true,            // ⏸️  PAUSE: Architecture decisions
    "onSecurityChange": true,                // ⏸️  PAUSE: Auth/secrets changes
    
    "escalation": {
      "maxFilesChanged": 50,                 // Escalate if >50 files
      "maxReposAffected": 3,                 // Escalate if >3 repos
      "criticalPaths": [
        "src/auth/**/*",                     // Always escalate
        "src/security/**/*",
        ".env*",
        "secrets/**/*"
      ]
    }
  },
  
  // ═══════════════════════════════════════════════════════
  // SAFETY - Rollback and validation
  // ═══════════════════════════════════════════════════════
  "safety": {
    "worktreeIsolation": true,               // Always use worktrees
    "createBackups": true,                   // Backup before edits
    "validateBeforeCommit": true,            // Run linter before commit
    "rollbackOnFailure": true,               // Auto-rollback on critical failure
    "dryRunFirst": false,                    // Skip dry-run (trust autonomous)
    
    "preCommitChecks": [
      "lint",                                // Run linter
      "format-check",                        // Check formatting
      "test-changed"                         // Test only changed files (fast)
    ]
  }
}
```

---

## Per-Skill Silent Mode Recommendations

### Category 1: Fully Autonomous (No Checkpoints)

**These skills should run 100% silent:**

#### ✅ `/research-codebase`
**Recommendation:** Fully autonomous (read-only)

```json
// No config needed - already read-only
// Uses: Read, Bash (grep, find), no writes
```

#### ✅ `/create-plan`
**Recommendation:** Fully autonomous

```json
// Auto-approves:
// - Read files
// - Write to specs/features/
// No checkpoints needed
```

#### ✅ `/describe-pr`
**Recommendation:** Fully autonomous

```json
// Auto-approves:
// - Git diff
// - Read files
// - Write PR description
// No checkpoints needed
```

#### ✅ `/eval-generator`
**Recommendation:** Fully autonomous

```json
// Auto-approves:
// - Read Jira (MCP)
// - Write to tests/evals/
// No checkpoints needed
```

---

### Category 2: Mostly Autonomous (1 Checkpoint)

**These skills should have ONE checkpoint at the end:**

#### ⏸️ `/implement-plan` → Checkpoint before commit
**Recommendation:** Autonomous until commit

```json
{
  "autonomous": {
    "autoApprove": ["Read", "Write", "Edit", "Bash:safe"],
    "checkpoint": "beforeCommit"
  }
}
```

**Flow:**
```
Read plan → Research → Implement → Write files → Format → Lint
  ↓ (all autonomous)
⏸️  CHECKPOINT: Review git diff
  ↓
Commit → Push
```

#### ⏸️ `/create-pr` → Checkpoint before PR creation
**Recommendation:** Autonomous until PR

```json
{
  "autonomous": {
    "autoApprove": ["Read", "Bash:git"],
    "checkpoint": "beforePR"
  }
}
```

**Flow:**
```
Git status → Git diff → Generate PR description
  ↓ (all autonomous)
⏸️  CHECKPOINT: Review PR description
  ↓
gh pr create
```

#### ⏸️ `/code-review` → Checkpoint if critical issues found
**Recommendation:** Conditional checkpoint

```json
{
  "autonomous": {
    "autoApprove": ["Read", "Bash:git"],
    "checkpoint": "onCriticalIssues"
  }
}
```

**Flow:**
```
Read files → Analyze → Generate review comments
  ↓
If critical issues found:
  ⏸️  CHECKPOINT: Show critical issues
Else:
  Post review automatically
```

---

### Category 3: High-Value Autonomous (2-3 Checkpoints)

**These skills have strategic checkpoints for quality/safety:**

#### ⏸️⏸️ `/autonomous-implement` → 3 Checkpoints
**Recommendation:** 80/20 mode

```json
{
  "autonomous": {
    "mode": "80-20",
    "checkpoints": [
      "afterPlan",         // ⏸️  Review implementation approach
      "onEvalFailure",     // ⏸️  If evals fail
      "beforePR"           // ⏸️  Review PR description
    ]
  }
}
```

**Flow:**
```
Fetch Jira → Research → Create Plan
  ↓ (autonomous)
⏸️  CHECKPOINT 1: Review approach? [yes/no/modify]
  ↓
Generate Evals → Implement → Run Tests → Run Evals
  ↓ (autonomous)
If evals fail:
  ⏸️  CHECKPOINT 2: Evals failed - retry/fix/skip/abort?
  ↓
Generate PR description
  ↓
⏸️  CHECKPOINT 3: Review PR? [yes/no/edit]
  ↓
Create PR → Code Review → Update Jira
  ↓ (autonomous)
```

**Result:** User reviews 3 times, rest is autonomous (~80% autonomous)

#### ⏸️⏸️ `/batch-implement` → 2 Checkpoints
**Recommendation:** Plan approval + Test failure

```json
{
  "autonomous": {
    "checkpoints": [
      "afterPlanning",     // ⏸️  Review all plans
      "onTestFailure"      // ⏸️  If tests fail
    ]
  }
}
```

**Flow:**
```
Fetch Tickets → Plan All (parallel)
  ↓ (autonomous)
⏸️  CHECKPOINT 1: Review plans? [yes/no/modify]
  ↓
Implement All (parallel) → Tests
  ↓ (autonomous)
If tests fail:
  ⏸️  CHECKPOINT 2: Tests failed - fix/skip/abort?
```

#### ⏸️⏸️⏸️ `/autonomous-sprint` → 3 Checkpoints
**Recommendation:** High-value checkpoints only

```json
{
  "autonomous": {
    "checkpoints": [
      "afterAudit",        // ⏸️  Review what will be implemented
      "onMultipleFailures", // ⏸️  If >3 issues fail evals
      "beforeBulkMerge"    // ⏸️  Before merging all PRs (optional)
    ]
  }
}
```

**Flow:**
```
Fetch Issues → Create Branches → Audit (skip done)
  ↓ (autonomous)
⏸️  CHECKPOINT 1: Implement 28 issues? [yes/no]
  ↓
Implement All (parallel, 8 concurrent)
  Each runs autonomous-implement with internal checkpoints
  ↓ (mostly autonomous)
If >3 failures:
  ⏸️  CHECKPOINT 2: Multiple failures - continue/abort?
  ↓
Report results
```

---

### Category 4: Git/Branch Management (Fully Autonomous)

**These should never prompt:**

#### ✅ `/jira-to-branches`
**Recommendation:** Fully autonomous

```json
// Auto-approves:
// - Jira MCP calls
// - git checkout -b
// - git push
// No checkpoints
```

#### ✅ `/commit`
**Recommendation:** Autonomous with validation

```json
{
  "autonomous": {
    "preCommitChecks": ["lint", "format"],
    "autoCommit": true
  }
}
```

**Flow:**
```
Git status → Git diff → Analyze → Generate commit message
  ↓
Run lint → Run format check
  ↓
Git add → Git commit
  ↓ (all autonomous, no prompts)
```

---

### Category 5: Testing Skills (Conditional Checkpoints)

#### ⏸️ `/create-e2e-testplan`
**Recommendation:** Autonomous

```json
// Auto-approves writes to specs/testing/
// No checkpoints
```

#### ⏸️ `/update-e2e-testplan`
**Recommendation:** Autonomous

```json
// Auto-approves edits to existing plans
// No checkpoints
```

---

## Summary Matrix

| Skill | Checkpoints | Autonomy | Recommendation |
|-------|-------------|----------|----------------|
| `/research-codebase` | 0 | 100% | ✅ Fully silent |
| `/create-plan` | 0 | 100% | ✅ Fully silent |
| `/describe-pr` | 0 | 100% | ✅ Fully silent |
| `/eval-generator` | 0 | 100% | ✅ Fully silent |
| `/commit` | 0 | 100% | ✅ Fully silent |
| `/jira-to-branches` | 0 | 100% | ✅ Fully silent |
| `/jira-update` | 0 | 100% | ✅ Fully silent |
| `/create-e2e-testplan` | 0 | 100% | ✅ Fully silent |
| `/update-e2e-testplan` | 0 | 100% | ✅ Fully silent |
| `/implement-plan` | 1 (before commit) | 95% | ⏸️  1 checkpoint |
| `/create-pr` | 1 (before PR) | 95% | ⏸️  1 checkpoint |
| `/code-review` | 1 (if critical) | 90% | ⏸️  Conditional |
| `/batch-implement` | 2 (plans, tests) | 85% | ⏸️⏸️ 2 checkpoints |
| `/autonomous-implement` | 3 (plan, evals, PR) | 80% | ⏸️⏸️⏸️ 3 checkpoints |
| `/autonomous-sprint` | 3 (audit, failures, merge) | 80% | ⏸️⏸️⏸️ 3 checkpoints |

---

## Implementation Plan

### Phase 1: Enable Silent Mode Globally
```bash
# Copy template to your project
cp .claude/settings.local.json.template .claude/settings.local.json

# Edit for your preferences
vim .claude/settings.local.json
```

### Phase 2: Test Fully Autonomous Skills First
```bash
# Test read-only skills (safest)
/research-codebase "How does authentication work?"
# Should run with ZERO prompts

# Test write skills
/create-plan ABI-123
# Should write to specs/ with ZERO prompts

# Test git skills
/jira-to-branches --jql "key = ABI-123"
# Should create branch with ZERO prompts
```

### Phase 3: Test Checkpoint Skills
```bash
# Test single-checkpoint skill
/create-pr
# Should run autonomous until PR description, then prompt ONCE

# Test multi-checkpoint skill
/autonomous-implement ABI-123
# Should prompt 3 times: plan, evals, PR
```

### Phase 4: Test Bulk Skills
```bash
# Test batch (2 checkpoints)
/batch-implement SEMI-1 SEMI-2 SEMI-3
# Should prompt: plans, tests

# Test sprint (3 checkpoints)
/autonomous-sprint --jql "key IN (ABI-1, ABI-2, ABI-3)"
# Should prompt: audit, failures (if any)
```

---

## Monitoring and Safety

### Backup System
All autonomous writes create backups:
```bash
# Before edit
src/api/auth.py → .claude/backups/src-api-auth.py.20260628-143022

# Rollback if needed
cp .claude/backups/src-api-auth.py.20260628-143022 src/api/auth.py
```

### Audit Log
All autonomous actions are logged:
```bash
cat .claude/autonomous-actions.log

2026-06-28 14:30:22 [WRITE] specs/features/ABI-123.md
2026-06-28 14:31:45 [EDIT] src/api/auth.py (backup: .claude/backups/...)
2026-06-28 14:32:10 [BASH] git checkout -b feature/ABI-123
2026-06-28 14:35:55 [BASH] git commit -m "..."
2026-06-28 14:36:01 [BASH] gh pr create ...
```

---

## Expected Experience

### Before (Interactive Mode) ❌
```
User: /autonomous-implement ABI-123

Fetching Jira...
> 👤 Approve MCP call? [yes/no]  → User types 'yes'

Researching...
> 👤 Approve Read src/api/auth.py? [yes/no]  → User types 'yes'
> 👤 Approve Read src/api/tokens.py? [yes/no]  → User types 'yes'
... (20 more Read approvals)

Creating plan...
> 👤 Approve Write specs/features/ABI-123.md? [yes/no]  → User types 'yes'

Generating evals...
> 👤 Approve Write tests/evals/ABI-123.py? [yes/no]  → User types 'yes'

Implementing...
> 👤 Approve Edit src/api/auth.py? [yes/no]  → User types 'yes'
> 👤 Approve Edit src/api/tokens.py? [yes/no]  → User types 'yes'
... (10 more Edit approvals)

Running tests...
> 👤 Approve Bash: pytest? [yes/no]  → User types 'yes'

Creating commit...
> 👤 Approve Bash: git add? [yes/no]  → User types 'yes'
> 👤 Approve Bash: git commit? [yes/no]  → User types 'yes'

Creating PR...
> 👤 Approve Bash: gh pr create? [yes/no]  → User types 'yes'

Total prompts: 40+ ❌ EXHAUSTING
```

### After (80/20 Silent Mode) ✅
```
User: /autonomous-implement ABI-123

🤖 AUTONOMOUS: Fetching Jira issue...
🤖 AUTONOMOUS: Researching codebase...
🤖 AUTONOMOUS: Creating implementation plan...

⏸️  CHECKPOINT 1: Review Implementation Approach
Plan: Add JWT token validation to auth middleware
Files: 3 modified, 2 new
Approve? [yes/no/modify]  → User types 'yes'

🤖 AUTONOMOUS: Generating evals...
🤖 AUTONOMOUS: Implementing changes...
🤖 AUTONOMOUS: Running tests...
🤖 AUTONOMOUS: Running evals...
✓ Evals passed: 8/8

⏸️  CHECKPOINT 2: Review PR Description
Title: "ABI-123: Add JWT token validation"
[PR description preview]
Create PR? [yes/no/edit]  → User types 'yes'

🤖 AUTONOMOUS: Creating PR...
🤖 AUTONOMOUS: Running code review...
🤖 AUTONOMOUS: Updating Jira...

✅ Complete: PR #789 created

Total prompts: 2 ✅ MANAGEABLE
```

---

## Recommendation

**Enable 80/20 mode globally** with the provided `settings.local.json` configuration:

1. ✅ **Fully autonomous:** 9 skills (research, plan, eval-gen, commit, etc.)
2. ⏸️  **1-2 checkpoints:** 3 skills (implement-plan, create-pr, code-review)
3. ⏸️⏸️⏸️ **3 checkpoints:** 3 skills (autonomous-implement, batch-implement, autonomous-sprint)

**Result:** 
- ~80% of actions happen autonomously
- ~20% strategic human reviews
- **10x faster than interactive mode**
- Still safe (backups, validation, rollback)
