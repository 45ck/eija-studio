"""Oracles for graph/rules/reference.py: fingerprints, verdict algebra, suppression expiry and the SARIF profile.

The official SARIF 2.1.0 JSON schema is not vendored (reuse terms are UNVERIFIED, see ADR-0095). The schema test
reads it from EIJA_SARIF_SCHEMA or .tmp/sarif-schema-2.1.0.json and reports a skip, which is NOT_RUN, when absent.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import itertools
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("weave_rules_reference", ROOT / "graph" / "rules" / "reference.py")
ref = importlib.util.module_from_spec(spec)
sys.modules["weave_rules_reference"] = ref
spec.loader.exec_module(ref)
CATALOGUE = json.loads((ROOT / "graph" / "rules" / "catalogue.json").read_text(encoding="utf-8"))
EXAMPLE = ROOT / "graph" / "schema" / "examples" / "wv-example.sarif.json"

# MEASUREMENT: computed by fingerprint_v1 on 2026-09-29; changing it means a new fingerprint version (eija.finding.v2).
GOLDEN_FINGERPRINT = "38354b0926aa0f7fdbd57c5e4a73bcf549b606018b0d958dd03ee9023ba34d91"


def test_fingerprint_golden_vector_is_pinned() -> None:
    fp = ref.fingerprint_v1("WV-010", ["repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC01"], {"kind": "verifies", "side": "in"})
    assert fp == GOLDEN_FINGERPRINT


def test_fingerprint_is_length_safe() -> None:
    # Doorstop concatenates fields without a separator: ("a","bc") and ("ab","c") collide there. Not here.
    assert ref.fingerprint_v1("WV-001", ["a", "bc"]) != ref.fingerprint_v1("WV-001", ["ab", "c"])
    assert ref.fingerprint_v1("WV-001", ["a"], {"x": "bc"}) != ref.fingerprint_v1("WV-001", ["a"], {"x": "b", "y": "c"})


def test_fingerprint_ignores_order_and_duplicates_but_not_rule_or_identity() -> None:
    a = ref.fingerprint_v1("WV-017", ["t2", "t1", "t1"], {"context": "Assurance", "form": "receipt"})
    b = ref.fingerprint_v1("WV-017", ["t1", "t2"], {"form": "receipt", "context": "Assurance"})
    assert a == b
    assert a != ref.fingerprint_v1("WV-018", ["t1", "t2"], {"form": "receipt", "context": "Assurance"})
    assert a != ref.fingerprint_v1("WV-017", ["t1", "t2"], {"form": "receipt", "context": "Governance"})


def test_fingerprint_rejects_floats_and_unsafe_integers() -> None:
    for bad in (1.0, 2**53, float("nan")):
        with pytest.raises(ValueError):
            ref.fingerprint_v1("WV-001", ["a"], {"n": bad})


def test_canonical_json_matches_jcs_on_the_subset() -> None:
    assert ref.canonical_json({"b": 1, "a": ["x", True, None], "c": "\u20ac\U0001F600"}) == '{"a":["x",true,null],"b":1,"c":"\u20ac\U0001F600"}'


# --------------------------------------------------------------------------------------------- verdict algebra
VALUES = ("FAIL", "NOT_RUN", "PASS")


def test_fold_is_commutative_associative_idempotent_exhaustively() -> None:
    for n in range(1, 5):
        for combo in itertools.product(VALUES, repeat=n):
            expected = ref.fold_verdicts(combo)
            for perm in set(itertools.permutations(combo)):
                assert ref.fold_verdicts(perm) == expected
            assert ref.fold_verdicts(list(combo) + list(combo)) == expected  # idempotent
    for a, b, c in itertools.product(VALUES, repeat=3):
        assert ref.fold_verdicts([ref.fold_verdicts([a, b]), c]) == ref.fold_verdicts([a, ref.fold_verdicts([b, c])])


def test_not_run_absorbs_pass_and_never_absorbs_fail() -> None:
    assert ref.fold_verdicts(["PASS", "NOT_RUN", "PASS"]) == "NOT_RUN"
    assert ref.fold_verdicts(["PASS", "NOT_RUN", "FAIL"]) == "FAIL"
    assert ref.fold_verdicts([]) == "NOT_RUN"  # nothing checked, nothing passed


def test_rule_verdict_truth_table() -> None:
    v = ref.rule_verdict
    assert v(0, True, "none") == "PASS"
    assert v(3, True, "none") == "FAIL"
    assert v(0, False, "none") == "NOT_RUN"  # tool missing
    assert v(2, False, "none") == "NOT_RUN"  # a rule that could not be evaluated has no findings to report
    # incomplete positively read relation: a seen finding is real, silence is not evidence
    assert v(1, True, "monotone") == "FAIL"
    assert v(0, True, "monotone") == "NOT_RUN"
    # incomplete negatively read (or derived) relation: even a finding may be an artefact of the missing facts
    assert v(0, True, "unsafe") == "NOT_RUN"
    assert v(5, True, "unsafe") == "NOT_RUN"
    with pytest.raises(ValueError):
        v(0, True, "sideways")


def _rule(pos, neg):
    return {"reads": {"pos": list(pos), "neg": list(neg)}}


def test_read_effect_classifies_direct_positive_negative_and_derived_reads() -> None:
    eff = lambda rule, incomplete: ref.read_effect(rule, incomplete, CATALOGUE)  # noqa: E731
    by_id = {r["id"]: r for r in CATALOGUE["rules"]}
    assert eff(by_id["WV-009"], ["partial_fact"]) == "monotone"  # positive base read
    assert eff(by_id["WV-009"], ["link"]) == "none"
    assert eff(by_id["WV-010"], ["okf_link"]) == "none"
    # WV-010 negates covered_link.verifies, derived from link_status.verifies, from link.verifies, ledger and nodes
    for rel in ("link.verifies", "link", "ledger", "node.symbol", "node"):
        assert eff(by_id["WV-010"], [rel]) == "unsafe", rel
    # a positive read of a derived relation is treated as unsafe: link_status is not monotone in the ledger
    assert eff(_rule(["covered_link.verifies"], []), ["ledger"]) == "unsafe"
    # union view and typed view overlap in both directions
    assert eff(_rule(["node.symbol"], []), ["node"]) == "monotone"
    assert eff(_rule(["node"], []), ["node.symbol"]) == "monotone"
    assert eff(_rule(["node.symbol"], []), ["node.test"]) == "none"
    # negation wins over a positive read of the same relation
    assert eff(_rule(["term_form"], ["term_form"]), ["term_form"]) == "unsafe"


def test_every_rule_with_a_negative_base_read_is_unsafe_when_that_relation_is_incomplete() -> None:
    n = 0
    for r in CATALOGUE["rules"]:
        for rel in r["reads"]["neg"]:
            assert ref.read_effect(r, [rel], CATALOGUE) == "unsafe", (r["id"], rel)
            n += 1
    assert n > 40


def _subsets(items):
    for k in range(len(items) + 1):
        yield from itertools.combinations(items, k)


def test_polarity_claim_over_all_small_worlds() -> None:
    """The soundness argument of rule_verdict, checked exhaustively on tiny worlds (a check of the declared polarity, not a
    proof for all inputs): for a positively read relation findings only grow with the facts, for a negatively read one
    (the cardinality-min template) findings only shrink, so a finding on partial input can be spurious."""
    import sqlite3

    facts = [("L1", "T1", "R1"), ("L2", "T2", "R1"), ("L3", "T3", "R2"), ("L4", "T4", "R2")]
    q = ref.cardinality_min_sql("node_requirement", "covered_verifies", "in")

    def anti(subset):
        db = sqlite3.connect(":memory:")
        db.executescript("CREATE TABLE node_requirement(id TEXT); CREATE TABLE covered_verifies(link_id TEXT, src TEXT, dst TEXT);"
                         "INSERT INTO node_requirement VALUES ('R1'),('R2'),('R3');")
        db.executemany("INSERT INTO covered_verifies VALUES (?,?,?)", subset)
        return {row[0] for row in db.execute(q, {"min": 1})}

    def pos(subset):  # a positive rule: two distinct verifiers point at one requirement (a redundancy note)
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE covered_verifies(link_id TEXT, src TEXT, dst TEXT)")
        db.executemany("INSERT INTO covered_verifies VALUES (?,?,?)", subset)
        return {row[0] for row in db.execute("SELECT DISTINCT a.dst FROM covered_verifies a JOIN covered_verifies b ON a.dst = b.dst AND a.src < b.src")}

    spurious = 0
    for small in _subsets(facts):
        for big in _subsets(facts):
            if set(small) <= set(big):
                assert pos(small) <= pos(big)  # monotone: findings on partial input are real
                assert anti(small) >= anti(big)  # anti-monotone: findings on partial input can vanish
                spurious += len(anti(small) - anti(big))
    assert spurious > 0, "the oracle must be able to show a finding that disappears when facts arrive"


def test_exit_codes_mirror_the_quality_lane_policy() -> None:
    assert [ref.exit_code(v) for v in VALUES] == [1, 2, 0]
    assert ref.exit_code("NOT_RUN", not_run_accepted=True) == 0


# ------------------------------------------------------------------------------------------------ suppressions
CTX = {"ledger_seq_max": 5, "releases": {"v0.2.0"}, "digests": {"repo://a.py#f": "sha256:aa"}, "as_of": None}


def _supp(**exp) -> dict:
    return {"justification": "reviewed", "evidence": "docs/adr/0001.md", "expires": exp}


def test_suppression_expiry_never_reads_a_clock() -> None:
    assert ref.suppression_status(_supp(ledger_seq=6), CTX) == "active"
    assert ref.suppression_status(_supp(ledger_seq=5), CTX) == "expired"
    assert ref.suppression_status(_supp(release="v0.3.0"), CTX) == "active"
    assert ref.suppression_status(_supp(release="v0.2.0"), CTX) == "expired"
    assert ref.suppression_status(_supp(until_digest="sha256:aa", subject="repo://a.py#f"), CTX) == "active"
    assert ref.suppression_status(_supp(until_digest="sha256:bb", subject="repo://a.py#f"), CTX) == "expired"
    assert ref.suppression_status(_supp(as_of="2026-12-31"), CTX) == "unevaluable"  # no --as-of: fails closed
    assert ref.suppression_status(_supp(as_of="2026-12-31"), {**CTX, "as_of": "2026-12-30"}) == "active"
    assert ref.suppression_status(_supp(as_of="2026-12-31"), {**CTX, "as_of": "2026-12-31"}) == "expired"


def test_suppression_without_evidence_or_expiry_does_not_suppress() -> None:
    assert ref.suppression_status({"justification": "", "evidence": "x", "expires": {"ledger_seq": 9}}, CTX) != "active"
    assert ref.suppression_status({"justification": "j", "evidence": "x"}, CTX) != "active"


# ---------------------------------------------------------------------------------------------------- SARIF
def test_example_is_byte_identical_to_the_committed_file() -> None:
    assert EXAMPLE.read_bytes() == ref.dumps_sarif(ref.example_document(CATALOGUE)).encode("utf-8")
    assert b"\r" not in EXAMPLE.read_bytes()


def test_example_satisfies_the_profile() -> None:
    assert ref.sarif_profile_problems(json.loads(EXAMPLE.read_text(encoding="utf-8"))) == []


FINDINGS = [
    {"rule": "WV-010", "message_id": "requirement-not-verified",
     "args": {"node": "repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC01", "kind": "verifies", "side": "in", "min": 1, "count": 0, "links_seen": "none"},
     "uri": "docs/verification/ACCEPTANCE_MATRIX.csv", "start_line": 2, "logical": ["repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC01"]},
    {"rule": "WV-025", "message_id": "dependency-cycle", "args": {"members": "a,b", "size": 2}, "uri": "src/a.py", "start_line": 1, "logical": ["repo://src/b.py", "repo://src/a.py"]},
    {"rule": "WV-025", "message_id": "dependency-cycle", "args": {"members": "c,d", "size": 2}, "uri": "src/c.py", "start_line": 1, "logical": ["repo://src/c.py"]},
]
ARTIFACTS = [("src/c.py", "0" * 64), ("src/a.py", "1" * 64), ("docs/verification/ACCEPTANCE_MATRIX.csv", "2" * 64)]


def test_output_is_independent_of_finding_and_artifact_order() -> None:
    outs = set()
    for perm in itertools.permutations(range(3)):
        for art in itertools.permutations(ARTIFACTS):
            doc = ref.build_sarif(CATALOGUE, [FINDINGS[i] for i in perm], artifacts=dict(art))
            outs.add(ref.dumps_sarif(doc))
    assert len(outs) == 1  # 6 finding orders x 6 artifact orders, one byte string


def test_two_findings_of_one_rule_get_distinct_fingerprints() -> None:
    doc = ref.build_sarif(CATALOGUE, FINDINGS)
    fps = [r["partialFingerprints"]["eijaFinding/v1"] for r in doc["runs"][0]["results"]]
    assert len(set(fps)) == len(fps) == 3


def test_fingerprint_survives_a_line_number_change() -> None:
    moved = [dict(FINDINGS[0], start_line=99)] + FINDINGS[1:]
    a = ref.build_sarif(CATALOGUE, FINDINGS)["runs"][0]["results"]
    b = ref.build_sarif(CATALOGUE, moved)["runs"][0]["results"]
    key = lambda rs: sorted(r["partialFingerprints"]["eijaFinding/v1"] for r in rs)  # noqa: E731
    assert key(a) == key(b)


def test_profile_checker_flags_each_nondeterministic_element() -> None:
    good = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    cases = {
        "guid": lambda d: d["runs"][0]["results"][0].__setitem__("guid", "3f2a"),
        "time": lambda d: d["runs"][0]["invocations"][0].__setitem__("startTimeUtc", "2026-09-29T00:00:00Z"),
        "machine": lambda d: d["runs"][0]["invocations"][0].__setitem__("machine", "PC"),
        "absolute uri": lambda d: d["runs"][0]["artifacts"][0]["location"].__setitem__("uri", "C:\\repo\\a.py"),
        "scheme uri": lambda d: d["runs"][0]["artifacts"][0]["location"].__setitem__("uri", "file:///repo/a.py"),
        "column kind": lambda d: d["runs"][0].pop("columnKind"),
        "baseline state": lambda d: d["runs"][0]["results"][0].__setitem__("baselineState", "new"),
        "unsorted results": lambda d: d["runs"][0]["results"].reverse(),
    }
    for name, mutate in cases.items():
        bad = copy.deepcopy(good)
        mutate(bad)
        assert ref.sarif_profile_problems(bad), name


def test_not_run_is_a_notification_and_an_open_result_never_a_pass() -> None:
    run = json.loads(EXAMPLE.read_text(encoding="utf-8"))["runs"][0]
    inv = run["invocations"][0]
    assert inv["executionSuccessful"] is False
    assert inv["toolExecutionNotifications"][0]["descriptor"]["id"] == "EIJA-NOTRUN"
    assert any(r["kind"] == "open" and r["ruleId"] == "WV-065" for r in run["results"])
    assert run["properties"]["verdict"] == "FAIL"  # FAIL dominates NOT_RUN in the chain
    assert ref.fold_verdicts(["PASS", "NOT_RUN"]) == "NOT_RUN"


def test_a_notrun_message_cannot_be_reported_as_a_finding() -> None:
    with pytest.raises(ValueError):
        ref.build_sarif(CATALOGUE, [{"rule": "WV-009", "message_id": "extraction-partial", "args": {"file": "a.py", "position": "1:1"}, "uri": "a.py"}])


def test_example_validates_against_the_official_schema_when_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    candidates = [os.environ.get("EIJA_SARIF_SCHEMA", ""), str(ROOT / ".tmp" / "sarif-schema-2.1.0.json"), str(ROOT / ".tmp" / "sarif-schema.json")]
    path = next((Path(c) for c in candidates if c and Path(c).is_file()), None)
    if path is None:
        pytest.skip("NOT_RUN: the OASIS SARIF 2.1.0 schema is not available offline (set EIJA_SARIF_SCHEMA)")
    schema = json.loads(path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft4Validator(schema)  # the published schema declares draft-04
    doc = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert list(validator.iter_errors(doc)) == []
    bad = copy.deepcopy(doc)
    bad["runs"][0]["results"][0]["level"] = "fatal"
    assert list(validator.iter_errors(bad)), "the schema check must be able to fail"
    assert len(hashlib.sha256(path.read_bytes()).hexdigest()) == 64


# ------------------------------------------------------------------------------------------------- templates
def _toy_db():
    import sqlite3

    db = sqlite3.connect(":memory:")
    db.executescript(
        """CREATE TABLE node_requirement(id TEXT PRIMARY KEY);
        CREATE TABLE covered_verifies(link_id TEXT, src TEXT, dst TEXT);
        INSERT INTO node_requirement VALUES ('R1'),('R2'),('R3');
        INSERT INTO covered_verifies VALUES ('L1','T1','R1'),('L2','T2','R1'),('L3','T3','R2');"""
    )
    return db


def test_cardinality_min_template_positive_negative_and_boundary() -> None:
    db = _toy_db()
    q = ref.cardinality_min_sql("node_requirement", "covered_verifies", "in")
    assert db.execute(q, {"min": 1}).fetchall() == [("R3", 0)]  # R3 has no covered verifier
    assert db.execute(q, {"min": 2}).fetchall() == [("R2", 1), ("R3", 0)]  # boundary: minimum 2
    assert db.execute(q, {"min": 0}).fetchall() == []
    db.execute("INSERT INTO covered_verifies VALUES ('L4','T4','R3')")  # repair: add the missing link
    assert db.execute(q, {"min": 1}).fetchall() == []
    db.execute("DELETE FROM covered_verifies WHERE dst = 'R1'")  # fire: remove all covered links of R1
    assert db.execute(q, {"min": 1}).fetchall() == [("R1", 0)]


def test_peer_parameter_separates_rules_that_differ_only_in_the_other_end() -> None:
    import sqlite3

    db = sqlite3.connect(":memory:")
    db.executescript(
        """CREATE TABLE node_transition(id TEXT); CREATE TABLE node_ui_control(id TEXT); CREATE TABLE node_symbol(id TEXT);
        CREATE TABLE covered_realises(link_id TEXT, src TEXT, dst TEXT);
        INSERT INTO node_transition VALUES ('T1'),('T2'),('T3'),('T4');
        INSERT INTO node_ui_control VALUES ('C1'); INSERT INTO node_symbol VALUES ('S1');
        INSERT INTO covered_realises VALUES ('L1','C1','T1'),('L2','S1','T1'),('L3','C1','T2'),('L4','S1','T3');"""
    )
    ui = ref.cardinality_min_sql("node_transition", "covered_realises", "in", "node_ui_control")
    code = ref.cardinality_min_sql("node_transition", "covered_realises", "in", "node_symbol")
    anyone = ref.cardinality_min_sql("node_transition", "covered_realises", "in")
    assert ui != code != anyone
    assert db.execute(ui, {"min": 1}).fetchall() == [("T3", 0), ("T4", 0)]  # T3 has code but no control
    assert db.execute(code, {"min": 1}).fetchall() == [("T2", 0), ("T4", 0)]  # T2 has a control but no code
    assert db.execute(anyone, {"min": 1}).fetchall() == [("T4", 0)]  # without the peer both defects are hidden
    with pytest.raises(ValueError):
        ref.cardinality_min_sql("node_transition", "covered_realises", "in", "x; DROP TABLE y")


def test_cardinality_min_template_side_and_injection_guard() -> None:
    q = ref.cardinality_min_sql("node_requirement", "covered_verifies", "out")
    assert "c.src = n.id" in q
    with pytest.raises(ValueError):
        ref.cardinality_min_sql("node_requirement; DROP TABLE x", "covered_verifies", "in")
    with pytest.raises(ValueError):
        ref.cardinality_min_sql("node_requirement", "covered_verifies", "sideways")
