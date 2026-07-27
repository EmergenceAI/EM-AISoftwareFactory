"""
Provenance logger — streams structured JSONL events for every harness step.

Two purposes:
  1. Audit trail  — immutable record of what ran, when, inputs/outputs, outcome.
  2. RL feedback  — reward-annotated trajectories consumable by a training loop.

Directory layout:
  provenance/
    runs/
      {run_id}.jsonl          ← one event per line, streamed as they happen
      {run_id}.summary.json   ← written atomically at run end
    index.jsonl               ← one summary per line across all runs
"""

from __future__ import annotations

import datetime
import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class StepRecord:
    step: str
    success: bool
    duration_ms: float
    output_preview: str = ""
    error: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0


@dataclass
class GateRecord:
    gate: str
    passed: bool
    attempt: int
    outputs: Dict[str, Any]
    duration_ms: float
    error: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

class ProvenanceLogger:
    """
    Writes provenance events to JSONL files immediately (no buffering).
    Partial runs are always recoverable.
    """

    def __init__(self, provenance_dir: Path):
        self.dir = Path(provenance_dir)
        self.runs_dir = self.dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.dir / "index.jsonl"

    # ------------------------------------------------------------------
    # Public event API
    # ------------------------------------------------------------------

    def start_run(self, run_id: str, issue_key: str, repository: str, repo_path: str) -> None:
        self._append(self._run_path(run_id), {
            "event": "run_start",
            "run_id": run_id,
            "issue_key": issue_key,
            "repository": repository,
            "repo_path": repo_path,
            "timestamp": _ts(),
        })

    def log_step(self, run_id: str, step: StepRecord) -> None:
        self._append(self._run_path(run_id), {
            "event": "step",
            "run_id": run_id,
            "step": step.step,
            "success": step.success,
            "duration_ms": step.duration_ms,
            "output_preview": step.output_preview[:500] if step.output_preview else "",
            "error": step.error,
            "tokens_in": step.tokens_in,
            "tokens_out": step.tokens_out,
            "cost_usd": step.cost_usd,
            "timestamp": _ts(),
            "reward": 1.0 if step.success else 0.0,
        })

    def log_gate(self, run_id: str, gate: GateRecord) -> None:
        # Detect flakiness: passed on this attempt, but previous attempt for this
        # gate (if any) failed — and no fix step ran between them in this run.
        flaky = self._is_flaky(run_id, gate)
        self._append(self._run_path(run_id), {
            "event": "gate",
            "run_id": run_id,
            "gate": gate.gate,
            "passed": gate.passed,
            "attempt": gate.attempt,
            "outputs": gate.outputs,
            "duration_ms": gate.duration_ms,
            "error": gate.error,
            "tokens_in": gate.tokens_in,
            "tokens_out": gate.tokens_out,
            "cost_usd": gate.cost_usd,
            "flaky": flaky,
            "timestamp": _ts(),
            "reward": 1.0 if gate.passed else 0.0,
        })

    def log_gate_loop(
        self,
        run_id: str,
        passed: bool,
        attempts: int,
        failures: Optional[List[GateRecord]] = None,
    ) -> None:
        self._append(self._run_path(run_id), {
            "event": "gate_loop_complete",
            "run_id": run_id,
            "passed": passed,
            "attempts": attempts,
            "remaining_failures": [
                {"gate": f.gate, "outputs": f.outputs} for f in (failures or [])
            ],
            "timestamp": _ts(),
            # Efficiency reward: fewer attempts = better; zero if didn't pass
            "reward": (1.0 / attempts) if passed else 0.0,
        })

    def log_error(self, run_id: str, error: str) -> None:
        self._append(self._run_path(run_id), {
            "event": "error",
            "run_id": run_id,
            "error": error,
            "timestamp": _ts(),
            "reward": 0.0,
        })

    def finish_run(
        self,
        run_id: str,
        issue_key: str,
        repository: str,
        overall_outcome: str,
        gate_attempts: int,
        steps: List[StepRecord],
        gate_results: List[GateRecord],
        pr_url: Optional[str],
        duration_ms: float,
    ) -> None:
        reward = {"success": 1.0, "partial": 0.5, "failed": 0.0}.get(overall_outcome, 0.0)
        total_cost = sum(s.cost_usd for s in steps) + sum(g.cost_usd for g in gate_results)
        total_tokens_in = sum(s.tokens_in for s in steps) + sum(g.tokens_in for g in gate_results)
        total_tokens_out = sum(s.tokens_out for s in steps) + sum(g.tokens_out for g in gate_results)

        summary = {
            "run_id": run_id,
            "issue_key": issue_key,
            "repository": repository,
            "overall_outcome": overall_outcome,
            "gate_attempts": gate_attempts,
            "steps_total": len(steps),
            "steps_succeeded": sum(1 for s in steps if s.success),
            "gates_total": len(gate_results),
            "gates_passed": sum(1 for g in gate_results if g.passed),
            "gate_breakdown": _gate_breakdown(gate_results),
            "pr_url": pr_url,
            "duration_ms": duration_ms,
            "cost_usd": round(total_cost, 6),
            "tokens_in": total_tokens_in,
            "tokens_out": total_tokens_out,
            "timestamp": _ts(),
            "reward": reward,
            "human_feedback": None,
            "human_rating": None,
        }

        # Atomic summary file
        summary_path = self.runs_dir / f"{run_id}.summary.json"
        summary_path.write_text(json.dumps(summary, indent=2))

        # Final event in run log
        self._append(self._run_path(run_id), {"event": "run_end", **summary})

        # Global index
        self._append(self.index_path, summary)

    # ------------------------------------------------------------------
    # Read / export
    # ------------------------------------------------------------------

    def read_run(self, run_id: str) -> List[Dict[str, Any]]:
        path = self._run_path(run_id)
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

    def export_rl_dataset(self, output_path: Path) -> int:
        """
        Export all completed runs as RL training trajectories.

        Each trajectory contains:
          - Metadata (run_id, issue, repo, overall reward)
          - Ordered step events with per-step rewards
          - Human feedback slot (if filled)

        Returns number of trajectories written.
        """
        trajectories = []
        for summary_file in sorted(self.runs_dir.glob("*.summary.json")):
            run_id = summary_file.stem.replace(".summary", "")
            events = self.read_run(run_id)
            summary = json.loads(summary_file.read_text())

            trajectories.append({
                "run_id": run_id,
                "issue_key": summary["issue_key"],
                "repository": summary["repository"],
                "overall_outcome": summary["overall_outcome"],
                "overall_reward": summary["reward"],
                "human_feedback": summary.get("human_feedback"),
                "human_rating": summary.get("human_rating"),
                "gate_breakdown": summary.get("gate_breakdown", {}),
                "trajectory": [
                    e for e in events if e["event"] in ("step", "gate", "gate_loop_complete")
                ],
            })

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(trajectories, indent=2))
        return len(trajectories)

    # ------------------------------------------------------------------
    # Analysis helpers (loop engineering)
    # ------------------------------------------------------------------

    def total_cost(self, run_id: str) -> float:
        """Sum cost_usd across all events in a run."""
        return sum(
            e.get("cost_usd", 0.0)
            for e in self.read_run(run_id)
            if e.get("event") in ("step", "gate")
        )

    def flaky_gates(self, run_id: str) -> List[str]:
        """
        Return gate names that flipped pass→fail→pass without a fix step in between.
        A gate is flaky if it passed on attempt N > 1 with no fix step between the
        previous failed attempt and this passing attempt.
        """
        events = self.read_run(run_id)
        flaky = [
            e["gate"] for e in events
            if e.get("event") == "gate" and e.get("flaky")
        ]
        return list(dict.fromkeys(flaky))  # deduplicated, order-preserving

    def rotate(self, max_age_days: int = 90) -> int:
        """
        Move run JSONL + summary files older than max_age_days to provenance/archive/.
        Returns count of files archived.
        """
        archive_dir = self.dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=max_age_days)
        archived = 0

        for summary_file in self.runs_dir.glob("*.summary.json"):
            try:
                summary = json.loads(summary_file.read_text())
                ts_str = summary.get("timestamp", "")
                ts = datetime.datetime.fromisoformat(ts_str.rstrip("Z"))
                if ts < cutoff:
                    run_id = summary_file.stem.replace(".summary", "")
                    for path in [summary_file, self._run_path(run_id)]:
                        if path.exists():
                            shutil.move(str(path), str(archive_dir / path.name))
                            archived += 1
            except Exception:
                continue  # skip unreadable files

        return archived

    def gate_failure_rates(self) -> Dict[str, float]:
        """
        Compute per-gate failure rate across all runs.
        Used to prioritise which gates need more fix capacity.
        """
        counts: Dict[str, int] = {}
        failures: Dict[str, int] = {}

        for summary_file in self.runs_dir.glob("*.summary.json"):
            run_id = summary_file.stem.replace(".summary", "")
            for event in self.read_run(run_id):
                if event.get("event") != "gate":
                    continue
                gate = event["gate"]
                counts[gate] = counts.get(gate, 0) + 1
                if not event["passed"]:
                    failures[gate] = failures.get(gate, 0) + 1

        return {
            gate: failures.get(gate, 0) / total
            for gate, total in counts.items()
        }

    def avg_attempts_to_pass(self) -> float:
        """Average gate loop attempts across successful runs."""
        attempts = []
        for f in self.runs_dir.glob("*.summary.json"):
            s = json.loads(f.read_text())
            if s["overall_outcome"] == "success":
                attempts.append(s["gate_attempts"])
        return sum(attempts) / len(attempts) if attempts else 0.0

    def success_rate(self) -> float:
        """Fraction of runs that ended in overall_outcome == 'success'."""
        summaries = list(self.runs_dir.glob("*.summary.json"))
        if not summaries:
            return 0.0
        successes = sum(
            1 for f in summaries
            if json.loads(f.read_text()).get("overall_outcome") == "success"
        )
        return successes / len(summaries)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _is_flaky(self, run_id: str, gate: GateRecord) -> bool:
        """
        True if this gate passed (attempt > 1) and the previous attempt for the
        same gate failed, with no fix step logged between them.
        """
        if not gate.passed or gate.attempt <= 1:
            return False
        events = self.read_run(run_id)
        prev_gate_failed = False
        fix_between = False
        for e in events:
            ev = e.get("event")
            if ev == "gate" and e.get("gate") == gate.gate and e.get("attempt") == gate.attempt - 1:
                prev_gate_failed = not e.get("passed", True)
            if ev == "step" and e.get("step", "").startswith("fix.") and prev_gate_failed:
                fix_between = True
        return prev_gate_failed and not fix_between

    def _run_path(self, run_id: str) -> Path:
        return self.runs_dir / f"{run_id}.jsonl"

    def _append(self, path: Path, event: Dict[str, Any]) -> None:
        with open(path, "a") as fh:
            fh.write(json.dumps(event) + "\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


def _gate_breakdown(gate_results: List[GateRecord]) -> Dict[str, Dict]:
    breakdown: Dict[str, Dict] = {}
    for g in gate_results:
        if g.gate not in breakdown:
            breakdown[g.gate] = {"attempts": 0, "final": "pass"}
        breakdown[g.gate]["attempts"] += 1
        breakdown[g.gate]["final"] = "pass" if g.passed else "fail"
    return breakdown
