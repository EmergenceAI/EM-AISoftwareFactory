# Harness Refactor: Single-Session Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the subprocess-per-step harness loop with a single Claude session that writes provenance events to a file, monitored by a thin Python wrapper.

**Architecture:** `autonomous-implement` runs as one session end-to-end (full context continuity). It appends JSON events to `.harness-results/provenance-events.jsonl` at each step. `executor.py` tail-reads that file in a background thread, forwarding events to the existing provenance logger, watchdog, checkpoint, circuit breaker, and server. `harness.py` becomes a thin wrapper — locks, starts executor, waits for completion.

**Tech Stack:** Python 3.9+, Claude CLI (`claude -p`), threading, existing harness modules (provenance, watchdog, checkpoint, circuit_breaker, locks, server).

## Global Constraints

- Do NOT modify: `server.py`, `provenance.py`, `locks.py`, `watchdog.py`, `circuit_breaker.py`, `checkpoint.py`, `tui.py`, `dashboard/index.html`, `scrubber.py`, gate skills (`run-linter`, `run-tests`, `run-evals`, `run-code-review`, `fix-failures`)
- All existing CLI commands (`watch`, `queue`, `cancel`, `resume`, `tui`, `server`, `cost`, `runs`, `provenance`) must continue to work unchanged
- Provenance JSONL format in `provenance/runs/` must remain identical — downstream tools depend on it
- `--skill` flag on `implement` CLI command must still work (skill mode bypass)

---

### Task 1: Provenance event writing in `autonomous-implement`

Add `--provenance-file` parameter to the skill. At each step the skill appends one JSON line to that file using the Write tool. This is what the Python harness will monitor.

**Files:**
- Modify: `skills/autonomous-implement/SKILL.md`

**Interfaces:**
- Produces: `--provenance-file <path>` parameter; events appended to that file at each step

- [ ] **Step 1: Add `--provenance-file` parameter to the Usage section**

In `skills/autonomous-implement/SKILL.md`, add to the Parameters list and Usage examples:

```markdown
# With harness provenance tracking
/autonomous-implement ABI-123 --provenance-file .harness-results/provenance-events.jsonl
```

Add to the Parameters list:
```markdown
- `--provenance-file <path>`: Path to JSONL file for appending structured progress events. Used by the harness to monitor live progress. If omitted, no events are written.
```

- [ ] **Step 2: Add provenance helper block near the top of Detailed Process**

After Step 0 (Load Knowledge Context), add a new section:

```markdown
### Provenance Helper (if --provenance-file provided)

Throughout this skill, append events to the provenance file after each major step.
Use the Write tool to append (read current content first, append new line, write back).
If the file does not exist yet, create it with the first event.

Event format — one JSON object per line, no trailing comma:

\`\`\`json
{"event": "step_start", "step": "<name>", "timestamp": "<ISO8601>"}
{"event": "step_end", "step": "<name>", "success": true, "duration_ms": 12345, "output_preview": "<first 300 chars of output>"}
{"event": "gate", "gate": "<name>", "attempt": 1, "passed": true, "outputs": {}}
{"event": "fix_start", "attempt": 1, "timestamp": "<ISO8601>"}
{"event": "fix_end", "attempt": 1, "success": true, "duration_ms": 12345}
{"event": "run_complete", "outcome": "success", "pr_url": "https://...", "timestamp": "<ISO8601>"}
\`\`\`

Steps to emit for: `fetch-issue`, `create-branch`, `research`, `plan`, `eval-gen`, `implement`,
each gate (`linter`, `tests`, `evals`, `code-review`), each fix attempt, and `create-pr`.
```

- [ ] **Step 3: Add step_start/step_end event writes at each major step**

For each of the 7 named steps (fetch-issue, create-branch, research, plan, eval-gen, implement, create-pr), add before the step starts:

```markdown
> **Provenance:** If `--provenance-file` provided, append:
> `{"event": "step_start", "step": "research", "timestamp": "<now ISO8601>"}`
```

And after the step completes (success or failure):

```markdown
> **Provenance:** Append:
> `{"event": "step_end", "step": "research", "success": true, "duration_ms": <elapsed ms>, "output_preview": "<first 300 chars>"}`
```

- [ ] **Step 4: Add gate event writes inside the verify-and-fix loop section**

In Step 7 (Verify & Fix), after each gate skill completes, append:

```markdown
> **Provenance:** After each gate result, append:
> `{"event": "gate", "gate": "linter", "attempt": 1, "passed": true, "outputs": <gate JSON result>}`
```

After each fix invocation starts/ends:

```markdown
> **Provenance:** Before fix: `{"event": "fix_start", "attempt": 1, "timestamp": "<now>"}`
> After fix: `{"event": "fix_end", "attempt": 1, "success": true, "duration_ms": <elapsed>}`
```

- [ ] **Step 5: Add run_complete event at the end**

After Step 8 (Create PR) succeeds or fails, append:

```markdown
> **Provenance:** Append final event:
> `{"event": "run_complete", "outcome": "success", "pr_url": "<url or null>", "timestamp": "<now ISO8601>"}`
```

`outcome` is `"success"` if all gates passed, `"partial"` if gates failed but PR was still created, `"failed"` if no PR was created.

- [ ] **Step 6: Verify the skill parses `--provenance-file` from args correctly**

Confirm the existing arg-parsing pseudocode in the skill handles `--provenance-file`. The skill already shows how args are parsed for `--context-file`. Add the same pattern:

```javascript
const provenanceFile = args['provenance-file'] || null
```

- [ ] **Step 7: Commit**

```bash
git add skills/autonomous-implement/SKILL.md
git commit -m "feat: add provenance event writing to autonomous-implement skill"
```

---

### Task 2: Provenance event writing in `verify-and-fix`

Same provenance events for the standalone gate loop skill (used when skill mode runs verify-and-fix directly).

**Files:**
- Modify: `skills/verify-and-fix/SKILL.md`

**Interfaces:**
- Produces: same `--provenance-file` param and event format as Task 1

- [ ] **Step 1: Add `--provenance-file` parameter**

In `skills/verify-and-fix/SKILL.md` Usage section add:

```markdown
- `--provenance-file <path>`: JSONL file for appending gate/fix events (used by harness)
```

- [ ] **Step 2: Add gate and fix event writes**

After each gate result and fix step, add the same provenance append instructions as in Task 1 Steps 3-5 (gate events, fix_start, fix_end, run_complete). Do not add step_start/step_end for research/plan — those don't run here.

- [ ] **Step 3: Commit**

```bash
git add skills/verify-and-fix/SKILL.md
git commit -m "feat: add provenance event writing to verify-and-fix skill"
```

---

### Task 3: Event monitor in `executor.py`

Add an `EventMonitor` class that tail-reads the provenance events file in a background thread and dispatches to provenance logger, watchdog, checkpoint, circuit breaker, and server.

**Files:**
- Modify: `harness/executor.py`

**Interfaces:**
- Consumes: `ProvenanceLogger` (from `harness.provenance`), `Watchdog` (from `harness.watchdog`), `Checkpoint` (from `harness.checkpoint`), `CircuitBreaker` (from `harness.circuit_breaker`), `_server_call` (from `harness.harness`)
- Produces: `EventMonitor` class with `start(path)`, `stop()`, `wait_for_complete(timeout)` → `dict | None`

- [ ] **Step 1: Add imports to executor.py**

At the top of `harness/executor.py` add:

```python
import threading
import json
import time
from harness.provenance import ProvenanceLogger, StepRecord, GateRecord
from harness.watchdog import Watchdog
from harness.checkpoint import Checkpoint
from harness.circuit_breaker import CircuitBreaker
```

- [ ] **Step 2: Write the EventMonitor class**

Add after the imports, before the `TaskResult` dataclass:

```python
class EventMonitor:
    """
    Tail-reads provenance-events.jsonl written by the skill.
    Dispatches each event to provenance, watchdog, checkpoint, circuit breaker, server.
    Runs in a background daemon thread — call start(), then wait_for_complete().
    """

    def __init__(
        self,
        run_id: str,
        issue_key: str,
        repo_path: Path,
        provenance: ProvenanceLogger,
        watchdog: Watchdog,
        checkpoint: Checkpoint,
        circuit_breaker: CircuitBreaker,
        server_call,        # callable matching _server_call signature
    ):
        self.run_id = run_id
        self.issue_key = issue_key
        self.repo_path = repo_path
        self.provenance = provenance
        self.watchdog = watchdog
        self.checkpoint = checkpoint
        self.circuit_breaker = circuit_breaker
        self._server_call = server_call
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._complete_event = threading.Event()
        self._final_event: Optional[dict] = None   # run_complete payload
        self._step_starts: dict = {}               # step → start time (float)

    def start(self, events_path: Path) -> None:
        """Start background monitoring of events_path."""
        self._thread = threading.Thread(
            target=self._monitor, args=(events_path,), daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the monitor to stop after current line."""
        self._stop_event.set()

    def wait_for_complete(self, timeout: float = 7200.0) -> Optional[dict]:
        """
        Block until run_complete event is seen or timeout elapses.
        Returns the run_complete payload dict, or None on timeout.
        """
        self._complete_event.wait(timeout=timeout)
        return self._final_event

    def _monitor(self, events_path: Path) -> None:
        """Tail-read the events file. One JSON line per event."""
        # Wait up to 60s for the file to appear (skill creates it on first write)
        deadline = time.time() + 60
        while not events_path.exists() and time.time() < deadline:
            if self._stop_event.is_set():
                return
            time.sleep(0.5)

        if not events_path.exists():
            return   # skill never started writing — nothing to do

        position = 0
        while not self._stop_event.is_set():
            try:
                with open(events_path) as f:
                    f.seek(position)
                    for raw_line in f:
                        line = raw_line.strip()
                        if line:
                            try:
                                event = json.loads(line)
                                self._dispatch(event)
                            except json.JSONDecodeError:
                                pass   # partial write — will retry next poll
                    position = f.tell()
            except OSError:
                pass
            time.sleep(0.5)

    def _dispatch(self, event: dict) -> None:
        """Route a parsed event to the correct handler."""
        ev = event.get("event")
        now = time.time()

        if ev == "step_start":
            step = event["step"]
            self._step_starts[step] = now
            self.watchdog.reset(step)
            self._server_call("update_run", self.run_id, current_step=step)
            print(f"   ▶  {step}")

        elif ev == "step_end":
            step = event["step"]
            success = event.get("success", False)
            t0 = self._step_starts.get(step, now)
            duration_ms = (now - t0) * 1000
            record = StepRecord(
                step=step,
                success=success,
                duration_ms=duration_ms,
                output_preview=event.get("output_preview", ""),
                error=event.get("error"),
            )
            self.provenance.log_step(self.run_id, record)
            completed = self.checkpoint.completed_steps() + [step]
            self.checkpoint.write(self.run_id, self.issue_key, completed)
            icon = "✅" if success else "❌"
            print(f"   {icon}  {step}")

        elif ev == "gate":
            gate = event["gate"]
            passed = event.get("passed", False)
            attempt = event.get("attempt", 1)
            outputs = event.get("outputs", {})
            t0 = self._step_starts.get(f"gate.{gate}", now)
            duration_ms = (now - t0) * 1000
            record = GateRecord(
                gate=gate,
                passed=passed,
                attempt=attempt,
                outputs=outputs,
                duration_ms=duration_ms,
                error=event.get("error"),
            )
            self.provenance.log_gate(self.run_id, record)
            if passed:
                self.circuit_breaker.record_success(gate)
                print(f"   ✅  {gate}")
            else:
                self.circuit_breaker.record_failure(gate, event.get("error", ""))
                print(f"   ❌  {gate}")

        elif ev == "fix_start":
            attempt = event.get("attempt", 1)
            self.watchdog.reset(f"fix.attempt{attempt}")
            print(f"   🔄  fix attempt {attempt}")

        elif ev == "run_complete":
            self._final_event = event
            self._complete_event.set()
            self.stop()
```

- [ ] **Step 3: Add `execute_with_provenance()` to Executor**

Add this method to the `Executor` class, after `execute_single_repo`:

```python
def execute_with_provenance(
    self,
    issue_key: str,
    repository: str,
    run_id: str,
    provenance: ProvenanceLogger,
    watchdog: Watchdog,
    checkpoint: Checkpoint,
    circuit_breaker: CircuitBreaker,
    server_call,
) -> TaskResult:
    """
    Execute issue with full observability: provenance, watchdog, checkpoint, circuit breaker.
    Starts one Claude session and monitors the skill-written provenance events file.
    """
    start_time = time.time()

    try:
        repo_config = self._get_repo_config(repository)
        repo_path = self.workspace_root / repo_config['path']

        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path not found: {repo_path}")

        results_dir = repo_path / ".harness-results"
        results_dir.mkdir(exist_ok=True)
        events_path = results_dir / "provenance-events.jsonl"
        # Remove stale events file from a prior run
        if events_path.exists():
            events_path.unlink()

        knowledge_context = self.knowledge_engine.get_repository_knowledge(repository)
        foundations = self.knowledge_engine.get_foundations_guidance('standards')
        context_file = self._create_knowledge_context_file(
            knowledge_context=knowledge_context,
            foundations_standards=foundations.get('standards', ''),
            repo_config=repo_config,
            repo_path=repo_path,
        )

        monitor = EventMonitor(
            run_id=run_id,
            issue_key=issue_key,
            repo_path=repo_path,
            provenance=provenance,
            watchdog=watchdog,
            checkpoint=checkpoint,
            circuit_breaker=circuit_breaker,
            server_call=server_call,
        )
        monitor.start(events_path)

        prompt = (
            f"/autonomous-implement {issue_key}"
            f" --context-file {context_file}"
            f" --provenance-file {events_path}"
        )
        cmd = [
            'claude',
            '--plugin-dir', str(self.factory_root),
            '--dangerously-skip-permissions',
            '-p', prompt,
        ]

        print(f"\n🚀 Launching claude for {issue_key} in {repo_path.name}...")
        proc = subprocess.run(
            cmd,
            cwd=str(repo_path),
            text=True,
            timeout=7200,  # 2-hour ceiling
            stdout=None,
            stderr=None,
        )

        final = monitor.wait_for_complete(timeout=30)  # grace period after proc exits
        monitor.stop()

        if context_file.exists():
            context_file.unlink()

        success = proc.returncode == 0 and (final or {}).get("outcome") in ("success", "partial")
        return TaskResult(
            repository=repository,
            issue_key=issue_key,
            success=success,
            pr_url=(final or {}).get("pr_url"),
            output=(final or {}).get("outcome", ""),
            error=None if success else f"exit code {proc.returncode}",
            duration_seconds=time.time() - start_time,
        )

    except subprocess.TimeoutExpired:
        monitor.stop()
        return TaskResult(
            repository=repository, issue_key=issue_key, success=False,
            error="claude timed out after 2 hours", duration_seconds=time.time() - start_time,
        )
    except Exception as exc:
        return TaskResult(
            repository=repository, issue_key=issue_key, success=False,
            error=str(exc), duration_seconds=time.time() - start_time,
        )
```

- [ ] **Step 4: Commit**

```bash
git add harness/executor.py
git commit -m "feat: add EventMonitor and execute_with_provenance to executor"
```

---

### Task 4: Slim down `harness.py`

Replace the 400-line subprocess step loop in `Harness.implement()` with a thin wrapper that sets up infrastructure and delegates to `executor.execute_with_provenance()`.

**Files:**
- Modify: `harness/harness.py`

**Interfaces:**
- Consumes: `Executor.execute_with_provenance()` from Task 3
- Produces: `HarnessResult` (unchanged dataclass, same fields)

- [ ] **Step 1: Remove the subprocess step loop**

In `harness/harness.py`, delete everything inside the `with RepoLock(...)` block after the watchdog start — that is, all of Steps 1–5 (research, plan, implement, gate loop, create-pr, auto-merge). Keep the lock acquisition, provenance start, server registration, and watchdog start.

Replace with a call to `execute_with_provenance`:

```python
with RepoLock(repo_path, run_id=run_id, issue_key=issue_key):
    self.provenance.start_run(run_id, issue_key, repository, str(repo_path))
    print(f"\n🏭 Harness run {run_id}  |  {issue_key} → {repository}")
    _server_call("register_run", run_id, issue_key, repository)

    watchdog = Watchdog(run_id=run_id, on_warn=self._on_warn, on_kill=self._on_kill)
    watchdog.start()

    task = executor.execute_with_provenance(
        issue_key=issue_key,
        repository=repository,
        run_id=run_id,
        provenance=self.provenance,
        watchdog=watchdog,
        checkpoint=checkpoint,
        circuit_breaker=self.circuit_breaker,
        server_call=_server_call,
    )

    watchdog.stop()
    overall_outcome = "success" if task.success else "partial" if task.pr_url else "failed"
    pr_url = task.pr_url
```

- [ ] **Step 2: Remove now-unused private methods**

Delete from `harness.py` (they were only used by the subprocess loop):
- `_skill()`
- `_gate()`
- `_commit()`
- `_write_failure_context()`
- `_merge()` (keep if auto-merge still needed; wire it from `task.pr_url`)

Keep: `_on_warn`, `_on_kill`, `_write_knowledge_context`, `_repo_config`, `_parse_tokens`.

- [ ] **Step 3: Fix the `HarnessResult` construction**

After the `with RepoLock` block, construct `HarnessResult` from what `execute_with_provenance` returned. The `steps` and `gate_results` lists now come from provenance (read from the JSONL file) rather than in-memory accumulation. Simplify to:

```python
overall_outcome = "success" if task.success else "partial" if task.pr_url else "failed"
_server_call("complete_run", run_id, overall_outcome)
self.provenance.end_run(run_id, overall_outcome, pr_url=task.pr_url,
                        gate_attempts=0, steps=[], gate_results=[])

return HarnessResult(
    run_id=run_id,
    issue_key=issue_key,
    repo=repository,
    overall_outcome=overall_outcome,
    gate_attempts=0,   # skill manages this internally now
    steps=[],          # readable from provenance JSONL if needed
    gate_results=[],
    pr_url=task.pr_url,
    duration_ms=(time.time() - t_start) * 1000,
    cost_usd=0.0,
    provenance_path=str(self.provenance.runs_dir / f"{run_id}.jsonl"),
)
```

- [ ] **Step 4: Wire the Executor into Harness.__init__**

`Harness` currently doesn't hold an `Executor`. Add it:

```python
from harness.executor import Executor

class Harness:
    def __init__(self, factory_root, workspace_config, max_gate_attempts=2, auto_merge=False):
        ...
        self._executor = Executor(factory_root, workspace_config)
```

Then use `self._executor` in `implement()`.

- [ ] **Step 5: Run smoke test**

```bash
cd /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory
python3 -c "from harness.harness import Harness; print('import OK')"
python3 -c "from harness.executor import Executor, EventMonitor; print('import OK')"
```

Both should print `import OK` with no errors.

- [ ] **Step 6: Commit**

```bash
git add harness/harness.py harness/executor.py
git commit -m "refactor: single-session harness — remove subprocess loop, delegate to executor"
```

---

### Task 5: End-to-end smoke test

Verify the full flow works with a real run before merging.

**Files:**
- No code changes — validation only

- [ ] **Step 1: Clean up any stale state**

```bash
cd /Users/malamunisamy/Documents/Development/em-semi
git checkout main
rm -rf .harness-results/
cd /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory
```

- [ ] **Step 2: Run harness implement**

```bash
python3 -m harness implement SEMI-1665
```

Expected terminal output:
```
🏭 Harness run run_XXXX  |  SEMI-1665 → semi
   ▶  fetch-issue
   ✅  fetch-issue
   ▶  create-branch
   ✅  create-branch
   ▶  research
   ✅  research
   ▶  plan
   ...
```

- [ ] **Step 3: Verify provenance events file is being written**

In a second terminal while the run is going:

```bash
tail -f /Users/malamunisamy/Documents/Development/em-semi/.harness-results/provenance-events.jsonl
```

Should see JSON lines appearing as each step completes.

- [ ] **Step 4: Verify main provenance log is populated**

```bash
tail -f /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory/provenance/runs/run_*.jsonl
```

Should see the same events forwarded into the main provenance log.

- [ ] **Step 5: Verify dashboard shows active run**

Open `http://localhost:8089/` — the run should appear with live step updates.

- [ ] **Step 6: Commit if all good, open PR**

```bash
cd /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory
git push origin feat/dark-factory-harness
gh pr view 7  # verify PR is up to date
```
