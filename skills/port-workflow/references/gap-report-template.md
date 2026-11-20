# Port gap report: `<workflow>`

Written by `/port-workflow` at step 8, committed in the bundle as `PORT_GAPS.md`, and pasted into
the PR body.

## Summary

- Workflow: `<em-semi workflow name>` → `<craft bundle path>`
- Outcome: success | partial | failed, with a one-line reason
- Parity: static tests `<passed>/<total>`, evals `<passed>/<total>`, app tests `<passed>/<total>`
- Live run: `<inputs>` on the local stack, bundle `<version>`: succeeded | failed (`<error>`) |
  not run (`<why>`); the report against the golden for the same inputs

## Pinned em-semi ref

`<sha>` (`<date>`), recorded as `EM_SEMI_REF` in `<vendor script path>`.

## Data sources

How the local data gets in (the em-semi pack profile, `ORG_ID`, `craft local data-init`), then one
row per redirected interface.

| em-semi interface | Run time (craft) | Grant | Still missing |
|---|---|---|---|
| | `data_query` over … / `db_query` over … | `dataScope` / `bundleDb` | none, or the gap |

## Stand-ins (no craft path yet)

| Interface | Stand-in file | Craft capability needed | Tests to re-run on real data |
|---|---|---|---|
| | | | |

## Outside write boundary

Changes the port needs but the skill does not make: runner-image packages, SDK, plane, CLI or
deployment-config changes. A platform gap the bundle works around (a `data.query` cast, a package
marker) is listed too, with *no (worked around)*.

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
