---
name: validate-plan
description: Validate that an implementation plan was correctly executed and verify all success criteria
---

# Validate Plan

You are tasked with validating that an implementation plan was correctly executed, verifying all success criteria and identifying any deviations or issues.

## Initial Setup

When invoked:

1. **Determine context** - Are you in an existing conversation or starting fresh?
   - If existing: Review what was implemented in this session
   - If fresh: Need to discover what was done through git and codebase analysis

2. **Locate the plan:**
   - If plan path provided, use it
   - Otherwise, search recent commits for plan references or ask user

3. **Gather implementation evidence:**
   ```bash
   # Check recent commits
   git log --oneline -n 20
   git diff HEAD~N..HEAD  # Where N covers implementation commits

   # Run comprehensive checks (adapt to your project)
   make check test
   # Or npm test, pytest, cargo test, etc.
   ```

## Validation Process

### Step 1: Context Discovery

If starting fresh or need more context:

1. **Read the implementation plan completely**

2. **Identify what should have changed:**
   - List all files that should be modified
   - Note all success criteria (automated and manual)
   - Identify key functionality to verify

3. **Spawn parallel research tasks to discover implementation:**

   **Task 1 - Verify database changes:**
   - Research if migrations were added and schema changes match plan
   - Check: migration files, schema version, table structure
   - Return: What was implemented vs what plan specified

   **Task 2 - Verify code changes:**
   - Find all modified files related to feature
   - Compare actual changes to plan specifications
   - Return: File-by-file comparison of planned vs actual

   **Task 3 - Verify test coverage:**
   - Check if tests were added/modified as specified
   - Run test commands and capture results
   - Return: Test status and any missing coverage

### Step 2: Systematic Validation

For each phase in the plan:

1. **Check completion status:**
   - Look for checkmarks in the plan (`- [x]`)
   - Verify the actual code matches claimed completion

2. **Run automated verification:**
   - Execute each command from "Automated Verification"
   - Document pass/fail status
   - If failures, investigate root cause

3. **Assess manual criteria:**
   - List what needs manual testing
   - Provide clear steps for user verification

4. **Think deeply about edge cases:**
   - Were error conditions handled?
   - Are there missing validations?
   - Could the implementation break existing functionality?

### Step 2.5: Architecture & Documentation Alignment

Before generating the validation report, validate architectural alignment.

**Note:** This is a human-in-the-loop process. When violations or concerns are found:
- The user decides whether to fix code, update docs, or justify exceptions
- Re-run `/validate-plan` after making changes
- Loop continues until violations are resolved or explicitly acknowledged

**Discover architectural documentation:**

Spawn parallel research tasks using the `Agent` tool:

1. **Task 1 - Locate Architecture Docs:**
   - Use `Grep` and `Glob` to find architecture decision records (ADRs) and architecture documents
   - Search locations: `docs/adr/`, `docs/architecture/`, `specs/architecture/`
   - Also search for files matching: `*adr*`, `*decision*`, `*architecture*`
   - Return: List of relevant documents with paths and brief descriptions

2. **Task 2 - Identify Affected Architectural Layers:**
   - Use `Agent` with `Explore` to determine:
     - Which architectural layers are affected by this plan
     - What patterns/conventions are used in affected areas
     - Integration points that might have documented constraints
   - Return: Component-to-architecture mapping with file references

**Review each found document against the plan:**
- Does the plan contradict any documented architectural decisions?
- Does it follow established patterns found in the codebase?
- Does it introduce new patterns that should be documented?

**Assess documentation freshness:**
- Do existing architecture docs need updating based on this change?
- Should a new ADR be created for decisions made in this plan?
- Are component diagrams or data flow docs still accurate?

### Step 3: Generate Validation Report

Create comprehensive validation summary:

```markdown
## Validation Report: [Plan Name]

### Implementation Status
✓ Phase 1: [Name] - Fully implemented
✓ Phase 2: [Name] - Fully implemented
⚠️ Phase 3: [Name] - Partially implemented (see issues)

### Automated Verification Results
✓ Build passes: `make build`
✓ Tests pass: `make test`
✗ Linting issues: `make lint` (3 warnings)

### Code Review Findings

#### Matches Plan:
- Database migration correctly adds [table]
- API endpoints implement specified methods
- Error handling follows plan

#### Deviations from Plan:
- Used different variable names in [file:line]
- Added extra validation in [file:line] (improvement)

#### Potential Issues:
- Missing index on foreign key could impact performance
- No rollback handling in migration

### Manual Testing Required:
1. UI functionality:
   - [ ] Verify [feature] appears correctly
   - [ ] Test error states with invalid input

2. Integration:
   - [ ] Confirm works with existing [component]
   - [ ] Check performance with large datasets

### Recommendations:
- Address linting warnings before merge
- Consider adding integration test for [scenario]
- Document new API endpoints

### Architecture & Documentation Alignment

#### Documents Reviewed:
- `[path/to/adr-001.md]` - [Brief description]
- `[path/to/architecture.md]` - [Brief description]
(Or: "No architecture documentation found in standard locations")

#### Alignment Status:

##### 🔴 Violations (must address before merge):
- [Specific violation with ADR/doc reference and plan section]

##### 🟡 Concerns (recommend review):
- [Pattern deviation or implicit assumption with references]

##### 🟢 Aligned:
- [Areas properly following documented architecture]

#### Documentation Updates Needed:
- [ ] Update `[doc path]` to reflect [specific change]
- [ ] Consider new ADR for [pattern/decision introduced]
- [ ] No documentation updates needed ✓

### Recommended Actions

🔴 **To address violations (must fix before merge)**:
1. Review each violation with its ADR/doc reference
2. Fix code to align with documented architecture, OR
3. If intentional deviation: update ADR and justify in PR description
4. Re-run `/validate-plan` after changes

🟡 **To address concerns (recommended)**:
1. Discuss with team whether pattern deviation is appropriate
2. If pattern is evolving: update architecture docs
3. If deviation is minor: acknowledge in PR and proceed

🟢 **If aligned**: Proceed to PR submission
```

## Working with Existing Context

If you were part of the implementation:
- Review the conversation history
- Check your todo list for what was completed
- Focus validation on work done in this session
- Be honest about any shortcuts or incomplete items

## Important Guidelines

- **Be thorough but practical** - Focus on what matters
- **Run all automated checks** - Don't skip verification commands
- **Document everything** - Both successes and issues
- **Think critically** - Question if the implementation truly solves the problem
- **Consider maintenance** - Will this be maintainable long-term?

## Validation Checklist

Always verify:

- [ ] All phases marked complete are actually done
- [ ] Automated tests pass
- [ ] Code follows existing patterns
- [ ] No regressions introduced
- [ ] Error handling is robust
- [ ] Documentation updated if needed
- [ ] Manual test steps are clear
- [ ] Implementation aligns with documented ADRs/architecture
- [ ] No architectural constraints violated
- [ ] Architecture docs updated if implementation changes patterns

## Relationship to Other Commands

Recommended workflow:

1. `/create-plan` - Create the implementation plan
2. `/implement-plan` - Execute the implementation
3. `/validate-plan` - Verify implementation correctness
4. Create PR with validation report

The validation works best after commits are made, as it can analyze the git history to understand what was implemented.

**Remember:** Good validation catches issues before they reach production. Be constructive but thorough in identifying gaps or improvements.
