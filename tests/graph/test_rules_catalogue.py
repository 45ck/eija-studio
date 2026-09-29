"""Oracles for graph/rules/catalogue.json (ADR-0095).

The catalogue is data, so its tests are load-time checks: the validator must accept the committed file and must
reject seeded defects (a validator that cannot fail is worse than none). Nothing here needs a network or a browser.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "graph" / "rules"
spec = importlib.util.spec_from_file_location("weave_check_catalogue", RULES / "check_catalogue.py")
check = importlib.util.module_from_spec(spec)
sys.modules["weave_check_catalogue"] = check
spec.loader.exec_module(check)


@pytest.fixture()
def cat() -> dict:
    return check.load()


def test_committed_catalogue_validates() -> None:
    assert check.validate() == []


def test_at_least_forty_rules_across_every_requested_category(cat: dict) -> None:
    assert len(cat["rules"]) >= 40
    for label, categories in check.REQUIRED_COVERAGE.items():
        n = sum(1 for r in cat["rules"] if r["category"] in categories)
        assert n >= 2, label


def test_files_are_ascii_lf_and_end_with_newline() -> None:
    for name in ("catalogue.json", "decisions.jsonl"):
        raw = (RULES / name).read_bytes()
        assert b"\r" not in raw, name
        raw.decode("ascii")
        assert raw.endswith(b"\n"), name


def test_catalogue_is_sorted_and_ids_are_never_reused(cat: dict) -> None:
    ids = [r["id"] for r in cat["rules"]]
    assert ids == sorted(ids)
    assert not ({x["id"] for x in cat["retired"]} & set(ids))


def test_stats_are_deterministic(cat: dict) -> None:
    a = json.dumps(check.stats(cat), sort_keys=True)
    b = json.dumps(check.stats(copy.deepcopy(cat)), sort_keys=True)
    assert a == b


def test_comment_only_edit_dirties_no_rule(cat: dict) -> None:
    fp = check.stats(cat)["change_footprints"]
    key = next(k for k in fp if k.startswith("comment-only"))
    assert fp[key]["dirty_rules"] == 0  # early cutoff: the normalised digest did not change


def test_every_derived_relation_used_by_a_negation_is_below_its_rule(cat: dict) -> None:
    strata = {r["name"]: r["stratum"] for r in cat["relations"]}
    for r in cat["rules"]:
        for name in r["reads"]["neg"]:
            s = check.relation_stratum(name, strata)
            assert s is not None and s < r["stratum"], (r["id"], name)


def test_metamodel_obligations_name_catalogue_rules(cat: dict) -> None:
    if not check.METAMODEL.is_file():
        pytest.skip("NOT_RUN: graph/schema/metamodel.json is not present")
    mm = json.loads(check.METAMODEL.read_text(encoding="utf-8"))
    named = {ob["rule"] for spec_ in mm["link_types"].values() for sig in spec_["signatures"] for ob in sig.get("obligations", [])}
    ids = {r["id"] for r in cat["rules"]}
    assert named <= ids


# ---------------------------------------------------------------- negative oracles: the validator must fail
def _mut(cat: dict, fn) -> list[str]:
    bad = copy.deepcopy(cat)
    fn(bad)
    return check.validate(bad)


def test_validator_rejects_wrong_stratum(cat: dict) -> None:
    errs = _mut(cat, lambda c: c["rules"][0].__setitem__("stratum", 3))
    assert any("stratum" in e for e in errs)


def test_validator_rejects_unknown_relation(cat: dict) -> None:
    errs = _mut(cat, lambda c: c["rules"][0]["reads"]["pos"].append("no_such_relation"))
    assert any("unknown relation" in e for e in errs)


def test_validator_rejects_unknown_link_kind(cat: dict) -> None:
    errs = _mut(cat, lambda c: c["rules"][0]["reads"]["pos"].append("link.not_a_kind"))
    assert any("not a kind" in e or "link kind" in e for e in errs)


def test_validator_rejects_undeclared_message_argument(cat: dict) -> None:
    errs = _mut(cat, lambda c: c["rules"][0]["messages"][0].__setitem__("text", "uses {nothing_declared}"))
    assert any("placeholder" in e for e in errs)


def test_validator_rejects_rule_without_decision_entry(cat: dict, tmp_path: Path, monkeypatch) -> None:
    lines = [ln for ln in check.DECISIONS.read_text(encoding="utf-8").splitlines() if '"rule": "WV-001"' not in ln]
    fake = tmp_path / "decisions.jsonl"
    fake.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    monkeypatch.setattr(check, "DECISIONS", fake)
    errs = check.validate(cat)
    assert any("WV-001" in e and "ADR-lite" in e for e in errs) or any("seq" in e for e in errs)


def test_validator_rejects_reused_retired_id(cat: dict) -> None:
    errs = _mut(cat, lambda c: c["retired"].append({"id": "WV-001", "name": "x", "merged_into": "WV-002", "reason": "x"}))
    assert any("retired id is reused" in e for e in errs)


def test_validator_rejects_missing_repair_revert(cat: dict) -> None:
    errs = _mut(cat, lambda c: c["rules"][0]["mutations"]["repair"].remove("RM-REVERT"))
    assert any("RM-REVERT" in e for e in errs)


def test_validator_rejects_severity_above_messages(cat: dict) -> None:
    errs = _mut(cat, lambda c: c["rules"][0].__setitem__("severity", "note"))
    assert any("severity" in e for e in errs)


def test_validator_rejects_negation_over_findings_below_stratum_three(cat: dict) -> None:
    def fn(c: dict) -> None:
        r = next(x for x in c["rules"] if x["id"] == "WV-045")
        r["stratum"] = 2

    errs = _mut(cat, fn)
    assert any("stratum" in e for e in errs)


def test_validator_rejects_metamodel_disagreement(cat: dict) -> None:
    if not check.METAMODEL.is_file():
        pytest.skip("NOT_RUN: graph/schema/metamodel.json is not present")

    def fn(c: dict) -> None:
        r = next(x for x in c["rules"] if x["id"] == "WV-010")
        r["params"]["min"] = 2

    errs = _mut(cat, fn)
    assert any("WV-010" in e and "metamodel" in e for e in errs)


def test_validator_rejects_two_template_rules_with_identical_params(cat: dict) -> None:
    def fn(c: dict) -> None:
        by = {r["id"]: r for r in c["rules"]}
        by["WV-063"]["params"].pop("peer")
        by["WV-031"]["params"].pop("peer")

    errs = _mut(cat, fn)
    assert any("WV-031, WV-063" in e and "identical template and params" in e for e in errs)


def test_realiser_rules_differ_by_peer_and_reads(cat: dict) -> None:
    by = {r["id"]: r for r in cat["rules"]}
    assert by["WV-031"]["params"]["peer"] == "ui_control" and "node.ui_control" in by["WV-031"]["reads"]["pos"]
    assert by["WV-063"]["params"]["peer"] == "symbol" and "node.symbol" in by["WV-063"]["reads"]["pos"]


def test_validator_rejects_peer_that_is_not_read_or_not_a_type(cat: dict) -> None:
    def unread(c: dict) -> None:
        r = next(x for x in c["rules"] if x["id"] == "WV-063")
        r["reads"]["pos"].remove("node.symbol")

    assert any("node.symbol is not read" in e for e in _mut(cat, unread))

    def unknown(c: dict) -> None:
        next(x for x in c["rules"] if x["id"] == "WV-063")["params"]["peer"] = "no_such_type"

    assert any("no_such_type" in e for e in _mut(cat, unknown))


def test_validator_rejects_a_negation_without_a_negative_read(cat: dict) -> None:
    def fn(c: dict) -> None:
        r = next(x for x in c["rules"] if x["id"] == "WV-093")
        r["reads"]["pos"] += r["reads"]["neg"]
        r["reads"]["neg"] = []
        r["stratum"] = 0

    errs = _mut(cat, fn)
    assert any("WV-093" in e and "negation" in e for e in errs)


def test_attribute_only_negation_allowlist_is_exact(cat: dict) -> None:
    ids = {r["id"] for r in cat["rules"]}
    assert set(check.ATTRIBUTE_ONLY_NEGATION) <= ids
    for rid in check.ATTRIBUTE_ONLY_NEGATION:
        r = next(x for x in cat["rules"] if x["id"] == rid)
        assert check.NEGATION.search(r["statement"]) and not r["reads"]["neg"], rid  # no stale entry


def test_every_rule_with_a_negation_in_its_statement_reads_something_negatively_or_is_reviewed(cat: dict) -> None:
    for r in cat["rules"]:
        if check.NEGATION.search(r["statement"]) and r["id"] not in check.ATTRIBUTE_ONLY_NEGATION:
            assert r["reads"]["neg"], r["id"]


# ------------------------------------------------------------------------------- decision entries: stub versus checked
NL = chr(10)


def _decisions() -> list[dict]:
    return [json.loads(line) for line in check.DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_decision_entries_say_honestly_which_alternatives_were_checked(cat: dict) -> None:
    ds = _decisions()
    stubs = [d for d in ds if not d["alternatives_checked"]]
    checked = [d for d in ds if d["alternatives_checked"]]
    assert {d["rule"] for d in checked} == {"WV-083", "WV-085", "WV-086"}  # the three rules whose tools were probed
    assert len({d["alternatives"] for d in checked}) == len(checked)
    assert all(d["alternatives"].startswith("STUB") for d in stubs)
    assert check.stats(cat)["decision_entries"] == {"total": len(ds), "alternatives_checked": len(checked), "stub": len(stubs)}


def test_promotion_gate_rejects_a_stub_and_shared_alternatives(tmp_path: Path, monkeypatch, cat: dict) -> None:
    def promote(c: dict) -> None:
        next(x for x in c["rules"] if x["id"] == "WV-001")["maturity"] = "experimental"

    assert any("WV-001" in e and "stub" in e for e in _mut(cat, promote))

    lines = [json.loads(line) for line in check.DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    for d in lines:
        if d["rule"] in ("WV-001", "WV-002"):
            d["alternatives_checked"] = True  # claims to be checked but the text is the shared stub
    fake = tmp_path / "decisions.jsonl"
    fake.write_text("".join(json.dumps(d, sort_keys=True) + NL for d in lines), encoding="utf-8", newline=NL)
    monkeypatch.setattr(check, "DECISIONS", fake)
    bad = copy.deepcopy(cat)
    for x in bad["rules"]:
        if x["id"] in ("WV-001", "WV-002"):
            x["maturity"] = "experimental"
    assert any("shared with another rule" in e for e in check.validate(bad))


def test_promotion_gate_accepts_a_rule_with_checked_own_alternatives(cat: dict) -> None:
    def promote(c: dict) -> None:
        next(x for x in c["rules"] if x["id"] == "WV-085")["maturity"] = "experimental"

    assert not [e for e in _mut(cat, promote) if "WV-085" in e]


# ------------------------------------------------------------------------------------ structural JSON Schema
def _validator(ref: str):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "graph" / "schema" / "rules.schema.json").read_text(encoding="utf-8"))
    sub = {"$schema": schema["$schema"], "$defs": schema["$defs"], "$ref": ref}
    return jsonschema.Draft202012Validator(sub)


def test_catalogue_and_decisions_match_the_structural_schema(cat: dict) -> None:
    assert list(_validator("#/$defs/catalogue").iter_errors(cat)) == []
    dv = _validator("#/$defs/decision_entry")
    for line in check.DECISIONS.read_text(encoding="utf-8").splitlines():
        assert list(dv.iter_errors(json.loads(line))) == [], line[:80]


def test_structural_schema_can_fail(cat: dict) -> None:
    bad = copy.deepcopy(cat)
    bad["rules"][0]["severity"] = "fatal"
    assert list(_validator("#/$defs/catalogue").iter_errors(bad))
    bad = copy.deepcopy(cat)
    del bad["rules"][1]["messages"]
    assert list(_validator("#/$defs/catalogue").iter_errors(bad))


def test_suppression_schema_accepts_each_expiry_kind_and_rejects_a_wall_clock_timestamp() -> None:
    v = _validator("#/$defs/suppression")
    base = {"id": "S-0001", "rule": "WV-025", "fingerprint": "a" * 64, "justification": "cycle tracked in ADR-0123", "evidence": "docs/adr/0123-x.md"}
    for exp in ({"ledger_seq": 12}, {"release": "v0.3.0"}, {"as_of": "2026-12-31"},
                {"until_digest": "sha256:" + "b" * 64, "subject": "repo://src/a.py#f"}):
        assert list(v.iter_errors({**base, "expires": exp})) == [], exp
    assert list(v.iter_errors({**base, "expires": {"at": "2026-12-31T00:00:00Z"}}))
    assert list(v.iter_errors({**base}))  # every suppression expires
