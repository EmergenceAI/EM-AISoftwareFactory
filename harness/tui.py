"""
Dark Factory TUI — live-refreshing terminal dashboard for the AI Software Factory harness.

Reads provenance files directly (no server dependency) and optionally fetches
active-run data from the REST server at http://localhost:8089/api if it is up.

Usage:
    python -m harness.tui
    python harness/tui.py
    harness tui          # if wired into the CLI
"""

from __future__ import annotations

import datetime
import json
import os
import sys
import termios
import threading
import time
import tty
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Rich import — graceful fallback
# ---------------------------------------------------------------------------

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.style import Style
    from rich.table import Table
    from rich.text import Text
    from rich import box
except ImportError:
    print("Error: 'rich' is not installed. Install it with:\n\n  pip install rich\n", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Path discovery
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent          # harness/
_FACTORY_ROOT = _HERE.parent           # EM-AISoftwareFactory/

PROV_DIR: Path = (
    Path(os.environ["HARNESS_PROVENANCE_DIR"])
    if "HARNESS_PROVENANCE_DIR" in os.environ
    else _FACTORY_ROOT / "provenance"
)
INDEX_PATH = PROV_DIR / "index.jsonl"
CIRCUIT_BREAKER_PATH = PROV_DIR / "circuit_breakers.json"
WORKSPACE_YAML = _FACTORY_ROOT / "workspace.yaml"

SERVER_BASE = "http://localhost:8089/api"

# ---------------------------------------------------------------------------
# Global state shared between refresh thread and key-binding thread
# ---------------------------------------------------------------------------

_state: Dict = {
    "active_runs": [],
    "today_stats": {},
    "gate_health": {},
    "circuit_states": {},
    "recent_runs": [],
    "last_refresh": None,
    "show_help": False,
    "overlay_text": None,   # non-None string = show overlay panel
    "running": True,
    "force_refresh": threading.Event(),
}
_state_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _read_index(limit: Optional[int] = None) -> List[dict]:
    """Return parsed lines from index.jsonl, newest-first. Returns [] if missing."""
    if not INDEX_PATH.exists():
        return []
    lines = []
    try:
        raw = INDEX_PATH.read_text().splitlines()
    except OSError:
        return []
    for line in reversed(raw):
        line = line.strip()
        if not line:
            continue
        try:
            lines.append(json.loads(line))
        except json.JSONDecodeError:
            pass
        if limit and len(lines) >= limit:
            break
    return lines


def load_recent_runs(limit: int = 10) -> List[dict]:
    """Read provenance/index.jsonl, return last `limit` summaries (newest first)."""
    return _read_index(limit=limit)


def load_today_stats() -> dict:
    """Filter index for today's runs. Return: total, success, partial, failed, cost_usd."""
    today = datetime.date.today().isoformat()
    stats = {"total": 0, "success": 0, "partial": 0, "failed": 0, "cost_usd": 0.0, "avg_attempts": 0.0}
    attempts_list: List[float] = []

    for entry in _read_index():
        ts = entry.get("timestamp", "")
        if not ts.startswith(today):
            # Index is append-only newest at bottom; once we pass today, stop
            continue
        stats["total"] += 1
        outcome = entry.get("overall_outcome", "failed")
        if outcome in stats:
            stats[outcome] += 1  # type: ignore[literal-required]
        # cost: not yet tracked in summary — placeholder based on reward heuristic
        reward = entry.get("reward", 0.0)
        stats["cost_usd"] += reward * 1.5  # rough proxy; real field TBD
        attempts = entry.get("gate_attempts", 1)
        if isinstance(attempts, (int, float)):
            attempts_list.append(float(attempts))

    if attempts_list:
        stats["avg_attempts"] = sum(attempts_list) / len(attempts_list)
    return stats


def load_gate_health(days: int = 7) -> Dict[str, dict]:
    """
    Scan provenance/index.jsonl for runs in the last N days.
    Per gate: pass_rate, avg_duration_ms, flakiness_rate.
    """
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat() + "Z"

    gate_data: Dict[str, dict] = {}

    runs_dir = PROV_DIR / "runs"
    if not runs_dir.exists():
        return gate_data

    # Collect gate events from JSONL run files that fall in window
    for summary_file in runs_dir.glob("*.summary.json"):
        try:
            summary = json.loads(summary_file.read_text())
        except (OSError, json.JSONDecodeError):
            continue

        if summary.get("timestamp", "") < cutoff:
            continue

        run_id = summary.get("run_id", "")
        if not run_id:
            continue

        run_file = runs_dir / f"{run_id}.jsonl"
        if not run_file.exists():
            continue

        try:
            events_raw = run_file.read_text().splitlines()
        except OSError:
            continue

        for line in events_raw:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event") != "gate":
                continue
            gate = event.get("gate", "unknown")
            passed = bool(event.get("passed", False))
            attempt = int(event.get("attempt", 1))
            duration_ms = float(event.get("duration_ms", 0.0))

            if gate not in gate_data:
                gate_data[gate] = {
                    "total_attempts": 0,
                    "passes": 0,
                    "first_attempt_passes": 0,
                    "total_duration_ms": 0.0,
                }
            gd = gate_data[gate]
            gd["total_attempts"] += 1
            if passed:
                gd["passes"] += 1
                if attempt == 1:
                    gd["first_attempt_passes"] += 1
            gd["total_duration_ms"] += duration_ms

    # Compute rates
    result: Dict[str, dict] = {}
    for gate, gd in gate_data.items():
        total = gd["total_attempts"]
        passes = gd["passes"]
        first_passes = gd["first_attempt_passes"]
        pass_rate = passes / total if total else 0.0
        # Flakiness: passed but not on first attempt (needed a retry)
        flakiness = (passes - first_passes) / total if total else 0.0
        avg_dur = gd["total_duration_ms"] / total if total else 0.0
        result[gate] = {
            "pass_rate": pass_rate,
            "flakiness_rate": flakiness,
            "avg_duration_ms": avg_dur,
            "total_attempts": total,
        }
    return result


def load_circuit_states() -> Dict[str, dict]:
    """Read provenance/circuit_breakers.json or return all-closed defaults."""
    defaults: Dict[str, dict] = {
        gate: {"state": "closed", "consecutive_failures": 0, "opened_at": None}
        for gate in ("linter", "tests", "evals", "code-review")
    }
    if not CIRCUIT_BREAKER_PATH.exists():
        return defaults
    try:
        data = json.loads(CIRCUIT_BREAKER_PATH.read_text())
        # Merge with defaults so any missing gate is closed
        for gate, info in data.items():
            defaults[gate] = info
        return defaults
    except (OSError, json.JSONDecodeError):
        return defaults


def _get_workspace_root() -> Optional[Path]:
    """Parse workspace.yaml to get the workspace root path."""
    if not WORKSPACE_YAML.exists():
        return None
    try:
        import yaml  # type: ignore[import-untyped]
        with open(WORKSPACE_YAML) as f:
            cfg = yaml.safe_load(f)
        root = cfg.get("workspace", {}).get("root")
        if root:
            return Path(root)
    except Exception:
        pass
    return None


def _try_server_queue() -> Optional[List[dict]]:
    """
    Attempt GET http://localhost:8089/api/queue.
    Returns list of active run dicts on success, None on failure.
    """
    try:
        req = urllib.request.Request(f"{SERVER_BASE}/queue", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def load_active_runs() -> List[dict]:
    """
    Try GET http://localhost:8089/api/queue first.
    Fall back to scanning {workspace_root}/*/.harness-results/checkpoint.json.
    """
    server_data = _try_server_queue()
    if server_data is not None:
        return server_data

    runs: List[dict] = []
    workspace_root = _get_workspace_root() or _FACTORY_ROOT.parent
    if not workspace_root.exists():
        return runs

    for checkpoint_path in workspace_root.rglob(".harness-results/checkpoint.json"):
        # Skip if older than 2 hours (stale)
        try:
            mtime = checkpoint_path.stat().st_mtime
            if time.time() - mtime > 7200:
                continue
        except OSError:
            continue

        try:
            data = json.loads(checkpoint_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue

        repo_path = checkpoint_path.parent.parent
        data["_repo_path"] = str(repo_path)
        data["_checkpoint_mtime"] = mtime
        runs.append(data)

    return runs


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _outcome_icon(outcome: str) -> str:
    return {"success": "✅", "partial": "⚠️ ", "failed": "❌"}.get(outcome, " ? ")


def _outcome_style(outcome: str) -> str:
    return {"success": "bold green", "partial": "bold yellow", "failed": "bold red"}.get(outcome, "")


def _short_run_id(run_id: str) -> str:
    """Return a compact run_id: first 8 chars of the last UUID-like segment."""
    parts = run_id.split("_")
    suffix = parts[-1] if parts else run_id
    return suffix[:8]


def _fmt_duration(ms: Optional[float]) -> str:
    if ms is None or ms <= 0:
        return "—"
    secs = int(ms / 1000)
    if secs < 60:
        return f"{secs}s"
    mins = secs // 60
    secs_rem = secs % 60
    if mins < 60:
        return f"{mins}m{secs_rem:02d}s" if secs_rem else f"{mins}m"
    hrs = mins // 60
    mins_rem = mins % 60
    return f"{hrs}h{mins_rem:02d}m"


def _elapsed_since(mtime: float) -> str:
    return _fmt_duration((time.time() - mtime) * 1000)


def _pass_bar(pass_rate: float, width: int = 20) -> Text:
    """Render a text progress bar with appropriate color."""
    filled = int(pass_rate * width)
    empty = width - filled
    bar_text = "█" * filled + "░" * empty

    if pass_rate > 0.85:
        color = "green"
    elif pass_rate >= 0.70:
        color = "yellow"
    else:
        color = "red"

    t = Text()
    t.append(bar_text, style=color)
    return t


def _circuit_icon(state: str) -> Text:
    if state == "open":
        return Text("⚠️  OPEN", style="bold red")
    return Text("● closed", style="green")


# ---------------------------------------------------------------------------
# Panel / table renderers
# ---------------------------------------------------------------------------

def _render_active_runs(active_runs: List[dict]) -> Panel:
    count = len(active_runs)
    title = f"Active Runs ({count})" if count else "Active Runs"

    table = Table(
        box=box.SIMPLE,
        show_header=False,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("icon", width=3, no_wrap=True)
    table.add_column("issue", style="bold cyan", no_wrap=True)
    table.add_column("step", no_wrap=True)
    table.add_column("elapsed", no_wrap=True)
    table.add_column("repo", style="dim", no_wrap=True)

    if not active_runs:
        table.add_row("", Text("No active runs", style="dim"), "", "", "")
    else:
        for run in active_runs:
            issue_key = run.get("issue_key", "—")
            completed = run.get("completed_steps", [])
            last_step = run.get("last_step", "—") or "—"
            mtime = run.get("_checkpoint_mtime")
            elapsed = _elapsed_since(mtime) if mtime else "—"

            # Determine icon from last step
            if "queued" in last_step.lower():
                icon = Text("⏳", style="dim")
                step_style = "dim"
            elif "gate" in last_step.lower():
                icon = Text("🔄", style="bold yellow")
                step_style = "bold yellow"
            elif completed:
                icon = Text("🔄", style="bold cyan")
                step_style = "bold cyan"
            else:
                icon = Text("⏳", style="dim")
                step_style = "dim"

            repo_path = run.get("_repo_path", "")
            repo_name = Path(repo_path).name if repo_path else run.get("repository", "—")

            table.add_row(
                icon,
                issue_key,
                Text(last_step, style=step_style),
                elapsed,
                repo_name,
            )

    return Panel(table, title=title, border_style="blue")


def _render_today_stats(stats: dict) -> Panel:
    total = stats.get("total", 0)
    success = stats.get("success", 0)
    partial = stats.get("partial", 0)
    failed = stats.get("failed", 0)
    cost = stats.get("cost_usd", 0.0)
    avg_att = stats.get("avg_attempts", 0.0)

    t = Text()
    t.append(f"Runs:  {total}\n", style="bold")
    t.append("✅ ", style="bold green")
    t.append(f"{success}  ", style="bold green")
    t.append("⚠️  ", style="bold yellow")
    t.append(f"{partial}  ", style="bold yellow")
    t.append("❌ ", style="bold red")
    t.append(f"{failed}\n", style="bold red")
    t.append(f"Cost:  ${cost:.2f}\n")
    t.append(f"Avg:   {avg_att:.1f} attempts")

    return Panel(t, title="Today", border_style="blue")


def _render_gate_health(
    gate_health: Dict[str, dict],
    circuit_states: Dict[str, dict],
) -> Panel:
    table = Table(
        box=box.SIMPLE,
        show_header=False,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("gate", width=14, no_wrap=True)
    table.add_column("bar", width=22, no_wrap=True)
    table.add_column("pct", width=10, no_wrap=True)
    table.add_column("flakiness", width=16, no_wrap=True)
    table.add_column("circuit", no_wrap=True)

    known_gates = ("linter", "tests", "evals", "code-review")
    all_gates = list(dict.fromkeys(list(known_gates) + list(gate_health.keys())))

    for gate in all_gates:
        info = gate_health.get(gate)
        cb = circuit_states.get(gate, {"state": "closed"})
        cb_icon = _circuit_icon(cb.get("state", "closed"))

        if not info:
            table.add_row(
                Text(gate, style="dim"),
                Text("─" * 20, style="dim"),
                Text("—", style="dim"),
                Text("—", style="dim"),
                cb_icon,
            )
            continue

        pass_rate = info["pass_rate"]
        flakiness = info["flakiness_rate"]
        bar = _pass_bar(pass_rate)

        pct_text = Text(f"{pass_rate*100:.0f}% pass")
        if pass_rate > 0.85:
            pct_text.stylize("green")
        elif pass_rate >= 0.70:
            pct_text.stylize("yellow")
        else:
            pct_text.stylize("red")

        if flakiness > 0.01:
            flak_text = Text(f"⚡ flaky {flakiness*100:.0f}%", style="yellow")
        else:
            flak_text = Text("")

        table.add_row(
            Text(gate),
            bar,
            pct_text,
            flak_text,
            cb_icon,
        )

    return Panel(table, title="Gate Health (7-day)", border_style="blue")


def _render_recent_runs(recent_runs: List[dict]) -> Panel:
    table = Table(
        box=box.SIMPLE,
        show_header=False,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("icon", width=4, no_wrap=True)
    table.add_column("run_id", width=12, no_wrap=True, style="dim")
    table.add_column("issue", width=12, no_wrap=True, style="bold")
    table.add_column("repo", width=14, no_wrap=True, style="dim")
    table.add_column("dur", width=8, no_wrap=True)
    table.add_column("att", width=6, no_wrap=True)
    table.add_column("cost", width=8, no_wrap=True)
    table.add_column("label", no_wrap=True)

    if not recent_runs:
        table.add_row("", "", Text("No runs yet", style="dim"), "", "", "", "", "")
    else:
        for run in recent_runs:
            outcome = run.get("overall_outcome", "failed")
            icon = _outcome_icon(outcome)
            style = _outcome_style(outcome)

            short_id = _short_run_id(run.get("run_id", "—"))
            issue = run.get("issue_key", "—")
            repo = run.get("repository", "—")
            dur = _fmt_duration(run.get("duration_ms"))
            attempts = run.get("gate_attempts")
            att_str = str(attempts) if attempts is not None else "—"

            # cost: placeholder from reward
            reward = run.get("reward")
            cost_str = f"${reward*1.5:.2f}" if reward is not None else "—"

            # label: human_feedback or needs-review for partial
            label = run.get("human_feedback") or ""
            if not label and outcome == "partial":
                label = "NEEDS-REVIEW"

            label_text = Text(label)
            if label == "NEEDS-REVIEW":
                label_text.stylize("bold yellow")

            table.add_row(
                Text(icon, style=style),
                short_id,
                Text(issue, style=style),
                repo,
                dur,
                att_str,
                cost_str,
                label_text,
            )

    return Panel(table, title="Recent Runs (last 10)", border_style="blue")


def _render_footer(show_help: bool) -> Panel:
    if show_help:
        help_text = (
            "[q/Q] quit  [r/R] force refresh  [w/W] watch run  "
            "[c/C] cancel run  [?] toggle help\n\n"
            "watch: streams live events from the run's JSONL file below the dashboard.\n"
            "cancel: sends a cancel request to the REST server (requires server running).\n"
            "Refresh interval: 2 seconds.  Data read directly from provenance/ files."
        )
        return Panel(Text(help_text, style="dim"), title="Help", border_style="dim")
    return Panel(
        Text(
            "[q] quit   [w] watch run   [c] cancel run   [r] refresh now   [?] help",
            style="dim",
        ),
        border_style="dim",
    )


def _render_overlay(text: str) -> Panel:
    return Panel(Text(text), title="Input", border_style="bold yellow")


def _build_layout(state: dict) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="top", size=10),
        Layout(name="gate", size=10),
        Layout(name="recent", size=14),
        Layout(name="footer", size=4),
    )

    # Header
    ts = state.get("last_refresh")
    ts_str = ts.strftime("%H:%M:%S") if ts else "—"
    header_text = Text()
    header_text.append("🏭 Dark Factory", style="bold white")
    header_text.append(f"   last refresh: {ts_str}", style="dim")
    layout["header"].update(Panel(header_text, border_style="bright_blue"))

    # Top row: active runs + today stats
    top = Layout()
    top.split_row(
        Layout(name="active", ratio=3),
        Layout(name="today", ratio=2),
    )
    top["active"].update(_render_active_runs(state.get("active_runs", [])))
    top["today"].update(_render_today_stats(state.get("today_stats", {})))
    layout["top"].update(top)

    # Gate health
    layout["gate"].update(
        _render_gate_health(
            state.get("gate_health", {}),
            state.get("circuit_states", {}),
        )
    )

    # Recent runs
    layout["recent"].update(_render_recent_runs(state.get("recent_runs", [])))

    # Footer / help / overlay
    overlay = state.get("overlay_text")
    if overlay:
        layout["footer"].update(_render_overlay(overlay))
    else:
        layout["footer"].update(_render_footer(state.get("show_help", False)))

    return layout


# ---------------------------------------------------------------------------
# Data refresh thread
# ---------------------------------------------------------------------------

def _refresh_data(state: dict, lock: threading.Lock) -> None:
    """Load all data and update state dict atomically."""
    active_runs = load_active_runs()
    today_stats = load_today_stats()
    gate_health = load_gate_health(days=7)
    circuit_states = load_circuit_states()
    recent_runs = load_recent_runs(limit=10)

    with lock:
        state["active_runs"] = active_runs
        state["today_stats"] = today_stats
        state["gate_health"] = gate_health
        state["circuit_states"] = circuit_states
        state["recent_runs"] = recent_runs
        state["last_refresh"] = datetime.datetime.now()


def _data_thread(state: dict, lock: threading.Lock) -> None:
    """Background thread: refresh data every 2 seconds or on force_refresh event."""
    while True:
        with lock:
            running = state.get("running", True)
        if not running:
            break
        _refresh_data(state, lock)
        # Wait 2s but wake up if force_refresh is set
        state["force_refresh"].wait(timeout=2.0)
        state["force_refresh"].clear()


# ---------------------------------------------------------------------------
# Key input thread
# ---------------------------------------------------------------------------

def _read_char() -> Optional[str]:
    """Read one character from stdin (non-blocking, raw mode)."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        return ch
    except Exception:
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _watch_run(run_id_or_issue: str, console: Console) -> None:
    """Stream live events from a run's JSONL file until Enter is pressed."""
    runs_dir = PROV_DIR / "runs"
    target_path: Optional[Path] = None

    # Resolve by run_id or issue_key
    candidate = runs_dir / f"{run_id_or_issue}.jsonl"
    if candidate.exists():
        target_path = candidate
    else:
        # Search summaries for matching issue_key
        for sf in sorted(runs_dir.glob("*.summary.json"), reverse=True):
            try:
                s = json.loads(sf.read_text())
            except Exception:
                continue
            if s.get("issue_key", "").lower() == run_id_or_issue.lower():
                run_id_found = s.get("run_id", sf.stem.replace(".summary", ""))
                target_path = runs_dir / f"{run_id_found}.jsonl"
                break

    if not target_path or not target_path.exists():
        console.print(f"[bold red]Run not found:[/bold red] {run_id_or_issue}")
        console.print("Press Enter to return...")
        sys.stdin.readline()
        return

    console.print(f"[bold cyan]Watching:[/bold cyan] {target_path.name}  (press Enter to stop)\n")
    stop_event = threading.Event()

    def _tail():
        seen_bytes = 0
        while not stop_event.is_set():
            try:
                data = target_path.read_bytes()
            except OSError:
                time.sleep(0.5)
                continue
            if len(data) > seen_bytes:
                new_data = data[seen_bytes:].decode(errors="replace")
                for line in new_data.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        console.print(line)
                        continue
                    ev_type = event.get("event", "?")
                    ts = event.get("timestamp", "")[:19].replace("T", " ")
                    if ev_type == "step":
                        icon = "✅" if event.get("success") else "❌"
                        console.print(
                            f"[dim]{ts}[/dim] {icon} step [bold]{event.get('step')}[/bold] "
                            f"({_fmt_duration(event.get('duration_ms'))})"
                        )
                    elif ev_type == "gate":
                        icon = "✅" if event.get("passed") else "❌"
                        console.print(
                            f"[dim]{ts}[/dim] {icon} gate [bold]{event.get('gate')}[/bold] "
                            f"attempt={event.get('attempt')} "
                            f"({_fmt_duration(event.get('duration_ms'))})"
                        )
                    elif ev_type == "error":
                        console.print(f"[dim]{ts}[/dim] [bold red]error[/bold red] {event.get('error')}")
                    elif ev_type == "run_end":
                        outcome = event.get("overall_outcome", "?")
                        console.print(
                            f"[dim]{ts}[/dim] [bold]run_end[/bold] outcome={outcome} "
                            f"reward={event.get('reward')}"
                        )
                    else:
                        console.print(f"[dim]{ts}[/dim] {ev_type}")
                seen_bytes = len(data)
            time.sleep(0.5)

    t = threading.Thread(target=_tail, daemon=True)
    t.start()

    # Wait for Enter
    try:
        sys.stdin.readline()
    except Exception:
        pass
    stop_event.set()
    t.join(timeout=1)
    console.print("\n[dim]Watch ended. Returning to dashboard...[/dim]")
    time.sleep(1)


def _cancel_run(run_id_or_issue: str, console: Console) -> None:
    """Send a cancel request to the REST server."""
    try:
        payload = json.dumps({"run_id": run_id_or_issue, "issue_key": run_id_or_issue}).encode()
        req = urllib.request.Request(
            f"{SERVER_BASE}/cancel",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            body = resp.read().decode()
            console.print(f"[bold green]Cancelled:[/bold green] {body}")
    except urllib.error.URLError:
        console.print("[bold yellow]Server not running[/bold yellow] — cannot cancel remotely.")
        console.print("To stop a run manually, kill the harness process.")

    console.print("Press Enter to return...")
    sys.stdin.readline()


def _key_thread(state: dict, lock: threading.Lock, live: "Live", console: Console) -> None:
    """Read keystrokes and update state. Runs in a background daemon thread."""
    while True:
        with lock:
            if not state.get("running", True):
                break

        ch = _read_char()
        if ch is None:
            continue

        if ch in ("q", "Q"):
            with lock:
                state["running"] = False
            break

        elif ch in ("r", "R"):
            state["force_refresh"].set()

        elif ch == "?":
            with lock:
                state["show_help"] = not state.get("show_help", False)

        elif ch in ("w", "W"):
            # Pause live, prompt user, stream events
            live.stop()
            console.print()
            console.print("[bold cyan]Watch run[/bold cyan] — enter run_id or issue_key (blank=cancel): ", end="")
            # Restore line mode for input
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
            try:
                val = sys.stdin.readline().strip()
            except Exception:
                val = ""
            if val:
                _watch_run(val, console)
            live.start(refresh=True)

        elif ch in ("c", "C"):
            live.stop()
            console.print()
            console.print("[bold yellow]Cancel run[/bold yellow] — enter run_id or issue_key (blank=cancel): ", end="")
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
            try:
                val = sys.stdin.readline().strip()
            except Exception:
                val = ""
            if val:
                _cancel_run(val, console)
            live.start(refresh=True)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Launch the TUI. Called by `harness tui` CLI command."""
    console = Console()

    # Initial data load
    lock = threading.Lock()
    _refresh_data(_state, lock)

    # Start data refresh thread
    dt = threading.Thread(target=_data_thread, args=(_state, lock), daemon=True)
    dt.start()

    with Live(
        _build_layout(_state),
        console=console,
        refresh_per_second=0.5,
        screen=True,
    ) as live:

        # Start key-binding thread (needs live handle for pause/resume)
        kt = threading.Thread(target=_key_thread, args=(_state, lock, live, console), daemon=True)
        kt.start()

        while True:
            with lock:
                if not _state.get("running", True):
                    break

            with lock:
                layout = _build_layout(_state)
            live.update(layout)
            time.sleep(0.1)  # tight loop; actual data refresh is every 2s

    # Teardown
    with lock:
        _state["running"] = False

    console.print("\n[bold]Dark Factory TUI exited.[/bold]")


if __name__ == "__main__":
    main()
