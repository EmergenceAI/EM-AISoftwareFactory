---
name: commit
description: Create git commits for changes made during the session with thoughtful, atomic commit organization
---

# Commit Changes

Create git commits for the changes made during this session with clear, descriptive messages and logical grouping.

## When to Use This Skill

Use this skill when:
- You've completed work and need to commit changes
- User asks to "commit", "save changes", or "create commits"
- Multiple changes need to be organized into logical commits
- Session work is complete and ready to be saved

## Process

### 1. Think About What Changed

**Review the session:**
- Review conversation history to understand what was accomplished
- Identify all changes made (files created, modified, deleted)
- Understand the purpose and context of each change

**Check current state:**
```bash
# See what changed
git status

# Review the actual changes
git diff

# Check for untracked files
git status --short
```

**Consider commit structure:**
- Should this be one commit or multiple logical commits?
- Which files belong together conceptually?
- What's the natural grouping of changes?

### 2. Plan Your Commit(s)

**Identify logical groups:**
- Group related changes together
- Separate unrelated changes into different commits
- Keep commits focused and atomic when possible

**Draft commit messages:**
- Use imperative mood ("Add feature" not "Added feature")
- Be clear and descriptive
- Focus on WHY the changes were made, not just WHAT changed
- First line: concise summary (<50 characters ideal, <72 max)
- Blank line
- Detailed explanation if needed (wrap at 72 characters)

**Examples of good commit messages:**

```
feat: Add real-time workflow status streaming

Implement SSE-based streaming for workflow run status updates.
Users can now see status changes without manual page refresh.

- Add useWorkflowRunLogs hook at page level
- Enable streaming for non-terminal run states
- Update status automatically across all tabs
```

```
docs: Add comprehensive SDLC skills documentation

Create detailed documentation for all Claude Code skills covering
the complete development lifecycle from research to PR creation.

- Add SKILLS_GUIDE.md for developers and non-developers
- Document all 12 skills with usage examples
- Include workflow diagrams and integration points
```

**Conventional commit prefixes:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting, missing semicolons, etc.
- `refactor:` - Code change that neither fixes a bug nor adds a feature
- `test:` - Adding or updating tests
- `chore:` - Maintenance, dependencies, build tools

### 3. Present Your Plan to the User

**Show your plan clearly:**

```
I plan to create [N] commit(s):

Commit 1: [Title]
Files:
- path/to/file1.ts
- path/to/file2.py
- path/to/file3.md

Message:
```
[Full commit message]
```

Commit 2: [Title]
Files:
- path/to/other-file.ts

Message:
```
[Full commit message]
```

Shall I proceed?
```

**Wait for user confirmation** before executing.

### 4. Execute Upon Confirmation

**Add files specifically:**
```bash
# NEVER use git add -A or git add .
# Always add specific files

git add path/to/file1.ts path/to/file2.py path/to/file3.md
git commit -m "commit message"
```

**For multi-line messages:**
```bash
git commit -m "$(cat <<'EOF'
feat: Add feature title

Detailed explanation of what changed and why.

- Bullet point 1
- Bullet point 2
EOF
)"
```

**Create commits in order:**
1. Add files for commit 1
2. Create commit 1
3. Add files for commit 2
4. Create commit 2
5. Continue for all planned commits

**Show the result:**
```bash
git log --oneline -n [number-of-commits-created]
```

### 5. Verify Success

**After committing:**
```bash
# Verify commits were created
git log --oneline -n 5

# Verify no unintended files left staged
git status

# Show what was committed
git show --stat HEAD
```

## Important Guidelines

### NEVER Add Attribution

**DO NOT include:**
- Co-author information
- Claude attribution
- "Generated with Claude" messages
- "Co-Authored-By" lines
- AI assistant credits

**Commits should be authored solely by the user.**

### Write As If User Wrote It

- Use first person or imperative mood
- Write naturally as the user would
- Focus on the work accomplished
- Don't mention that an AI helped

### Keep Commits Focused

**Atomic commits:**
- One logical change per commit
- All files in a commit should be related
- Commit can be reverted cleanly if needed

**Good groupings:**
- All files for a single feature
- Related documentation updates
- Test files with the code they test
- Configuration changes together

**Bad groupings:**
- Mixing unrelated features
- Combining fixes with new features
- Random assortment of files

### Commit Message Quality

**Good messages:**
```
feat: Add user authentication with OAuth

Implement OAuth 2.0 authentication flow using Auth0.
Users can now log in with Google or GitHub accounts.

- Add OAuth callback handler
- Create user session management
- Add login/logout UI components
```

**Bad messages:**
```
changes
fixed stuff
update files
WIP
.
```

### File Selection

**Always use specific files:**
```bash
# ✅ Good
git add src/auth.ts src/components/Login.tsx

# ❌ Bad
git add .
git add -A
git add --all
```

**Why?**
- Prevents accidentally committing unintended files
- Makes commit intent clear
- Avoids committing sensitive files (.env, credentials)
- Avoids committing large binaries or generated files

## Common Scenarios

### Scenario 1: Single Feature Implementation

**Changes:**
- Added new API endpoint
- Created frontend component
- Added tests
- Updated documentation

**Approach:**
- One commit with all related files
- Clear message explaining the feature
- List key changes in commit body

### Scenario 2: Multiple Unrelated Changes

**Changes:**
- Fixed bug in feature A
- Added new feature B
- Updated dependencies

**Approach:**
- Three separate commits
- Each with focused files and message
- Order: fixes first, then features, then chore

### Scenario 3: Large Refactoring

**Changes:**
- Renamed 20 files
- Updated imports everywhere
- No functionality changed

**Approach:**
- One commit (or a few logical commits)
- Clear message that this is refactoring
- Note that behavior unchanged

### Scenario 4: Documentation Only

**Changes:**
- Added README
- Updated API docs
- Added code comments

**Approach:**
- Use `docs:` prefix
- One or more commits depending on scope
- Group related documentation together

## Usage Examples

```bash
# Commit work from current session
/commit

# System will analyze changes and propose commit plan
```

## Integration with Workflow

**Typical workflow:**

```bash
# 1. Do work
/implement-plan TICKET-123

# 2. Validate
/validate-plan

# 3. Review
/code-review

# 4. Commit work
/commit

# 5. Create PR
/create-pr
```

**Or manual approach:**

```bash
# After completing work in session
/commit

# Then push and create PR separately
git push
gh pr create
```

## What This Skill Does NOT Do

**Does not:**
- Push commits to remote (user does that)
- Create PR (use `/create-pr` for that)
- Run tests or linting
- Amend existing commits (creates new ones)
- Rewrite history

**Only:**
- Organizes changes into logical commits
- Creates commits with good messages
- Stages specific files intentionally

## Success Criteria

- [x] Changes analyzed and understood
- [x] Commits planned logically
- [x] Clear, descriptive messages written
- [x] User approved the plan
- [x] Specific files added (not -A or .)
- [x] Commits created successfully
- [x] No AI attribution added
- [x] Result shown to user
- [x] No unintended files committed

## Remember

**You have full context:**
- You know what was done in this session
- You understand why changes were made
- You can write meaningful commit messages

**User trusts your judgment:**
- Group related changes appropriately
- Write clear, helpful messages
- Keep commits focused and atomic

**Write as the user:**
- Commits should look like the user created them
- No AI references or attribution
- Natural, professional git history
