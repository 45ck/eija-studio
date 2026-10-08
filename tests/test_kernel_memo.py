"""The memo in front of the kernel (ADR-0191) only skips asking the same frozen objects the same question: every answer
equals a fresh computation, a copy or an edit is asked afresh, a refusal still comes from the policy, a built app is
reused without callers sharing it, and the largest model the kernel accepts loads."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from eija_studio.application.memo import IdentityMemo, ensure_conforms, model_hash
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import check_policy, ensure_policy
from eija_studio.domain.screens import screens_for
from eija_studio.domain.data import data_for
from eija_studio.interfaces.app_build import app_files

ROOT = Path(__file__).resolve().parents[1]
PACK = load_pack(ROOT / "packs" / "library-loan")


def test_the_memo_answers_by_identity_and_holds_its_arguments():
    memo, calls = IdentityMemo(size=2), []
    a, b, c = object(), object(), object()
    assert memo.get((a,), lambda: calls.append("a") or 1) == 1
    assert memo.get((a,), lambda: calls.append("a") or 2) == 1  # same object: kept
    memo.get((b,), lambda: calls.append("b") or 3)
    memo.get((c,), lambda: calls.append("c") or 4)  # a is the oldest and goes
    assert memo.get((a,), lambda: calls.append("a") or 5) == 5
    assert calls == ["a", "b", "c", "a"]


def _cancel_from_loan() -> Workflow:
    data = PACK.model.model_dump(mode="json")
    next(t for t in data["transitions"] if t["action"] == "Cancel")["from_state"] = "OnLoan"
    return Workflow.model_validate(data)


def test_hash_and_policy_match_the_kernel_for_copies_and_edits():
    model = PACK.model
    assert model_hash(model) == model.semantic_hash
    ensure_conforms(model, PACK, ensure_policy)  # conforms: no error, now and when asked again
    ensure_conforms(model, PACK, ensure_policy)
    # An edit is a new object, so it is asked afresh, and refused by the policy itself, with its codes and refs.
    edited = _cancel_from_loan()
    assert model_hash(edited) == edited.semantic_hash != model_hash(model)
    for _ in range(2):
        with pytest.raises(DomainError) as refused:
            ensure_conforms(edited, PACK, ensure_policy)
        assert refused.value.code == "POLICY_BLOCKED" and refused.value.details["codes"] == check_policy(edited, PACK) != []
    # A copy with an update is never answered from the original's entry.
    copy = model.model_copy(update={"initial_state": "OnLoan"})
    assert model_hash(copy) == copy.semantic_hash != model_hash(model)


def test_a_built_app_is_reused_but_each_caller_gets_its_own_copy():
    model, data = PACK.model, data_for(PACK)
    screens = screens_for(PACK, model, data)
    files, manifest = app_files(PACK, model, screens)
    files["app/service.py"] = "tampered"
    manifest["oracle"]["cases"] = -1
    again, kept = app_files(PACK, model, screens)
    assert again["app/service.py"] != "tampered" and kept["oracle"]["cases"] > 0
    # Other screens are another app.
    retitled = screens.screens[0].model_copy(update={"title": "Another title"})
    other = screens.model_copy(update={"screens": (retitled, *screens.screens[1:])})
    assert app_files(PACK, model, other)[0]["app/screens.json"] != again["app/screens.json"]


def test_the_largest_model_the_kernel_accepts_loads_and_passes_its_policy(tmp_path):
    spec = importlib.util.spec_from_file_location("large_pack", ROOT / "scripts" / "large_pack.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pack = load_pack(module.write_large_pack(ROOT / "packs" / "library-loan", tmp_path / "large", states=999, entities=999))
    assert len(pack.model.states) == module.MAX_STATES and len(pack.model.transitions) == module.MAX_TRANSITIONS
    assert len(data_for(pack).entities) == module.MAX_ENTITIES
    assert check_policy(pack.model, pack) == []
