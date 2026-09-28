"""Bridge between the real runtime store and the TLA+ state.

`Harness.abstract` (alpha) reads a `UnitOfWork` and returns the same nested tuple that
`Key(...)` in Excursion.tla prints. `Harness.concretise` (gamma) writes such a key into a scratch store.
Both use only the application's `UnitOfWork` port, except for the environment (directory changes),
which - like the existing kernel tests - is applied with SQL on the fixture actors table because the
kernel deliberately has no revocation API.

Abstraction losses, stated so they are not mistaken for agreement: audit event *bodies*, outbox
*payloads*, result JSON fields other than instance state/version, and timestamps are not compared. The
binding hash is decoded by recomputing the runtime's binding formula, so a change to that formula
makes decoding fail loudly instead of silently agreeing.
"""
from __future__ import annotations

from typing import Any

from eija_studio.application.runtime import execute, initialise
from eija_studio.application.ports import UnitOfWork
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow, fingerprint

from .model import UNKNOWN_ACTORS, action_universe, directory, op_ids, transition_table

Key = tuple  # (state, version, audit, ops, outbox, directory) - see Key(s) in Excursion.tla

CASE_ID = "tla-case"


class AbstractionError(RuntimeError):
    """The store holds something the abstraction cannot represent (never treated as agreement)."""


class Harness:
    """One workflow, one preview instance, bounded operation ids."""

    def __init__(self, workflow: Workflow, ops: int, *, case_id: str = CASE_ID):
        self.workflow, self.ops = workflow, op_ids(ops)
        self.instance_id, self.case_id = "", case_id  # set by start()
        self.table = transition_table(workflow)
        self.actor_ids = tuple(a[0] for a in directory())
        self.max_ver = ops
        self._decode: dict[str, dict[str, tuple]] = {}

    # -- commands ----------------------------------------------------------------------------
    def command(self, op: str, actor: str, action: str, ver: int) -> ExecuteCommand:
        return ExecuteCommand(operation_id=op, actor_id=actor, instance_id=self.instance_id, action=action, expected_version=ver)

    def binding(self, command: ExecuteCommand) -> str:
        """Recomputes the runtime's operation binding (application/runtime.py)."""
        return fingerprint({"case": self.case_id, "subject": self.workflow.semantic_hash,
                            "command": command.model_dump(mode="json")})

    def execute_command(self, u: UnitOfWork, cmd: dict[str, Any]) -> dict:
        """The REAL `execute`; raises DomainError exactly as the application does."""
        return execute(u, self.case_id, self.workflow, self.command(cmd["op"], cmd["actor"], cmd["action"], cmd["ver"]))

    def run(self, u: UnitOfWork, cmd: dict[str, Any]) -> tuple[str, dict | None]:
        """Run one command and name the outcome like the spec does: (code, result or None)."""
        try:
            result = self.execute_command(u, cmd)
        except DomainError as exc:
            return exc.code, None
        except Exception as exc:  # noqa: BLE001 - any other failure is a disagreement, reported by name
            return "EXC:" + type(exc).__name__, None
        return ("DUPLICATE" if result["duplicate"] else "COMMITTED"), result

    # -- alpha ---------------------------------------------------------------------------------
    def _index(self, op: str) -> dict[str, tuple]:
        if op not in self._decode:
            self._decode[op] = {
                self.binding(self.command(op, a, act, v)): (a, act, v)
                for a in self.actor_ids + UNKNOWN_ACTORS for act in action_universe() for v in range(self.max_ver + 1)}
        return self._decode[op]

    def abstract(self, u: UnitOfWork) -> Key:
        instance = u.find_instance(self.instance_id, self.case_id)
        if instance is None:
            raise AbstractionError("preview instance is missing")
        signatures = []
        for op in self.ops:
            row = u.find_operation(op)
            if row is None:
                signatures.append(())
                continue
            bound = self._index(op).get(row["binding"])
            if bound is None:
                raise AbstractionError(f"operation {op} has a binding outside the modelled command space")
            after = row["result"]["instance"]
            signatures.append((*bound, after["state"], after["version"]))
        rows = u.observations(self.case_id)["outbox"]
        outbox = tuple(sum(1 for r in rows if r["operation_id"] == op) for op in self.ops)
        directory_rows = tuple((int(u.actor(a)["active"]), int(u.actor(a)["assigned"])) for a in self.actor_ids)
        return (instance["state"], instance["version"], u.effect_counts()["audit"], tuple(signatures), outbox, directory_rows)

    def light(self, u: UnitOfWork) -> tuple:
        """Cheap footprint used to confirm that a non-committing command changed nothing."""
        instance = u.find_instance(self.instance_id, self.case_id)
        counts = u.effect_counts()
        return (instance["state"], instance["version"], counts["audit"], counts["outbox"], counts["operations"])

    # -- gamma ---------------------------------------------------------------------------------
    def concretise(self, u: Any, key: Key) -> None:
        """Replace the scratch store's contents with the state `key` (scratch stores only)."""
        for table in ("instances", "operations", "audit", "outbox"):
            u.db.execute(f"DELETE FROM {table}")
        state, version, audit, ops, outbox, dirs = key
        u.create_instance({"id": self.instance_id, "case_id": self.case_id, "model_hash": self.workflow.semantic_hash,
                           "state": state, "version": version})
        for actor, (active, assigned) in zip(self.actor_ids, dirs):
            u.db.execute("UPDATE actors SET active=?, assigned=? WHERE id=?", (active, assigned, actor))
        for op, sig, queued in zip(self.ops, ops, outbox):
            if sig:
                actor, action, ver, res_state, res_ver = sig
                entry = self.table[action]
                result = {"duplicate": False, "committed": True,
                          "instance": {"id": self.instance_id, "case_id": self.case_id, "model_hash": self.workflow.semantic_hash,
                                       "state": res_state, "version": res_ver},
                          "effects": [*entry["audit"], *entry["notify"], *entry["other"]]}
                u.record_operation(op, self.binding(self.command(op, actor, action, ver)), result)
                for effect in entry["notify"][:queued]:
                    u.enqueue(self.case_id, op, effect)
            elif queued:
                raise AbstractionError("outbox rows without an operation record cannot be concretised")
        for i in range(audit):
            u.event("Audit:Concretised", {"case_id": self.case_id, "n": i})

    def environment(self, u: Any, env: dict[str, Any]) -> None:
        """Apply an environment step (directory change) to the store."""
        column = {"active": "active", "assigned": "assigned"}[env["kind"]]
        u.db.execute(f"UPDATE actors SET {column}=? WHERE id=?", (int(env["val"]), env["actor"]))

    def start(self, u: UnitOfWork) -> Key:
        """Create the preview instance with the kernel's own `initialise` and abstract it."""
        self.instance_id = initialise(u, self.case_id, self.workflow)["id"]
        self._decode.clear()
        return self.abstract(u)
