"""Watchdog — background thread that alerts and escalates hung harness steps.

The watchdog runs as a daemon thread alongside the main harness process.  It
monitors how long the current step has been running and escalates in two
stages:

1. **Warn** — calls the caller-supplied ``on_warn`` callback once per step.
2. **Kill** — calls ``on_kill``, then terminates the subprocess (if one was
   registered via :meth:`Watchdog.set_step`) and raises an internal flag so
   the harness knows the run has been aborted.

Thresholds (warn → hard kill)::

    research, plan, fix:  20 min warn  / 60 min kill
    implement:            45 min warn  / 90 min kill  (implement is longest)
    any gate:             15 min warn  / 60 min kill
    create-pr:            10 min warn  / 30 min kill

Typical usage::

    import subprocess
    from harness.watchdog import Watchdog

    def warn_handler(step: str, elapsed: float) -> None:
        print(f"WARNING: step '{step}' has been running for {elapsed/60:.1f} min")

    def kill_handler(step: str, elapsed: float) -> None:
        print(f"ERROR: killing step '{step}' after {elapsed/60:.1f} min")
        mark_run_failed()

    watchdog = Watchdog(run_id="run_abc", on_warn=warn_handler, on_kill=kill_handler)
    watchdog.start()

    proc = subprocess.Popen(["claude", ...])
    watchdog.set_step("research", proc)
    proc.wait()

    watchdog.set_step("plan", proc2)
    ...

    watchdog.stop()
"""

import subprocess
import threading
import time
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Threshold tables (seconds)
# ---------------------------------------------------------------------------

WARN_THRESHOLDS_S: dict = {
    "research":  20 * 60,
    "plan":      20 * 60,
    "fix":       20 * 60,
    "implement": 45 * 60,
    "create-pr": 10 * 60,
    "default":   15 * 60,  # gates and any unrecognised step
}

KILL_THRESHOLDS_S: dict = {
    "research":  60 * 60,
    "plan":      60 * 60,
    "fix":       60 * 60,
    "implement": 90 * 60,
    "create-pr": 30 * 60,
    "default":   60 * 60,
}


def _warn_threshold(step: str) -> float:
    return WARN_THRESHOLDS_S.get(step, WARN_THRESHOLDS_S["default"])


def _kill_threshold(step: str) -> float:
    return KILL_THRESHOLDS_S.get(step, KILL_THRESHOLDS_S["default"])


# ---------------------------------------------------------------------------
# Watchdog class
# ---------------------------------------------------------------------------

class Watchdog:
    """Background thread that monitors and escalates hung harness steps.

    Parameters
    ----------
    run_id:
        Unique identifier for the current harness run (used in log messages).
    on_warn:
        Callback invoked once per step when elapsed time exceeds the warn
        threshold.  Signature: ``(step_name: str, elapsed_s: float) -> None``.
    on_kill:
        Callback invoked when elapsed time exceeds the kill threshold.  The
        watchdog kills the subprocess (if set) immediately after this callback
        returns.  Signature: ``(step_name: str, elapsed_s: float) -> None``.
    check_interval:
        How often (in seconds) the background thread wakes to check elapsed
        time.  Default is 30 seconds.
    """

    def __init__(
        self,
        run_id: str,
        on_warn: Callable[[str, float], None],
        on_kill: Callable[[str, float], None],
        check_interval: int = 30,
    ) -> None:
        self._run_id = run_id
        self._on_warn = on_warn
        self._on_kill = on_kill
        self._check_interval = check_interval

        # Mutable step state — protected by _lock.
        self._lock = threading.Lock()
        self._step_name: Optional[str] = None
        self._step_started_at: Optional[float] = None
        self._proc: Optional[subprocess.Popen] = None
        self._warned: bool = False
        self._killed: bool = False  # True once the hard-kill fires for the current step

        # Thread control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background watchdog thread.

        The thread is marked as a daemon so it does not prevent the process
        from exiting if the main thread terminates unexpectedly.
        """
        if self._thread is not None and self._thread.is_alive():
            return  # already running

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=f"watchdog-{self._run_id}",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the watchdog thread to stop and wait for it to finish.

        Should be called after all steps have completed (or on error cleanup).
        Safe to call even if the watchdog was never started.
        """
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self._check_interval + 5)
            self._thread = None

    def set_step(
        self,
        step_name: str,
        proc: Optional[subprocess.Popen] = None,
    ) -> None:
        """Update the step being watched.

        Resets the step timer and clears the warned/killed flags so fresh
        thresholds apply to the new step.

        Parameters
        ----------
        step_name:
            Human-readable step name (e.g. ``"research"``, ``"implement"``).
        proc:
            The subprocess running this step.  If provided and the kill
            threshold is exceeded, the watchdog will call ``proc.kill()``
            (SIGKILL) to terminate it immediately.
        """
        with self._lock:
            self._step_name = step_name
            self._step_started_at = time.monotonic()
            self._proc = proc
            self._warned = False
            self._killed = False

    # ------------------------------------------------------------------
    # Background thread
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Main loop executed by the background thread."""
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self._check_interval)
            if self._stop_event.is_set():
                break
            self._check()

    def _check(self) -> None:
        """Single iteration of the watchdog check — called every check_interval."""
        with self._lock:
            if self._step_name is None or self._step_started_at is None:
                return  # no active step

            step = self._step_name
            elapsed = time.monotonic() - self._step_started_at
            warn_at = _warn_threshold(step)
            kill_at = _kill_threshold(step)
            proc = self._proc
            already_warned = self._warned
            already_killed = self._killed

        # --- Kill threshold (checked first so we don't warn+kill in same tick) ---
        if elapsed >= kill_at and not already_killed:
            with self._lock:
                self._killed = True

            # Call handler outside the lock to avoid re-entrancy issues.
            try:
                self._on_kill(step, elapsed)
            except Exception:
                pass  # watchdog must never crash the harness

            # Terminate the subprocess.
            if proc is not None:
                try:
                    proc.kill()
                except (ProcessLookupError, OSError):
                    pass  # already finished

            return  # do not also warn after killing

        # --- Warn threshold ---
        if elapsed >= warn_at and not already_warned:
            with self._lock:
                self._warned = True

            try:
                self._on_warn(step, elapsed)
            except Exception:
                pass
