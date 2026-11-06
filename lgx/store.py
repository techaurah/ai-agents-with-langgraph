"""A cross-thread memory store for the lgx teaching stand-in.

Mirrors the role of LangGraph's Store (InMemoryStore and the database
stores): long-term memory that lives outside any single thread, organised
by namespaces (tuples like ("leads", "brightpath-dental")) with a key and a
dict value per item. Checkpoints remember where one conversation got to;
the store remembers facts across conversations. The implementation is a
dict with substring search: enough to teach what to write, when to write
it, and what stale memory costs (Lessons 22 to 24).
"""

from __future__ import annotations

import copy
import json


class Store:
    """Namespace-keyed long-term memory (teaching stand-in)."""

    def __init__(self):
        self._data: dict[tuple, dict[str, dict]] = {}

    def put(self, namespace: tuple, key: str, value: dict) -> None:
        self._data.setdefault(tuple(namespace), {})[key] = copy.deepcopy(value)

    def get(self, namespace: tuple, key: str):
        found = self._data.get(tuple(namespace), {}).get(key)
        return copy.deepcopy(found) if found is not None else None

    def delete(self, namespace: tuple, key: str) -> bool:
        bucket = self._data.get(tuple(namespace), {})
        if key in bucket:
            del bucket[key]
            return True
        return False

    def search(self, namespace_prefix: tuple = (), query: str = "") -> list:
        """Items under a namespace prefix, optionally filtered by a
        substring query over the JSON of each value."""
        prefix = tuple(namespace_prefix)
        results = []
        for namespace, bucket in sorted(self._data.items()):
            if namespace[: len(prefix)] != prefix:
                continue
            for key in sorted(bucket):
                value = bucket[key]
                if query and query.lower() not in json.dumps(value).lower():
                    continue
                results.append({
                    "namespace": namespace,
                    "key": key,
                    "value": copy.deepcopy(value),
                })
        return results

    def count(self, namespace_prefix: tuple = ()) -> int:
        return len(self.search(namespace_prefix))
