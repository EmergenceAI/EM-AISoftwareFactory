# Harness Refactor: Single-Session Architecture with Skill-Side Provenance

## Problem

The current `harness.py` breaks `autonomous-implement` into separate Claude subprocesses per step
(research, plan, implement, fix, create-pr). Each subprocess starts cold with no memory of previous
steps. This causes:

- Fix agents introducing regressions (no context of what implement agent built)
- Missing eval generation step (subprocess loop didn't replicate it)
- `/create-pr` stalling for human confirmation in non-interactive mode
- API stream timeouts treated as test failures
- Tests ran against full 14k-file suite instead of affected files

The original `autonomous-implement` skill ran as one session and worked reliably. The harness
broke it apart to gain observability, losing continuity in the process.

## Design

Keep one Claude session. The skill writes provenance events to a file as it progresses. The Python
harness monitors that file — driving the watchdog, checkpoint, circuit breaker, and server
notifications from the event stream.

### Event Flow

```
Python harness
  └── starts ONE Claude session (autonomous-implement)
        ├── research       → appends step event to provenance-events.jsonl
        ├── plan           → appends step event
        ├── eval-generator → appends step event  (was missing from subprocess loop)
        ├── implement      → appends step event + commits
        ├── gate loop (full context — skill owns this via /verify-and-fix)
        │     ├── /run-linter       → writes linter.json, skill appends gate event
        │     ├── /run-tests        → writes tests.json, skill appends gate event
        │     ├── /run-evals        → writes evals.json, skill appends gate event
        │     └── /run-code-review  → writes code-review.json, skill appends gate event
        ├── /fix-failures  (same session — knows why everything was written)
        └── /create-pr     → appends run_complete event with pr_url

Python harness (tail-reading provenance-events.jsonl)
  ├── forwards events → provenance/runs/run_*.jsonl  (main provenance log)
  ├── HTTP notify     → server  (dashboard + TUI update live)
  ├── watchdog reset  → on each step_start event
  ├── checkpoint      → on each step_end event
  └── circuit breaker → on each gate event
```

### Provenance Event Schema

Written by the skill via the Write tool, appended to `.harness-results/provenance-events.jsonl`:

```json
{"event": "step_start", "step": "research", "timestamp": "..."}
{"event": "step_end",   "step": "research", "success": true, "duration_ms": 192000, "output_preview": "..."}
{"event": "gate",       "gate": "linter",   "attempt": 1, "passed": true,  "outputs": {...}}
{"event": "gate",       "gate": "tests",    "attempt": 1, "passed": false, "failures": [...]}
{"event": "fix_start",  "attempt": 1}
{"event": "fix_end",    "attempt": 1, "success": true}
{"event": "run_complete", "outcome": "success", "pr_url": "https://..."}
```

### Files Changed

| File | Change |
|------|--------|
| `skills/autonomous-implement/SKILL.md` | Add `--provenance-file` param; append events at each step, gate, fix, PR |
| `skills/verify-and-fix/SKILL.md` | Same — append gate/fix events when called standalone |
| `harness/executor.py` | Pass `--provenance-file`; tail-read events; drive watchdog/checkpoint/server/provenance |
| `harness/harness.py` | Remove subprocess step loop; delegate to executor + monitor |

### Files Unchanged

`server.py`, `provenance.py`, `locks.py`, `watchdog.py`, `circuit_breaker.py`, `checkpoint.py`,
`tui.py`, `dashboard/index.html`, `scrubber.py`, gate skills (`run-linter`, `run-tests`, etc.)

## What This Fixes

- **Context continuity** — fix agent knows what implement agent built
- **Eval generation** — skill's full flow runs, including `/eval-generator`
- **No confirmation stall** — skill runs end-to-end, no interactive prompt in -p mode
- **API timeouts** — within one session, Claude retries automatically
- **Test scoping** — skill's `/run-tests` call can scope to changed files with full context
