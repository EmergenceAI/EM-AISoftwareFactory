---
name: implement-plan
description: Implement features from Jira tickets with structured phases and verification
---

# Implement Plan

You are tasked with implementing a Jira ticket by creating and executing a phased implementation plan.

## Getting Started

When given a ticket reference (e.g., `@SEMI-123` or `SEMI-456`):

### Phase 0: Research and Planning

1. **Fetch ticket context** (cached for performance):
   - Check if `.claude/cache/SEMI-XXX.md` exists
   - If exists: Read it silently (already fetched)
   - If not exists: Fetch once and cache it:
     - Invoke the `mcp__atlassian__jira_get_issue` tool with parameter `issue_key: "SEMI-XXX"`
     - Format the result as markdown
     - Save to `.claude/cache/SEMI-XXX.md` for reuse
   - This happens once per ticket - subsequent uses are instant

2. **Read the ticket** completely - understand summary, description, acceptance criteria

3. **Check for existing plan** in `specs/features/FEAT-XXX/implementation-plan.md`

4. **Research the codebase**:
   - **Read all referenced files fully** - never use limit/offset parameters, you need complete context
   - Use Glob and Grep to find related files and patterns
   - Understand existing architecture and patterns
   - Identify dependencies and integration points
   - Look for similar implementations to maintain consistency

5. **Think deeply** about how the pieces fit together:
   - What files need to be created or modified?
   - What are the logical phases of work?
   - What are the risks and edge cases?
   - How does this fit with existing patterns?

6. **Create or update the implementation plan**:
   - If no plan exists, create `specs/features/FEAT-XXX/implementation-plan.md` (see template below)
   - If a plan exists but needs updates based on your research, update it
   - Break work into logical, testable phases
   - **Include unit tests as part of each phase's changes**
   - Define clear success criteria (automated and manual) for each phase
   - Include specific file paths and code patterns

7. **Present the plan for approval**:
   - Summarize your research findings
   - Present the phased implementation plan
   - Highlight any risks, assumptions, or questions
   - **Wait for explicit approval before implementing**

### After Approval: Implementation

8. **Create a todo list** to track your progress

9. **Start implementing** phase by phase, following the approved plan

If no ticket reference provided, ask for one.

## Implementation Philosophy

This skill follows a **research-first, plan-approval, then-implement** workflow:

1. **Research Phase**: Thoroughly understand the ticket, explore the codebase, and identify all affected areas
2. **Planning Phase**: Create a detailed, phased implementation plan with clear success criteria
3. **Approval Phase**: Present the plan and wait for explicit approval before coding
4. **Implementation Phase**: Execute the approved plan phase by phase with verification

Jira tickets describe what needs to be done, but reality can be messy. Your job is to:
- Research thoroughly before proposing a plan
- Follow the ticket requirements while adapting to what you find
- Break work into logical phases and implement each fully before moving to the next
- **Write unit tests for your changes** - tests are not optional, they're part of the implementation
- Verify your work makes sense in the broader codebase context
- Track progress using todo lists and plan checkboxes
- **Never start implementation without plan approval**

**Testing Philosophy:**
- Add unit tests as you implement, not as an afterthought
- Look at existing test patterns in the codebase and follow them
- Test the primary functionality, edge cases, and error conditions
- Ensure new tests pass AND existing tests still pass
- Tests should be readable and maintainable

When things don't match expectations during research or implementation, think about why and communicate clearly. The ticket and acceptance criteria are your guide, but your judgment matters too.

## Research and Approval Workflow

### During Research:
1. **Explore thoroughly**: Use Glob/Grep to find relevant files, read them completely
2. **Document findings**: Note file paths, line numbers, existing patterns, and dependencies
3. **Identify phases**: Break the work into logical, testable chunks
4. **Consider risks**: What could go wrong? What assumptions are you making?

### Presenting the Plan:
Format your plan presentation as:
```
# Research Summary for [TICKET-ID]

## What I Found
- [Key files and their purposes]
- [Existing patterns and architecture]
- [Dependencies and integration points]

## Proposed Implementation Plan
[Link to specs/features/FEAT-XXX/implementation-plan.md]

### Phase 1: [Name]
- Files to modify: [specific paths]
- Changes: [what will be done]
- Success criteria: [how we'll verify]

### Phase 2: [Name]
...

## Risks and Assumptions
- [Any concerns or unknowns]
- [Assumptions being made]

## Questions
- [Any clarifications needed]

Ready to proceed with implementation?
```

### After Approval:
Only after receiving explicit approval (user says "yes", "approved", "go ahead", etc.):
1. Create your todo list
2. Begin Phase 1 implementation
3. Follow the verification workflow for each phase

If you encounter a mismatch:
- STOP and think deeply about why the approach won't work
- Present the issue clearly:
  ```
  Issue in Phase [N]:
  Expected: [based on ticket/plan]
  Found: [actual situation]
  Why this matters: [explanation]

  How should I proceed?
  ```

## Verification Approach

After implementing a phase:
- **Write and run unit tests first** - verify your changes work as expected
- Run the success criteria checks:
  - Check project's build/test configuration files
  - Look in README, CONTRIBUTING, or CI config for test commands
  - Common locations: `Makefile`, `package.json`, `pom.xml`, `build.gradle`, `Rakefile`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `mix.exs`, etc.
- Ensure both new tests AND existing tests pass (no regressions)
- Fix any issues before proceeding
- Update your progress in both the plan and your todos
- Check off completed items in the plan file itself using Edit
- **Pause for human verification**: After completing all automated verification for a phase, pause and inform the human that the phase is ready for manual testing. Use this format:
  ```
  Phase [N] Complete - Ready for Manual Verification

  Automated verification passed:
  - ✅ Unit tests: X/X passing (ran [test command])
  - ✅ All tests: X/X passing (no regressions)
  - ✅ Type checking: No errors (if applicable)
  - ✅ Linting: No errors
  - [List other automated checks that passed]

  Please perform the manual verification steps listed in the plan:
  - [List manual verification items from the plan]

  Let me know when manual testing is complete so I can proceed to Phase [N+1].
  ```

If instructed to execute multiple phases consecutively, skip the pause until the last phase. Otherwise, assume you are just doing one phase.

do not check off items in the manual testing steps until confirmed by the user.


## If You Get Stuck

When something isn't working as expected:
- First, make sure you've read and understood all the relevant code
- Consider if the codebase has evolved since the plan was written
- Present the mismatch clearly and ask for guidance

Use sub-tasks sparingly - mainly for targeted debugging or exploring unfamiliar territory.

## Writing Unit Tests

When adding tests for your implementation:

1. **Find existing test patterns**: Look for similar tests in the codebase
   - **Use `Glob` to search for test files** - each language has conventions:
     - Look for files with `test` or `spec` in the name
     - Common patterns: `*.test.*`, `*_test.*`, `test_*.*`, `*Test.*`, `*Spec.*`
     - Common directories: `test/`, `tests/`, `__tests__/`, `spec/`
   - **Read existing tests** to understand the testing setup and patterns
   - **Follow the same patterns**: testing framework, utilities, mocking approach, file naming

2. **Test file location**: Follow project conventions
   - **Check where existing tests live** - projects vary widely
   - Common patterns:
     - **Mirror structure**: Source in `src/`, tests in `test/` or `tests/` with same directory structure
     - **Co-located**: Test files next to source files (e.g., `feature.go` + `feature_test.go`)
     - **Separate directory**: All tests in dedicated directory (e.g., `tests/`, `spec/`, `__tests__/`)
   - **Match the naming convention**: If existing tests use `*Test.java`, do the same; if they use `test_*.py`, follow that

3. **What to test**:
   - **Primary functionality**: Does the core feature work as expected?
   - **Edge cases**: Empty inputs, null/nil values, boundary conditions, special characters
   - **Error handling**: How does it behave when things go wrong?
   - **Integration points**: Does it interact correctly with other components/modules/services?

4. **Test structure** (adapt to project's testing framework):
   - Use descriptive test names (e.g., `test_should_enable_streaming_for_running_run`)
   - Group related tests (e.g., `describe`/`class`/`suite` blocks)
   - Set up test fixtures/mocks for isolation
   - Clean up resources if needed

5. **Running tests**:
   - **First, check project documentation** (README, CONTRIBUTING.md, docs/)
   - **Look for test commands** in build/project configuration:
     - Project build files (e.g., `Makefile`, `package.json`, `pom.xml`, `build.gradle`, `Cargo.toml`, `mix.exs`, `Rakefile`, `pyproject.toml`, etc.)
     - CI configuration (e.g., `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`, `Jenkinsfile`, etc.)
     - Test framework config files
   - **Try common commands** for the project's language/framework if not documented
   - **Run specific tests** per project conventions (file path, pattern, or test name)
   - **Use watch/continuous mode** during development if the framework supports it

## Creating Implementation Plans

During the research phase, if no plan exists in `specs/features/FEAT-XXX/`, create one based on your research findings.

A good implementation plan should:
- Be based on actual code research, not assumptions
- Break work into logical, independently testable phases
- **Include unit tests as explicit changes in each phase**
- Include specific file paths and line references from your research
- Define clear automated and manual success criteria (tests are automated criteria!)
- Highlight risks, dependencies, and open questions

**File:** `specs/features/FEAT-XXX/implementation-plan.md`

```markdown
# Implementation Plan: [Ticket Summary]

**Ticket:** [KEY] ([Jira Link])
**Status:** [Status]
**Assignee:** [Name]
**Plan Status:** 🔍 Research → ⏸️ Awaiting Approval → ✅ Approved → 🚧 In Progress → ✅ Complete

## Context
[Description from ticket]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Research Findings

### Key Files
- `path/to/file1` - [Purpose and relevance]
- `path/to/file2` - [Purpose and relevance]

### Existing Patterns
- [Pattern 1 found in codebase that we'll follow]
- [Pattern 2 that's relevant]

### Dependencies & Integration Points
- [System/service A that we integrate with]
- [Component B that will be affected]

### Risks & Assumptions
- ⚠️ [Risk or concern identified]
- 💭 [Assumption being made]

---

## Phase 1: [Phase Name]
### Changes
- [ ] Create/modify `specific/file/path:123` - [what changes]
- [ ] Update `another/file:45-67` - [what changes]
- [ ] Add unit tests for the changes in `test/path/to/test-file`
  - Test primary functionality
  - Test edge cases
  - Test error handling

### Success Criteria
**Automated:**
- [ ] Unit tests pass: Run project-specific test command (e.g., `make test`, `npm test`, `pytest`)
- [ ] All existing tests still pass: Verify no regressions
- [ ] Type checking passes: If applicable (e.g., `make check`, `tsc`, `mypy`)
- [ ] Linting passes: Run project linter (e.g., `make lint`, `eslint`, `ruff`, `golangci-lint`)

**Manual:**
- [ ] Verify behavior Z in UI/CLI
- [ ] Check logs show expected output

## Phase 2: [Next Phase]
...
```

## Resuming Work

If a plan already exists in `specs/features/FEAT-XXX/implementation-plan.md`:

### If the plan has NO checkmarks:
- The plan was created but implementation hasn't started
- Review the plan to understand it
- **Wait for approval before implementing** (unless explicitly told the plan is already approved)

### If the plan has SOME checkmarks:
- The plan is approved and implementation is in progress
- Trust that completed work is done
- Pick up from the first unchecked item
- Verify previous work only if something seems off
- Continue with the verification workflow

### If you find issues with an existing plan:
- Present what's wrong and suggest updates
- Get approval for plan changes before continuing

Remember: You're implementing a solution, not just checking boxes. Keep the end goal and acceptance criteria in mind and maintain forward momentum.
