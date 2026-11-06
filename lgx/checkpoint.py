"""Checkpoint storage for the lgx teaching stand-in.

A checkpoint is a plain dict:

    {"checkpoint_id": int, "step": int, "total_steps": int,
     "state": {...}, "next_node": str or None,
     "status": "running" | "interrupted" | "error" | "done",
     "interrupt": payload or None, "edited": bool}

Checkpointers save one checkpoint per super-step, keyed by thread id. This
mirrors the role of LangGraph's checkpointer family (InMemorySaver for
development, SQLite and Postgres savers for durable storage, per the
framework documentation checked 2026-11-06; see RESEARCH.md). The two
implementations here are a dict and a JSON file: enough to teach the
semantics, including a resume in a brand new process.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path


class BaseCheckpointer:
    """Interface shared by the stand-in checkpointers."""

    def save(self, thread_id: str, checkpoint: dict) -> dict:
        raise NotImplementedError

    def latest(self, thread_id: str):
        raise NotImplementedError

    def history(self, thread_id: str) -> list:
        raise NotImplementedError

    def load(self, thread_id: str, checkpoint_id: int):
        raise NotImplementedError

    def threads(self) -> list:
        raise NotImplementedError


class InMemoryCheckpointer(BaseCheckpointer):
    """Checkpoints in a dict. Lost when the process exits.

    Stand-in for LangGraph's in-memory saver: same role (fast, per-process),
    same limitation (nothing survives a restart).
    """

    def __init__(self):
        self._data: dict[str, list[dict]] = {}

    def save(self, thread_id, checkpoint):
        entries = self._data.setdefault(thread_id, [])
        stored = copy.deepcopy(checkpoint)
        stored["checkpoint_id"] = len(entries)
        entries.append(stored)
        return copy.deepcopy(stored)

    def latest(self, thread_id):
        entries = self._data.get(thread_id)
        if not entries:
            return None
        return copy.deepcopy(entries[-1])

    def history(self, thread_id):
        return copy.deepcopy(self._data.get(thread_id, []))

    def load(self, thread_id, checkpoint_id):
        for entry in self._data.get(thread_id, []):
            if entry["checkpoint_id"] == checkpoint_id:
                return copy.deepcopy(entry)
        return None

    def threads(self):
        return sorted(self._data)


class FileCheckpointer(BaseCheckpointer):
    """Checkpoints as one JSON file per thread in a directory.

    Stand-in for the file and database savers: a new instance pointed at the
    same directory sees every thread the old instance wrote, which is what
    makes the crash-and-resume drill in Lesson 16 a real durability test
    rather than a shared-memory trick.
    """

    def __init__(self, directory):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, thread_id: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", thread_id)
        return self.dir / f"{safe}.json"

    def _read(self, thread_id: str) -> list:
        path = self._path(thread_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, thread_id: str, entries: list) -> None:
        self._path(thread_id).write_text(
            json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8"
        )

    def save(self, thread_id, checkpoint):
        entries = self._read(thread_id)
        stored = copy.deepcopy(checkpoint)
        stored["checkpoint_id"] = len(entries)
        entries.append(stored)
        self._write(thread_id, entries)
        return copy.deepcopy(stored)

    def latest(self, thread_id):
        entries = self._read(thread_id)
        if not entries:
            return None
        return copy.deepcopy(entries[-1])

    def history(self, thread_id):
        return copy.deepcopy(self._read(thread_id))

    def load(self, thread_id, checkpoint_id):
        for entry in self._read(thread_id):
            if entry["checkpoint_id"] == checkpoint_id:
                return copy.deepcopy(entry)
        return None

    def threads(self):
        return sorted(p.stem for p in self.dir.glob("*.json"))
