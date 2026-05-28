---
name: create-bug
description: Create bug reports in Jira with automatic context gathering and regression detection
---

# Create Bug Report

Create comprehensive bug reports in Jira with automatic environment detection, regression analysis, and screenshot references.

## When to Use This Skill

Use this skill to:
- Report bugs discovered during development or testing
- Create structured bug reports with full context
- Auto-detect environment and version information
- Check if bug is a regression

## Usage

```bash
/create-bug "Bug summary"

# With screenshot
/create-bug "Login fails" screenshots/error.png
```

## Process

### Step 1: Gather Bug Information

**Ask user:**

```
I'll create a bug report in Jira.

1. Bug summary (what's broken):
> {User provides}

2. Expected behavior (what should happen):
> {User provides}

3. Actual behavior (what actually happens):
> {User provides}

4. Steps to reproduce:
> 1. {User provides numbered steps}
> 2. 
> 3. 

5. Did this work before? [Y/n]
> {User answers}

6. Screenshot or log file path? (optional, Enter to skip)
> {User provides path or skips}
```

### Step 2: Auto-Detect Environment

**Gather automatically (no user input):**

```bash
# Version from git tags
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "untagged")
COMMIT=$(git rev-parse --short HEAD)

# Environment from branch
BRANCH=$(git branch --show-current)
case "$BRANCH" in
  main|master) ENV="Production";;
  release/*) ENV="Staging";;
  *) ENV="Development";;
esac

# System info
OS=$(uname -s)

# Reporter
REPORTER_NAME=$(git config user.name)
REPORTER_EMAIL=$(git config user.email)

# Date
DATE=$(date +"%Y-%m-%d")
```

**Result:**
```markdown
## Environment

- **Version:** v2.1.0-rc14 (commit: abc123)
- **Branch:** mala/fix-auth (Development)
- **OS:** macOS
- **Reporter:** Mala <mmunisamy@emergence.ai>
- **Date:** 2026-04-14
```

### Step 3: Regression Detection

**If user answered "Yes, it worked before":**

```bash
# Search recent commits (last 2 weeks)
git log --oneline --since="2 weeks ago" | head -10

# Find recent PRs
gh pr list --state merged --limit 5 --json number,title,mergedAt 2>/dev/null

# Present findings
```

**Show to user:**
```
Recent commits (last 2 weeks):
1. abc123 (3 days ago) - "feat: Add password validation"
2. def456 (1 week ago) - "fix: Update login endpoint"
3. ghi789 (10 days ago) - "refactor: Auth service"

Any of these might have introduced the bug?

If yes, enter commit hash (or Enter to skip):
> abc123

✅ Marked as regression: abc123 - "feat: Add password validation"
```

**If user said "No" or "Unknown":**
```
Skipping regression analysis.
```

### Step 4: Get Jira Priorities

**Fetch from Jira project:**

```markdown
Invoke `mcp__atlassian__jira_search_fields` tool to get priority options.

Then ask:
```
Jira priorities for SEMI project:
1. Blocker
2. Critical
3. Major
4. Minor
5. Trivial

Select priority [1-5] or Enter for "Major":
> 2

✅ Priority: Critical
```
```

**Fallback if MCP fails:**
```
Select priority:
1. High
2. Medium
3. Low

[Enter for Medium]:
```

### Step 5: Discover Project Info

**Get Jira project settings:**

```bash
# Get project key from environment (set in .claude/.env)
source .claude/.env 2>/dev/null
PROJECT_KEY=${JIRA_PROJECT_KEY}

# Fallback: Try to detect from cached issues
if [ -z "$PROJECT_KEY" ]; then
  PROJECT_KEY=$(ls .claude/cache/*.md 2>/dev/null | head -1 | grep -oE '[A-Z]+-[0-9]+' | cut -d- -f1)
fi

# Last resort: Ask user
if [ -z "$PROJECT_KEY" ]; then
  echo "Jira project key? (e.g., SEMI)"
  read PROJECT_KEY
fi

echo "✅ Using Jira project: $PROJECT_KEY"

# Get components via MCP
mcp__atlassian__jira_get_project_components
  project_key: "{PROJECT_KEY}"

# Returns: ["Frontend", "Backend", "Database", "API", ...]
```

**Ask for component:**
```
Available components:
1. Frontend
2. Backend
3. Database
4. API
5. Infrastructure

Select (comma-separated or Enter to skip):
> 1,2

✅ Components: Frontend, Backend
```

### Step 6: Validate Screenshot/Log

**If path provided:**

```bash
# Check file exists
if [ -f "{screenshot-path}" ]; then
    echo "✅ Screenshot found: {screenshot-path}"
else
    echo "⚠️ File not found: {screenshot-path}"
fi
```

> **Note:** Screenshots must be manually uploaded to the Jira issue after creation.

### Step 7: Show Preview

**Complete bug report preview:**

```markdown
═══════════════════════════════════════════════════
PREVIEW: Bug Report for Jira
═══════════════════════════════════════════════════

Project: SEMI
Priority: Critical
Components: Frontend, Backend
Labels: bug, regression (if detected), needs-triage

────────────────────────────────────────────────────
Bug: Login fails with special characters in password
────────────────────────────────────────────────────

## Expected Behavior

Login should succeed with any valid password meeting complexity requirements.

## Actual Behavior

Login fails with "Invalid credentials" error when password contains special characters (@, #, $).

## Steps to Reproduce

1. Navigate to login page
2. Enter email: test@example.com
3. Enter password with special chars: Test@123#
4. Click Login
5. Observe error: "Invalid credentials"

## Environment

- **Version:** v2.1.0-rc14 (commit: abc123)
- **Branch:** mala/fix-auth (Development)
- **OS:** macOS
- **Reporter:** Mala <mmunisamy@emergence.ai>
- **Date:** 2026-04-14

## Regression

✅ **Regression** - Introduced by commit abc123

- **Commit:** abc123 - "feat: Add password validation"
- **Author:** John Doe
- **Date:** 3 days ago
- **Review commit:** `git show abc123`

## Screenshots

**Local file:** screenshots/login-error.png (123 KB)

**To attach:**
1. Open issue after creation
2. Upload file manually

────────────────────────────────────────────────────

Create this bug in Jira? [Y/n/e]
```

### Step 8: Create in Jira

**If user confirms:**

```markdown
Invoke `mcp__atlassian__jira_create_issue` tool:

Parameters:
  project_key: "SEMI"
  summary: "Login fails with special characters in password"
  issue_type: "Bug"
  description: {Full bug report markdown from above}
  additional_fields: {
    "priority": {"name": "Critical"},
    "components": [{"name": "Frontend"}, {"name": "Backend"}],
    "labels": ["bug", "regression", "needs-triage"]
  }

Returns: SEMI-1234
```

**Save local copy:**
```bash
mkdir -p .claude/bugs
cat > .claude/bugs/SEMI-1234_bug-report.md <<EOF
{Bug report content}
EOF
```

### Step 9: Output Summary

```markdown
✅ Bug Created in Jira!

**Issue:** SEMI-1234
**URL:** https://emergenceai.atlassian.net/browse/SEMI-1234
**Priority:** Critical
**Regression:** Yes (commit abc123)

**📎 Screenshot:** screenshots/login-error.png
   (Manual upload required)

**Suggested actions:**
- Assign to: John Doe (regression author)
- Review commit: git show abc123
- Investigate: backend/auth/password_validator.py

**Local copy:** .claude/bugs/SEMI-1234_bug-report.md
```

## Success Criteria

- [x] Collects essential bug information from user
- [x] Auto-detects environment (version, branch, OS)
- [x] Detects regression if applicable
- [x] Fetches Jira priorities and components via MCP
- [x] Shows preview before creating
- [x] Creates bug in Jira
- [x] Saves local copy
- [x] Notes screenshot path (manual upload)

## Integration with Other Skills

```bash
# After creating bug
/create-bug "Issue" → SEMI-1234 created

# Investigate
/research-codebase "How does {feature} work?"

# Create fix plan
/create-plan SEMI-1234

# Implement fix
/implement-plan SEMI-1234
```

## Notes

**Keep it simple:**
- Just gather: summary, expected, actual, steps
- Auto-detect: version, branch, OS, reporter, date
- Optional: screenshot path, regression commit
- No complex type detection
- No package versions
- No detailed environment info

**Jira-specific:**
- Uses MCP for all Jira operations
- Fetches project priorities and components dynamically
- No hardcoded values
