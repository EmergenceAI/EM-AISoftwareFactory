"""Per-repo file lock to prevent concurrent harness runs on the same repository.

Uses POSIX ``fcntl.flock`` for kernel-enforced mutual exclusion.  The lock
file lives at ``{repo_path}/.harness-results/repo.lock``; its JSON content
identifies the current holder so operators can inspect stale locks.

Typical usage::

    from pathlib import Path
    from harness.locks import RepoLock

    with RepoLock(repo_path, run_id="run_20240726_abc123", issue_key="ABI-42"):
        # safe to operate on the repo
        ...
"""

import fcntl
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class LockError(Exception):
    """Raised when a lock cannot be acquired within the configured timeout."""


class RepoLock:
    """Exclusive per-repo lock implemented with ``fcntl.flock``.

    Parameters
    ----------
    repo_path:
        Root of the repository being operated on.
    run_id:
        Unique identifier for this harness run (written into the lock record).
    issue_key:
        Jira / issue key associated with this run (written into the lock record).
    timeout:
        Maximum seconds to wait before raising :class:`LockError`.  Default
        is 300 seconds (5 minutes).

    Lock record (JSON written inside the lock file)::

        {
            "run_id":     "run_20240726_abc123",
            "issue_key":  "ABI-42",
            "started_at": "2024-07-26T12:00:00Z",
            "pid":        12345
        }
    """

    _POLL_INTERVAL = 5  # seconds between acquisition attempts
    _LOCK_SUBDIR = ".harness-results"
    _LOCK_FILENAME = "repo.lock"

    def __init__(
        self,
        repo_path: Path,
        run_id: str,
        issue_key: str,
        timeout: int = 300,
    ) -> None:
        self._repo_path = Path(repo_path)
        self._run_id = run_id
        self._issue_key = issue_key
        self._timeout = timeout
        self._lock_path = self._repo_path / self._LOCK_SUBDIR / self._LOCK_FILENAME
        self._lock_fh = None  # file handle kept open while lock is held

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------

    def __enter__(self) -> "RepoLock":
        self._acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._release()
        return False  # do not suppress exceptions

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_dir(self) -> None:
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)

    def _acquire(self) -> None:
        """Block until the lock is acquired or *timeout* is exceeded."""
        self._ensure_dir()
        deadline = time.monotonic() + self._timeout
        attempt = 0

        while True:
            fh = open(self._lock_path, "a+")  # open for append+read; creates if missing
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # Lock acquired — write our record and keep the file open.
                fh.seek(0)
                fh.truncate()
                record = {
                    "run_id": self._run_id,
                    "issue_key": self._issue_key,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "pid": os.getpid(),
                }
                fh.write(json.dumps(record, indent=2))
                fh.flush()
                self._lock_fh = fh
                print(
                    f"[lock] acquired for {self._issue_key} (run {self._run_id})"
                    f" on {self._repo_path}"
                )
                return
            except BlockingIOError:
                # Lock is held by another process.
                fh.close()
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise LockError(
                        f"Could not acquire lock on {self._lock_path} "
                        f"within {self._timeout}s. "
                        f"Current holder: {read_lock_record(self._repo_path)}"
                    )
                attempt += 1
                holder = read_lock_record(self._repo_path)
                holder_info = (
                    f"held by run={holder['run_id']} pid={holder['pid']}"
                    if holder
                    else "held (unknown holder)"
                )
                print(
                    f"[lock] waiting for repo lock ({holder_info}); "
                    f"queue position ~{attempt}, "
                    f"{int(remaining)}s remaining …"
                )
                time.sleep(min(self._POLL_INTERVAL, remaining))

    def _release(self) -> None:
        """Release the lock and remove the holder record."""
        if self._lock_fh is None:
            return
        try:
            self._lock_fh.seek(0)
            self._lock_fh.truncate()
            fcntl.flock(self._lock_fh, fcntl.LOCK_UN)
        finally:
            self._lock_fh.close()
            self._lock_fh = None
        print(
            f"[lock] released for {self._issue_key} (run {self._run_id})"
        )


def read_lock_record(repo_path: Path) -> Optional[dict]:
    """Return the current lock holder record, or ``None`` if unlocked or unreadable.

    Parameters
    ----------
    repo_path:
        Root of the repository whose lock file should be read.

    Returns
    -------
    dict or None
        Parsed JSON record with keys ``run_id``, ``issue_key``,
        ``started_at``, ``pid``; or ``None`` if the file does not exist or
        contains no valid JSON.
    """
    lock_path = Path(repo_path) / RepoLock._LOCK_SUBDIR / RepoLock._LOCK_FILENAME
    try:
        content = lock_path.read_text().strip()
        if not content:
            return None
        return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
