"""The kernel's memo (ADR-0191) only skips asking the same frozen objects the same question: every answer equals a fresh
computation, a copy or an edit is computed afresh, callers cannot change what is kept, and the largest model the
kernel accepts loads."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from eija_studio.domain.models import IdentityMemo, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import check_policy, declared_codes, law_violations
from eija_studio.domain.screens import screens_for
from eija_studio.domain.data import data_for
from eija_studio.interfaces.app_build import app_files

ROOT = Path(__file__).resolve().parents[1]
PACK = load_pack(ROOT / "packs" / "library-loan")


def _fresh_policy(model: Workflow) -> list[str]:
    return sorted(set(declared_codes(model, PACK)) | {v.code for v in law_violations(model, PACK)})


def test_the_memo_answers_by_identity_and_holds_its_arguments():
    memo, calls = IdentityMemo(size=2), []
    a, b, c = object(), object(), object()
    assert memo.get((a,), lambda: calls.append("a") or 1) == 1
    assert memo.get((a,), lambda: calls.append("a") or 2) == 1  # same object: kept
    memo.get((b,), lambda: calls.append("b") or 3)
    memo.get((c,), lambda: calls.append("c") or 4)  # a is the oldest and goes
    assert memo.get((a,), lambda: calls.append("a") or 5) == 5
    assert calls == ["a", "b", "c", "a"]


def test_semantic_hash_and_policy_match_a_fresh_computation_for_copies_and_edits():
    model = PACK.model
    assert model.semantic_hash == model._semantic_hash()
    assert check_policy(model, PACK) == _fresh_policy(model) == []
    # An edit is a new object, so it is checked afresh: Cancel taken by a Clerk breaks no law, Cancel from OnLoan does.
    data = model.model_dump(mode="json")
    moved = next(t for t in data["transitions"] if t["action"] == "Cancel")
    moved["from_state"] = "OnLoan"
    edited = Workflow.model_validate(data)
    assert edited.semantic_hash == edited._semantic_hash() != model.semantic_hash
    assert check_policy(edited, PACK) == _fresh_policy(edited) != []
    # A copy with an update is never answered from the original's entry.
    copy = model.model_copy(update={"initial_state": "OnLoan"})
    assert copy.semantic_hash == copy._semantic_hash() != model.semantic_hash


def test_callers_cannot_change_what_the_memo_keeps():
    data = PACK.model.model_dump(mode="json")
    next(t for t in data["transitions"] if t["action"] == "Cancel")["from_state"] = "OnLoan"
    edited = Workflow.model_validate(data)
    first = check_policy(edited, PACK)
    first.append("TAMPERED")
    assert "TAMPERED" not in check_policy(edited, PACK)


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
    pack = load_pack(module.write_large_pack(tmp_path / "large", states=999, entities=999))
    assert len(pack.model.states) == module.MAX_STATES and len(pack.model.transitions) == module.MAX_TRANSITIONS
    assert len(data_for(pack).entities) == module.MAX_ENTITIES
    assert check_policy(pack.model, pack) == []
