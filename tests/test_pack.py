"""WBS 1.1: domain packs. The excursion pack is a faithful transcription of the kernel's excursion constants, a
structurally different second pack loads, and a defective pack is refused with sorted diagnostics, never a crash.

PROOF (measured, not predicted):
- golden equivalence: the excursion pack's model has the old baseline's semantic hash and is byte-equal to it;
- differential: the pack-driven policy returns exactly the legacy ``check_policy`` codes on every example and on
  every SMT differential candidate (the count is asserted);
- negative controls: dropping one law from the pack makes the differential disagree; each planted defect in the
  malformed corpus yields ``PACK_INVALID`` and never another exception.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from eija_studio.domain.models import BASE_GUARDS, Workflow
from eija_studio.domain.pack import Pack, PackError, load_pack, parse_pack, ui_key
from eija_studio.domain.policy import baseline, check_policy
from legacy_policy import CANONICAL_OPTIONS, EFFECTS, FORBIDDEN, check_policy as legacy_policy

ROOT = Path(__file__).resolve().parents[1]
EXCURSION, LIBRARY = ROOT / "packs" / "excursion", ROOT / "packs" / "library-loan"
UNSAFE_LOAN = LIBRARY / "variants" / "unsafe-return-without-loan.json"


def raw(location: Path = EXCURSION) -> dict:
    return json.loads((location / "pack.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def excursion() -> Pack:
    return load_pack(EXCURSION)


@pytest.fixture(scope="module")
def library() -> Pack:
    return load_pack(LIBRARY)


# ---- golden equivalence ---------------------------------------------------------------------------------

def test_excursion_pack_model_is_the_old_baseline(excursion):
    assert excursion.model.semantic_hash == baseline().semantic_hash
    assert excursion.model.model_dump(mode="json") == baseline().model_dump(mode="json")
    example = Workflow.model_validate_json((ROOT / "examples" / "excursion-baseline.json").read_text(encoding="utf-8"))
    assert excursion.model.semantic_hash == example.semantic_hash


def test_excursion_pack_transcribes_the_policy_constants(excursion):
    assert {a.id: a.required_effects for a in excursion.actions} == EFFECTS
    assert excursion.effects.forbidden == FORBIDDEN
    assert {m.id: {"label": m.label, "supported": m.supported, "consequences": list(m.consequences)}
            for m in excursion.meanings} == CANONICAL_OPTIONS
    extra = {a.id: set(a.guards) - set(BASE_GUARDS) for a in excursion.actions}
    assert extra == {"Submit": set(), "Recommend": {"actor_assigned"}, "Approve": set(), "Reject": set(), "Revise": set()}


@pytest.mark.parametrize("path", sorted((ROOT / "examples").glob("*.json")), ids=lambda p: p.stem)
def test_pack_policy_equals_legacy_policy_on_the_examples(excursion, path):
    model = Workflow.model_validate_json(path.read_text(encoding="utf-8"))
    assert check_policy(model, excursion) == legacy_policy(model)


def _differential(pack: Pack, mutants: int = 1500, fresh: int = 500) -> tuple[int, int, list]:
    differential = pytest.importorskip("verification.smt.differential", reason="z3-solver (extra `smt`) is not installed: NOT_RUN")
    total, valid, disagreements = 0, 0, []
    for model, schema_valid in differential.candidates(20260928, mutants, fresh):
        total, valid = total + 1, valid + int(schema_valid)
        legacy, generic = legacy_policy(model), check_policy(model, pack)
        if legacy != generic:
            disagreements.append((legacy, generic))
    return total, valid, disagreements


def test_pack_policy_equals_legacy_policy_on_every_smt_differential_candidate(excursion):
    total, valid, disagreements = _differential(excursion)
    assert total >= 1000 and valid >= 500, (total, valid)  # measured 2572 candidates, 815 schema-valid (seed 20260928)
    assert disagreements == []


@pytest.mark.parametrize("law_id", ["approve-held-by-registrar", "reject-source-bounded", "shape-recommendation"])
def test_negative_control_a_dropped_law_makes_the_differential_disagree(law_id):
    document = raw()
    document["laws"] = [law for law in document["laws"] if law["id"] != law_id]
    _, _, disagreements = _differential(parse_pack(document), 150, 50)
    assert disagreements, f"dropping {law_id} went unnoticed: the differential has no teeth"


# ---- the second pack ----------------------------------------------------------------------------------------

def test_library_loan_is_structurally_different(library, excursion):
    finals = {law.state for law in library.laws if law.kind == "state_final"}
    assert len(library.model.states) == 5 and len(library.roles) == 3 and len(finals) == 2
    assert all(t.from_state not in finals for t in library.model.transitions)
    assert {law.kind for law in library.laws if law.kind == "path_requires"} == {"path_requires"}
    assert "path_requires" not in {law.kind for law in excursion.laws}
    assert check_policy(library.model, library) == []


def test_library_loan_unsafe_variant_is_refused_by_the_sequence_law_only(library):
    unsafe = Workflow.model_validate_json(UNSAFE_LOAN.read_text(encoding="utf-8"))
    assert check_policy(unsafe, library) == ["LOAN_RETURN_WITHOUT_CHECKOUT"]
    # Negative control: without the sequence law nothing else notices the defect.
    document = raw(LIBRARY)
    document["laws"] = [law for law in document["laws"] if law["kind"] != "path_requires"]
    assert check_policy(unsafe, parse_pack(document)) == []


def test_ui_keys_derive_from_pack_ids(library):
    assert ui_key(library.id, "state", "OnLoan") == "library-loan.state.OnLoan"


# ---- malformed packs: sorted diagnostics, never a crash --------------------------------------------------------

def _broken(edit) -> dict:
    document = raw()
    edit(document)
    return document


def _first_law(d: dict) -> dict:
    return d["laws"][0]


MALFORMED = {
    "not-an-object": [],
    "missing-fixtures": _broken(lambda d: d.pop("fixtures")),
    "unknown-law-kind": _broken(lambda d: _first_law(d).update(kind="teleport")),
    "law-names-undeclared-state": _broken(lambda d: d["laws"].append(
        {"id": "ghost", "kind": "state_final", "code": "GHOST", "state": "Limbo"})),
    "transition-with-undeclared-role": _broken(lambda d: d["model"]["transitions"][0].update(role="Janitor")),
    "duplicate-law-ids": _broken(lambda d: d["laws"].append(copy.deepcopy(d["laws"][0]))),
    "actor-with-undeclared-role": _broken(lambda d: d["fixtures"]["actors"][0].update(role="Janitor")),
    "proposal-names-unknown-meaning": _broken(lambda d: d["fixtures"]["proposals"]["fallback"][0].update(interpretation="teleport")),
    "model-id-differs": _broken(lambda d: d["model"].update(id="other")),
    "bad-binding": _broken(lambda d: d["language"]["terms"][0]["binds"].append("https://example.org/x")),
    "effect-not-in-catalog": _broken(lambda d: d["actions"][0]["required_effects"].append("Audit:Nowhere")),
    "wrong-type": _broken(lambda d: d.update(roles="Teacher")),
}


@pytest.mark.parametrize("name", sorted(MALFORMED))
def test_malformed_pack_is_refused_with_sorted_diagnostics(name):
    with pytest.raises(PackError) as caught:
        parse_pack(MALFORMED[name])
    assert caught.value.code == "PACK_INVALID"
    assert caught.value.diagnostics and list(caught.value.diagnostics) == sorted(caught.value.diagnostics)


def test_several_defects_are_all_reported_and_sorted():
    document = _broken(lambda d: (d["model"]["transitions"][0].update(role="Janitor"), d["fixtures"]["actors"][0].update(role="Ghost")))
    with pytest.raises(PackError) as caught:
        parse_pack(document)
    assert len(caught.value.diagnostics) == 2 and list(caught.value.diagnostics) == sorted(caught.value.diagnostics)


@pytest.mark.parametrize("content", [b"{not json", b"\xff\xfe\x00bad", b"[" * 100_000], ids=["syntax", "encoding", "deep"])
def test_unreadable_files_are_diagnostics(tmp_path, content):
    (tmp_path / "pack.json").write_bytes(content)
    with pytest.raises(PackError) as caught:
        load_pack(tmp_path)
    assert caught.value.code == "PACK_INVALID"


def test_missing_pack_is_a_diagnostic(tmp_path):
    with pytest.raises(PackError, match="cannot be read"):
        load_pack(tmp_path / "nowhere")


def _paths(value, prefix=()):
    yield prefix
    children = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    for key, child in children:
        yield from _paths(child, (*prefix, key))


PATHS = [p for p in _paths(raw()) if p]


@settings(max_examples=50, derandomize=True, deadline=None)
@given(st.sampled_from(PATHS), st.sampled_from([None, 0, "", "x", [], {}, True]))
def test_random_single_edits_never_crash_the_loader(path, value):
    document = raw()
    target = document
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    try:
        parse_pack(document)
    except PackError as error:
        assert error.diagnostics == tuple(sorted(error.diagnostics))


# ---- contract ------------------------------------------------------------------------------------------------

def test_committed_pack_schema_is_the_models_schema():
    committed = json.loads((ROOT / "contracts" / "pack.schema.json").read_text(encoding="utf-8"))
    assert committed == Pack.model_json_schema()


def test_both_packs_validate_against_the_committed_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "contracts" / "pack.schema.json").read_text(encoding="utf-8"))
    for location in (EXCURSION, LIBRARY):
        jsonschema.Draft202012Validator(schema).validate(raw(location))
