# PR Description Template

This template is used by the `/describe-pr` skill to generate pull request descriptions.

---

## What does this PR do?

[Brief 1-2 sentence description of the changes]

## Why are we doing this?

[Context and motivation - what problem are we solving? Link to Jira ticket if applicable]

## What problem does it solve?

[Specific problem being addressed - be concrete about the issue]

## How does it solve the problem?

[Technical approach and key implementation details - focus on the "how"]

## What are the changes?

### User-Facing Changes
- [Changes visible to end users - UI, API, behavior]
- None

### Internal/Technical Changes
- [Implementation details, refactoring, infrastructure changes]

### Breaking Changes
- [Any breaking changes or migration requirements - be explicit]
- [ ] None

## How to verify it

### Automated Verification
- [ ] All tests pass: `make test` (or project-specific test command)
- [ ] Linting passes: `make lint`
- [ ] Type checking passes: `make typecheck` (if applicable)
- [ ] Build succeeds: `make build`
- [ ] Integration tests pass: `make test-integration` (if applicable)

### Manual Verification
- [ ] [Specific manual test step - e.g., "Navigate to X page and verify Y"]
- [ ] [Performance test - e.g., "Load test with 1000 items"]
- [ ] [Edge case - e.g., "Test with empty dataset"]

## Related Documents

[Automatically populated by /describe-pr skill]

- Implementation Plan: `specs/features/FEAT-XXX/implementation-plan.md`
- Jira Ticket: `.claude/cache/SEMI-XXX.md`
- Code Review: `.claude/reviews/{number}_review.md`
- Research: `specs/research/YYYY-MM-DD-topic.md`

## Checklist

- [ ] Tests added/updated to cover changes
- [ ] Documentation updated (README, API docs, comments)
- [ ] No breaking changes (or breaking changes documented above)
- [ ] Security implications considered and addressed
- [ ] Performance implications considered
- [ ] Database migrations tested (if applicable)
- [ ] Feature flags added for gradual rollout (if needed)

## Screenshots/Examples

[If applicable, add screenshots showing before/after, or example output]

```
# Example command output or API response
```

## Additional Notes

[Any other context, gotchas, deployment considerations, or follow-up work]

### Deployment Notes
- [Special deployment steps, if any]
- [Environment variable changes needed]
- [Database migration order]

### Follow-up Work
- [Link to follow-up tickets/issues]
- [Known limitations to address later]
