"""
Dark Factory observability server.

FastAPI application providing:
  - REST API for run history, stats, gate health, circuit breakers
  - SSE streaming for live run tailing
  - Prometheus metrics (text format, no prometheus_client dependency)
  - Static dashboard at /

Usage:
    # Start standalone
    python -m harness.server

    # Or from harness code:
    from harness.server import ensure_server_running
    ensure_server_running(provenance_dir, factory_root)
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

try:
    import fastapi
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print(
        "ERROR: fastapi and uvicorn are required. Install with:\n"
        "  pip install fastapi uvicorn[standard]\n"
        "or:\n"
        "  uv add fastapi uvicorn"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_SERVER_VERSION = "1.0.0"
_PORT = int(os.environ.get("HARNESS_SERVER_PORT", "8089"))
_SERVER_START_TIME = time.time()

# Resolve provenance directory: env var > default relative to this file
_DEFAULT_PROVENANCE_DIR = Path(__file__).parent.parent / "provenance"
_PROVENANCE_DIR: Path = Path(
    os.environ.get("HARNESS_PROVENANCE_DIR", str(_DEFAULT_PROVENANCE_DIR))
)

# Dashboard static files
_DASHBOARD_DIR = Path(__file__).parent / "dashboard"

# ---------------------------------------------------------------------------
# Active runs registry
# ---------------------------------------------------------------------------

# Dict of run_id → {"issue_key", "repository", "status", "pid", "started_at", ...}
_active_runs: Dict[str, dict] = {}
_active_subprocesses: Dict[str, subprocess.Popen] = {}


def register_run(run_id: str, issue_key: str, repository: str, pid: Optional[int] = None) -> None:
    """Called by harness instances when a run starts."""
    _active_runs[run_id] = {
        "run_id": run_id,
        "issue_key": issue_key,
        "repository": repository,
        "status": "running",
        "current_step": None,
        "pid": pid,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


def update_run(run_id: str, **kwargs) -> None:
    """Update metadata for an active run (e.g., current_step)."""
    if run_id in _active_runs:
        _active_runs[run_id].update(kwargs)


def complete_run(run_id: str, outcome: str) -> None:
    """Mark a run complete and remove from active tracking."""
    _active_runs.pop(run_id, None)
    _active_subprocesses.pop(run_id, None)


# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------

def _runs_dir() -> Path:
    return _PROVENANCE_DIR / "runs"


def _run_jsonl_path(run_id: str) -> Path:
    return _runs_dir() / f"{run_id}.jsonl"


def _run_summary_path(run_id: str) -> Path:
    return _runs_dir() / f"{run_id}.summary.json"


def _index_path() -> Path:
    return _PROVENANCE_DIR / "index.jsonl"


def _circuit_breakers_path() -> Path:
    return _PROVENANCE_DIR / "circuit_breakers.json"


def _read_index() -> List[dict]:
    """Read all summaries from index.jsonl, newest first."""
    idx = _index_path()
    if not idx.exists():
        return []
    lines = idx.read_text().splitlines()
    results = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return list(reversed(results))  # newest first


def _read_summary(run_id: str) -> Optional[dict]:
    path = _run_summary_path(run_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _read_run_events(run_id: str) -> List[dict]:
    path = _run_jsonl_path(run_id)
    if not path.exists():
        return []
    events = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def _parse_ts(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _days_ago(n: int) -> datetime:
    from datetime import timedelta
    return datetime.now(timezone.utc) - timedelta(days=n)


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def _compute_stats() -> dict:
    summaries = _read_index()

    today = datetime.now(timezone.utc).date()
    cutoff_7d = _days_ago(7)

    total = len(summaries)
    successes = sum(1 for s in summaries if s.get("overall_outcome") == "success")
    success_rate = (successes / total) if total else 0.0

    # Cost estimation: ~$0.01 per 1000 tokens; use duration as proxy
    # In reality, cost is not tracked in provenance; return 0 if no cost field
    def _cost(s: dict) -> float:
        return float(s.get("cost_usd", 0.0))

    runs_today = [
        s for s in summaries
        if _parse_ts(s.get("timestamp")) and _parse_ts(s.get("timestamp")).date() == today
    ]
    runs_7d = [
        s for s in summaries
        if _parse_ts(s.get("timestamp")) and _parse_ts(s.get("timestamp")) >= cutoff_7d
    ]

    avg_gate_attempts = (
        sum(s.get("gate_attempts", 0) for s in summaries) / total
        if total else 0.0
    )

    return {
        "success_rate": round(success_rate, 3),
        "avg_cost_usd": round(sum(_cost(s) for s in summaries), 4),
        "avg_gate_attempts": round(avg_gate_attempts, 2),
        "runs_today": len(runs_today),
        "cost_today_usd": round(sum(_cost(s) for s in runs_today), 4),
        "runs_7d": len(runs_7d),
        "cost_7d_usd": round(sum(_cost(s) for s in runs_7d), 4),
        "total_runs": total,
    }


def _compute_gate_health() -> dict:
    """Per-gate pass rate, avg duration, circuit state over last 7 days."""
    cutoff = _days_ago(7)

    gate_stats: Dict[str, dict] = defaultdict(lambda: {
        "pass": 0, "fail": 0, "duration_ms_sum": 0.0, "duration_count": 0
    })

    summaries = _read_index()
    for s in summaries:
        ts = _parse_ts(s.get("timestamp"))
        if ts and ts < cutoff:
            continue
        run_id = s.get("run_id")
        if not run_id:
            continue
        for event in _read_run_events(run_id):
            if event.get("event") != "gate":
                continue
            gate = event.get("gate", "unknown")
            gs = gate_stats[gate]
            if event.get("passed"):
                gs["pass"] += 1
            else:
                gs["fail"] += 1
            dur = event.get("duration_ms")
            if dur is not None:
                gs["duration_ms_sum"] += float(dur)
                gs["duration_count"] += 1

    # Read circuit breaker state
    cb_state: dict = {}
    cb_path = _circuit_breakers_path()
    if cb_path.exists():
        try:
            cb_state = json.loads(cb_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    result = {}
    for gate, gs in gate_stats.items():
        total = gs["pass"] + gs["fail"]
        pass_rate = gs["pass"] / total if total else 0.0
        avg_dur = gs["duration_ms_sum"] / gs["duration_count"] if gs["duration_count"] else 0.0
        circuit = cb_state.get(gate, {}).get("state", "closed")
        result[gate] = {
            "gate": gate,
            "pass_rate": round(pass_rate, 3),
            "total_attempts": total,
            "passes": gs["pass"],
            "failures": gs["fail"],
            "avg_duration_ms": round(avg_dur, 1),
            "circuit_state": circuit,
        }

    return result


# ---------------------------------------------------------------------------
# Prometheus metrics renderer
# ---------------------------------------------------------------------------

def _render_prometheus() -> str:
    """
    Build Prometheus text format from provenance data.
    Does NOT import prometheus_client.
    """
    lines: List[str] = []

    def metric_line(name: str, labels: dict, value: float) -> str:
        if labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
            return f"{name}{{{label_str}}} {value}"
        return f"{name} {value}"

    # ── dark_factory_runs_total ─────────────────────────────────────────
    lines += [
        "# HELP dark_factory_runs_total Total harness runs by outcome and repo",
        "# TYPE dark_factory_runs_total counter",
    ]
    counts: Dict[tuple, int] = defaultdict(int)
    for s in _read_index():
        key = (s.get("overall_outcome", "unknown"), s.get("repository", "unknown"))
        counts[key] += 1
    for (outcome, repo), n in sorted(counts.items()):
        lines.append(metric_line("dark_factory_runs_total", {"outcome": outcome, "repo": repo}, n))

    # ── dark_factory_gate_results_total ────────────────────────────────
    lines += [
        "# HELP dark_factory_gate_results_total Gate pass/fail counts",
        "# TYPE dark_factory_gate_results_total counter",
    ]
    gate_counts: Dict[tuple, int] = defaultdict(int)
    for s in _read_index():
        run_id = s.get("run_id")
        if not run_id:
            continue
        for event in _read_run_events(run_id):
            if event.get("event") != "gate":
                continue
            gate = event.get("gate", "unknown")
            result = "pass" if event.get("passed") else "fail"
            gate_counts[(gate, result)] += 1
    for (gate, result), n in sorted(gate_counts.items()):
        lines.append(metric_line("dark_factory_gate_results_total", {"gate": gate, "result": result}, n))

    # ── dark_factory_run_duration_seconds histogram ────────────────────
    lines += [
        "# HELP dark_factory_run_duration_seconds Harness run duration",
        "# TYPE dark_factory_run_duration_seconds histogram",
    ]
    buckets = [60, 120, 300, 600, 900, 1800, float("inf")]
    bucket_labels = ["60", "120", "300", "600", "900", "1800", "+Inf"]
    repo_durations: Dict[str, List[float]] = defaultdict(list)
    for s in _read_index():
        dur_s = float(s.get("duration_ms", 0)) / 1000.0
        repo = s.get("repository", "unknown")
        repo_durations[repo].append(dur_s)
    for repo, durations in sorted(repo_durations.items()):
        bucket_counts = [0] * len(buckets)
        for dur in durations:
            for i, b in enumerate(buckets):
                if dur <= b:
                    bucket_counts[i] += 1
        cum = 0
        for i, (b_label, b_count) in enumerate(zip(bucket_labels, bucket_counts)):
            cum += b_count
            lines.append(metric_line(
                "dark_factory_run_duration_seconds_bucket",
                {"repo": repo, "le": b_label}, cum
            ))
        total_dur = sum(durations)
        lines.append(metric_line("dark_factory_run_duration_seconds_sum", {"repo": repo}, round(total_dur, 3)))
        lines.append(metric_line("dark_factory_run_duration_seconds_count", {"repo": repo}, len(durations)))

    # ── dark_factory_active_runs gauge ─────────────────────────────────
    lines += [
        "# HELP dark_factory_active_runs Currently running harness runs",
        "# TYPE dark_factory_active_runs gauge",
        f"dark_factory_active_runs {len(_active_runs)}",
    ]

    # ── dark_factory_cost_dollars_total counter ────────────────────────
    lines += [
        "# HELP dark_factory_cost_dollars_total Total API cost in USD",
        "# TYPE dark_factory_cost_dollars_total counter",
    ]
    repo_costs: Dict[str, float] = defaultdict(float)
    for s in _read_index():
        repo = s.get("repository", "unknown")
        repo_costs[repo] += float(s.get("cost_usd", 0.0))
    for repo, cost in sorted(repo_costs.items()):
        lines.append(metric_line("dark_factory_cost_dollars_total", {"repo": repo}, round(cost, 6)))

    # ── dark_factory_circuit_breaker_open gauge ────────────────────────
    lines += [
        "# HELP dark_factory_circuit_breaker_open Circuit breaker state (1=open/broken, 0=closed/healthy)",
        "# TYPE dark_factory_circuit_breaker_open gauge",
    ]
    cb_state: dict = {}
    cb_path = _circuit_breakers_path()
    if cb_path.exists():
        try:
            cb_state = json.loads(cb_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    for gate, info in sorted(cb_state.items()):
        is_open = 1 if info.get("state") == "open" else 0
        lines.append(metric_line("dark_factory_circuit_breaker_open", {"gate": gate}, is_open))

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# SSE streaming
# ---------------------------------------------------------------------------

async def _tail_run_events(run_id: str) -> AsyncIterator[str]:
    """
    Yield SSE-formatted lines for a run's JSONL file.
    Emits existing lines, then tails for new lines until run_end or disconnect.
    """
    path = _run_jsonl_path(run_id)
    position = 0

    # Wait up to 5s for the file to appear (run may have just started)
    for _ in range(10):
        if path.exists():
            break
        await asyncio.sleep(0.5)

    if not path.exists():
        yield f"data: {json.dumps({'error': 'run not found', 'run_id': run_id})}\n\n"
        return

    finished = False
    while not finished:
        try:
            with open(path, "r") as fh:
                fh.seek(position)
                while True:
                    line = fh.readline()
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    position = fh.tell()
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    yield f"data: {json.dumps(event)}\n\n"
                    if event.get("event") in ("run_end", "error"):
                        finished = True
                        break
        except OSError:
            pass

        if not finished:
            await asyncio.sleep(0.5)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Dark Factory Observability Server",
    version=_SERVER_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {
        "status": "ok",
        "uptime_s": round(time.time() - _SERVER_START_TIME, 1),
        "active_runs_count": len(_active_runs),
        "server_version": _SERVER_VERSION,
    }


# ── Static dashboard ────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def dashboard():
    index = _DASHBOARD_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index), media_type="text/html")
    return JSONResponse(
        {"error": "Dashboard not found", "hint": "Expected at harness/dashboard/index.html"},
        status_code=404,
    )


# ── Runs ───────────────────────────────────────────────────────────────────

@app.get("/api/runs", tags=["runs"])
async def list_runs(
    repo: Optional[str] = Query(None),
    outcome: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    summaries = _read_index()

    if repo:
        summaries = [s for s in summaries if s.get("repository") == repo]
    if outcome:
        summaries = [s for s in summaries if s.get("overall_outcome") == outcome]

    total = len(summaries)
    page = summaries[offset: offset + limit]

    # Enrich with active-run info
    active_ids = set(_active_runs.keys())
    for s in page:
        s["is_active"] = s.get("run_id") in active_ids

    return {"total": total, "offset": offset, "limit": limit, "runs": page}


@app.get("/api/runs/{run_id}", tags=["runs"])
async def get_run(run_id: str) -> dict:
    summary = _read_summary(run_id)
    events = _read_run_events(run_id)

    if not summary and not events:
        # May be an in-progress run without a summary yet
        active = _active_runs.get(run_id)
        if not active:
            raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")
        return {
            "run_id": run_id,
            "summary": active,
            "events": events,
            "is_active": True,
        }

    return {
        "run_id": run_id,
        "summary": summary,
        "events": events,
        "is_active": run_id in _active_runs,
    }


@app.get("/api/runs/{run_id}/events", tags=["runs"])
async def stream_run_events(run_id: str) -> StreamingResponse:
    return StreamingResponse(
        _tail_run_events(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/runs", tags=["runs"], status_code=202)
async def spawn_run(body: dict) -> dict:
    """
    Spawn a harness run as a background subprocess.
    Body: {"issue_key": "ABI-123", "repository": "runtime"}
    Returns: {"run_id": "run_..."}
    """
    issue_key = body.get("issue_key")
    repository = body.get("repository", "runtime")
    if not issue_key:
        raise HTTPException(status_code=400, detail="issue_key is required")

    # Build run_id now so we can return it immediately
    import uuid as _uuid
    run_id = f"run_{int(time.time())}_{_uuid.uuid4().hex[:8]}"

    factory_root = Path(__file__).parent.parent
    cmd = [
        sys.executable, "-m", "harness.cli", "implement", issue_key,
        "--repo", repository,
        "--harness",
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(factory_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        register_run(run_id, issue_key, repository, pid=proc.pid)
        _active_subprocesses[run_id] = proc
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to spawn: {exc}") from exc

    return {"run_id": run_id, "issue_key": issue_key, "repository": repository, "pid": proc.pid}


@app.post("/api/runs/{run_id}/cancel", tags=["runs"])
async def cancel_run(run_id: str) -> dict:
    proc = _active_subprocesses.get(run_id)
    active = _active_runs.get(run_id)

    if not proc and not active:
        raise HTTPException(status_code=404, detail=f"Active run {run_id!r} not found")

    killed = False
    if proc:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            killed = True
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.terminate()
                killed = True
            except (ProcessLookupError, OSError):
                pass
    elif active and active.get("pid"):
        try:
            os.kill(active["pid"], signal.SIGTERM)
            killed = True
        except (ProcessLookupError, PermissionError, OSError):
            pass

    complete_run(run_id, "cancelled")
    return {"run_id": run_id, "cancelled": killed}


# ── Queue ──────────────────────────────────────────────────────────────────

@app.get("/api/queue", tags=["queue"])
async def get_queue() -> dict:
    active = list(_active_runs.values())

    # "waiting" runs: look for lock files
    waiting = []
    lock_dir = _PROVENANCE_DIR / "locks"
    if lock_dir.exists():
        for lf in lock_dir.glob("*.lock"):
            try:
                info = json.loads(lf.read_text())
                waiting.append(info)
            except (json.JSONDecodeError, OSError):
                waiting.append({"lock_file": str(lf)})

    return {"active": active, "waiting": waiting}


# ── Stats ──────────────────────────────────────────────────────────────────

@app.get("/api/stats", tags=["stats"])
async def get_stats() -> dict:
    return _compute_stats()


# ── Gates ─────────────────────────────────────────────────────────────────

@app.get("/api/gates/health", tags=["gates"])
async def get_gate_health() -> dict:
    return _compute_gate_health()


# ── Circuit Breakers ───────────────────────────────────────────────────────

@app.get("/api/circuit-breakers", tags=["circuit-breakers"])
async def get_circuit_breakers() -> dict:
    path = _circuit_breakers_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/circuit-breakers/{gate}/reset", tags=["circuit-breakers"])
async def reset_circuit_breaker(gate: str) -> dict:
    path = _circuit_breakers_path()
    state: dict = {}
    if path.exists():
        try:
            state = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            state = {}

    if gate not in state:
        raise HTTPException(status_code=404, detail=f"Gate {gate!r} not found in circuit breakers")

    state[gate]["state"] = "closed"
    state[gate]["reset_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(state, indent=2))
    return {"gate": gate, "state": "closed", "message": "Circuit breaker reset"}


# ── Prometheus metrics ─────────────────────────────────────────────────────

@app.get("/metrics", tags=["metrics"], response_class=fastapi.responses.PlainTextResponse)
async def prometheus_metrics() -> str:
    return _render_prometheus()


# ---------------------------------------------------------------------------
# ensure_server_running helper (called by harness.py)
# ---------------------------------------------------------------------------

def ensure_server_running(provenance_dir: Path, factory_root: Path) -> bool:
    """
    Start the server as a background subprocess if not already running.
    Writes PID to provenance_dir/.server.pid.
    Returns True if started, False if already running.
    """
    pid_file = Path(provenance_dir) / ".server.pid"

    # Check if already running
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)  # signal 0 = existence check, no actual signal
            # Process exists — server is running
            return False
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            pass  # stale PID or not running; start it

    # Start the server
    cmd = [sys.executable, "-m", "harness.server"]
    env = os.environ.copy()
    env["HARNESS_PROVENANCE_DIR"] = str(provenance_dir)

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(factory_root),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(proc.pid))
        # Give it a moment to bind
        time.sleep(1.0)
        print(f"  Dark Factory server started (PID {proc.pid}) → http://localhost:{_PORT}/")
        return True
    except OSError as exc:
        print(f"  WARNING: Could not start observability server: {exc}")
        return False


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Resolve provenance dir from env or default
    prov_dir = Path(os.environ.get("HARNESS_PROVENANCE_DIR", str(_DEFAULT_PROVENANCE_DIR)))
    prov_dir.mkdir(parents=True, exist_ok=True)
    (prov_dir / "runs").mkdir(parents=True, exist_ok=True)

    # Write our own PID so ensure_server_running can detect us
    pid_file = prov_dir / ".server.pid"
    pid_file.write_text(str(os.getpid()))

    print(f"Dark Factory Observability Server v{_SERVER_VERSION}")
    print(f"  Dashboard : http://localhost:{_PORT}/")
    print(f"  API docs  : http://localhost:{_PORT}/docs")
    print(f"  Metrics   : http://localhost:{_PORT}/metrics")
    print(f"  Provenance: {prov_dir}")

    uvicorn.run(
        "harness.server:app",
        host="0.0.0.0",
        port=_PORT,
        log_level="info",
        reload=False,
    )
