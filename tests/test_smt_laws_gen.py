"""WBS 1.4: SMT laws generated from a domain pack (verification/smt/laws_gen.py) and their gates (laws_gate.py).

Proof: over the hand-written grammar, the generated encoding of the excursion pack is equivalent to the hand-written
one code by code (``hand XOR generated`` UNSAT), implies every hand-written authority invariant, and is implied by it.
Negative controls: a pack with a law deleted or weakened (or its forbidden effects dropped) fails that gate; a deleted
clause is caught by the differential against the real ``check_policy``. A new pack's Bend and TLC evidence is NOT_RUN
with the pack's reason, never PASS. Tests marked ``formal`` run whole differentials (seconds each).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from eija_studio.application.formal import attach, for_pack, packet_view, verifier_view
from eija_studio.domain.formal import FormalArtifact, NOT_RUN, PASS
from eija_studio.domain.pack import PACKS_ROOT, load_pack

pytest.importorskip("z3", reason="z3-solver is in the `smt` extra; without it the proof is NOT_RUN, not passed")

from formal_support import StubSource, context_of, subject_of
from verification.smt import laws as cli
from verification.smt import laws_gate as LG
from verification.smt import laws_gen as G

formal = pytest.mark.formal
EXCURSION = load_pack(PACKS_ROOT / "excursion")
LIBRARY = load_pack(PACKS_ROOT / "library-loan")


def test_generated_encoding_is_equivalent_to_the_hand_encoding_code_by_code():
    result = LG.equivalence(EXCURSION)
    assert result["verdict"] == "PASS" and result["admits_equivalent"] == "proved"
    assert result["codes_equivalent"] == result["codes_total"] >= 20
    assert {r["status"] for r in result["hand_invariants_implied_by_generated_policy"]} == {"proved"}
    assert {r["status"] for r in result["generated_laws_implied_by_hand_policy"]} == {"proved"}
    assert len(result["generated_laws_implied_by_hand_policy"]) == len(EXCURSION.laws)  # every law is encoded


@pytest.mark.parametrize("broken,refuted", [
    (LG.without_law(EXCURSION, "approve-held-by-registrar"), "INV-TEACHER-NOT-DECIDER"),
    (LG.weaken_source_law(EXCURSION, "reject-source-bounded"), "INV-REJECT-SOURCE-BOUNDED"),
    (LG.without_forbidden_effects(EXCURSION), "INV-FORBIDDEN-EFFECTS-EXCLUDED"),
])
def test_a_deleted_or_weakened_law_fails_the_equivalence_gate(broken, refuted):
    result = LG.equivalence(broken)
    assert result["verdict"] == "FAIL"
    assert any(r["status"] == "differs" for r in result["codes"])
    assert refuted in {r["id"] for r in result["hand_invariants_implied_by_generated_policy"] if r["status"] == "refuted"}


@formal
def test_every_planted_pack_defect_fails_the_equivalence_gate():
    controls = LG.equivalence_controls(EXCURSION)
    assert len(controls) == len(EXCURSION.laws) + 7 + 1  # every law deleted, every source law widened, forbidden dropped
    assert all(c["detected"] for c in controls), [c["control"] for c in controls if not c["detected"]]


def test_the_grammar_refuses_a_pack_that_does_not_fit_it():
    """A comparison over a grammar missing some of the pack's names would prove nothing: refused, not narrowed."""
    with pytest.raises(ValueError, match="does not fit"):
        LG._hand_grammar(LIBRARY, LG.E.new_workflow("misfit"))


def test_generic_proof_on_a_new_pack_is_not_vacuous_and_reports_what_it_does_not_encode():
    g = G.grammar(LIBRARY)
    invariants = G.law_invariants(g, LIBRARY)
    assert len(invariants) == 9 and all(LG._falsifiable(g, i) for i in invariants)
    assert {x["law"]: x["status"] for x in G.not_encoded(LIBRARY)} == {"returned-requires-loan": "NOT_RUN",
                                                                       "runtime-evidence": "NOT_RUN"}
    assert LG._solver(g.canonical(), LG.E.admits(G.policy_clauses(g, LIBRARY))).check() == LG.z3.sat


@formal
@pytest.mark.parametrize("pack", [EXCURSION, LIBRARY], ids=["excursion", "library-loan"])
def test_generated_encoding_agrees_with_the_real_policy_and_a_deleted_clause_is_caught(pack):
    proof = LG.pack_proof(pack, random_mutants=100)
    diff = proof["differential"]
    assert proof["verdict"] == "PASS" and diff["candidates"] > 500 and diff["disagreements"] == []
    assert diff["clauses_never_fired"] == [] and diff["clauses_never_silent"] == []
    assert proof["negative_control"]["detected"]


def test_a_deleted_clause_is_caught_by_the_differential_quickly():
    first_law = next(c.id for c in G.policy_clauses(G.grammar(LIBRARY), LIBRARY) if c.name.startswith("law:"))
    res = LG.differential(LIBRARY, random_mutants=0, drop=frozenset({first_law}))
    assert res.candidates > 0 and res.disagreements


def test_cli_reports_not_run_without_z3(monkeypatch, capsys):
    monkeypatch.setattr(cli.importlib.util, "find_spec", lambda name: None)
    assert cli.main(["--pack", str(PACKS_ROOT / "library-loan")]) == cli.NOT_RUN_EXIT
    assert "NOT_RUN" in capsys.readouterr().err


# ---- a new pack's Bend and TLC evidence is NOT_RUN with the pack's reason ------------------------------------------

def _pass_like(kind: str) -> FormalArtifact:
    return FormalArtifact(kind, {"protocol": "p", "anything": "a report about another pack's model"}, {})


def test_a_new_pack_reports_bend_and_tlc_not_run_with_the_reason_never_pass():
    items = for_pack([_pass_like(k) for k in ("bend_proof", "smt_proof", "bounded_model_check")], LIBRARY)
    by = {i.kind: i.artifact for i in items}
    assert set(by) == {"bend_proof", "smt_proof", "bounded_model_check"} and all("not_run" in a for a in by.values())
    assert "Bend" in by["bend_proof"]["not_run"]["reason"]
    view = {v["kind"]: v for v in verifier_view(LIBRARY)}
    assert view["tlc"]["status"] == NOT_RUN and "TLA+" in view["tlc"]["reason"]
    assert view["bend_proof"]["status"] == NOT_RUN and PASS not in {v["status"] for v in view.values()}


def test_the_hand_encoded_pack_keeps_its_reports_unchanged():
    """Negative control of the substitution: nothing is replaced for a pack whose verifiers read the reports."""
    items = [_pass_like(k) for k in ("bend_proof", "smt_proof", "bounded_model_check")]
    assert for_pack(items, EXCURSION) == items and for_pack(items, None) == items


def test_the_packet_of_a_new_pack_shows_bend_not_run_through_the_real_kernel():
    base, cand = LIBRARY.model, LIBRARY.model
    source = StubSource([_pass_like("bend_proof")])
    receipts = attach(source, base, cand, subject_of(cand), [], lambda r: r, "2026-01-01T00:00:00+00:00", lambda: "id",
                      LIBRARY)
    view = packet_view(receipts, subject_of(cand), lambda r: True, context_of(base, cand), [], LIBRARY)
    status = {e["kind"]: e["status"] for e in view["evidence"]}
    assert status["bend_proof"] == NOT_RUN
    assert {v["kind"]: v["status"] for v in view["verifiers"]}["tlc"] == NOT_RUN


def test_packs_declare_verifiers_by_evidence_kind():
    root = Path(PACKS_ROOT)
    for location in sorted(p for p in root.iterdir() if (p / "pack.json").is_file()):
        kinds = {v.kind for v in load_pack(location).verifiers}
        assert {"bend_proof", "smt_proof", "bounded_model_check", "tlc"} <= kinds, location.name
