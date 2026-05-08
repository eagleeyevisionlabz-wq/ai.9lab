"""Append-only JSONL audit logger.

Writes one file per task: <audit_dir>/<task_id>.jsonl
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from m3ta_uitars.contracts import AuditEntry


class AuditLogger:
    def __init__(self, audit_dir: Path) -> None:
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, Lock] = {}
        self._locks_guard = Lock()

    def _path(self, task_id: str) -> Path:
        return self.audit_dir / f"{task_id}.jsonl"

    def _lock_for(self, task_id: str) -> Lock:
        with self._locks_guard:
            lock = self._locks.get(task_id)
            if lock is None:
                lock = Lock()
                self._locks[task_id] = lock
            return lock

    def log(self, entry: AuditEntry) -> Path:
        path = self._path(entry.task_id)
        line = entry.model_dump_json() + "\n"
        with self._lock_for(entry.task_id):
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line)
        return path

    def read(self, task_id: str) -> list[dict[str, Any]]:
        path = self._path(task_id)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
