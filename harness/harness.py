"""
Harness — owns the full implementation loop, calling individual skills as steps.

Integrated with:
  - scrubber    : secrets removed from output before provenance writes
  - locks       : per-repo file lock prevents concurrent runs on the same repo
  - checkpoint  : survives mid-run crashes; resumes from the last completed step
  - circuit_breaker : skips a gate that has failed N consecutive cross-run times
  - watchdog    : background thread alerts/kills hung steps
  - server      : registers each run for live observability (if server is up)
"""

from __future__ import annotations

import json
import re
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .checkpoint import Checkpoint
from .circuit_breaker import CircuitBreaker, CircuitOpenError
from .locks import LockError, RepoLock
from .provenance import GateRecord, ProvenanceLogger, StepRecord
from .scrubber import scrub
from .watchdog import Watchdog

# Server integration is optional. We probe lazily to avoid import-time noise
# when fastapi/uvicorn are not installed.
def _server_call(fn_name: str, *args, **kwargs) -> None:
    """Call a server function if the server module is importable. Silent no-op otherwise."""
    try:
        import importlib, io, contextlib
        with contextlib.redirect_stderr(io.StringIO()):  # suppress install-hint prints
            srv = importlib.import_module(".server", package="harness")
        getattr(srv, fn_name)(*args, **kwargs)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class HarnessResult:
    run_id: str
    issue_key: str
    repo: str
    overall_outcome: str      # "success" | "partial" | "failed"
    gate_attempts: int
    steps: List[StepRecord]
    gate_results: List[GateRecord]
    pr_url: Optional[str]
    duration_ms: float
    cost_usd: float
    provenance_path: str

    def summary(self) -> str:
        outcome_icon = {
            "success": "✅ SUCCESS",
            "partial": "⚠️  PARTIAL",
            "failed":  "❌ FAILED",
        }.get(self.overall_outcome, self.overall_outcome)

        lines = [
            f"\n{'='*64}",
            f"Harness Result: {self.issue_key}  [{self.repo}]",
            f"{'='*64}",
            f"Outcome   : {outcome_icon}",
            f"Duration  : {self.duration_ms/1000:.1f}s",
            f"Gate loop : {self.gate_attempts} attempt(s)",
            f"Cost      : ${self.cost_usd:.4f}",
            "",
            "Steps:",
        ]
        for s in self.steps:
            icon = "✅" if s.success else "❌"
            cost = f"  ${s.cost_usd:.4f}" if s.cost_usd else ""
            lines.append(f"  {icon} {s.step} ({s.duration_ms/1000:.1f}s){cost}")
            if s.error:
                lines.append(f"     ↳ {s.error}")

        if self.gate_results:
            lines += ["", "Gates (final attempt):"]
            seen: Dict[str, GateRecord] = {}
            for g in self.gate_results:
                seen[g.gate] = g
            for gate, g in seen.items():
                icon = "✅" if g.passed else "❌"
                lines.append(f"  {icon} {gate}")

        if self.pr_url:
            lines.append(f"\nPR: {self.pr_url}")

        lines += [f"\nProvenance: {self.provenance_path}", f"{'='*64}\n"]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_GATE_ORDER = ("linter", "tests", "evals", "code-review")

_GATE_PROMPTS = {
    "linter":      "/run-linter --output {result_file}",
    "tests":       "/run-tests --output {result_file}",
    "evals":       "/run-evals {issue_key} --output {result_file}",
    "code-review": "/run-code-review --output {result_file}",
}

_RESULT_FILES = {gate: f".harness-results/{gate}.json" for gate in _GATE_ORDER}

# Steps that produce code output (watch for secrets)
_SCRUB_STEPS = {"research", "plan", "implement", "create-pr"}


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

class Harness:
    """
    Deterministic implementation loop with per-step provenance, reliability
    primitives, and live observability via the embedded server.
    """

    def __init__(
        self,
        factory_root: Path,
        workspace_config: Dict[str, Any],
        *,
        max_gate_attempts: int = 3,
        auto_merge: bool = False,
        provenance_dir: Optional[Path] = None,
        skill_timeout: int = 3600,
        knowledge_engine=None,
    ):
        self.factory_root = Path(factory_root)
        self.workspace_config = workspace_config
        self.workspace_root = Path(workspace_config["workspace"]["root"])
        self.max_gate_attempts = max_gate_attempts
        self.auto_merge = auto_merge
        self.skill_timeout = skill_timeout

        if knowledge_engine is None:
            from .knowledge import KnowledgeEngine
            knowledge_engine = KnowledgeEngine(str(self.factory_root / "knowledge"))
        self._knowledge = knowledge_engine

        prov_dir = provenance_dir or (self.factory_root / "provenance")
        self.provenance = ProvenanceLogger(prov_dir)
        self.circuit_breaker = CircuitBreaker(prov_dir)
        self._prov_dir = prov_dir

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def implement(self, issue_key: str, repository: str) -> HarnessResult:
        """
        Run the full implementation loop for one issue in one repository.

        Steps
        -----
        1. research-codebase   (skipped if checkpoint says done)
        2. create-plan
        3. implement-plan
        4. gate loop  — linter → tests → evals → code-review (up to N retries)
           circuit breaker skips any gate that is "open"
        5. create-pr
        6. auto-merge (if policy allows and all gates passed)
        """
        run_id = f"run_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        t_start = time.time()

        repo_cfg  = self._repo_config(repository)
        repo_path = self.workspace_root / repo_cfg["path"]

        if not repo_path.exists():
            raise FileNotFoundError(
                f"Repository path not found: {repo_path}\n"
                f"Clone the repo or update workspace.yaml."
            )

        (repo_path / ".harness-results").mkdir(exist_ok=True)

        # Ensure the observability server is running (silent if fastapi not installed)
        _server_call("ensure_server_running", self._prov_dir, self.factory_root)  # server is optional

        knowledge   = self._knowledge.get_repository_knowledge(repository)
        foundations = self._knowledge.get_foundations_guidance("standards")
        ctx_file    = self._write_knowledge_context(knowledge, foundations, repo_cfg, repo_path)

        checkpoint = Checkpoint(repo_path)
        # Resume: if there's an existing checkpoint for THIS issue, reuse the run_id
        existing = checkpoint.read()
        if existing and existing.get("issue_key") == issue_key:
            run_id = existing["run_id"]
            print(f"\n♻️  Resuming {run_id}  (completed: {existing.get('completed_steps', [])})")
        elif existing:
            print(f"\n⚠️  Stale checkpoint for {existing.get('issue_key')} found — clearing")
            checkpoint.clear()

        steps: List[StepRecord] = []
        gate_results: List[GateRecord] = []
        pr_url: Optional[str] = None
        overall_outcome = "failed"
        gate_attempt = 0
        watchdog: Optional[Watchdog] = None

        try:
            # Acquire exclusive lock on the repo — waits up to 5 min if busy
            with RepoLock(repo_path, run_id=run_id, issue_key=issue_key):
                self.provenance.start_run(run_id, issue_key, repository, str(repo_path))
                print(f"\n🏭 Harness run {run_id}  |  {issue_key} → {repository}")

                _server_call("register_run", run_id, issue_key, repository)

                # Start watchdog
                watchdog = Watchdog(
                    run_id=run_id,
                    on_warn=self._on_warn,
                    on_kill=self._on_kill,
                )
                watchdog.start()

                # ── Step 1: Research ──────────────────────────────────
                if not checkpoint.should_skip("research"):
                    step = self._skill(
                        f"/research-codebase {issue_key} --context-file {ctx_file}",
                        repo_path, run_id, "research", watchdog=watchdog,
                    )
                    steps.append(step)
                    self.provenance.log_step(run_id, step)
                    if step.success:
                        checkpoint.write(run_id, issue_key, ["research"])

                # ── Step 2: Plan ──────────────────────────────────────
                if not checkpoint.should_skip("plan"):
                    step = self._skill(
                        f"/create-plan {issue_key} --context-file {ctx_file}",
                        repo_path, run_id, "plan", watchdog=watchdog,
                    )
                    steps.append(step)
                    self.provenance.log_step(run_id, step)
                    if not step.success:
                        raise RuntimeError(f"Planning failed: {step.error}")
                    checkpoint.write(run_id, issue_key, checkpoint.completed_steps() + ["plan"])

                # ── Step 3: Implement ─────────────────────────────────
                if not checkpoint.should_skip("implement"):
                    step = self._skill(
                        f"/implement-plan {issue_key}",
                        repo_path, run_id, "implement", watchdog=watchdog,
                    )
                    steps.append(step)
                    self.provenance.log_step(run_id, step)
                    if not step.success:
                        raise RuntimeError(f"Implementation failed: {step.error}")
                    checkpoint.write(run_id, issue_key, checkpoint.completed_steps() + ["implement"])

                # ── Step 4: Gate loop ─────────────────────────────────
                gates_passed = False
                while gate_attempt < self.max_gate_attempts:
                    gate_attempt += 1
                    print(f"\n🔄  Gate loop — attempt {gate_attempt}/{self.max_gate_attempts}")
                    failures: List[GateRecord] = []

                    for gate_name in _GATE_ORDER:
                        # Circuit breaker check
                        try:
                            self.circuit_breaker.check(gate_name)
                        except CircuitOpenError as ce:
                            print(f"   ⚡ {gate_name} — circuit open, skipping ({ce})")
                            self.provenance.log_error(run_id, f"circuit_open:{gate_name}:{ce}")
                            continue

                        gr = self._gate(gate_name, issue_key, repo_path, run_id, gate_attempt, watchdog)
                        gate_results.append(gr)
                        self.provenance.log_gate(run_id, gr)

                        if gr.passed:
                            self.circuit_breaker.record_success(gate_name)
                            print(f"   ✅  {gate_name}")
                        else:
                            self.circuit_breaker.record_failure(gate_name, gr.error or "")
                            print(f"   ❌  {gate_name}")
                            failures.append(gr)

                    if not failures:
                        gates_passed = True
                        self.provenance.log_gate_loop(run_id, passed=True, attempts=gate_attempt)
                        print("✅  All gates passed")
                        break

                    if gate_attempt < self.max_gate_attempts:
                        fix_ctx = self._write_failure_context(failures, repo_path, gate_attempt)
                        step = self._skill(
                            f"/fix-failures --failures-file {fix_ctx}",
                            repo_path, run_id, f"fix.attempt{gate_attempt}", watchdog=watchdog,
                        )
                        steps.append(step)
                        self.provenance.log_step(run_id, step)
                    else:
                        self.provenance.log_gate_loop(
                            run_id, passed=False, attempts=gate_attempt, failures=failures
                        )

                # ── Step 5: Create PR ─────────────────────────────────
                label_flag = "" if gates_passed else "--label NEEDS-REVIEW"
                step = self._skill(
                    f"/create-pr {label_flag}".strip(),
                    repo_path, run_id, "create-pr", watchdog=watchdog,
                )
                steps.append(step)
                self.provenance.log_step(run_id, step)

                # ── Step 6: Auto-merge ────────────────────────────────
                if gates_passed and self.auto_merge:
                    merge_step = self._merge(pr_url, repo_path)
                    steps.append(merge_step)
                    self.provenance.log_step(run_id, merge_step)

                overall_outcome = "success" if gates_passed else "partial"

        except LockError as le:
            self.provenance.log_error(run_id, f"lock_timeout:{le}")
            print(f"\n⏳  Could not acquire repo lock: {le}")
        except Exception as exc:
            self.provenance.log_error(run_id, str(exc))
            print(f"\n❌  Harness error: {exc}")
        finally:
            if watchdog:
                watchdog.stop()
            checkpoint.clear()
            ctx_file.unlink(missing_ok=True)
            _server_call("complete_run", run_id, overall_outcome)

        duration_ms = (time.time() - t_start) * 1000
        total_cost = sum(s.cost_usd for s in steps) + sum(g.cost_usd for g in gate_results)

        self.provenance.finish_run(
            run_id=run_id,
            issue_key=issue_key,
            repository=repository,
            overall_outcome=overall_outcome,
            gate_attempts=gate_attempt,
            steps=steps,
            gate_results=gate_results,
            pr_url=pr_url,
            duration_ms=duration_ms,
        )

        return HarnessResult(
            run_id=run_id,
            issue_key=issue_key,
            repo=repository,
            overall_outcome=overall_outcome,
            gate_attempts=gate_attempt,
            steps=steps,
            gate_results=gate_results,
            pr_url=pr_url,
            duration_ms=duration_ms,
            cost_usd=round(total_cost, 6),
            provenance_path=str(self.provenance._run_path(run_id)),
        )

    # ------------------------------------------------------------------
    # Skill invocation
    # ------------------------------------------------------------------

    def _skill(
        self,
        prompt: str,
        repo_path: Path,
        run_id: str,
        step_name: str,
        *,
        watchdog: Optional[Watchdog] = None,
    ) -> StepRecord:
        """
        Call a skill via `claude -p` subprocess.

        Uses Popen so the watchdog can kill the process if it hangs.
        Parses token/cost from stdout. Scrubs secrets before storing output.
        """
        t0 = time.time()
        print(f"   ▶  {step_name}")

        cmd = [
            "claude",
            "--plugin-dir", str(self.factory_root),
            "--dangerously-skip-permissions",
            "-p", prompt,
        ]
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(repo_path),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if watchdog:
                watchdog.set_step(step_name, proc)

            try:
                stdout, stderr = proc.communicate(timeout=self.skill_timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                return StepRecord(
                    step=step_name, success=False,
                    duration_ms=(time.time() - t0) * 1000,
                    error=f"Timed out after {self.skill_timeout}s",
                )

            duration_ms = (time.time() - t0) * 1000
            success = proc.returncode == 0
            tokens_in, tokens_out, cost_usd = _parse_tokens(stdout or "")

            # Scrub secrets from output before storing
            output_text = stdout or ""
            if step_name in _SCRUB_STEPS or step_name.startswith("fix."):
                output_text = scrub(output_text)

            return StepRecord(
                step=step_name,
                success=success,
                duration_ms=duration_ms,
                output_preview=output_text,
                error=scrub(stderr) if (stderr and not success) else None,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_usd=cost_usd,
            )

        except FileNotFoundError:
            return StepRecord(
                step=step_name, success=False, duration_ms=0,
                error="claude CLI not found — install with: brew install claude-code",
            )

    # ------------------------------------------------------------------
    # Gate execution
    # ------------------------------------------------------------------

    def _gate(
        self,
        gate: str,
        issue_key: str,
        repo_path: Path,
        run_id: str,
        attempt: int,
        watchdog: Optional[Watchdog],
    ) -> GateRecord:
        """Run a single gate skill and read its structured JSON result file."""
        t0 = time.time()
        result_file = repo_path / _RESULT_FILES[gate]
        result_file.unlink(missing_ok=True)

        prompt = _GATE_PROMPTS[gate].format(issue_key=issue_key, result_file=result_file)
        step = self._skill(prompt, repo_path, run_id, f"gate.{gate}.attempt{attempt}", watchdog=watchdog)

        duration_ms = (time.time() - t0) * 1000

        if result_file.exists():
            try:
                outputs: Dict[str, Any] = json.loads(result_file.read_text())
                passed = bool(outputs.get("passed", False))
            except json.JSONDecodeError:
                outputs = {"raw": step.output_preview[:200]}
                passed = step.success
        else:
            outputs = {"raw": step.output_preview[:200]}
            passed = step.success

        return GateRecord(
            gate=gate,
            passed=passed,
            attempt=attempt,
            outputs=outputs,
            duration_ms=duration_ms,
            error=step.error,
            tokens_in=step.tokens_in,
            tokens_out=step.tokens_out,
            cost_usd=step.cost_usd,
        )

    # ------------------------------------------------------------------
    # Merge
    # ------------------------------------------------------------------

    def _merge(self, pr_url: Optional[str], repo_path: Path) -> StepRecord:
        t0 = time.time()
        if not pr_url:
            return StepRecord(step="auto-merge", success=False, duration_ms=0,
                              error="No PR URL available for auto-merge")
        try:
            proc = subprocess.run(
                ["gh", "pr", "merge", "--squash", "--auto", pr_url],
                cwd=str(repo_path), text=True, capture_output=True, timeout=120,
            )
            success = proc.returncode == 0
            return StepRecord(
                step="auto-merge", success=success,
                duration_ms=(time.time() - t0) * 1000,
                output_preview=proc.stdout,
                error=proc.stderr if not success else None,
            )
        except FileNotFoundError:
            return StepRecord(step="auto-merge", success=False, duration_ms=0,
                              error="gh CLI not found")

    # ------------------------------------------------------------------
    # Watchdog callbacks
    # ------------------------------------------------------------------

    def _on_warn(self, step: str, elapsed: float) -> None:
        mins = elapsed / 60
        print(f"\n⚠️  Watchdog: step '{step}' has been running {mins:.0f}m — still in progress")

    def _on_kill(self, step: str, elapsed: float) -> None:
        mins = elapsed / 60
        print(f"\n🔴  Watchdog: killing step '{step}' after {mins:.0f}m (hard limit reached)")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _write_failure_context(self, failures: List[GateRecord], repo_path: Path, attempt: int) -> Path:
        ctx = repo_path / f".harness-results/failures-{attempt}.json"
        ctx.write_text(json.dumps(
            [{"gate": f.gate, "outputs": f.outputs} for f in failures], indent=2
        ))
        return ctx

    def _write_knowledge_context(
        self,
        knowledge: Dict[str, str],
        foundations: Dict[str, str],
        repo_cfg: Dict[str, Any],
        repo_path: Path,
    ) -> Path:
        content = f"""# Repository Knowledge Context
# Auto-generated by the Harness — do not edit

## Repository: {repo_cfg['name']}
**Language:** {repo_cfg.get('language', 'unknown')}
**Build System:** {repo_cfg.get('build_system', 'unknown')}

## Architecture
{knowledge.get('architecture', 'No architecture documentation available.')}

## Coding Patterns
{knowledge.get('patterns', 'No coding patterns documented.')}

## Conventions
{knowledge.get('conventions', 'No conventions documented.')}

## Dependencies
{knowledge.get('dependencies', 'No dependency information available.')}

## Foundations Standards
{foundations.get('standards', '')}
"""
        ctx_path = repo_path / f".knowledge_context_{repo_cfg['name']}.md"
        ctx_path.write_text(content)
        return ctx_path

    def _repo_config(self, repository: str) -> Dict[str, Any]:
        for repo in self.workspace_config.get("repositories", []):
            if repo["name"] == repository:
                return repo
        raise ValueError(f"Repository '{repository}' not found in workspace.yaml")


# ---------------------------------------------------------------------------
# Token / cost parsing
# ---------------------------------------------------------------------------

# Claude CLI emits token/cost info in various formats depending on version.
# Try multiple patterns; return zeros if none match.
_TOKEN_PATTERNS = [
    # "Tokens: 1,234 input, 567 output"
    re.compile(r"Tokens?:\s*([\d,]+)\s*input[,\s]+([\d,]+)\s*output", re.I),
    # "1,234 in / 567 out"
    re.compile(r"([\d,]+)\s*in\s*/\s*([\d,]+)\s*out", re.I),
    # "input_tokens: 1234" / "output_tokens: 567"
    re.compile(r"input_tokens[\":\s]+([\d,]+).*?output_tokens[\":\s]+([\d,]+)", re.I | re.S),
]
_COST_PATTERN = re.compile(r"Cost[:\s]+\$?([\d.]+)", re.I)


def _parse_tokens(text: str) -> Tuple[int, int, float]:
    """Parse tokens_in, tokens_out, cost_usd from claude CLI stdout."""
    tokens_in = tokens_out = 0
    cost_usd = 0.0

    for pat in _TOKEN_PATTERNS:
        m = pat.search(text)
        if m:
            tokens_in  = int(m.group(1).replace(",", ""))
            tokens_out = int(m.group(2).replace(",", ""))
            break

    m = _COST_PATTERN.search(text)
    if m:
        try:
            cost_usd = float(m.group(1))
        except ValueError:
            pass

    return tokens_in, tokens_out, cost_usd
