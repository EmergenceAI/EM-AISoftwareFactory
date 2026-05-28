---
name: create-e2e-testplan
description: Create comprehensive end-to-end test plans for features and releases
---

# Create E2E Test Plan

Create comprehensive end-to-end test plans that cover critical user flows, integration points, and acceptance criteria.

## When to Use This Skill

Use this skill to create E2E test plans for:
- New features being developed
- Complete releases
- Critical user flows that need validation
- Integration testing scenarios
- Regression test suites

## Initial Setup

When invoked, respond with:

```
I'll help you create an end-to-end test plan.

Please provide:
1. Feature/ticket reference (e.g., SEMI-790) or release version (e.g., v2.1.0)
2. Scope: Is this for a single feature or an entire release?
3. Any specific user flows or scenarios to focus on?
```

Then wait for user input.

## Steps to Follow

### Step 1: Gather Context

**If ticket/feature provided:**
- Check if `.claude/cache/SEMI-XXX.md` exists and read it
- If not cached:
  - Invoke the `mcp__atlassian__jira_get_issue` tool with parameter `issue_key: "SEMI-XXX"`
  - Format the result as markdown
  - Save to `.claude/cache/SEMI-XXX.md` for reuse
  - Read the cached file to understand requirements

**If Confluence page referenced:**
- Extract page ID from URL if needed (pattern: `/pages/{page_id}/`)
- Check if `.claude/cache/CONF-{page-id}.md` exists and read it
- If not cached:
  - Invoke the `mcp__atlassian__confluence_get_page` tool with parameter `page_id: "{page_id}"`
  - Format the result as markdown
  - Save to `.claude/cache/CONF-{page-id}.md` for reuse
  - Read the cached file

**Find related documentation:**
- Implementation plan: `specs/features/FEAT-XXX/implementation-plan*.md`
- Existing research: `specs/research/*{topic}*.md`
- Code review: `.claude/reviews/{pr-number}_review.md`

**Read all discovered documents FULLY** (no limit/offset).

### Step 2: Research the Implementation

**Use parallel agents to understand the feature:**

**Agent 1 - Frontend Research:**
- Find UI components related to the feature
- Identify user interaction points
- Document navigation flows
- Return: Component paths, user actions, UI states

**Agent 2 - Backend Research:**
- Find API endpoints related to the feature
- Identify data models and business logic
- Document integration points
- Return: API routes, services, database tables

**Agent 3 - Integration Points:**
- Find external service integrations
- Identify dependencies on other features
- Document data flow across components
- Return: Integration points, dependencies

### Step 3: Identify Test Scenarios

Based on research findings, identify:

**Critical User Flows:**
- Primary use cases from ticket acceptance criteria
- Happy path scenarios
- Common user workflows

**Edge Cases:**
- Boundary conditions
- Error states
- Invalid inputs
- Race conditions

**Integration Scenarios:**
- Cross-component interactions
- External service integrations
- Database operations
- Real-time updates (if applicable)

**Non-Functional Requirements:**
- Performance expectations
- Security considerations
- Accessibility requirements
- Browser/device compatibility

### Step 4: Define Test Cases

For each test scenario, create structured test cases:

```markdown
### TC-{number}: {Test Case Title}

**Priority:** High | Medium | Low
**Type:** Functional | Integration | Performance | Security
**Prerequisites:**
- User logged in as [role]
- Feature flag [X] enabled
- Test data: [specific dataset]

**Test Steps:**
1. Navigate to [page/URL]
2. Click [button/link]
3. Enter [data] in [field]
4. Verify [expected result]
5. ...

**Expected Results:**
- [Specific outcome 1]
- [Specific outcome 2]
- UI displays [expected state]
- API returns [expected response]

**Test Data:**
- Input: [specific values]
- Expected output: [specific values]

**Acceptance Criteria Mapping:**
- ✓ Covers AC #1: [description]
- ✓ Covers AC #2: [description]
```

### Step 5: Define Test Data Requirements

**Identify data needs:**
- User accounts with specific roles/permissions
- Sample datasets (products, workflows, etc.)
- Configuration settings
- External service mocks/stubs

**Document test data setup:**
```markdown
## Test Data Requirements

### User Accounts
- `test_admin@example.com` - Admin role with full permissions
- `test_user@example.com` - Standard user role
- `test_readonly@example.com` - Read-only access

### Sample Data
- 10 workflow runs in various states (pending, running, completed, failed)
- 5 products with different configurations
- Historical data covering last 30 days

### Environment Configuration
- Feature flag `enable_streaming` = true
- API endpoint: `https://dev.example.com/api`
```

### Step 6: Define Environment Setup

**Document environment requirements:**
- Backend services needed
- Database state
- External service configurations
- Feature flags
- Environment variables

### Step 7: Create Test Execution Strategy

**Define execution approach:**

**Manual Testing:**
- Which scenarios require human verification
- Expected duration for manual tests
- Required test environment

**Automated Testing:**
- Which scenarios can be automated
- Recommended automation framework
- Test automation priority

**Regression Testing:**
- Which tests should be in regression suite
- How often to run regression tests

### Step 8: Generate Test Plan Document

**Filename:** `specs/testing/e2e/{feature-name}-e2e-testplan.md` or `specs/testing/e2e/{release}-e2e-testplan.md`

**Structure:**

```markdown
---
feature: "[Feature Name or Release Version]"
ticket: "SEMI-XXX" (if applicable)
created_date: YYYY-MM-DD
created_by: [username]
test_plan_version: 1.0
status: draft | approved | in-progress | completed
last_updated: YYYY-MM-DD
last_updated_by: [username]
---

# E2E Test Plan: [Feature Name or Release Version]

**Feature:** [Feature Name]
**Ticket:** [SEMI-XXX] ([Jira Link])
**Version:** 1.0
**Created:** YYYY-MM-DD
**Status:** Draft

## Overview

[Brief description of what's being tested and why]

## Scope

### In Scope
- [Feature area 1]
- [Feature area 2]
- [Integration with system X]

### Out of Scope
- [What's not being tested]
- [Deferred to other test plans]

## Test Objectives

- Validate [objective 1]
- Ensure [objective 2]
- Verify [objective 3]

## Related Documentation

- Implementation Plan: `specs/features/FEAT-XXX/implementation-plan.md`
- Jira Ticket: `.claude/cache/SEMI-XXX.md`
- API Documentation: [link]
- Design Document: `.claude/cache/CONF-123456.md`

## Environment Setup

### Prerequisites
- Services: [backend API, database, external services]
- Accounts: [test users with specific roles]
- Configuration: [feature flags, environment variables]

### Test Environment
- URL: https://dev.example.com
- API: https://dev.example.com/api
- Database: PostgreSQL (test instance)

### Test Data Setup
[Instructions to set up test data]

```bash
# Commands to prepare test environment
make setup-test-env
npm run seed-test-data
```

## Test Scenarios

### Functional Testing

#### TC-001: [Primary User Flow]
**Priority:** High
**Type:** Functional

**Prerequisites:**
- User logged in as admin
- Test data seeded

**Test Steps:**
1. Navigate to feature page
2. Perform action X
3. Verify result Y

**Expected Results:**
- Result Y appears
- No errors in console
- Data saved correctly

**Acceptance Criteria Mapping:**
- ✓ AC #1: User can perform action X
- ✓ AC #2: Result Y is displayed

---

#### TC-002: [Edge Case Scenario]
...

### Integration Testing

#### TC-101: [Cross-Component Integration]
**Priority:** High
**Type:** Integration

...

### Performance Testing

#### TC-201: [Load Test Scenario]
**Priority:** Medium
**Type:** Performance

**Test Steps:**
1. Set up load testing tool (k6, JMeter, etc.)
2. Simulate [N] concurrent users
3. Measure response times

**Expected Results:**
- p95 response time < 500ms
- No errors under load
- System remains stable

---

## Non-Functional Testing

### Security Testing
- [ ] Authentication properly enforced
- [ ] Authorization checks in place
- [ ] Input validation prevents injection
- [ ] Sensitive data not exposed

### Accessibility Testing
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] ARIA labels present
- [ ] Color contrast meets WCAG standards

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Test Data Requirements

### User Accounts
| Email | Role | Permissions |
|-------|------|-------------|
| test_admin@example.com | Admin | Full access |
| test_user@example.com | User | Standard access |

### Sample Data
- [Description of required data]
- [Scripts to generate data]

## Test Execution

### Manual Test Execution
**Duration:** ~2 hours
**Required:** QA tester familiar with feature

**Process:**
1. Set up test environment
2. Execute test cases in order
3. Document results in test management tool
4. Report bugs with reproducible steps

### Automated Test Execution
**Framework:** Playwright / Cypress / Selenium
**Location:** `tests/e2e/{feature-name}/`

**Run tests:**
```bash
npm run test:e2e
# or
pytest tests/e2e/
```

### Regression Testing
**Frequency:** Before each release
**Duration:** ~30 minutes
**Scope:** Core user flows

## Success Criteria

- [ ] All high-priority test cases pass
- [ ] No critical or high-severity bugs
- [ ] Performance benchmarks met
- [ ] Security checks pass
- [ ] Acceptance criteria validated

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| External service unavailable | Test blocked | Use mocks/stubs |
| Test data corruption | Flaky tests | Automated data reset |
| Environment instability | False failures | Health checks before tests |

## Test Results Tracking

**Test Execution Log:**
- Date: [When tests were run]
- Environment: [Which environment]
- Results: [Pass/Fail counts]
- Issues Found: [Links to bugs]

## Sign-off

- [ ] Test Plan Approved by: [Name]
- [ ] Tests Executed by: [Name]
- [ ] Results Reviewed by: [Name]
- [ ] Feature Approved for Release: [Name]
```

### Step 9: Present Test Plan

Show summary to user:

```
I've created an E2E test plan for [Feature/Release]:

**Location:** `specs/testing/e2e/{name}-e2e-testplan.md`

**Summary:**
- Total test cases: [N]
- High priority: [N]
- Medium priority: [N]
- Low priority: [N]

**Coverage:**
- Functional: [N] test cases
- Integration: [N] test cases
- Performance: [N] test cases
- Security: [N] checks

**Estimated Execution Time:**
- Manual: ~[X] hours
- Automated: ~[Y] minutes

Next steps:
1. Review and approve test plan
2. Set up test environment
3. Execute test cases
4. Track results

Would you like me to:
- Add more test scenarios?
- Focus on specific areas?
- Create automation scripts?
```

## Important Guidelines

**Be Comprehensive:**
- Cover happy paths and edge cases
- Include integration and non-functional testing
- Map all acceptance criteria to test cases

**Be Specific:**
- Detailed test steps anyone can follow
- Exact expected results
- Specific test data values

**Be Practical:**
- Prioritize high-value test cases
- Balance manual and automated testing
- Consider execution time

**Be Traceable:**
- Map to acceptance criteria
- Reference implementation details
- Link to requirements

**Leverage Existing Work:**
- Use implementation plans for context
- Reference code reviews for known issues
- Check validation reports for edge cases

## Integration with Other Skills

**Create test plan after implementation:**
```bash
1. /create-plan SEMI-790           # Plan feature
2. /implement-plan SEMI-790        # Implement feature
3. /validate-plan                  # Validate implementation
4. /create-e2e-testplan SEMI-790   # Create E2E test plan ← You are here
5. Execute tests
6. /code-review                    # Final review before release
```

**Use research for context:**
```bash
1. /research-codebase              # Understand existing feature
   "How does authentication work?"
2. /create-e2e-testplan            # Create tests for authentication
```

## Usage Examples

```bash
# Create test plan for a feature
/create-e2e-testplan SEMI-790

# Create test plan for a release
/create-e2e-testplan v2.1.0

# Create test plan with specific focus
/create-e2e-testplan SEMI-790 Focus on security testing
```

## Test Automation Recommendations

Based on the test plan, suggest which tests should be automated:

**High Priority for Automation:**
- Regression tests (run frequently)
- Smoke tests (quick validation)
- Critical user flows

**Medium Priority:**
- Integration tests
- Data validation tests

**Low Priority (Manual):**
- Visual design tests
- Exploratory testing
- User experience validation

Include example automation structure:
```
tests/e2e/
├── {feature-name}/
│   ├── setup.ts           # Test data and environment setup
│   ├── happy-path.test.ts # Primary user flows
│   ├── edge-cases.test.ts # Error and boundary conditions
│   └── integration.test.ts# Cross-component tests
└── helpers/
    └── common.ts          # Shared utilities
```
