---
name: split-pr
description: Split a large feature branch into multiple smaller, focused PRs with dependency tracking
---

# Split PR

Split a large feature branch into multiple smaller, focused pull requests. This skill helps you break down complex changes into reviewable chunks while maintaining proper dependencies.

## When to Use This Skill

Use this skill when you have:
- A feature branch with >300 lines changed
- Changes spanning multiple services (backend + frontend + tests)
- Mixed concerns that could be separated (API + UI + tests + docs)
- A PR that's too large for effective code review

**Before using:** Make sure all changes are committed on your feature branch.

## Process

### 1. Validate Current State

**Check current branch and changes:**
```bash
# Verify not on main/master
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo "ERROR: Cannot split from main/master"
    exit 1
fi

# Get all changed files
git diff main...HEAD --name-only

# Get diff stats
git diff main...HEAD --stat
```

**Show user what's on the branch:**
```
Your current branch: {branch-name}

Files changed: {count}
Total lines: {additions + deletions}

All committed changes:
{git log --oneline main..HEAD}
```

### 2. Analyze and Group Changed Files

**Categorize all changed files automatically:**

```bash
# Get all changed files
git diff main...HEAD --name-only
```

**Suggested groupings by service:**

**Group A: Backend API & Service Logic**
- backend/api/
- backend/modules/
- backend/core/

**Group B: Common/Shared Library**
- common/common_semi/model/
- common/common_semi/db/
- common/alembic/versions/

**Group C: Frontend (Dashboard)**
- client-dashboard/src/components/
- client-dashboard/src/pages/
- client-dashboard/src/api/

**Group D: Frontend (A2A Client)**
- a2a-client/src/

**Group E: Workflow Service**
- workflow/app/

**Group F: Agent Service**
- agent/

**Group G: MCP Service**
- mcp/app/

**Group H: Tests**
- backend/tests/
- e2e-tests/
- Any /tests/ directories

**Group I: Documentation & Config**
- *.md files
- docs/
- .github/
- scripts/

### 3. Present Suggested Grouping

**Show user the suggested splits:**

```
## Suggested PR Split

I analyzed your changes and suggest splitting into {N} PRs:

### PR 1: Backend API Changes (5 files, 120 lines)
Files:
  - backend/api/v2/products.py
  - backend/modules/v2/products/service.py
  - backend/modules/v2/products/schemas.py

Dependencies: None (can merge first)

### PR 2: Frontend Integration (4 files, 180 lines)
Files:
  - client-dashboard/src/components/ProductFilter.tsx
  - client-dashboard/src/api/use-products-query.ts
  - client-dashboard/src/types/product.ts

Dependencies: Requires PR 1 (needs API endpoints)

### PR 3: Integration Tests (3 files, 90 lines)
Files:
  - backend/tests/integration/products/test_product_filtering.py

Dependencies: Requires PR 1 (tests API)

### PR 4: Documentation (2 files, 40 lines)
Files:
  - README.md
  - docs/api/products.md

Dependencies: None (can merge anytime)


Would you like me to:
a) Create these PRs automatically (recommended grouping)
b) Let you customize the grouping first
c) Cancel (split manually)
```

**Wait for user decision.**

### 4. If User Chooses Custom Grouping

**Interactive file assignment:**

Use AskUserQuestion to let user assign files to groups:

```
For each changed file, assign to a PR group:

File: backend/api/v2/products.py
  → Group: [1-Backend, 2-Frontend, 3-Tests, 4-Docs, 5-New Group]

File: client-dashboard/src/components/ProductFilter.tsx
  → Group: [1-Backend, 2-Frontend, 3-Tests, 4-Docs, 5-New Group]

...
```

Or ask user to specify grouping:
```
Define your PR groups (one per line):

Group 1 Name: Backend API
Group 1 Files: backend/api/, backend/modules/

Group 2 Name: Frontend
Group 2 Files: client-dashboard/

Group 3 Name: Tests
Group 3 Files: backend/tests/, e2e-tests/
```

### 5. Detect Dependencies

**Analyze dependencies between groups:**

**Common dependency patterns:**
- Frontend depends on Backend (needs API endpoints)
- Tests depend on Backend (tests API/service logic)
- Docs depend on Backend (documents API)
- Common changes usually come first (other services depend on them)

**Ask user to confirm dependencies:**
```
Detected dependencies:

PR 2 (Frontend) → Depends on PR 1 (Backend)
  Reason: Frontend uses API endpoints added in PR 1

PR 3 (Tests) → Depends on PR 1 (Backend)
  Reason: Tests validate API changes in PR 1

Is this correct? Should any PR be independent?
```

### 6. Create Branches and PRs

**For each group:**

**Create new branch:**
```bash
# Save current branch
ORIGINAL_BRANCH=$(git branch --show-current)

# Create branch for group 1
git checkout -b {original-branch}-part-1-backend

# Reset to main
git reset main

# Stage only files for this group
git add backend/api/v2/products.py
git add backend/modules/v2/products/service.py

# Create commit
git commit -m "Part 1: Backend API changes for {feature}

Split from original branch: {original-branch}
Part 1 of {N}: Backend API implementation

{relevant commit messages from original branch}"

# Push branch
git push -u origin {original-branch}-part-1-backend
```

**Create PR for each branch:**
```bash
gh pr create \
  --base main \
  --title "Part 1/{N}: Backend API - {feature-name}" \
  --body "{generated-description-with-dependencies}"
```

**Return to original branch:**
```bash
git checkout {original-branch}
```

### 7. Link PRs with Dependencies

**In PR descriptions, add dependency information:**

For PR 2 (depends on PR 1):
```markdown
## Dependencies

⚠️ **Depends on:** #123 (Part 1: Backend API)

**Merge order:** 
1. Merge #123 first
2. Then merge this PR

**Why:** This PR uses API endpoints added in #123.
```

For independent PRs:
```markdown
## Dependencies

✅ **Independent** - Can be merged in any order
```

### 8. Present Results

**Summary for user:**

```
## PRs Created Successfully!

Created {N} PRs from branch: {original-branch}

### PR 1: Backend API
- **Number:** #123
- **Branch:** {original-branch}-part-1-backend  
- **Files:** 5
- **Lines:** 120
- **Dependencies:** None
- **URL:** {pr-url}
- **Status:** ✅ Ready to review

### PR 2: Frontend Integration
- **Number:** #124
- **Branch:** {original-branch}-part-2-frontend
- **Files:** 4
- **Lines:** 180
- **Dependencies:** #123 (merge #123 first)
- **URL:** {pr-url}
- **Status:** ⏳ Blocked by #123

### PR 3: Integration Tests
- **Number:** #125
- **Branch:** {original-branch}-part-3-tests
- **Files:** 3
- **Lines:** 90
- **Dependencies:** #123 (tests API)
- **URL:** {pr-url}
- **Status:** ⏳ Blocked by #123

### PR 4: Documentation
- **Number:** #126
- **Branch:** {original-branch}-part-4-docs
- **Files:** 2
- **Lines:** 40
- **Dependencies:** None
- **URL:** {pr-url}
- **Status:** ✅ Ready to review


## Merge Strategy

**Recommended order:**
1. Merge #123 (Backend API) first
2. Merge #126 (Documentation) anytime (independent)
3. After #123 merged: Merge #124 (Frontend)
4. After #123 merged: Merge #125 (Tests)

**Your original branch:** {original-branch}
  - Still exists with all changes
  - You can delete it after all parts are merged
  - Or keep it as reference

## Next Steps

1. Review each PR individually
2. Merge in recommended order
3. Monitor CI/CD for each PR
4. Delete part branches after merge (optional)
```

## Safety Mechanisms

### Preserve Original Branch

**CRITICAL: Never modify or delete the original branch**

The original branch stays intact with all changes. We only:
- Create NEW branches from main
- Selectively add files to each new branch
- Original branch remains as backup

If something goes wrong, user can delete the new branches and still has original work.

### Verify Each Part Builds

**Before creating PRs, verify each group:**

```bash
# For each group, verify it compiles/tests
git checkout {part-branch}

# Try to build (if applicable)
cd backend && uv sync  # For backend parts
cd client-dashboard && npm install  # For frontend parts

# Run quick check
npm run check  # or pytest, etc.
```

**If part doesn't build alone:**
- Warn user: "Part 2 may not build without Part 1"
- Suggest: "Consider including {file} in Part 2 as well"
- Ask: "Proceed anyway? (can fix in PR)"

### Handle Shared Files

**If same file needs to be in multiple groups:**

Ask user:
```
⚠️ Conflict: backend/core/config.py changed in both:
  - PR 1 (Backend API)
  - PR 3 (Tests)

Options:
a) Include in PR 1 only (tests PR will conflict until PR 1 merges)
b) Include in both (duplicate, resolve conflicts later)
c) Create separate PR just for shared files
```

## Advanced Features

### Merge Base Strategy

**For dependent PRs:**

**Option 1: All PRs based on main (default)**
```
main ← PR 1 (backend)
main ← PR 2 (frontend, will conflict until PR 1 merges)
main ← PR 3 (tests, will conflict until PR 1 merges)
```

**Option 2: Sequential PRs (safer for tight dependencies)**
```
main ← PR 1 (backend)
PR 1 ← PR 2 (frontend, based on PR 1 branch)
PR 1 ← PR 3 (tests, based on PR 1 branch)
```

Ask user which strategy to use.

### Commit Message Strategy

**Option 1: Single commit per PR (clean)**
- Create one new commit for each group
- Combines all relevant changes from original branch
- Clean history

**Option 2: Preserve original commits (history)**
- Cherry-pick commits from original branch
- Maintains original commit messages
- May be incomplete (commits mixed concerns)

Recommend Option 1 for cleaner history.

## Usage Examples

```bash
# Basic usage - analyze and suggest split
/split-pr

# With custom number of groups
/split-pr --groups 3

# Specify merge strategy upfront
/split-pr --strategy sequential

# Preview only (don't create PRs)
/split-pr --dry-run
```

## Integration with create-pr

**Workflow when create-pr detects large PR:**

```bash
# User runs create-pr on large branch
/create-pr

# create-pr detects: 450 lines changed
# Shows: "⚠️ Large PR detected. Consider using /split-pr to break this down."

# User runs split-pr
/split-pr

# split-pr analyzes and suggests groups
# User confirms
# split-pr creates multiple branches + PRs
# Done!
```

## File Grouping Heuristics

**Automatic grouping logic:**

1. **By service directory:**
   - All backend/ files → Backend group
   - All client-dashboard/ files → Frontend group
   - All workflow/ files → Workflow group

2. **By type:**
   - All test files → Tests group
   - All .md files → Docs group
   - All migration files → Migration group

3. **By coupling:**
   - If backend/api/ and backend/modules/ both changed for same feature → Same group
   - If backend/api/ and client-dashboard/ both changed for same feature → Can split (API first, then frontend)

4. **By commit:**
   - Analyze commit messages
   - Group files that were committed together
   - Respect logical boundaries

**Smart suggestions:**
- Common/ changes usually go in first PR (others depend on it)
- Migrations go with the code that uses new schema
- Tests can be separate (if testing existing API)
- Docs can be separate (independent)

## Edge Cases

### Circular Dependencies

If frontend and backend are tightly coupled:
- Suggest: Keep together in one PR
- Or: Create feature flag to deploy separately

### File Modified in Multiple Ways

If same file has unrelated changes:
- Suggest: Use `git add -p` to stage hunks separately
- Or: Keep all changes to that file in one PR

### Breaking Changes

If split would create breaking change:
- Warn: "Splitting this would break {service}"
- Suggest: Keep breaking change atomic (all in one PR)
- Or: Add backward compatibility layer first

## Success Criteria

After /split-pr completes:

- [x] Original branch preserved (unchanged)
- [x] N new branches created (one per group)
- [x] N PRs created on GitHub
- [x] Dependencies documented in PR descriptions
- [x] Merge order specified
- [x] Each PR focused and reviewable
- [x] User can merge PRs in sequence
- [x] Original branch can be deleted after all parts merged

## Output Format

```
## Split Complete! 🎉

Created {N} PRs from: {original-branch}

📋 **PR Summary:**

1. **#123** - Backend API (5 files, 120 lines) ✅ Ready
   Branch: {original}-part-1-backend
   
2. **#124** - Frontend (4 files, 180 lines) ⏳ Needs #123
   Branch: {original}-part-2-frontend
   
3. **#125** - Tests (3 files, 90 lines) ⏳ Needs #123
   Branch: {original}-part-3-tests

📊 **Merge Strategy:**
1. Review & merge #123 first
2. Then merge #124 and #125 (independent of each other)

💡 **Original Branch:** {original-branch}
   - Still exists with all changes
   - Can be deleted after all parts merged
   - Or keep as reference

🔗 **Quick Links:**
- PR #123: {url}
- PR #124: {url}
- PR #125: {url}
```

## Parameters

```bash
# Basic - auto-suggest grouping
/split-pr

# Specify number of groups
/split-pr --groups 3

# Custom merge strategy
/split-pr --strategy sequential  # PR 2 based on PR 1, PR 3 on PR 2
/split-pr --strategy independent # All based on main

# Dry run - show plan without creating
/split-pr --dry-run

# Use specific base branch
/split-pr --base develop
```

## Safety Features

### Confirmation Required

**Before creating any branches/PRs:**
```
I suggest splitting into {N} PRs:

{show suggested groups with files}

Proceed with this split? (yes/no)
```

### Rollback Plan

If user wants to undo:
```bash
# Delete created branches (if not merged)
git branch -D {original}-part-1-backend
git branch -D {original}-part-2-frontend

# Close PRs on GitHub
gh pr close {number}

# Original branch still intact!
git checkout {original-branch}
```

### Conflict Detection

Before creating PRs, check each part:
```bash
# Can this part merge cleanly to main?
git merge-base --is-ancestor main {part-branch}

# Are there conflicts?
git merge --no-commit --no-ff main
```

Warn user about potential conflicts.

## Integration with Other Skills

**Complete workflow for large changes:**

```bash
# 1. Implement feature on one branch
/implement-plan SEMI-123

# 2. Validate implementation
/validate-plan

# 3. Run code review on full change
/code-review

# 4. Split into smaller PRs
/split-pr

# 5. Each PR gets auto-reviewed separately
# (pr-auto-code-review.yml runs on each)

# 6. Merge in sequence
```

**Or:**

```bash
# After implementation, realize it's too big
git status  # 20 files changed!

# Split before creating any PR
/split-pr

# Creates 3 smaller PRs automatically
# Each gets reviewed separately
# Easier to merge incrementally
```

## Best Practices

### When to Split

**Good candidates for splitting:**
- Feature + tests → Separate (tests can follow)
- Backend + frontend → Separate (API first, UI second)
- Multiple independent features → Separate PRs
- Refactoring + new feature → Separate (refactor first)

**When NOT to split:**
- Changes are tightly coupled (split would break both)
- Splitting creates breaking changes
- Total changes <200 lines (already small)
- Changes to single service with <5 files

### Naming Convention

**Branch names:**
```
{original-branch}-part-{N}-{group-name}

Example:
  feat/SEMI-123-product-filtering
  → feat/SEMI-123-part-1-backend-api
  → feat/SEMI-123-part-2-frontend-ui
  → feat/SEMI-123-part-3-tests
```

**PR titles:**
```
Part {N}/{Total}: {Group Name} - {Feature}

Example:
  Part 1/3: Backend API - Add product filtering
  Part 2/3: Frontend UI - Add product filter component  
  Part 3/3: Tests - Integration tests for product filtering
```

### Documentation in Each PR

**Each PR description should include:**
```markdown
## Part {N} of {Total}: {Group Name}

**Feature:** {overall feature name}
**Ticket:** {JIRA-XXX}

### What's in This PR
{Changes specific to this part}

### What's NOT in This PR
{Deferred to other parts}

### Dependencies
- **Depends on:** #{other-PR} (must merge first)
- **Blocks:** #{dependent-PR} (should merge before)

### Related PRs
- Part 1: #{number} - Backend API
- Part 2: #{number} - Frontend (this PR)
- Part 3: #{number} - Tests

### Merge Order
1. Merge Part 1 first
2. Then merge Part 2 (this PR)
3. Finally merge Part 3
```

## Limitations

**What this skill CAN'T do:**
- Automatically resolve conflicts between parts
- Determine optimal split (requires human judgment)
- Guarantee each part builds independently
- Predict all dependencies

**What it CAN do:**
- Suggest logical groupings based on file paths
- Create branches and PRs automatically
- Document dependencies
- Save time on mechanical git operations

## Example Session

```
User: /split-pr

Claude: Analyzing your branch feat/SEMI-456-dashboard-filtering...

Found 12 files changed, 520 lines.

I suggest splitting into 3 PRs:

PR 1: Backend API (5 files, 180 lines)
  - backend/api/v2/products.py
  - backend/modules/v2/products/service.py
  - backend/modules/v2/products/schemas.py
  Dependencies: None

PR 2: Frontend (5 files, 260 lines)
  - client-dashboard/src/components/ProductFilter.tsx
  - client-dashboard/src/api/use-products-query.ts
  Dependencies: PR 1 (needs API)

PR 3: Tests (2 files, 80 lines)
  - backend/tests/integration/products/test_filtering.py
  Dependencies: PR 1 (tests API)

Proceed with this split? (yes/customize/cancel)

User: yes

Claude: Creating branches and PRs...

✅ Created branch: feat/SEMI-456-part-1-backend-api
✅ Created PR #789: Part 1/3: Backend API - Product filtering
✅ Created branch: feat/SEMI-456-part-2-frontend
✅ Created PR #790: Part 2/3: Frontend - Product filter UI
✅ Created branch: feat/SEMI-456-part-3-tests
✅ Created PR #791: Part 3/3: Tests - Product filtering tests

All PRs created! 

Merge order: #789 → #790 and #791

Original branch feat/SEMI-456-dashboard-filtering preserved.
```
