---
name: create-plan
description: Create detailed implementation plans through interactive research and collaboration
---

# Create Implementation Plan

Create detailed implementation plans through **interactive research and skeptical analysis**. Work collaboratively with the user to understand requirements, research the codebase, and produce actionable technical specifications.

## Initial Response

When invoked without parameters:

```
I'll help you create a detailed implementation plan.

Please provide:
1. The task/ticket description (or ticket reference like SEMI-XXX)
2. Any relevant context, constraints, or requirements
3. Links to related research or implementations

Tip: You can provide a ticket reference: `/create-plan SEMI-790`
```

When invoked with a ticket reference:
- Immediately fetch the ticket using MCP (see "Understand Requirements" section below for fetch logic)
- Begin research process
- Start asking clarifying questions

## Process

### 1. Understand Requirements

**Read all context completely:**
- Jira tickets (`.claude/cache/SEMI-XXX.md` or fetch if not cached)
- Confluence pages (fetch with MCP tools if provided)
- Related plans (`specs/features/FEAT-XXX/`)
- Research documents (`specs/research/`)
- Any mentioned code files
- **Always read files FULLY** (no limit/offset)

**If Jira ticket reference provided:**
- Check if `.claude/cache/SEMI-XXX.md` exists and read it
- If not cached:
  - Invoke the `mcp__atlassian__jira_get_issue` tool with parameter `issue_key: "SEMI-XXX"`
  - Format the result as markdown
  - Save to `.claude/cache/SEMI-XXX.md` for reuse
  - Read the cached file

**If Confluence URL provided:**
- Extract page ID from URL (pattern: `/pages/{page_id}/`)
- Check if `.claude/cache/CONF-{page-id}.md` exists and read it
- If not cached:
  - Invoke the `mcp__atlassian__confluence_get_page` tool with parameter `page_id: "{page_id}"`
  - Format the result as markdown
  - Save to `.claude/cache/CONF-{page-id}.md` for reuse
  - Read the cached file

**Research the codebase in parallel:**
- Use `Agent` tool with `Explore` subagent to find relevant files
- Use `Agent` tool to analyze current implementation
- Use `Glob` and `Grep` to find patterns and similar features
- Read all identified files completely

**Present your understanding:**
```
Based on the ticket and my research:

**Current State:**
- [What exists now - file:line references]
- [Patterns discovered]
- [Constraints identified]

**Questions:**
- [Specific technical questions]
- [Clarifications needed]
```

### 2. Design and Structure

**Propose approach:**
```
**Design Options:**
1. [Option A] - [pros/cons]
2. [Option B] - [pros/cons]

**Recommended Approach:** [Your recommendation with reasoning]
```

**Get feedback, then propose plan structure:**
```
**Proposed Phases:**
1. [Phase name] - [what it accomplishes]
2. [Phase name] - [what it accomplishes]

Does this structure make sense?
```

### 3. Write the Plan

**Filename:** `specs/features/FEAT-XXX/implementation-plan-{username}.md`
- `FEAT-XXX` matches the ticket (e.g., FEAT-790 for SEMI-790)
- `{username}` from `git config user.name` or ask user
- If no ticket: `specs/research/YYYY-MM-DD-topic-{username}.md`

**Template:**

```markdown
# [Feature Name] Implementation Plan

**Ticket:** SEMI-XXX ([Jira Link])
**Author:** {username}
**Date:** YYYY-MM-DD
**Status:** 🔍 Research → ⏸️ Awaiting Approval → ✅ Approved → 🚧 In Progress

## Context

[What we're building and why]

## Current State

[What exists now, what's missing, constraints discovered]

**Key Findings:**
- [Discovery with file:line reference]
- [Pattern to follow]
- [Constraint to work within]

## Desired End State

[What success looks like and how to verify it]

## What We're NOT Doing

[Out of scope items to prevent scope creep]

## Implementation Approach

[High-level strategy and reasoning]

---

## Phase 1: [Name]

### Overview
[What this phase accomplishes]

### Changes

- [ ] Modify `path/to/file:123` - [what changes]
- [ ] Add tests in `test/path/to/file` - [what to test]
  - Test primary functionality
  - Test edge cases
  - Test error handling

### Success Criteria

**Automated:**
- [ ] Tests pass (run project test command)
- [ ] Type checking passes (if applicable)
- [ ] Linting passes
- [ ] Build succeeds

**Manual:**
- [ ] Feature works as expected in UI/CLI
- [ ] Performance is acceptable
- [ ] No regressions in related features

---

## Phase 2: [Name]

[Similar structure...]

---

## Testing Strategy

**Unit Tests:**
- [What to test, edge cases]

**Integration Tests:**
- [End-to-end scenarios]

**Manual Testing:**
1. [Specific verification steps]

## Performance Considerations

[Performance implications, optimizations needed]

## Migration/Rollback

[How to handle existing data, how to rollback]

## References

- Ticket: `.claude/cache/SEMI-XXX.md`
- Similar implementation: `[file:line]`
- Related plan: `specs/features/FEAT-YYY/implementation-plan.md`
```

**After writing:**
```
I've created the implementation plan at:
`specs/features/FEAT-XXX/implementation-plan-{username}.md`

Please review and let me know if you need any adjustments to:
- Phase breakdown
- Technical approach
- Success criteria
- Scope
```

## Guidelines

**Be Skeptical:**
- Question vague requirements
- Identify potential issues early
- Verify assumptions with code research
- Don't accept surface-level understanding

**Be Interactive:**
- Get feedback at each major step
- Don't write full plan in one shot
- Allow course corrections
- Ask clarifying questions

**Be Thorough:**
- Read all files completely
- Research actual code patterns
- Include specific file:line references
- Define both automated and manual success criteria
- Reference similar implementations

**Be Practical:**
- Focus on incremental, testable changes
- Consider edge cases and errors
- Include rollback strategy
- Separate in-scope from out-of-scope
- Write tests as part of implementation, not separate phase

**Research First:**
- Use `Agent` tool to explore codebase in parallel
- Read all relevant files completely before planning
- Find existing patterns to follow
- Identify integration points and dependencies
- Only ask questions you can't answer through code

**No Open Questions:**
- If you encounter unknowns, STOP and research/ask
- Don't write plan with unresolved questions
- Every decision must be made before finalizing
- Plan must be complete and actionable

## Success Criteria Format

**Automated Verification:**
Things that can be run by CI or scripts:
- Test commands
- Type checking
- Linting
- Build process
- Specific files existing
- API endpoint responses

**Manual Verification:**
Things requiring human testing:
- UI/UX functionality
- Performance under real load
- Edge case behavior
- User acceptance
- Error message quality

Example:
```markdown
### Success Criteria

**Automated:**
- [ ] All tests pass: `[test command]`
- [ ] Type checking passes: `[check command]`
- [ ] Linting passes: `[lint command]`

**Manual:**
- [ ] Feature works correctly in UI
- [ ] Performance acceptable with realistic data
- [ ] Error messages are clear
```

## Common Patterns

**Database Changes:**
Schema → Store methods → Business logic → API → Client

**New Features:**
Research patterns → Data model → Backend → API → UI → Tests

**Refactoring:**
Document behavior → Plan incremental changes → Maintain compatibility → Migration

**Bug Fixes:**
Reproduce → Failing test → Fix → Test passes → Regression tests

## Agent Tool Usage

Spawn parallel research tasks for efficiency:

```
Use Agent tool with focused prompts:
- Explore: "Find all files in [directory] related to [feature]"
- Research: "Analyze how [file] implements [functionality]"
- Pattern: "Find similar [feature] implementations in [directory]"
```

**Be specific:**
- Include exact directories to search
- Request file:line references
- Ask for specific information
- Wait for all tasks before synthesizing

**Verify results:**
- Cross-check against actual code
- Spawn follow-up tasks if needed
- Read identified files yourself

**Getting Username:**
```bash
git config user.name
# Or ask: "What username should I use for the filename?"
```
