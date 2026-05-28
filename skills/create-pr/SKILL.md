---
name: create-pr
description: Create pull request on GitHub with comprehensive description and context
---

# Create Pull Request

Create a pull request on GitHub from your current branch with a comprehensive description, linking to implementation plans, test plans, and related tickets.

## When to Use This Skill

Use this skill to:
- Create PR from current feature branch
- Generate PR title and description automatically
- Link PR to related documentation
- Set up PR with proper labels and reviewers

## Process

### 1. Validate Current State and PR Size

**Check current branch:**
```bash
git branch --show-current
```

**Verify not on main/master:**
```bash
# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Check if on main/master
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo "ERROR: Cannot create PR from main/master branch"
    echo "Please switch to a feature branch first"
    exit 1
fi
```

**Analyze PR size and suggest splitting if too large:**
```bash
# Get diff stats
git diff main...HEAD --stat

# Count changed files and lines
FILES_CHANGED=$(git diff main...HEAD --numstat | wc -l)
LINES_CHANGED=$(git diff main...HEAD --numstat | awk '{sum+=$1+$2} END {print sum}')
```

**PR Size Guidelines:**
- **SMALL (Ideal for fixes):** ≤3 files, ≤100 lines
  - Fastest review
  - Lowest risk
  - Easy to understand
  - Quick to merge

- **MEDIUM:** 4-10 files, 101-300 lines
  - Reasonable review size
  - May need detailed review

- **LARGE:** 11+ files or 301+ lines
  - Harder to review thoroughly
  - Higher risk of issues
  - Consider splitting

**If PR is LARGE (>300 lines or >10 files), recommend splitting:**
```
⚠️ This PR is large ({FILES_CHANGED} files, {LINES_CHANGED} lines changed).

**Recommendation:** Consider splitting into smaller PRs for:
- Faster review cycles
- Lower merge risk
- Easier to understand
- Atomic changes

**Suggested splits:**
1. Core logic changes (backend/modules/)
2. API endpoint changes (backend/api/)
3. Frontend integration (client-dashboard/)
4. Tests (backend/tests/, e2e-tests/)

**Or:** Create PR as-is if changes are tightly coupled.

Would you like to:
a) Create PR as-is (all changes together)
b) Help me identify how to split this
c) Cancel and split manually
```

**STOP and confirm with user:**
```
I'm about to create a PR from the following branch:

**Branch:** {current-branch}
**Base:** main
**Size:** {FILES_CHANGED} files, {LINES_CHANGED} lines ({size-category})

**Recent commits on this branch:**
{show git log --oneline main..HEAD | head -10}

**Files changed:**
{show git diff --stat main...HEAD}

Is this correct? Should I proceed with creating a PR from this branch?
```

**Wait for explicit user confirmation before proceeding.**

**If user says NO:**
- Ask which branch they want to use
- Or exit and let them switch branches manually

**If user says YES, check if branch is pushed:**
```bash
git status
```

**If branch not pushed:**
```bash
git push -u origin {branch-name}
```

### 2. Analyze Changes

**Get commit history on branch:**
```bash
# Commits since diverging from main
git log main..HEAD --oneline

# Full diff from main
git diff main...HEAD --stat
```

**Extract ticket reference from branch name:**
- Pattern: `TICKET-XXX`, `FEAT-XXX`, `feature/TICKET-XXX`, etc.
- Examples:
  - `TICKET-123-fix-streaming` → TICKET-123
  - `feat/TICKET-456-new-dashboard` → TICKET-456
  - `username/feature-exploration` → No ticket (generic)

### 3. Discover Related Documents

**If ticket found, check for:**
```bash
# Implementation plan
specs/features/FEAT-{ticket}/implementation-plan*.md

# Test plan
specs/testing/e2e/*{ticket}*.md

# Cached ticket
.claude/cache/TICKET-{ticket}.md

# Cached Confluence
.claude/cache/CONF-*.md

# Code review (if already done)
.claude/reviews/*review.md
```

**Read discovered documents** to understand context.

### 4. Generate PR Title

**Title Format:**

**If ticket found:**
```
feat: [Brief description from ticket summary]
fix: [Brief description]
chore: [Brief description]
docs: [Brief description]
```

**Prefix guidelines:**
- `feat:` - New feature
- `fix:` - Bug fix
- `chore:` - Maintenance, refactoring
- `docs:` - Documentation only
- `test:` - Test additions/updates
- `perf:` - Performance improvements

**If no ticket:**
- Derive from commit messages
- Ask user for title if unclear

**Keep title concise (<70 characters)**

### 5. Generate PR Description

**Read templates:**
- Check `.claude/templates/pr_description.md`
- Check `.github/pull_request_template.md`
- Use default template if none exist

**Generate comprehensive description:**

```markdown
## What does this PR do?

[Summary from ticket or commits - 1-2 sentences]

## Why are we doing this?

**Jira Ticket:** [TICKET-XXX]({jira-url}/browse/TICKET-XXX)

[Context from ticket description]

## What problem does it solve?

[Problem statement from ticket or commit analysis]

## How does it solve the problem?

[Technical approach - read from implementation plan if exists]

Key changes:
- [Change 1 with file reference]
- [Change 2 with file reference]

## What are the changes?

### User-Facing Changes
- [List changes visible to end users]

### Internal/Technical Changes
- Modified: `client-dashboard/src/pages/run/page.tsx` - [description]
- Added: `tests/e2e/streaming.spec.ts` - [description]

### Breaking Changes
- [ ] None
- [ ] [List breaking changes if any]

## How to verify it

### Automated Verification
- [x] Tests pass: `npm test` ✅
- [x] Type checking passes: `npm run check` ✅
- [x] Linting passes: `npm run lint` ✅
- [ ] Build succeeds: `npm run build` [Run if possible]

### Manual Verification
- [ ] Navigate to running workflow run details page
- [ ] Verify status updates automatically without refresh
- [ ] Verify SSE connection in Network tab

## Related Documents

- Implementation Plan: `specs/features/FEAT-XXX/implementation-plan.md`
- Test Plan: `specs/testing/e2e/feature-e2e-testplan.md`
- Jira Ticket: [TICKET-XXX]({jira-url}/browse/TICKET-XXX)
- Code Review: `.claude/reviews/{number}_review.md` (if done)

## Checklist

- [x] Tests added/updated
- [x] Documentation updated (if needed)
- [x] No breaking changes
- [x] Security implications considered
- [x] Performance implications considered

## Screenshots/Examples

[If applicable - can add after PR created]

## Additional Notes

[Any other context, gotcas, follow-up work]
```

### 6. Run Automated Verification

**Attempt to run verification commands:**

```bash
# Try project test command
npm test 2>&1 | head -20
# or: pytest, make test, cargo test, etc.

# Try linting
npm run lint 2>&1 | head -20

# Try type checking
npm run check 2>&1 | head -20
```

**Mark checkboxes based on results:**
- `[x]` if passed
- `[ ]` if failed (with note about failure)
- `[ ]` if couldn't run (with note)

### 7. Create PR on GitHub

**Save description locally:**
```bash
mkdir -p .claude/prs
# Write to .claude/prs/draft-{branch-name}.md
```

**Create PR:**
```bash
gh pr create \
  --title "{generated-title}" \
  --body-file .claude/prs/draft-{branch-name}.md \
  --base main
```

**Get PR number from response:**
```bash
# gh returns URL like: https://github.com/org/repo/pull/123
# Extract: 123
```

**Rename description file:**
```bash
mv .claude/prs/draft-{branch-name}.md .claude/prs/{number}_description.md
```

### 8. Add Labels (If Applicable)

**Extract labels from:**
- Ticket labels (if Jira ticket found)
- Commit message patterns (feat, fix, docs, test)
- File changes (frontend, backend, both)

**Add labels:**
```bash
gh pr edit {number} --add-label "feature"
gh pr edit {number} --add-label "frontend"
gh pr edit {number} --add-label "backend"
```

### 9. Present PR Information

```
## PR Created Successfully!

**PR:** #{number} - {title}
**URL:** {pr-url}
**Base Branch:** main
**Head Branch:** {current-branch}

**Description Saved:** `.claude/prs/{number}_description.md`

### Summary
- Files changed: {N}
- Commits: {M}
- Related ticket: TICKET-XXX
- Implementation plan: `specs/features/FEAT-XXX/implementation-plan.md`

### Verification Status
- [x] Tests: Passed
- [x] Linting: Passed
- [ ] Manual testing: Required (see PR description)

### Next Steps
1. Review PR description on GitHub
2. Complete manual verification steps
3. Request reviewers
4. Wait for CI/CD checks
5. Address review feedback
6. Merge when approved

**PR URL:** {pr-url}
```

## Important Notes

### Safety Checks

**CRITICAL: Always verify branch before creating PR**

The skill will:
1. ✅ Check current branch is NOT main/master
2. ✅ Show branch name and recent commits
3. ✅ Show files that will be in the PR
4. ✅ **WAIT for explicit user confirmation**
5. ✅ Only proceed after user says "yes"

**This prevents:**
- Creating PR from wrong branch
- Creating PR from main/master
- Including unintended changes
- Accidentally exposing work-in-progress

### Branch Requirements

**Must be on feature branch:**
- Not main/master
- Branch should be pushed to remote
- User must confirm branch name and changes

**If branch not pushed:**
```bash
git push -u origin {branch-name}
```

### PR Description Quality

**Comprehensive but concise:**
- Focus on "why" not just "what"
- Link to related documents
- Include verification steps
- Note breaking changes prominently

**Run verifications:**
- Always try to run automated checks
- Mark what passed/failed
- Note what requires manual testing

### Related Documents

**Automatically discovers and links:**
- Implementation plans in `specs/features/`
- Test plans in `specs/testing/e2e/`
- Jira tickets in `.claude/cache/`
- Confluence pages in `.claude/cache/`
- Code reviews in `.claude/reviews/`

### Labels

**Common labels:**
- `feature` - New functionality
- `fix` - Bug fixes
- `chore` - Maintenance
- `docs` - Documentation
- `frontend` - Frontend changes
- `backend` - Backend changes
- `tests` - Test updates

**Add labels based on:**
- Changes in client-dashboard/ → `frontend`
- Changes in backend/ → `backend`
- Prefix in title → `feat`, `fix`, `chore`, `docs`

## Usage Examples

```bash
# Create PR from current branch
/create-pr

# Create PR with specific title
/create-pr "feat: Add real-time workflow streaming"

# Create PR with custom base branch
/create-pr --base release/2.1

# Create PR as draft
/create-pr --draft
```

## Enhanced Workflow

**Option 1: Simple (just create PR):**
```bash
/create-pr
# Creates PR with auto-generated description
# You can edit description on GitHub after
```

**Option 2: Enhanced (run describe-pr after):**
```bash
/create-pr
# Creates basic PR

/describe-pr {pr-number}
# Enhances description with more detail, runs verifications
# Updates PR description automatically
```

**Option 3: All-in-One:**
The skill can optionally call `/describe-pr` internally after creating PR to generate comprehensive description immediately.

## Integration with Other Skills

**Complete PR creation workflow:**

```bash
# After implementation complete
/validate-plan

# Run code review
/code-review

# Create PR with comprehensive description
/create-pr

# PR created and description generated!
```

**Or manual approach:**

```bash
# Create PR manually on GitHub
gh pr create --title "feat: Add feature" --body "Initial"

# Generate comprehensive description
/describe-pr {pr-number}
```

## Default Template

If no template found, uses this structure:

```markdown
## What does this PR do?
[Brief summary]

## Why are we doing this?
[Context and motivation]

## What problem does it solve?
[Problem statement]

## How does it solve the problem?
[Technical approach]

## What are the changes?

### User-Facing Changes
- [List]

### Internal/Technical Changes
- [List with file references]

### Breaking Changes
- [ ] None

## How to verify it

### Automated Verification
- [ ] Tests pass: `npm test`
- [ ] Linting passes: `npm run lint`
- [ ] Type checking passes: `npm run check`

### Manual Verification
- [ ] [Steps to test manually]

## Related Documents

- Implementation Plan: [link]
- Test Plan: [link]
- Jira Ticket: [link]

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Security implications considered
- [ ] Performance implications considered
```

## Parameters (Optional)

```bash
# Basic
/create-pr

# With title
/create-pr "feat: Add real-time streaming"

# As draft
/create-pr --draft

# Different base branch
/create-pr --base release/2.1

# With reviewers
/create-pr --reviewer username1,username2

# With labels
/create-pr --label feature,frontend
```

## Success Criteria

- [x] PR created on GitHub
- [x] Comprehensive description generated
- [x] Related documents linked
- [x] Automated verifications run and marked
- [x] Manual verification steps documented
- [x] Labels added appropriately
- [x] PR URL provided to user

## File Storage

**PR description saved to:**
- `.claude/prs/{pr-number}_description.md`

This allows:
- Local reference
- Can be edited before updating GitHub
- Tracked in git (if desired)
- Reusable for similar PRs
