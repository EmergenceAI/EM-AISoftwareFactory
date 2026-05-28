---
name: update-e2e-testplan
description: Update end-to-end test plans between two releases to cover new features and changes
---

# Update E2E Test Plan

Update existing end-to-end test plans to reflect changes between two releases, adding tests for new features and updating existing tests for modifications.

## When to Use This Skill

Use this skill to update E2E test plans when:
- Preparing for a new release
- Features have been added or modified
- API contracts have changed
- Integration points have been updated
- Test coverage needs to be expanded

## Initial Setup

When invoked, respond with:

```
I'll help you update the E2E test plan between two releases.

Please provide:
1. Previous release/tag (e.g., v2.0.0, release/2.0, or commit SHA)
2. Current release/tag (e.g., v2.1.0, HEAD, main)
3. Existing test plan path (e.g., specs/testing/e2e/release-2.0-e2e-testplan.md)

Or I can help you:
- Find available releases: `git tag --list`
- Find existing test plans: `specs/testing/e2e/*.md`
```

Then wait for user input.

## Steps to Follow

### Step 1: Identify Releases and Validate

**Get available releases:**
```bash
git tag --list --sort=-version:refname | head -20
```

**Validate releases exist:**
```bash
git rev-parse {previous-release}
git rev-parse {current-release}
```

**Find existing test plans:**
```bash
find specs/testing/e2e -name "*testplan.md"
```

### Step 2: Analyze Changes Between Releases

**Get comprehensive diff:**
```bash
# Overall stats
git diff --stat {previous-release}..{current-release}

# Detailed changes
git diff {previous-release}..{current-release}

# Commit history
git log --oneline {previous-release}..{current-release}
```

**Identify changed areas:**
- New files added
- Modified files
- Deleted files
- Package dependencies changed
- Database migrations added

### Step 3: Categorize Changes

**Use parallel agents to categorize changes:**

**Agent 1 - New Features:**
- Find new UI components
- Find new API endpoints
- Find new service methods
- Return: List of new features with file paths

**Agent 2 - Modified Features:**
- Find modified components
- Find changed API contracts
- Find updated business logic
- Return: List of modifications with file:line references

**Agent 3 - Breaking Changes:**
- Find removed endpoints
- Find changed data models
- Find deprecated features
- Return: List of breaking changes with impact

**Agent 4 - Related Tickets:**
- Search commit messages for ticket references (SEMI-XXX)
- Fetch related Jira tickets
- Return: List of tickets implemented between releases

### Step 4: Read Existing Test Plan

**Read the current test plan completely:**
- Understand existing test coverage
- Identify existing test cases
- Note test data requirements
- Review success criteria

### Step 5: Map Changes to Test Impact

**For each change, determine:**

**New Test Cases Needed:**
- New features require new test scenarios
- New integration points need integration tests
- New API endpoints need API tests

**Existing Tests to Update:**
- Modified features need updated test steps
- Changed APIs need updated expected results
- Altered flows need updated navigation

**Tests to Deprecate:**
- Removed features should have tests marked deprecated
- Changed workflows may obsolete old tests

**Tests to Remove:**
- Tests for completely removed functionality

### Step 6: Generate Updated Test Plan

**Create new version of test plan:**

**Filename:** `specs/testing/e2e/{release}-e2e-testplan.md`

**Update frontmatter:**
```yaml
---
feature: "Release {version}"
previous_version: "{previous-release}"
current_version: "{current-release}"
created_date: [original date]
created_by: [original author]
test_plan_version: [incremented version, e.g., 2.0]
status: draft
last_updated: [current date]
last_updated_by: [username]
change_summary: "Updated for release {version} - added {N} new tests, updated {M} tests, deprecated {K} tests"
---
```

**Add Change Summary section:**
```markdown
## Change Summary ({previous-release} → {current-release})

### Release Changes

**New Features:**
- Feature A - [Brief description] (SEMI-XXX)
- Feature B - [Brief description] (SEMI-YYY)

**Modified Features:**
- Feature C - [What changed] (SEMI-ZZZ)

**Deprecated Features:**
- Feature D - [Marked for removal]

**Breaking Changes:**
- API endpoint /old/path removed
- Database schema changed for table X

### Test Plan Updates

**New Test Cases Added:** {N}
- TC-XXX: Test new feature A
- TC-YYY: Test new feature B

**Updated Test Cases:** {M}
- TC-003: Updated for API changes
- TC-015: Updated expected results

**Deprecated Test Cases:** {K}
- ~~TC-050: Old feature removed~~

**Removed Test Cases:** {L}
- Removed tests for feature D (no longer exists)

### Coverage Impact

| Category | Previous | Current | Change |
|----------|----------|---------|--------|
| Total Tests | {N} | {N+X} | +{X} |
| Functional | {N} | {N} | +{X} |
| Integration | {N} | {N} | +{X} |
| Performance | {N} | {N} | = |

### Test Data Updates

**New Test Data Required:**
- [New data needed for feature A]

**Updated Test Data:**
- [Modified data for feature C]
```

**Update Test Scenarios:**

Mark deprecated tests:
```markdown
### ~~TC-050: Old Feature Test~~ [DEPRECATED]
**Status:** ⚠️ DEPRECATED - Feature removed in v2.1.0
**Reason:** Feature D was removed
**Removed in:** Release v2.1.0
```

Add new tests:
```markdown
### TC-XXX: [New Feature A Test] [NEW]
**Status:** ✨ NEW in v2.1.0
**Related:** SEMI-XXX
**Priority:** High
**Type:** Functional

[Test case details...]
```

Update existing tests:
```markdown
### TC-003: [Modified Feature Test] [UPDATED]
**Status:** ✏️ UPDATED for v2.1.0
**Changes:** API endpoint changed from /old to /new

**Previous Expected Result:**
- API returns data at /old/endpoint

**Updated Expected Result:**
- API returns data at /new/endpoint
- Response includes new field: `additionalData`

[Updated test steps...]
```

### Step 7: Generate Change Report

Create detailed change report:

```markdown
## Detailed Change Analysis

### New Features Requiring Tests

#### Feature A: [Name] (SEMI-XXX)

**Description:** [What was added]

**Files Changed:**
- `client-dashboard/src/components/FeatureA/` (new)
- `backend/api/v2/featurea.py` (new)

**Test Cases Added:**
- TC-XXX: Primary user flow
- TC-YYY: Edge case handling
- TC-ZZZ: Integration with existing feature

**Test Data Required:**
- New user role: feature_a_user
- Sample data: 10 feature A records

---

#### Feature B: [Name] (SEMI-YYY)

[Similar structure...]

### Modified Features

#### Feature C: [Name] (SEMI-ZZZ)

**Description:** [What changed]

**Files Changed:**
- `client-dashboard/src/components/FeatureC/index.tsx` (+15, -8)
- `backend/services/featurec_service.py` (+42, -20)

**Breaking Changes:**
- API response structure changed
- New required field: `timestamp`

**Test Cases Updated:**
- TC-003: Updated expected API response
- TC-015: Added validation for new field

**Migration Notes:**
- Old API still works with deprecation warning
- Will be removed in v3.0.0

### Deprecated Features

#### Feature D: [Name]

**Reason:** Replaced by Feature A

**Files Removed:**
- `client-dashboard/src/components/FeatureD/` (removed)

**Test Cases Deprecated:**
- ~~TC-050: Feature D primary flow~~
- ~~TC-051: Feature D edge cases~~

**Migration Path:**
- Users should use Feature A instead
- Migration guide: [link]
```

### Step 8: Update Test Automation

**Identify automation updates needed:**

```markdown
## Test Automation Updates

### New Automated Tests Required

**Location:** `tests/e2e/feature-a/`

```typescript
// tests/e2e/feature-a/happy-path.test.ts
describe('Feature A - Primary Flow', () => {
  test('TC-XXX: User can create Feature A item', async () => {
    // New test implementation
  });
});
```

### Updated Automated Tests

**Location:** `tests/e2e/feature-c/api-integration.test.ts`

```diff
- expect(response.data).toHaveProperty('oldField');
+ expect(response.data).toHaveProperty('timestamp');
+ expect(response.data.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}/);
```

### Deprecated Automated Tests

**Action Required:**
- Remove `tests/e2e/feature-d/` directory
- Update CI/CD to skip deprecated tests
```

### Step 9: Update Environment and Data Requirements

**Document new requirements:**

```markdown
## Updated Environment Setup

### New Services Required
- Feature A API endpoint (new microservice)

### Configuration Changes
```bash
# New environment variables
export FEATURE_A_ENABLED=true
export FEATURE_A_API_KEY=xxx
```

### Database Migration
```bash
# Run new migrations
alembic upgrade head

# Migrations added:
- 2026_01_14_add_feature_a_tables.py
- 2026_01_15_modify_feature_c_schema.py
```

### Updated Test Data

**New Data:**
- `tests/fixtures/feature-a-data.json`

**Modified Data:**
- `tests/fixtures/feature-c-data.json` (updated schema)

**Deprecated Data:**
- ~~`tests/fixtures/feature-d-data.json`~~ (no longer needed)
```

### Step 10: Create Migration Guide for Testers

**Document how to migrate test execution:**

```markdown
## Test Execution Migration Guide

### For QA Testers

**What's New:**
1. Feature A requires new test user role
2. Feature C has new validation - update test scripts
3. Feature D removed - skip those test cases

**Setup Changes:**
```bash
# Old setup
npm run setup-tests

# New setup (includes Feature A data)
npm run setup-tests --with-feature-a
```

**Execution Changes:**
- TC-050, TC-051 deprecated - skip or remove from test runs
- TC-XXX, TC-YYY new - add to regression suite
- TC-003, TC-015 updated - review new expected results

### For Automation Engineers

**Update Test Framework:**
```bash
# Update dependencies
npm install playwright@latest

# Update test data
npm run seed-test-data
```

**CI/CD Updates:**
- Add Feature A tests to nightly run
- Remove deprecated Feature D tests
- Update smoke test suite
```

### Step 11: Save Updated Test Plan

**Save to:** `specs/testing/e2e/{current-release}-e2e-testplan.md`

**Also update:** `specs/testing/e2e/CHANGELOG.md`

```markdown
# E2E Test Plan Changelog

## Version 2.1.0 (2026-01-14)

**Previous Version:** 2.0.0
**Changes:**
- Added 15 new test cases for Feature A and Feature B
- Updated 8 test cases for modified Feature C
- Deprecated 2 test cases for removed Feature D
- Updated test data requirements
- Added new environment setup steps

**Tickets Covered:**
- SEMI-XXX: Feature A implementation
- SEMI-YYY: Feature B implementation
- SEMI-ZZZ: Feature C enhancements

**Breaking Changes:**
- Feature D removed - migrate to Feature A
- API endpoint /old/path removed

---

## Version 2.0.0 (2025-12-01)

[Previous changelog entries...]
```

### Step 12: Present Update Summary

Show summary to user:

```
I've updated the E2E test plan from {previous-release} to {current-release}:

**Location:** `specs/testing/e2e/{current-release}-e2e-testplan.md`

**Changes Summary:**
- New test cases: {N} (for new features)
- Updated test cases: {M} (for modifications)
- Deprecated test cases: {K} (features removed)

**Coverage:**
- Previous: {N} total tests
- Current: {N+X} total tests (+{X})

**New Features Tested:**
- Feature A (SEMI-XXX): {N} test cases
- Feature B (SEMI-YYY): {M} test cases

**Breaking Changes:**
- {K} tests deprecated due to removed features
- {L} tests updated for API changes

**Action Required:**
1. Review new test cases
2. Update test automation scripts
3. Set up new test data
4. Run updated test suite
5. Validate breaking changes

**Test Automation:**
- New automated tests: {N}
- Updated automated tests: {M}
- Files to update: `tests/e2e/{features}/`

Would you like me to:
- Generate automation code stubs?
- Create test data fixtures?
- Detail specific test cases?
```

## Important Guidelines

**Be Thorough:**
- Compare all changes between releases
- Don't miss new features or modifications
- Track deprecations and removals

**Be Clear About Changes:**
- Mark new tests clearly with [NEW]
- Mark updates with [UPDATED] and change description
- Mark deprecated tests with [DEPRECATED]

**Maintain Traceability:**
- Link to commit SHAs
- Reference Jira tickets
- Note file changes

**Consider Impact:**
- Breaking changes need immediate testing
- New features need comprehensive coverage
- Modifications may need regression testing

**Update Automation:**
- Identify which tests need automation updates
- Provide code examples where helpful
- Note framework/dependency changes

## Integration with Other Skills

**Complete release testing workflow:**

```bash
# 1. Compare releases
git diff v2.0.0..v2.1.0

# 2. Update test plan
/update-e2e-testplan v2.0.0 v2.1.0

# 3. Review updated plan
cat specs/testing/e2e/v2.1.0-e2e-testplan.md

# 4. Execute updated tests
npm run test:e2e

# 5. Code review for test changes
/code-review tests/e2e/
```

**After major implementation:**

```bash
1. /implement-plan SEMI-790        # Implement feature
2. /create-e2e-testplan SEMI-790   # Create initial tests
3. [Features get merged]
4. /update-e2e-testplan            # Update for release
```

## Usage Examples

```bash
# Update test plan between tagged releases
/update-e2e-testplan v2.0.0 v2.1.0

# Update using commit SHAs
/update-e2e-testplan abc123 def456

# Update from release branch to main
/update-e2e-testplan release/2.0 main

# Update with specific test plan
/update-e2e-testplan v2.0.0 v2.1.0 specs/testing/e2e/main-testplan.md
```

## Handling Special Cases

**Hotfix Releases:**
- Focus on changed components only
- Regression test around fix area
- May not need full test plan update

**Major Version Updates:**
- Comprehensive review of all tests
- Expect significant changes
- May create new test plan rather than update

**Beta/RC Releases:**
- Update test plan incrementally
- Track issues found in testing
- Refine tests before final release
