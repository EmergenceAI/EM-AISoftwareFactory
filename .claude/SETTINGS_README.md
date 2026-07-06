# AI Software Factory - Settings Configuration

## Quick Start

The AI Software Factory is configured for **80/20 autonomous mode** by default:
- ✅ 80% of actions happen automatically
- ✅ 20% strategic human checkpoints
- ✅ 10x faster than manual mode

**No setup required** - it works autonomously out of the box!

---

## How It Works

### Default Configuration (Everyone)

**File:** `.claude/settings.json` (checked into git)

- Auto-approves safe operations (Read, Write tests/specs/src, safe git/bash commands)
- Strategic checkpoints (before PR, on test failure, on security changes)
- Automatic backups before edits
- Enforces Foundations standards (air-gapped, test coverage, etc.)

**Result:** Skills run autonomously with minimal prompts

### Personal Overrides (Just You)

**File:** `.claude/settings.local.json` (git-ignored, optional)

Want different settings? Create your personal override:

```bash
# Copy template
cp .claude/settings.local.json.template .claude/settings.local.json

# Edit your preferences
vim .claude/settings.local.json
```

**Your `.local.json` overrides the project defaults.**

---

## Configuration Hierarchy

```
.claude/settings.local.json    (highest priority - your overrides)
        ↓ overrides
.claude/settings.json           (project defaults)
        ↓ overrides
Claude's built-in defaults      (lowest priority)
```

---

## What's Automated by Default

### ✅ Fully Autonomous (No Prompts)

**File Operations:**
- Read any file
- Write to `specs/`, `tests/`, `src/`, `*.md`
- Edit with automatic backup

**Git Operations:**
- `git status`, `git diff`, `git log`
- `git checkout -b` (create branch)
- `git add`, `git commit`, `git push`

**Build/Test:**
- `poetry install`, `poetry run`, `poetry build`
- `pnpm install`, `pnpm test`
- `pytest`, `vitest`
- `docker build`, `docker-compose up`

**GitHub:**
- `gh pr list`, `gh pr view`
- `gh pr create`, `gh pr merge`
- `gh issue list`, `gh issue view`

**MCP (Jira/Confluence):**
- All read operations (get issue, search, view page)

### ❌ Never Auto-Approved (Always Prompt)

**Destructive Operations:**
- `git reset --hard`
- `git push --force`
- `git clean -f`
- `rm -rf`
- `sudo` commands

**Sensitive Files:**
- `.env*` files
- `secrets/` directory
- `src/auth/` directory
- `src/security/` directory

### ⏸️ Strategic Checkpoints

You'll be prompted at these critical moments:

1. **Before PR creation** - Review PR description
2. **On test failure** - Tests failed, fix/skip/abort?
3. **On eval failure** - Evals failed, retry/continue?
4. **Multi-repo changes** - Affects multiple repositories
5. **Architecture changes** - Structural changes
6. **Security changes** - Auth, secrets, permissions

---

## Skill Autonomy Levels

### 100% Autonomous (0 prompts)
- `/research-codebase`
- `/create-plan`
- `/describe-pr`
- `/eval-generator`
- `/commit`
- `/jira-to-branches`
- `/jira-update`

### 95% Autonomous (1 checkpoint)
- `/implement-plan` - ⏸️ before commit
- `/create-pr` - ⏸️ before PR
- `/code-review` - ⏸️ if critical issues

### 80% Autonomous (3 checkpoints)
- `/autonomous-implement` - ⏸️ plan, evals, PR
- `/batch-implement` - ⏸️ plans, test failures
- `/autonomous-sprint` - ⏸️ audit, failures, summary

---

## Customization Examples

### Want More Control?

Add to `.claude/settings.local.json`:

```json
{
  "checkpoints": {
    "beforeCommit": true,      // Prompt before every commit
    "beforePush": true,         // Prompt before every push
    "beforePR": true            // Prompt before PR (default)
  },
  "safety": {
    "dryRunFirst": true         // Show what will happen first
  }
}
```

### Want More Autonomy?

```json
{
  "checkpoints": {
    "beforePR": false,          // Skip PR review
    "onTestFailure": false      // Continue on test failure
  }
}
```

### Disable Autonomous Mode Entirely

```json
{
  "autonomous": {
    "enabled": false            // Back to manual approval for everything
  }
}
```

### Add Custom File Patterns

```json
{
  "permissions": {
    "Write": {
      "rules": [
        {
          "pattern": "custom/path/**/*",
          "autoApprove": true,
          "backup": true
        }
      ]
    }
  }
}
```

### Add Custom Bash Commands

```json
{
  "permissions": {
    "Bash": {
      "allowedPatterns": [
        "make build",
        "make test",
        "custom-script.sh *"
      ]
    }
  }
}
```

---

## Safety Features

### Automatic Backups

Every edit creates a backup:
```
Before: src/api/auth.py
Backup: .claude/backups/src-api-auth.py.20260629-143022
```

Restore if needed:
```bash
cp .claude/backups/src-api-auth.py.20260629-143022 src/api/auth.py
```

### Audit Log

All autonomous actions logged:
```bash
cat .claude/autonomous-actions.log
```

### Worktree Isolation

Parallel work happens in isolated git worktrees:
- No conflicts between concurrent changes
- Clean rollback on failure
- Automatic cleanup

### Pre-Commit Validation

Before every commit:
- ✅ Lint check
- ✅ Format check  
- ✅ Test changed files

### Rollback on Failure

If something fails:
- Automatic rollback to last known good state
- Backups preserved
- Error logged

---

## Foundations Standards Integration

The configuration enforces Foundations team standards:

### Air-Gapped Compatibility
```json
{
  "foundations": {
    "enforceAirGapped": true    // Warns on cloud-specific APIs
  }
}
```

### Test Coverage
```json
{
  "foundations": {
    "enforceTestCoverage": 80   // Requires 80% coverage
  }
}
```

### Security Checks
```json
{
  "foundations": {
    "requireGitleaksPass": true  // Blocks if secrets detected
  }
}
```

---

## Troubleshooting

### "Too many prompts still!"

Check if `.claude/settings.json` is being loaded:
```bash
# Should show autonomous: enabled: true
cat .claude/settings.json | grep -A2 autonomous
```

### "Settings not taking effect"

Your `.local.json` might override project settings:
```bash
# Check if you have overrides
cat .claude/settings.local.json 2>/dev/null || echo "No local overrides"
```

### "Want to reset to defaults"

```bash
# Remove local overrides
rm .claude/settings.local.json

# Now factory defaults apply
```

### "Git operation blocked"

Check if command is in `allowedPatterns`:
```bash
# View allowed patterns
cat .claude/settings.json | grep -A50 allowedPatterns
```

Add to `.local.json` if you need it:
```json
{
  "permissions": {
    "Bash": {
      "allowedPatterns": [
        "your-command-here *"
      ]
    }
  }
}
```

---

## Testing Your Configuration

### Test Autonomous Mode

```bash
# Should run with 0 prompts
/research-codebase "How does authentication work?"

# Should run with 0 prompts
/create-plan ABI-123

# Should prompt only before PR
/create-pr
```

### Test Checkpoints

```bash
# Should prompt 3 times: plan, evals, PR
/autonomous-implement ABI-123

# Should prompt 2 times: plans, on test failure
/batch-implement SEMI-1 SEMI-2 SEMI-3
```

### Verify Auto-Approval

```bash
# Check what's auto-approved
cat .claude/settings.json | jq '.permissions.autoApprove'

# Check allowed bash patterns
cat .claude/settings.json | jq '.permissions.Bash.allowedPatterns'
```

---

## Files Reference

| File | Purpose | Git Tracked | Who |
|------|---------|-------------|-----|
| `settings.json` | Factory defaults (80/20 mode) | ✅ Yes | Everyone |
| `settings.local.json.template` | Customization example | ✅ Yes | Template |
| `settings.local.json` | Your personal overrides | ❌ No (.gitignore) | Just you |

---

## Expected Experience

### Before (Manual Mode) ❌
```
User: /autonomous-implement ABI-123

> Approve Read src/api/auth.py? [yes/no] → yes
> Approve Read src/api/tokens.py? [yes/no] → yes
... (20 more Read prompts)
> Approve Write specs/features/ABI-123.md? [yes/no] → yes
> Approve Edit src/api/auth.py? [yes/no] → yes
... (10 more Edit prompts)
> Approve git add? [yes/no] → yes
> Approve git commit? [yes/no] → yes
> Approve gh pr create? [yes/no] → yes

Total: 40+ prompts ❌
```

### After (80/20 Mode) ✅
```
User: /autonomous-implement ABI-123

🤖 AUTONOMOUS: Fetching Jira...
🤖 AUTONOMOUS: Researching codebase...
🤖 AUTONOMOUS: Creating plan...

⏸️  CHECKPOINT 1: Review approach? [yes/no]
→ yes

🤖 AUTONOMOUS: Generating evals...
🤖 AUTONOMOUS: Implementing...
🤖 AUTONOMOUS: Running tests...
✓ Tests passed: 15/15
✓ Evals passed: 8/8

⏸️  CHECKPOINT 2: Create PR? [yes/no]
→ yes

🤖 AUTONOMOUS: Creating PR #789...
🤖 AUTONOMOUS: Running code review...
✓ Complete!

Total: 2 prompts ✅
```

---

## Summary

**Default (everyone):**
- ✅ 80/20 autonomous mode enabled
- ✅ Safe operations auto-approved
- ✅ Strategic checkpoints only
- ✅ Backups and validation automatic
- ✅ Foundations standards enforced

**Customize (optional):**
- Copy `.template` to `.local.json`
- Override any setting
- Your changes are git-ignored
- Reset anytime by deleting `.local.json`

**Questions?**
- See [SILENT_MODE_STRATEGY.md](../SILENT_MODE_STRATEGY.md) for full details
- See [FOUNDATIONS_KNOWLEDGE_COMPLETE.md](../FOUNDATIONS_KNOWLEDGE_COMPLETE.md) for standards
