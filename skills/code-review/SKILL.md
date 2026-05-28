---
name: code-review
description: Run comprehensive code review using parallel agents, then synthesize findings
---

# Code Review

Run a comprehensive code review using parallel agents, then synthesize findings.

The goal is to catch real problems — bugs, security holes, and code that will be hard to maintain. Perfection is a matter of opinion. A good PR review is direct and kind, not exhaustive.

## Scope

Determine what code to review using this priority:

1. **User specifies scope** - If the user provides a branch name, commit SHA, PR number/URL, or file paths, review that
2. **On a feature branch** - Review all changes on current branch vs main/master (`git diff main...HEAD`)
3. **On main/master with staged changes** - Review staged files (`git diff --staged`)
4. **On main/master, nothing staged** - Review the latest commit (`git show HEAD`)

**Examples:**
- "review my branch" → branch diff
- "review pr 123" or "review https://github.com/org/repo/pull/123" → fetch PR via `gh`
- "review commit abc123" → that specific commit
- "review src/auth.ts" → just that file's recent changes
- (no scope given, on feature branch) → automatic branch diff

**Review only what changed.** Agents should report issues in the diff or code directly affected by the change. Do not report pre-existing issues in unrelated files.

## Discover Related Documents

After determining scope, find related documents before launching agents:

**Extract identifiers from branch name and PR title:**
- Ticket numbers (e.g., `feat/SEMI-1234-description` → `SEMI-1234`)
- Feature keywords from branch name or PR title

**Search for related documents using Glob:**
- `specs/features/*{ticket}*/implementation-plan*.md`
- `specs/research/*{ticket}*.md` or `specs/research/*{keyword}*.md`
- `.claude/cache/SEMI-{ticket}.md` (cached Jira tickets)
- `.claude/cache/CONF-*.md` (cached Confluence pages)

**Record discovered paths** for inclusion in the review document later.

This step is lightweight — just glob for matching filenames, don't read the documents. The paths are included in the saved review document so context can be found later.

## Instructions

### Select agents by PR size

Assess the diff before launching agents:

- **Small PRs** (≤100 lines changed or ≤3 files): Launch agents 1–4 (Test Runner, Linter, Code Reviewer, Security) only
- **Medium and large PRs** (>100 lines or >3 files): Launch all 9 agents

### Launch selected agents in parallel

Use a single message with multiple `Agent` tool calls:

#### Agent 1: Test Runner
Run relevant tests for the changed files. Report:
- Which tests were run
- Pass/fail status
- Any test failures with details

#### Agent 2: Linter & Static Analysis
Run linters for the changed files.

Report:
- Linting tool(s) used
- Any warnings or errors found
- Auto-fixable vs manual fixes needed
- Type errors or unresolved references

#### Agent 3: Code Reviewer
First, check if `skills.md` or a similar project style guide exists. If so, read it to understand project conventions.

Review the code changes and provide up to 5 concrete improvements, ranked by:
- Impact (how much this improves the code)
- Effort (how hard it is to implement)

Only include genuinely important issues. If the code is clean, report fewer items or none.

**Format each suggestion as:**
```
1. [HIGH/MED/LOW Impact, HIGH/MED/LOW Effort] Title
   - What: Description of the issue
   - Why: Why this matters
   - How: Concrete suggestion to fix
```

Focus on non-obvious improvements - skip formatting, naming nitpicks, and things linters catch.

#### Agent 4: Security Reviewer
Review the code changes for security concerns:
- Input validation and sanitization
- Injection risks (SQL, command, XSS)
- Authentication/authorization issues
- Secrets or credentials in code
- Error handling that leaks sensitive info

**Calibrate severity to the trust boundary.** Internal tooling where inputs are controlled by developers is lower risk than user-facing application code. For example, an unquoted variable in a script that receives input from `git diff --name-only` is not the same severity as command injection in a web handler.

Also check error handling:
- Missing try/catch where needed
- Swallowed errors hiding problems
- Unhelpful error messages

Report issues with severity (Critical/High/Medium/Low) and specific file:line references.
If no issues found, report "No security concerns identified."

#### Agent 5: Quality & Style Reviewer
First, check if `skills.md` or a similar project style guide exists. If so, read it to understand project conventions.

Review the code changes for quality and style issues:

**Quality:**
1. Complexity - functions too long, deeply nested, high cyclomatic complexity
2. Dead code - unused imports, unreachable code, unused variables
3. Duplication - copy-pasted logic that should be abstracted

**Style Guidelines:**
4. Naming conventions - does naming match project patterns and style guide?
5. File/folder organization - are files in the right place?
6. Architectural patterns - does code follow established patterns in the codebase?
7. Consistency - does new code match the style of surrounding code?
8. Project conventions - does code follow rules in the project style guide (if present)?

For each issue found, provide:
- File and location
- What the issue is
- Suggested fix

If code is clean, report "No quality or style issues identified."

#### Agent 6: Test Quality Reviewer
Review test coverage and quality for the changed code:

**Coverage (with ROI lens):**
- Are critical paths tested? (auth, payments, data integrity)
- Are edge cases that matter tested?
- Is the coverage proportionate to the risk? (not all code needs equal coverage)
- Would adding more tests here provide diminishing returns?

**Quality:**
- Do tests verify behavior, not implementation details?
- Will these tests break for the wrong reasons? (testing internals, brittle selectors)
- Are assertions focused on outcomes users care about?
- Would these tests catch real bugs without false positives?

**Test Code Quality:**
- Are there many similar tests that could be parameterized/data-driven?
- Is there copy-pasted setup that should be extracted to helpers/fixtures?
- Could table-driven tests reduce boilerplate while improving clarity?
- Is test code held to the same quality standards as production code?

**Flakiness Risk:**
- Are there timing dependencies, race conditions, or order-sensitive assertions?
- Do tests rely on external state that could change?
- Are async operations properly awaited/mocked?

**Anti-patterns:**
- Testing implementation details (private methods, internal state)
- Mocking so heavily that tests don't verify real behavior
- Tests that pass but don't actually assert meaningful outcomes
- Coverage for coverage's sake on low-risk code

Report issues with specific suggestions. If tests are well-balanced, report "Test coverage is appropriate and behavior-focused."

#### Agent 7: Performance Reviewer
Review the code changes for performance concerns:
- N+1 queries or inefficient data fetching
- Blocking operations in async contexts
- Unnecessary re-renders (React) or recomputations
- Memory leaks (unclosed resources, growing collections)
- Missing pagination for large datasets
- Expensive operations in hot paths

For each concern, explain the impact and suggest a fix.
If no concerns, report "No performance concerns identified."

#### Agent 8: Dependency, Breaking Changes & Deployment Safety Reviewer
Review changes for dependency, compatibility, and deployment concerns:

**Dependencies (if package files changed):**
- Are new dependencies justified? Check if functionality could use existing deps
- Are dependencies well-maintained? (check for recent commits, known vulnerabilities)
- Impact on bundle size for frontend dependencies

**Breaking Changes (if public APIs or exports changed):**
- Are any public interfaces, types, or exports modified?
- Would existing consumers of this code break?
- Is a version bump needed? (major for breaking, minor for features, patch for fixes)

**API Contract Changes (TREAT AS HIGH RISK):**
- Treat any changes to API contracts as high risk. API contracts include:
  - Public REST endpoints (routes, request/response shapes, headers)
  - GraphQL schemas (types, queries, mutations, subscriptions)
  - OpenAPI / Swagger definitions
  - Protobuf definitions
  - Public TypeScript interfaces exported from the package
- Flag any of the following as potential breaking changes:
  - Removed fields
  - Renamed fields
  - Type changes (e.g., string → number, optional → required)
  - Response shape changes (nesting, wrapping, flattening)
  - Status code changes
- For each flagged change, explicitly state: **"This may introduce a breaking change."**
- Suggest versioning or backward compatibility strategies such as:
  - API versioning (URL path or header-based)
  - Deprecation periods with sunset headers
  - Additive-only changes (new fields alongside old ones)
  - Feature flags for gradual rollout
  - Schema evolution patterns (optional new fields, keeping old fields)

**Deployment Safety:**
- Are there database migrations that could fail or lock tables?
- Is there backwards compatibility with existing data/state in production?
- Are there deployment ordering issues? (config changes, service dependencies)
- Would a feature flag help with safe rollout?
- Could this be rolled back safely if issues arise?

**Observability:**
- If this fails in production, how would we know?
- Are there logs, metrics, or alerts that would surface issues?
- Are error cases observable, not silent?
- Do critical paths have monitoring coverage?

Report issues with specific file references.
If no concerns, report "No dependency, compatibility, or deployment concerns."

#### Agent 9: Simplification & Maintainability Reviewer
Review the code changes with fresh eyes, asking "could this be simpler?"

**Simplification:**
- Are there abstractions that don't pull their weight?
- Could we achieve the same result with less code?
- Are we solving problems we don't actually have?
- Is there a more straightforward approach using existing patterns/libraries?

**Maintainability ROI:**
- Will future developers understand this easily?
- Does the complexity match the problem complexity?
- Are we adding cognitive load for marginal benefit?
- Would a "dumber" solution be easier to maintain long-term?

**Look for:**
- Premature abstractions (helpers used once, unnecessary indirection)
- Over-configured solutions when simple would suffice
- Framework-level solutions for one-off problems
- Clever code that sacrifices clarity

**Change Atomicity & Reviewability:**
- Does this change represent one logical unit of work? (atomic commit)
- Are there unrelated changes mixed in that should be separate commits?
- Could any cleanup/refactoring be split out as a preceding commit?
- Is there feature work bundled with unrelated fixes?
- Is this sized appropriately for PR review? (not so large it's overwhelming)
- Does it include enough context to review without jumping everywhere?
- Would splitting this up lose important context a reviewer needs?

For each finding, explain:
- What could be simplified
- The simpler alternative
- Maintenance cost saved

If the code is appropriately simple and atomic, report "Code complexity is proportionate to the problem and changes are well-scoped."

## Synthesize Results

### Calibrate to PR size

Before triaging, assess the scope of the diff. A small, focused change (bug fix, config tweak, minor refactor) deserves a short review. Do not produce a detailed report for a trivial change — that wastes the author's time and buries real signal in noise. Match the depth of your output to the complexity of the change.

### Triage findings

Collect all agent results and triage into three buckets:

**Blockers** — must be fixed before merge:
- Bugs or incorrect logic that will break in production
- Security vulnerabilities with a realistic exploit path (not theoretical risks in controlled environments)
- Major performance problems (e.g. N+1 queries, blocking the event loop)
- Linter errors (not warnings)
- Failing tests
- Clear violations of project conventions in skills.md

A blocker should fail the "would a senior engineer hold the PR for this?" test. Missing config sections, follow-up improvements, and nice-to-haves are suggestions, not blockers.

**Suggestions** — worth considering but not blocking:
- Minor security improvements (Medium/Low severity, defense-in-depth)
- Minor performance improvements
- Quality, style, or maintainability concerns that are real but not severe

**Nits** — drop entirely. Do not include in output.

Prune suggestions ruthlessly — only include ones where acting on the feedback would meaningfully improve the PR.

### Tone

Write findings as a colleague who read the code carefully, not as an audit report. Explain what you noticed and why it matters. Be direct and specific. Skip preamble.

### Output Format

If there are no blockers and no meaningful suggestions, skip the sections entirely and just write:

```markdown
## Code Review

LGTM. No concerns.
```

Otherwise:

```markdown
## Code Review

### Blockers (X)
1. [Bug] Title — file:line
   What goes wrong and why.
2. [Security] Title — file:line
   What the risk is and how to fix it.

### Suggestions (X)
1. [Quality] Title — file:line
   Brief, specific description.

### Verdict: [Approve | Needs Work]
One sentence. Blockers require fixes before merge. Suggestions are at the author's discretion.
```

Omit any section that has no entries. Do not include an "All Clear" list of agents that found nothing.

### Verdict Guidelines

- **Approve** — No blockers. Suggestions are at the author's discretion.
- **Needs Work** — One or more blockers that must be addressed before merge.

## Senior Review

Before presenting the review, pass the draft through one final agent. This agent is a very senior software engineer who has written and received thousands of code reviews. Their job is to review the review itself.

Give this agent the full draft review, the PR/branch title, and the diff size (files changed, lines added/removed). The agent should:

1. **Read it as the author would.** Is this review something you'd want to receive? Does it respect the effort that went into the PR? A first-time CI setup and a critical bugfix deserve different energy — match the tone to the PR's ambition.

2. **Check severity calibration.** Are any findings rated higher than a senior engineer would rate them? Downgrade or cut anything inflated.

3. **Check length.** A busy author should be able to read this in under 60 seconds and know exactly what to do. If the review is longer than the diff warrants, cut it down.

4. **Check the bar.** Would a reasonable senior engineer approve this PR with minor comments? If so, the verdict should be Approve, not Needs Work.

**Rewrite as needed.** The agent produces the final version of the review. This is what gets presented — not the earlier draft.

## Save Review Document

After synthesizing results, save the review to `.claude/reviews/`. This happens automatically — no user action needed.

### Determine file path

- **If reviewing a PR:** `.claude/reviews/{number}_review.md`
- **If no PR (branch review pre-PR):** `.claude/reviews/YYYY-MM-DD-{branch-name}-review.md`

If the file already exists, overwrite it. A code review is a point-in-time assessment — the old version is stale once the code changes. Git history preserves previous reviews.

### Gather metadata

Run these commands to collect metadata:

```bash
git rev-parse HEAD                        # current commit hash
git branch --show-current                 # current branch
basename $(git rev-parse --show-toplevel) # repository name
git config user.name                      # reviewer username
date -u +%Y-%m-%dT%H:%M:%SZ              # current timestamp
```

### Document structure

Write the review document with this structure:

```markdown
---
date: [ISO timestamp]
reviewer: [username]
git_commit: [commit hash]
branch: [branch name]
repository: [repo name]
pr_number: [PR number, omit if no PR]
scope: [branch diff | staged changes | commit {SHA} | PR {number}]
verdict: [Approve | Needs Work]
tags: [code-review, relevant-component-names]
status: complete
last_updated: [YYYY-MM-DD]
last_updated_by: [username]
---

# Code Review: [PR title or branch name]

**Date**: [ISO timestamp]
**Reviewer**: [username]
**Git Commit**: [commit hash]
**Branch**: [branch name]
**Scope**: [description of what was reviewed]

## Code Review Summary

[The full synthesized output — Blockers, Suggestions, and Verdict sections as formatted above. Or "LGTM. No concerns." if clean.]

## Related Documents

[List all documents discovered in the "Discover Related Documents" step. Only include categories where documents were found.]

- Implementation Plan: `specs/features/FEAT-XXX/implementation-plan.md`
- Research: `specs/research/YYYY-MM-DD-topic.md`
- Jira Ticket: `.claude/cache/SEMI-XXX.md`
- Confluence Page: `.claude/cache/CONF-123456789.md`
```

## Usage Examples

```bash
# Review current branch
/code-review

# Review specific PR
/code-review pr 123
/code-review https://github.com/org/repo/pull/123

# Review specific commit
/code-review commit abc123

# Review specific files
/code-review src/auth.ts src/users.ts
```

## Integration with Other Skills

**Recommended workflow:**

1. `/create-plan SEMI-790` - Create implementation plan
2. `/implement-plan SEMI-790` - Execute implementation
3. `/validate-plan` - Verify success criteria
4. `/code-review` - Comprehensive code review
5. Create PR with review findings addressed

The code review complements validation by focusing on code quality, security, and maintainability beyond just functional correctness.
