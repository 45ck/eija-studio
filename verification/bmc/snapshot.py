"""Observing and restoring the sandbox database between explored transitions.

The checker never touches the runtime's tables except (a) through `execute` and (b) to restore a
previously observed state so the next move can start from it, and (c) to apply the environment moves
(revocation, assignment) which the task explicitly models as changes to the actors table."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from eija_studio.adapters.sqlite_store import SQLiteStore


@dataclass(frozen=True)
class Snapshot:
    """Complete observable database state. Audit/outbox keep order but not sequence numbers."""
    instances: tuple[tuple[Any, ...], ...]   # id, case_id, model_hash, state, version
    actors: tuple[tuple[Any, ...], ...]      # id, role, active, assigned
    operations: tuple[tuple[Any, ...], ...]  # id, binding, body
    audit: tuple[tuple[Any, ...], ...]       # kind, body (in commit order)
    outbox: tuple[tuple[Any, ...], ...]      # id, case_id, operation_id, kind, body

    @property
    def instance(self) -> tuple[Any, ...]:
        return self.instances[0]

    @property
    def state(self) -> str:
        return self.instance[3]

    @property
    def version(self) -> int:
        return self.instance[4]

    def actor_table(self) -> dict[str, tuple[str, bool, bool]]:
        return {a[0]: (a[1], bool(a[2]), bool(a[3])) for a in self.actors}


class Observer:
    """Read-only view of a sandbox store plus the restore/mutate helpers used by the search."""

    def __init__(self, store: SQLiteStore):
        self.store = store
        self._db = sqlite3.connect(store.path, timeout=10)
        self._db.execute("PRAGMA query_only=ON")

    def close(self) -> None:
        self._db.close()

    def read(self) -> Snapshot:
        q = self._db.execute
        return Snapshot(
            instances=tuple(q("SELECT id,case_id,model_hash,state,version FROM instances ORDER BY id")),
            actors=tuple(q("SELECT id,role,active,assigned FROM actors ORDER BY id")),
            operations=tuple(q("SELECT id,binding,body FROM operations ORDER BY id")),
            audit=tuple(q("SELECT kind,body FROM audit ORDER BY seq")),
            outbox=tuple(q("SELECT id,case_id,operation_id,kind,body FROM outbox ORDER BY id")))

    def restore(self, snap: Snapshot) -> None:
        with self.store.transaction() as u:
            db = u.db
            for table in ("instances", "operations", "audit", "outbox"):
                db.execute(f"DELETE FROM {table}")
            db.executemany("INSERT INTO instances VALUES(?,?,?,?,?)", snap.instances)
            db.executemany("INSERT INTO operations VALUES(?,?,?)", snap.operations)
            db.executemany("INSERT INTO audit(kind,body) VALUES(?,?)", snap.audit)
            db.executemany("INSERT INTO outbox VALUES(?,?,?,?,?)", snap.outbox)
            db.executemany("UPDATE actors SET role=?,active=?,assigned=? WHERE id=?",
                           [(a[1], a[2], a[3], a[0]) for a in snap.actors])

    def set_actor_flag(self, actor: str, column: str, value: int) -> None:
        """Environment move: revoke/restore (`active`) or assign/unassign (`assigned`) a fixture actor."""
        if column not in ("active", "assigned"):
            raise ValueError("Only the active and assigned flags are environment variables")
        with self.store.transaction() as u:
            u.db.execute(f"UPDATE actors SET {column}=? WHERE id=?", (value, actor))
