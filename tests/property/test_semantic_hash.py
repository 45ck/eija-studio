"""``Workflow.semantic_hash``: invariant under presentation order, sensitive to every semantic edit.

ARCHITECTURE.md: "Order of definitions is non-semantic, but state/action identities are not." The hash
is the subject of receipts and decisions, so a collision between different meanings would let evidence
for one model vouch for another, and instability under reordering would make evidence spuriously stale.

What this establishes: over generated workflows the hash equals across exactly the pairs whose
independent normal form (``property_strategies.normal_form``) is equal. What it does NOT establish:
collision resistance of SHA-256, or that the normal form itself is the right definition of meaning.
"""
from __future__ import annotations

import re

import pytest
from hypothesis import assume, given, settings, strategies as st
from pydantic import ValidationError

from eija_studio.domain.models import Workflow
from eija_studio.domain.policy import apply_transaction, demo_candidate
from eija_studio.domain.transactions import RetargetTransition
from .property_strategies import normal_form, reordered, semantic_edits, workflows
from .property_support import examples

HEX64 = re.compile(r"[0-9a-f]{64}")


@settings(max_examples=examples(150))
@given(st.data())
def test_hash_invariant_under_reordering(data):
    """Permuting states, transitions, guards and effects never changes the hash."""
    workflow = data.draw(workflows())
    variant = data.draw(reordered(workflow))
    assert normal_form(variant) == normal_form(workflow)
    assert variant.semantic_hash == workflow.semantic_hash
    assert HEX64.fullmatch(workflow.semantic_hash)


@settings(max_examples=examples(300))
@given(st.data())
def test_hash_equality_coincides_with_semantic_equality(data):
    """hash(a) == hash(b) exactly when the independent normal forms agree, for pairs that are
    identical, reordered, one-edit apart, or unrelated."""
    a = data.draw(workflows())
    partner = data.draw(st.sampled_from(["same", "reordered", "edited", "unrelated"]))
    if partner == "same":
        b = a
    elif partner == "reordered":
        b = data.draw(reordered(a))
    elif partner == "edited":
        _, b = data.draw(semantic_edits(a))
    else:
        b = data.draw(workflows())
    assert (a.semantic_hash == b.semantic_hash) == (normal_form(a) == normal_form(b))


@settings(max_examples=examples(300))
@given(st.data())
def test_every_semantic_edit_changes_the_hash(data):
    """Any edit that changes the normal form changes the hash; identities (ids, actions, names) count."""
    workflow = data.draw(workflows())
    kind, edited = data.draw(semantic_edits(workflow))
    if normal_form(edited) != normal_form(workflow):
        assert edited.semantic_hash != workflow.semantic_hash, f"edit {kind!r} did not change the hash"
    else:
        assert edited.semantic_hash == workflow.semantic_hash


@settings(max_examples=examples(100))
@given(workflows())
def test_hash_survives_serialisation_round_trip(workflow):
    """The hash is a function of the contract, not of the Python object that carries it."""
    assert Workflow.model_validate_json(workflow.model_dump_json()).semantic_hash == workflow.semantic_hash
    assert Workflow.model_validate(workflow.model_dump(mode="python")).semantic_hash == workflow.semantic_hash


@settings(max_examples=examples(60))
@given(st.lists(st.sampled_from(["Submitted", "Recommended"]), min_size=1, max_size=6))
def test_semantic_transactions_are_last_writer_wins(sources):
    """Applying a history of typed rejection-source edits yields the model of the last edit only."""
    def reject_from(state: str) -> RetargetTransition:
        return RetargetTransition(kind="retarget_transition", transition="TR-REJECT", end="source", state=state)
    model = demo_candidate()
    for source in sources:
        model = apply_transaction(model, reject_from(source))
    direct = apply_transaction(demo_candidate(), reject_from(sources[-1]))
    assert model.semantic_hash == direct.semantic_hash
    assert normal_form(model) == normal_form(direct)


@pytest.mark.xfail(strict=True, reason=(
    "KERNEL FINDING (found by the deep profile): Transition rejects duplicate required_effects and duplicate "
    "guards but accepts duplicate forbidden_effects, and semantic_hash sorts without de-duplicating. "
    "forbidden_effects=['X'] and ['X', 'X'] mean the same but hash differently, so evidence for one model is "
    "spuriously STALE for the other. Fail-safe, not a collision. Fix in a separate kernel change: reject the "
    "duplicate (mirroring required_effects) or de-duplicate in semantic_hash."))
@settings(max_examples=examples(60))
@given(st.data())
def test_duplicate_forbidden_effect_is_not_a_semantic_difference(data):
    """A duplicated forbidden effect is either refused by the contract or hashes like the original."""
    workflow = data.draw(workflows())
    index = data.draw(st.integers(0, len(workflow.transitions) - 1))
    forbidden = workflow.transitions[index].forbidden_effects
    assume(forbidden)
    document = workflow.model_dump(mode="json")
    document["transitions"][index]["forbidden_effects"] = [*list(forbidden), forbidden[0]]
    try:
        duplicated = Workflow.model_validate(document)
    except ValidationError:
        return  # refused, like a duplicate required effect
    assert duplicated.semantic_hash == workflow.semantic_hash
