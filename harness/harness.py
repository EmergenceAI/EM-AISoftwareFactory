"""
Harness — thin wrapper that delegates to executor.execute_with_provenance().

Integrated with:
  - locks       : per-repo file lock prevents concurrent runs on the same repo
  - checkpoint  : survives mid-run crashes; resumes from the last completed step
  - circuit_breaker : skips a gate that has failed N consecutive cross-run times
  - watchdog    : background thread alerts/kills hung steps
  - server      : registers each run for live observability (if server is up)
"""

from __future__ import annotations

import re
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .checkpoint import Checkpoint
from .circuit_breaker import CircuitBreaker
from .executor import Executor
from .locks import LockError, RepoLock
from .provenance import GateRecord, ProvenanceLogger, StepRecord
from .watchdog import Watchdog

import os as _os
_SERVER_BASE = f"http://localhost:{_os.environ.get('HARNESS_SERVER_PORT', '8089')}"


def _server_call(fn_name: str, *args, **kwargs) -> None:
    """Notify the running server via HTTP. Silent no-op if server is down or deps missing."""
    try:
        import urllib.request as _req, json as _json
        if fn_name == "ensure_server_running":
            import importlib, io, contextlib
            with contextlib.redirect_stderr(io.StringIO()):
                srv = importlib.import_module(".server", package="harness")
            srv.ensure_server_running(*args, **kwargs)
            return
        if fn_name == "register_run":
            run_id, issue_key, repository = args[0], args[1], args[2]
            url = f"{_SERVER_BASE}/api/runs/{run_id}/register"
            body = {"issue_key": issue_key, "repository": repository, "pid": kwargs.get("pid")}
        elif fn_name == "update_run":
            run_id = args[0]
            url = f"{_SERVER_BASE}/api/runs/{run_id}"
            body = kwargs
        elif fn_name == "complete_run":
            run_id, outcome = args[0], args[1]
            url = f"{_SERVER_BASE}/api/runs/{run_id}/complete"
            body = {"outcome": outcome}
        else:
            return
        data = _json.dumps(body).encode()
        method = "PATCH" if fn_name == "update_run" else "POST"
        r = _req.Request(url, data=data, headers={"Content-Type": "application/json"}, method=method)
        _req.urlopen(r, timeout=2)
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
# Harness
# ---------------------------------------------------------------------------

class Harness:
    """
    Thin implementation loop: sets up infrastructure, delegates SDLC steps to
    executor.execute_with_provenance(), and wraps the result in HarnessResult.
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

        self._executor = Executor(self.factory_root, workspace_config)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def implement(self, issue_key: str, repository: str) -> HarnessResult:
        """
        Run the full implementation loop for one issue in one repository.
        Delegates to executor.execute_with_provenance() for the SDLC workflow.
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
        _server_call("ensure_server_running", self._prov_dir, self.factory_root)

        checkpoint = Checkpoint(repo_path)
        # Resume: if there's an existing checkpoint for THIS issue, reuse the run_id
        existing = checkpoint.read()
        if existing and existing.get("issue_key") == issue_key:
            run_id = existing["run_id"]
            print(f"\n♻️  Resuming {run_id}  (completed: {existing.get('completed_steps', [])})")
        elif existing:
            print(f"\n⚠️  Stale checkpoint for {existing.get('issue_key')} found — clearing")
            checkpoint.clear()

        pr_url: Optional[str] = None
        overall_outcome = "failed"
        watchdog: Optional[Watchdog] = None

        try:
            # Acquire exclusive lock on the repo — waits up to 5 min if busy
            with RepoLock(repo_path, run_id=run_id, issue_key=issue_key):
                self.provenance.start_run(run_id, issue_key, repository, str(repo_path))
                print(f"\n🏭 Harness run {run_id}  |  {issue_key} → {repository}")
                _server_call("register_run", run_id, issue_key, repository)

                watchdog = Watchdog(run_id=run_id, on_warn=self._on_warn, on_kill=self._on_kill)
                watchdog.start()

                task = self._executor.execute_with_provenance(
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
                watchdog = None
                overall_outcome = "success" if task.success else "partial" if task.pr_url else "failed"
                pr_url = task.pr_url

                if self.auto_merge and task.pr_url:
                    merge_step = self._merge(task.pr_url, repo_path)
                    self.provenance.log_step(run_id, merge_step)

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
            _server_call("complete_run", run_id, overall_outcome)

        duration_ms = (time.time() - t_start) * 1000

        self.provenance.finish_run(
            run_id=run_id,
            issue_key=issue_key,
            repository=repository,
            overall_outcome=overall_outcome,
            gate_attempts=0,
            steps=[],
            gate_results=[],
            pr_url=pr_url,
            duration_ms=duration_ms,
        )

        return HarnessResult(
            run_id=run_id,
            issue_key=issue_key,
            repo=repository,
            overall_outcome=overall_outcome,
            gate_attempts=0,
            steps=[],
            gate_results=[],
            pr_url=pr_url,
            duration_ms=duration_ms,
            cost_usd=0.0,
            provenance_path=str(self.provenance._run_path(run_id)),
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
