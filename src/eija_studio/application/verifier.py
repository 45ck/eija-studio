"""Bounded synthetic runtime experiments. Not a theorem prover or human study."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from eija_studio.domain.models import Workflow, ExecuteCommand, DomainError, fingerprint
from .runtime import initialise, execute
from .ports import StoreFactory

# Hand-authored oracle, separate from the runtime's transition/guard evaluator.
# It shares authorship and the policy requirements: not an independently blinded oracle.
ORACLE = {
    "Submit": ("Teacher", "Draft", "Submitted"),
    "Recommend": ("Teacher", "Submitted", "Recommended"),
    "Approve": ("Registrar", "Recommended", "Approved"),
    "Reject": ("Registrar", "Recommended", "Rejected"),
    "Revise": ("Teacher", "Rejected", "Draft"),
}
ACTORS = [("teacher-assigned", "Teacher", True, True), ("teacher-unassigned", "Teacher", True, False),
          ("teacher-revoked", "Teacher", False, True), ("registrar", "Registrar", True, False), ("viewer", "Viewer", True, False)]


def verify_runtime(model: Workflow, subject: dict, store_factory: StoreFactory) -> dict:
    cells = []
    candidate = any(t.action == "Recommend" for t in model.transitions)
    rejection_source = next(t.from_state for t in model.transitions if t.action == "Reject")
    with TemporaryDirectory(prefix="eija-check-") as td:
        store = store_factory(Path(td))
        for actor_id, role, active, assigned in ACTORS:
            for state in model.states:
                for action, (required_role, source, target) in ORACLE.items():
                    if not candidate and action in {"Approve", "Reject"}:
                        source = "Submitted"
                    if action == "Reject":
                        source = rejection_source  # Explicit allowed policy parameter, not inferred safety.
                    allowed = active and role == required_role and state == source and (action != "Recommend" or assigned)
                    if action == "Recommend" and not candidate:
                        allowed = False
                    with store.transaction() as u:
                        item = initialise(u, "oracle", model, state=state)
                        before = u.effect_counts()
                    expected = {"accepted": allowed, "state": target if allowed else state,
                                "version": 1 if allowed else 0, "audit": int(allowed),
                                "outbox": int(allowed and action == "Recommend"), "operations": int(allowed)}
                    command = ExecuteCommand(operation_id=uuid4().hex, actor_id=actor_id, instance_id=item["id"], action=action, expected_version=0)
                    accepted = False
                    try:
                        with store.transaction() as u:
                            execute(u, "oracle", model, command)
                        accepted = True
                    except DomainError:
                        pass
                    with store.transaction() as u:
                        after = u.find_instance(item["id"], "oracle")
                        counts = u.effect_counts()
                    actual = {"accepted": accepted, "state": after["state"], "version": after["version"],
                              **{k: counts[k] - before[k] for k in ("audit", "outbox", "operations")}}
                    cells.append({"actor": actor_id, "state": state, "action": action, "expected": expected, "actual": actual})
    artifact = {"protocol": "bounded-runtime-matrix-v1", "expected_cells": len(ACTORS) * len(model.states) * len(ORACLE),
                "matrix": {"actors": [a[0] for a in ACTORS], "states": list(model.states), "actions": list(ORACLE)},
                "cells": cells, "limitations": ["Synthetic fixture directory; no real SSO", "No human-outcome measurement",
                "One-step state/action matrix, not exhaustive arbitrary sequences", "Same-author oracle, not an independent holdout"]}
    return {"id": uuid4().hex, "claim": "runtime_matrix", "kind": "integration_test", "subject": subject,
            "producer": "eija-local-verifier", "method": artifact["protocol"], "created_at": datetime.now(timezone.utc).isoformat(),
            "artifact_hash": fingerprint(artifact), "artifact": artifact}
