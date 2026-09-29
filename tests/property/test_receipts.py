"""Receipts: tamper evidence and computed (never asserted) status.

Two layers protect a runtime-matrix receipt, and they answer different questions:

* ``ReceiptSigner.authentic`` (HMAC over the whole body): was this written by a holder of the local key?
* ``assess_receipt`` (``domain.evidence``): does the *raw observation matrix inside* still prove the
  claim for this subject? It recomputes from typed cells and never reads ``status``.

The properties: any single-field mutation of a sealed receipt is caught by the seal; an attacker who
holds the key and re-seals is still caught by the artifact hash; an attacker who additionally
recomputes the artifact hash (an internally consistent forgery) is still caught by the recomputed
matrix, except for fields the design declares non-semantic (the free-text ``limitations``).

What this establishes: no generated single-field mutation turns a failing or altered receipt into PASS.
What it does NOT establish: protection against an attacker who can forge a *coherent* matrix of wrong
actual results that equal the expected ones (that is the same-author oracle limitation recorded in the
receipt), or against reading the local key (ADR: the seal is a local integrity check, not attestation).
"""
from __future__ import annotations

import copy
from typing import Any

import pytest
from hypothesis import assume, given, settings, strategies as st

from eija_studio.adapters.receipts import ReceiptSigner
from eija_studio.domain.evidence import aggregate_status, assess_receipt
from eija_studio.domain.models import fingerprint
from .property_support import ephemeral_studio, examples, scratch_directory, selected_case

CLAIM, KIND = "runtime_matrix", "integration_test"
Path_ = tuple[Any, ...]

# Fields that carry no evidential weight even in a re-sealed receipt. ARCHITECTURE.md: "Layout/
# presentation is excluded from runtime applicability but included in the decision subject."
NEUTRAL_WHEN_RESEALED: set[Path_] = {("id",), ("created_at",), ("local_signature",), ("subject", "presentation")}


class Genuine:
    """A genuine sealed receipt, its subject and signer. A plain class with a short ``repr`` on purpose:
    Hypothesis pretty-prints dataclass fields and would render the 40 kB receipt for every example."""

    def __init__(self, receipt: dict, subject: dict, signer: ReceiptSigner, groups: dict[str, list[tuple]]) -> None:
        self.receipt, self.subject, self.signer, self.groups = receipt, subject, signer, groups

    def __repr__(self) -> str:
        return "Genuine(receipt=<sealed runtime-matrix receipt>)"

    @property
    def paths(self) -> list[tuple]:
        return [p for group in self.groups.values() for p in group]


def grouped(paths: list[tuple]) -> dict[str, list[tuple]]:
    """Bucket mutation targets by structural role so that the ~3 000 matrix cells do not drown the few
    dozen envelope fields that matter as much."""
    groups: dict[str, list[tuple]] = {"envelope": [], "subject": [], "artifact": [], "matrix": [], "cells": []}
    for path in paths:
        if path[0] == "subject":
            groups["subject"].append(path)
        elif path[0] == "artifact" and len(path) > 1 and path[1] == "cells":
            groups["cells"].append(path)
        elif path[0] == "artifact" and len(path) > 1 and path[1] == "matrix":
            groups["matrix"].append(path)
        elif path[0] == "artifact":
            groups["artifact"].append(path)
        else:
            groups["envelope"].append(path)
    return groups


def build_genuine() -> Genuine:
    """One genuine sealed receipt from the real verifier."""
    with scratch_directory() as directory:
        studio = ephemeral_studio(directory)
        case = selected_case(studio)
        case = studio.verify(case["id"], case["version"])
        receipt = case["receipts"][0]
        subject = studio.view(case["id"])["packet"]["subject"]
        assert studio.signer.authentic(receipt) and assess_receipt(receipt, subject, CLAIM, KIND) == "PASS"
        return Genuine(receipt, subject, studio.signer, grouped(json_paths(receipt)))


@pytest.fixture(scope="module")
def genuine() -> Genuine:
    return build_genuine()


def json_paths(value: Any, prefix: Path_ = ()) -> list[Path_]:
    """Every addressable node below the root (dict keys and list indexes), containers included."""
    found: list[Path_] = []
    children = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    for key, child in children:
        found.append(prefix + (key,))
        found.extend(json_paths(child, prefix + (key,)))
    return found


def resolve(root: Any, path: Path_) -> tuple[Any, Any]:
    parent = root
    for step in path[:-1]:
        parent = parent[step]
    return parent, path[-1]


MUTATIONS = ("perturb", "delete", "retype", "add_key")


def mutate(receipt: dict, path: Path_, kind: str) -> dict | None:
    """A deep copy with exactly one change at ``path``; None when the mutation does not apply."""
    copy_ = copy.deepcopy(receipt)
    parent, key = resolve(copy_, path)
    value = parent[key]
    if kind == "perturb":
        if isinstance(value, bool):
            parent[key] = not value
        elif isinstance(value, int):
            parent[key] = value + 1
        elif isinstance(value, str):
            parent[key] = value + "x"
        elif isinstance(value, list):
            parent[key] = value + [None]
        elif isinstance(value, dict):
            parent[key] = {**value, "zz-extra": 1}
        else:
            return None
    elif kind == "delete":
        if isinstance(parent, dict):
            del parent[key]
        else:
            parent.pop(key)
    elif kind == "retype":
        parent[key] = None if value is not None else 0
    elif kind == "add_key":
        if not isinstance(value, dict):
            return None
        value["zz-extra"] = "x"
    return copy_ if copy_ != receipt else None


def reseal(signer: ReceiptSigner, receipt: dict, *, rehash: bool) -> dict:
    """What an attacker holding the local key can do after editing a receipt."""
    forged = copy.deepcopy(receipt)
    if rehash and isinstance(forged.get("artifact"), dict):
        forged["artifact_hash"] = fingerprint(forged["artifact"])
    return signer.seal(forged)


def is_neutral(path: Path_, kind: str, *, rehashed: bool) -> bool:
    """Mutations a correct assessor may legitimately ignore, each with the reason.

    * ``id``, ``created_at``, ``local_signature``: metadata; ``presentation``: excluded from runtime applicability.
    * An *added unknown key* in ``subject`` (and, once the hash is recomputed, in ``artifact``): the
      assessor compares only the technical dimensions and reads only named artifact fields, so an unread
      key cannot change a verdict; the seal and the artifact hash are what bind it.
    * Free-text ``limitations`` once the hash is recomputed: prose, not an observation.
    """
    if path in NEUTRAL_WHEN_RESEALED or (rehashed and path == ("artifact_hash",)):
        return True  # (a recomputed hash overwrites the mutation)
    if path in {("subject",), ("artifact",)} and kind in {"perturb", "add_key"}:
        return path == ("subject",) or rehashed
    return rehashed and path[:2] == ("artifact", "limitations")


class Mutation:
    """Where and how a receipt was changed; the mutated receipt itself stays out of Hypothesis' repr."""

    def __init__(self, path: Path_, kind: str, receipt: dict) -> None:
        self.path, self.kind, self.receipt = path, kind, receipt

    def __repr__(self) -> str:
        return f"Mutation({self.kind} at {self.path})"


@st.composite
def single_mutation(draw, genuine: Genuine) -> Mutation:
    """One mutation at a path drawn uniformly from a structural group, then uniformly within it."""
    group = draw(st.sampled_from(sorted(genuine.groups)))
    targets = genuine.groups[group]
    path, kind = targets[draw(st.integers(0, len(targets) - 1))], draw(st.sampled_from(MUTATIONS))
    mutated = mutate(genuine.receipt, path, kind)
    assume(mutated is not None)
    return Mutation(path, kind, mutated)


def test_the_genuine_receipt_is_pass_and_authentic(genuine):
    receipt, subject, signer = genuine.receipt, genuine.subject, genuine.signer
    assert signer.authentic(receipt)
    assert assess_receipt(receipt, subject, CLAIM, KIND) == "PASS"
    assert aggregate_status([receipt], subject, signer.authentic) == "PASS"
    assert len(genuine.paths) > 1000  # the matrix is really in there: mutation has a large surface


@settings(max_examples=examples(400))
@given(st.data())
def test_any_single_field_mutation_breaks_the_seal(genuine, data):
    """The seal covers every field except itself. Weaker (and required by the lane brief): the mutated
    receipt is either inauthentic or no longer assessed PASS."""
    receipt, subject, signer = genuine.receipt, genuine.subject, genuine.signer
    m = data.draw(single_mutation(genuine))
    path, kind, mutated = m.path, m.kind, m.receipt
    assert not signer.authentic(mutated), f"{kind} at {path} kept the seal valid"
    assert (not signer.authentic(mutated)) or assess_receipt(mutated, subject, CLAIM, KIND) != "PASS"


@settings(max_examples=examples(400))
@given(st.data())
def test_resealed_mutation_is_caught_by_artifact_hash_or_subject(genuine, data):
    """The attacker holds the key and re-seals but does not recompute ``artifact_hash``."""
    receipt, subject, signer = genuine.receipt, genuine.subject, genuine.signer
    m = data.draw(single_mutation(genuine))
    path, kind, mutated = m.path, m.kind, m.receipt
    forged = reseal(signer, mutated, rehash=False)
    assert signer.authentic(forged)
    outcome = assess_receipt(forged, subject, CLAIM, KIND)
    if is_neutral(path, kind, rehashed=False):
        return
    assert outcome != "PASS", f"{kind} at {path} was accepted after re-sealing"


@settings(max_examples=examples(500))
@given(st.data())
def test_coherent_forgery_is_caught_by_recomputation(genuine, data):
    """The attacker re-seals AND recomputes ``artifact_hash``: the recomputed matrix (shape, coverage,
    types and expected-versus-actual) must still reject every single-field alteration of the artifact
    and of the technical subject. Only the prose ``limitations`` and presentation are non-semantic."""
    receipt, subject, signer = genuine.receipt, genuine.subject, genuine.signer
    m = data.draw(single_mutation(genuine))
    path, kind, mutated = m.path, m.kind, m.receipt
    forged = reseal(signer, mutated, rehash=True)
    outcome = assess_receipt(forged, subject, CLAIM, KIND)
    if is_neutral(path, kind, rehashed=True):
        return
    assert outcome != "PASS", f"{kind} at {path} survived a coherent forgery"


@settings(max_examples=examples(200))
@given(st.data())
def test_flipping_one_observed_result_is_a_recomputed_failure(genuine, data):
    """A coherent forgery that changes one cell's *actual* observation is FAIL: status is recomputed
    from raw observations, never taken from the receipt."""
    receipt, subject, signer = genuine.receipt, genuine.subject, genuine.signer
    forged = copy.deepcopy(receipt)
    cells = forged["artifact"]["cells"]
    cell = cells[data.draw(st.integers(0, len(cells) - 1))]
    field = data.draw(st.sampled_from(["accepted", "state", "version", "audit", "outbox", "operations"]))
    actual = cell["actual"]
    actual[field] = (not actual[field]) if field == "accepted" else (1 - actual[field] if field != "state" else
                     data.draw(st.sampled_from([s for s in forged["artifact"]["matrix"]["states"] if s != actual["state"]])))
    forged["status"] = "PASS"  # an asserted status is ignored
    forged = reseal(signer, forged, rehash=True)
    assert signer.authentic(forged)
    assert assess_receipt(forged, subject, CLAIM, KIND) == "FAIL"
    assert aggregate_status([forged], subject, signer.authentic) == "FAIL"
    assert aggregate_status([forged, receipt], subject, signer.authentic) == "CONFLICT"


@settings(max_examples=examples(200))
@given(st.data())
def test_altered_receipts_never_make_a_passing_aggregate(genuine, data):
    """No list containing an inauthentic receipt aggregates to PASS: the forgery counts as FAIL, and next
    to a genuine PASS it is CONFLICT rather than an average."""
    receipt, subject, signer = genuine.receipt, genuine.subject, genuine.signer
    mutated = data.draw(single_mutation(genuine)).receipt
    assert aggregate_status([mutated], subject, signer.authentic) == "FAIL"
    assert aggregate_status([mutated, receipt], subject, signer.authentic) == "CONFLICT"


@settings(max_examples=examples(100))
@given(st.data())
def test_stale_subject_dimension_makes_receipt_stale(genuine, data):
    """A change in any technical subject dimension is STALE, whatever the receipt body says; the
    presentation dimension is excluded from runtime applicability by design."""
    receipt, subject, signer = genuine.receipt, genuine.subject, genuine.signer
    dimension = data.draw(st.sampled_from(["semantic", "implementation", "policy", "environment", "harness"]))
    other = {**subject, dimension: subject[dimension] + data.draw(st.text(min_size=1, max_size=5))}
    assert assess_receipt(receipt, other, CLAIM, KIND) == "STALE"
    assert assess_receipt(receipt, {**subject, "presentation": "changed"}, CLAIM, KIND) == "PASS"


@settings(max_examples=examples(100))
@given(st.data())
def test_other_claims_and_kinds_are_unknown(genuine, data):
    """This verifier has no authority for any other claim or evidence kind, however green the body."""
    receipt, subject = genuine.receipt, genuine.subject
    claim = data.draw(st.text(min_size=1, max_size=12).filter(lambda s: s != CLAIM))
    assert assess_receipt(receipt, subject, claim, KIND) == "UNKNOWN"
    kind = data.draw(st.text(min_size=1, max_size=12).filter(lambda s: s != KIND))
    assert assess_receipt(receipt, subject, CLAIM, kind) == "UNKNOWN"


@settings(max_examples=examples(60))
@given(st.data())
def test_seal_properties(genuine, data):
    """seal is a pure function of the body, ignores any existing signature, and is key-bound."""
    receipt, signer = genuine.receipt, genuine.signer
    body = {k: v for k, v in receipt.items() if k != "local_signature"}
    junk = data.draw(st.text(max_size=20))
    assert signer.seal({**body, "local_signature": junk}) == signer.seal(body) == receipt
    with scratch_directory() as other_directory:
        assert not ReceiptSigner(other_directory).authentic(receipt), "a different workspace key accepted the receipt"
    for bad in (None, 0, [], {}, b"x"):
        assert not signer.authentic({**body, "local_signature": bad})
