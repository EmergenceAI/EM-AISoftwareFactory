---
name: describe-pr
description: Generate comprehensive pull request descriptions following the repository template
---

# Generate PR Description

You are tasked with generating a comprehensive pull request description following the repository's standard template.

## Steps to Follow

### 1. Read the PR Description Template

- First, check if `.claude/templates/pr_description.md` exists
- If it doesn't exist, check if there's a template in `.github/pull_request_template.md`
- If neither exists, use the default template structure (see below)
- Read the template carefully to understand all sections and requirements

### 2. Identify the PR to Describe

**Check if current branch has an associated PR:**
```bash
gh pr view --json url,number,title,state 2>/dev/null
```

**If no PR exists for current branch, or if on main/master:**
```bash
gh pr list --limit 10 --json number,title,headRefName,author
```

Ask the user which PR they want to describe.

### 3. Check for Existing Description

- Check if `.claude/prs/{number}_description.md` already exists
- If it exists, read it and inform the user you'll be updating it
- Consider what has changed since the last description was written

### 4. Gather Comprehensive PR Information

**Get the full PR diff:**
```bash
gh pr diff {number}
```

If you get an error about no default remote repository, instruct the user to run:
```bash
gh repo set-default
```

**Get commit history:**
```bash
gh pr view {number} --json commits
```

**Review the base branch:**
```bash
gh pr view {number} --json baseRefName
```

**Get PR metadata:**
```bash
gh pr view {number} --json url,title,number,state
```

### 5. Discover Related Documents

Search for related implementation plans, research, and context:

**Extract ticket numbers from branch name or PR title:**
- Pattern: `SEMI-XXX`, `FEAT-XXX`, etc.

**Search for related documents:**
```bash
# Implementation plans
specs/features/FEAT-{ticket}/implementation-plan*.md

# Research documents
specs/research/*{ticket}*.md

# Cached Jira tickets
.claude/cache/SEMI-{ticket}.md

# Cached Confluence pages
.claude/cache/CONF-*.md

# Code reviews
.claude/reviews/{number}_review.md
```

Record discovered paths to include in the PR description.

### 6. Analyze the Changes Thoroughly

Think deeply about the code changes, their architectural implications, and potential impacts:

- Read through the entire diff carefully
- For context, read any files that are referenced but not shown in the diff
- Understand the purpose and impact of each change
- Identify user-facing changes vs internal implementation details
- Look for breaking changes or migration requirements
- Check if changes align with implementation plan (if one exists)

### 7. Handle Verification Requirements

Look for any checklist items in the "How to verify it" section of the template:

**For each verification step:**

**If it's a command you can run:**
```bash
# Examples: make check test, npm test, pytest, cargo test, etc.
```
- Run it
- If it passes, mark the checkbox as checked: `- [x]`
- If it fails, keep it unchecked and note what failed: `- [ ]` with explanation

**If it requires manual testing:**
- UI interactions, external services, etc.
- Leave unchecked and note for user: `- [ ] [Manual] Description of what to test`

Document any verification steps you couldn't complete.

### 8. Generate the Description

Fill out each section from the template thoroughly:

- Answer each question/section based on your analysis
- Be specific about problems solved and changes made
- Focus on user impact where relevant
- Include technical details in appropriate sections
- Write a concise changelog entry
- Ensure all checklist items are addressed (checked or explained)
- Link to related documents discovered in step 5

### 9. Save the Description

Write the completed description to `.claude/prs/{number}_description.md`

### 10. Update the PR

**Update the PR description directly:**
```bash
gh pr edit {number} --body-file .claude/prs/{number}_description.md
```

Confirm the update was successful.

If any verification steps remain unchecked, remind the user to complete them before merging.

## Default Template Structure

If no template exists in `.claude/templates/pr_description.md` or `.github/pull_request_template.md`, use this structure:

```markdown
## What does this PR do?

[Brief description of the changes]

## Why are we doing this?

[Context and motivation - link to ticket/issue if applicable]

## What problem does it solve?

[Specific problem being addressed]

## How does it solve the problem?

[Technical approach and key implementation details]

## What are the changes?

### User-Facing Changes
- [List changes visible to end users]

### Internal/Technical Changes
- [List implementation details, refactoring, etc.]

### Breaking Changes
- [List any breaking changes or migration requirements]
- [ ] None

## How to verify it

### Automated Verification
- [ ] Tests pass: `[test command]`
- [ ] Linting passes: `[lint command]`
- [ ] Build succeeds: `[build command]`
- [ ] Type checking passes: `[typecheck command]`

### Manual Verification
- [ ] [Manual test step 1]
- [ ] [Manual test step 2]

## Related Documents

- Implementation Plan: `specs/features/FEAT-XXX/implementation-plan.md`
- Jira Ticket: `.claude/cache/SEMI-XXX.md`
- Code Review: `.claude/reviews/{number}_review.md`

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Security implications considered
- [ ] Performance implications considered

## Screenshots/Examples

[If applicable, add screenshots or example output]

## Additional Notes

[Any other context, gotchas, or follow-up work]
```

## Important Notes

- This command works across different repositories - always read the local template
- Be thorough but concise - descriptions should be scannable
- Focus on the "why" as much as the "what"
- Include any breaking changes or migration notes prominently
- If the PR touches multiple components, organize the description accordingly
- Always attempt to run verification commands when possible
- Clearly communicate which verification steps need manual testing
- Link to related implementation plans and tickets for context

## Usage Examples

```bash
# Generate description for current branch's PR
/describe-pr

# Generate description for specific PR
/describe-pr 123

# Update existing PR description
/describe-pr 456
```

## Integration with Other Skills

**Recommended workflow:**

1. `/create-plan SEMI-790` - Create implementation plan
2. `/implement-plan SEMI-790` - Execute implementation
3. `/validate-plan` - Verify success criteria
4. `/code-review` - Comprehensive review
5. `/describe-pr` - Generate PR description
6. Submit PR with comprehensive context!

The PR description automatically links to:
- Implementation plans
- Code reviews
- Jira tickets
- Confluence pages

This provides reviewers with complete context for the changes.

## File Storage

PR descriptions are saved to:
- `.claude/prs/{pr-number}_description.md`

This directory is git-ignored by default, but you can commit descriptions if desired.

## Creating a Custom Template

To customize the PR description template, create:

**`.claude/templates/pr_description.md`**

Or use GitHub's built-in template:

**`.github/pull_request_template.md`**

The skill will automatically use your custom template when generating descriptions.
