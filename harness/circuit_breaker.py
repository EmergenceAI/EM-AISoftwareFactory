"""Circuit breaker — prevents runaway retries when a gate is systemically broken.

State persists across harness runs in ``provenance/circuit_breakers.json``::

    {
        "linter":      { "state": "open",   "consecutive_failures": 5,
                         "opened_at": "2024-07-26T12:00:00Z", "last_error": "..." },
        "tests":       { "state": "closed", "consecutive_failures": 0 },
        "evals":       { "state": "closed", "consecutive_failures": 2 },
        "code-review": { "state": "closed", "consecutive_failures": 0 }
    }

A gate transitions **closed → open** after :data:`OPEN_THRESHOLD` consecutive
failures.  Once open, :meth:`CircuitBreaker.check` raises
:class:`CircuitOpenError` immediately so the harness does not keep trying a
broken gate.

Use :meth:`CircuitBreaker.reset` (or fix the underlying problem and call
:meth:`CircuitBreaker.record_success`) to close an open circuit.

Typical usage::

    from pathlib import Path
    from harness.circuit_breaker import CircuitBreaker, CircuitOpenError

    cb = CircuitBreaker(provenance_dir=Path("provenance"))

    # Before running a gate:
    try:
        cb.check("linter")
    except CircuitOpenError as exc:
        print(f"Skipping linter gate — circuit open: {exc}")
        mark_run_failed()
        return

    # After the gate finishes:
    if gate_passed:
        cb.record_success("linter")
    else:
        cb.record_failure("linter", error=stderr_tail)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


OPEN_THRESHOLD = 5  # consecutive failures required to open a circuit


class CircuitOpenError(Exception):
    """Raised by :meth:`CircuitBreaker.check` when the circuit is open.

    The exception message includes the gate name, failure count, time opened,
    and the last recorded error to aid diagnosis.
    """


class CircuitBreaker:
    """Persistent, cross-run circuit breaker for harness gates.

    Parameters
    ----------
    provenance_dir:
        Directory where provenance artefacts are stored.  The state file is
        written as ``{provenance_dir}/circuit_breakers.json``.
    """

    _FILENAME = "circuit_breakers.json"
    _TMP_FILENAME = ".circuit_breakers.json.tmp"

    def __init__(self, provenance_dir: Path) -> None:
        self._dir = Path(provenance_dir)
        self._path = self._dir / self._FILENAME
        self._tmp_path = self._dir / self._TMP_FILENAME

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(self, gate: str) -> None:
        """Raise :class:`CircuitOpenError` if *gate*'s circuit is open.

        Parameters
        ----------
        gate:
            Gate identifier (e.g. ``"linter"``, ``"tests"``).

        Raises
        ------
        CircuitOpenError
            When the gate's circuit is in the ``"open"`` state.
        """
        state = self._load()
        entry = state.get(gate, {})
        if entry.get("state") == "open":
            raise CircuitOpenError(
                f"Circuit for gate '{gate}' is OPEN after "
                f"{entry.get('consecutive_failures', OPEN_THRESHOLD)} consecutive failures "
                f"(opened at {entry.get('opened_at', 'unknown')}). "
                f"Last error: {entry.get('last_error', 'N/A')}. "
                f"Fix the underlying issue, then call reset('{gate}') to re-enable."
            )

    def record_failure(self, gate: str, error: str = "") -> None:
        """Increment the failure counter for *gate*.

        Transitions the circuit to ``"open"`` when the counter reaches
        :data:`OPEN_THRESHOLD`.

        Parameters
        ----------
        gate:
            Gate identifier.
        error:
            Optional short description / tail of the error output for
            diagnostic purposes.
        """
        state = self._load()
        entry = state.setdefault(gate, {"state": "closed", "consecutive_failures": 0})
        entry["consecutive_failures"] = entry.get("consecutive_failures", 0) + 1
        entry["last_error"] = error

        if entry["consecutive_failures"] >= OPEN_THRESHOLD and entry["state"] != "open":
            entry["state"] = "open"
            entry["opened_at"] = _utc_now()
            print(
                f"[circuit-breaker] OPENED gate '{gate}' after "
                f"{entry['consecutive_failures']} consecutive failures."
            )
        else:
            entry["state"] = "closed"

        self._save(state)

    def record_success(self, gate: str) -> None:
        """Reset the failure counter for *gate* and close the circuit.

        Parameters
        ----------
        gate:
            Gate identifier.
        """
        state = self._load()
        entry = state.setdefault(gate, {"state": "closed", "consecutive_failures": 0})
        was_open = entry.get("state") == "open"
        entry["consecutive_failures"] = 0
        entry["state"] = "closed"
        entry.pop("opened_at", None)
        entry.pop("last_error", None)
        self._save(state)

        if was_open:
            print(f"[circuit-breaker] CLOSED gate '{gate}' after successful run.")

    def reset(self, gate: str) -> None:
        """Manually reset *gate* to closed state with zero failures.

        Use this after fixing an underlying infrastructure problem that caused
        the circuit to open.

        Parameters
        ----------
        gate:
            Gate identifier.
        """
        state = self._load()
        state[gate] = {"state": "closed", "consecutive_failures": 0}
        self._save(state)
        print(f"[circuit-breaker] Manually RESET gate '{gate}'.")

    def all_states(self) -> Dict[str, dict]:
        """Return the full state dictionary for all tracked gates.

        Returns
        -------
        dict
            Mapping of gate name → state entry.  Keys within each entry:
            ``state``, ``consecutive_failures``, and optionally ``opened_at``
            and ``last_error``.
        """
        return self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> Dict:
        """Load and return the state dict from disk; returns ``{}`` on any error."""
        try:
            content = self._path.read_text().strip()
            if not content:
                return {}
            return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _save(self, state: Dict) -> None:
        """Atomically write *state* to the state file."""
        self._dir.mkdir(parents=True, exist_ok=True)
        self._tmp_path.write_text(json.dumps(state, indent=2))
        os.replace(self._tmp_path, self._path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
