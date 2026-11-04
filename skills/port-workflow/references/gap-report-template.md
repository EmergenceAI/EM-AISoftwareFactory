# Port gap report: `<workflow>`

Written by `/port-workflow` at step 8, committed in the bundle as `PORT_GAPS.md`, and pasted into
the PR body.

## Summary

- Workflow: `<em-semi workflow name>` → `<craft bundle path>`
- Outcome: success | partial | failed, with a one-line reason
- Parity: static tests `<passed>/<total>`, evals `<passed>/<total>`

## Pinned em-semi ref

`<sha>` (`<date>`), recorded as `EM_SEMI_REF` in `<vendor script path>`.

## Stand-ins (waiting on craft capability)

| Interface | Stand-in file | Craft capability needed | Tests to re-run on real data |
|---|---|---|---|
| | | | |

## Outside write boundary

Changes the port needs but the skill does not make: runner-image packages, SDK, plane changes.

| Need | Why | Blocks |
|---|---|---|
| | | yes / no |

## Pre-existing em-semi test failures

Vendored em-semi tests that already fail at the pinned ref. Quarantined by nodeid in
`conftest.py`, never fixed by editing vendored code.

| Test nodeid | Failure | Notes |
|---|---|---|
| | | |

## Evals

| Suite | Source (ported from em-semi path / generated) | Result |
|---|---|---|
| | | |

## Not ported

Things deliberately left behind (inbox messages, chat/agent profiles, …), each with a reason.
