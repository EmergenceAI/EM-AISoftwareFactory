"""Checkpoint — write after each successful step so harness can resume after crash.

Checkpoint file: ``{repo_path}/.harness-results/checkpoint.json``

File schema::

    {
        "run_id":          "run_20240726_abc123",
        "issue_key":       "ABI-123",
        "completed_steps": ["research", "plan", "implement"],
        "last_step":       "implement",
        "timestamp":       "2024-07-26T12:00:00Z"
    }

Atomic write is achieved by writing to a ``.tmp`` sibling file and then
calling ``os.replace()`` so readers never observe a partial state.

Typical usage::

    from pathlib import Path
    from harness.checkpoint import Checkpoint

    cp = Checkpoint(repo_path)

    # On startup, resume from previous crash if checkpoint exists.
    completed = cp.completed_steps()

    for step in all_steps:
        if cp.should_skip(step):
            print(f"[checkpoint] skipping already-completed step: {step}")
            continue

        run_step(step)
        completed.append(step)
        cp.write(run_id, issue_key, completed)

    cp.clear()
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


class Checkpoint:
    """Read/write harness checkpoints for a single repository.

    Parameters
    ----------
    repo_path:
        Root directory of the repository being operated on.  The checkpoint
        file is stored at ``{repo_path}/.harness-results/checkpoint.json``.
    """

    _SUBDIR = ".harness-results"
    _FILENAME = "checkpoint.json"
    _TMP_FILENAME = ".checkpoint.json.tmp"

    def __init__(self, repo_path: Path) -> None:
        self._base_dir = Path(repo_path) / self._SUBDIR
        self._path = self._base_dir / self._FILENAME
        self._tmp_path = self._base_dir / self._TMP_FILENAME

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write(self, run_id: str, issue_key: str, completed_steps: List[str]) -> None:
        """Atomically write a checkpoint record.

        Writes to a ``.tmp`` file first, then uses ``os.replace()`` for an
        atomic rename so the checkpoint file is never in a partial state.

        Parameters
        ----------
        run_id:
            Unique identifier for the current harness run.
        issue_key:
            Jira / issue key associated with the run.
        completed_steps:
            Ordered list of step names that have been completed successfully.
        """
        self._base_dir.mkdir(parents=True, exist_ok=True)

        record = {
            "run_id": run_id,
            "issue_key": issue_key,
            "completed_steps": list(completed_steps),
            "last_step": completed_steps[-1] if completed_steps else None,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # Write to tmp first, then atomically replace the real file.
        self._tmp_path.write_text(json.dumps(record, indent=2))
        os.replace(self._tmp_path, self._path)

    def read(self) -> Optional[dict]:
        """Return the checkpoint dict, or ``None`` if no checkpoint exists.

        Returns
        -------
        dict or None
            Parsed checkpoint record, or ``None`` if the file does not exist
            or cannot be decoded.
        """
        try:
            content = self._path.read_text().strip()
            if not content:
                return None
            return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    def clear(self) -> None:
        """Delete the checkpoint file.

        Should be called at run end (whether success or failure) to prevent
        a stale checkpoint from being picked up by the next run.  Safe to
        call even if no checkpoint exists.
        """
        try:
            self._path.unlink()
        except FileNotFoundError:
            pass
        # Also clean up any leftover tmp file.
        try:
            self._tmp_path.unlink()
        except FileNotFoundError:
            pass

    def completed_steps(self) -> List[str]:
        """Return the list of already-completed step names, or ``[]``.

        Convenience wrapper around :meth:`read` that always returns a list.
        """
        record = self.read()
        if record is None:
            return []
        return record.get("completed_steps", [])

    def should_skip(self, step_name: str) -> bool:
        """Return ``True`` if *step_name* is already recorded as completed.

        Parameters
        ----------
        step_name:
            Name of the step to check (e.g. ``"research"``, ``"plan"``).
        """
        return step_name in self.completed_steps()
