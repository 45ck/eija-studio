"""Compatibility is computed. A supplied green status is never sufficient."""
from __future__ import annotations
from itertools import product
from typing import Any, Callable
from .models import fingerprint

TECHNICAL_DIMENSIONS = ("semantic", "implementation", "policy", "environment", "harness")


def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str) -> str:
    if claim != "runtime_matrix" or kind != "integration_test":
        return "UNKNOWN"  # This verifier has no authority to establish other claims.
    if receipt.get("claim") != claim or receipt.get("kind") != kind:
        return "UNKNOWN"
    if not isinstance(receipt.get("subject"), dict):
        return "FAIL"
    if any(receipt.get("subject", {}).get(k) != subject.get(k) for k in TECHNICAL_DIMENSIONS):
        return "STALE"
    artifact = receipt.get("artifact")
    if not isinstance(artifact, dict) or fingerprint(artifact) != receipt.get("artifact_hash"):
        return "FAIL"
    if receipt.get("producer") != "eija-local-verifier" or receipt.get("method") != "bounded-runtime-matrix-v1":
        return "UNKNOWN"
    # Never use receipt['status'] as an authority. Recompute from typed observations.
    cells = artifact.get("cells")
    expected = artifact.get("expected_cells")
    if not isinstance(cells, list) or not cells or type(expected) is not int or len(cells) != expected:
        return "FAIL"
    if artifact.get("protocol") != "bounded-runtime-matrix-v1":
        return "UNKNOWN"
    matrix = artifact.get("matrix")
    if not isinstance(matrix, dict) or set(matrix) != {"actors", "states", "actions"}:
        return "FAIL"
    actors = {"teacher-assigned", "teacher-unassigned", "teacher-revoked", "registrar", "viewer"}
    actions = {"Submit", "Recommend", "Approve", "Reject", "Revise"}
    baseline_states = {"Draft", "Submitted", "Approved", "Rejected"}
    if any(not isinstance(v, list) or not all(isinstance(x, str) for x in v) or len(v) != len(set(v)) for v in matrix.values()):
        return "FAIL"
    states = set(matrix["states"])
    if set(matrix["actors"]) != actors or set(matrix["actions"]) != actions or states not in (baseline_states, baseline_states | {"Recommended"}):
        return "FAIL"
    required_keys = set(product(actors, states, actions))
    observed_keys = []
    fields = {"accepted", "state", "version", "audit", "outbox", "operations"}
    for cell in cells:
        if not isinstance(cell, dict) or set(cell) != {"actor", "state", "action", "expected", "actual"}:
            return "FAIL"
        key = (cell["actor"], cell["state"], cell["action"])
        if not all(isinstance(x, str) for x in key):
            return "FAIL"
        observed_keys.append(key)
        for label in ("expected", "actual"):
            observation = cell[label]
            if not isinstance(observation, dict) or set(observation) != fields:
                return "FAIL"
            if type(observation["accepted"]) is not bool or not isinstance(observation["state"], str) or observation["state"] not in states:
                return "FAIL"
            if any(type(observation[k]) is not int or observation[k] not in (0, 1) for k in ("version", "audit", "outbox", "operations")):
                return "FAIL"
    if len(observed_keys) != len(required_keys) or set(observed_keys) != required_keys:
        return "FAIL"
    return "PASS" if all(c["expected"] == c["actual"] for c in cells) else "FAIL"


def aggregate_status(
    receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool]
) -> str:
    statuses = [assess_receipt(r, subject, "runtime_matrix", "integration_test") if authenticator(r) else "FAIL" for r in receipts]
    current = [s for s in statuses if s in {"PASS", "FAIL"}]
    if "PASS" in current and "FAIL" in current:
        return "CONFLICT"
    if "FAIL" in current:
        return "FAIL"
    if "PASS" in current:
        return "PASS"
    return "STALE" if "STALE" in statuses else "UNKNOWN"
