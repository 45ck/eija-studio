"""PO-T5 (external tool adapters: NOT_RUN semantics), PO-X1..X5 (drift between models and code) and file hygiene.

The Alloy runs are integration tests: they need Java and the pinned jar (graph/formal/TOOLS.lock); when either is
missing the test is skipped, which is NOT_RUN and never a pass.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import re
import shutil
import sys
from pathlib import Path

import pytest
from eijaref import closure, suites

from conftest import FORMAL, ROOT

sys.path.insert(0, str(FORMAL))
run_alloy = importlib.import_module("run_alloy")

ALLOY = FORMAL / "alloy"
HAVE_ALLOY = shutil.which("java") is not None and any(j.is_file() for j in run_alloy.DEFAULT_JARS) \
    and run_alloy.sha256_file(next(j for j in run_alloy.DEFAULT_JARS if j.is_file())) == run_alloy.LOCK["sha256"]


# ---- the runner's own contract -------------------------------------------------------------------------------

def test_po_t5_declared_commands_parse_names_kinds_and_expect_clauses() -> None:
    text = "// comment check ignored for 3 expect 1\n/* run hidden for 2 expect 0 */\ncheck a for 5 but 4 Int expect 0\nrun b { some x } for 3 expect 1\nrun for 2\n"
    got = run_alloy.declared_commands(text)
    assert [(c["kind"], c["name"], c["expect"]) for c in got] == [("check", "a", 0), ("run", "b", 1), ("run", None, None)]


def test_po_t5_a_missing_or_wrong_jar_is_not_run_never_pass(tmp_path, monkeypatch) -> None:
    model = tmp_path / "m.als"
    model.write_text("sig A {}\nrun {} for 2 expect 1\n", encoding="utf-8")
    monkeypatch.setenv("EIJA_ALLOY_JAR", str(tmp_path / "absent.jar"))
    assert run_alloy.run(model)["verdict"] == "NOT_RUN"
    fake = tmp_path / "fake.jar"
    fake.write_bytes(b"not alloy")
    monkeypatch.setenv("EIJA_ALLOY_JAR", str(fake))
    r = run_alloy.run(model)
    assert r["verdict"] == "NOT_RUN" and "sha256" in r["reason"]


def test_po_t5_a_model_without_expect_clauses_or_commands_cannot_pass(tmp_path, monkeypatch) -> None:
    if not HAVE_ALLOY:
        pytest.skip("NOT_RUN: java or the pinned Alloy jar is absent")
    monkeypatch.delenv("EIJA_ALLOY_JAR", raising=False)
    bare = tmp_path / "bare.als"
    bare.write_text("sig A {}\nrun {} for 2\n", encoding="utf-8")
    assert run_alloy.run(bare)["verdict"] == "FAIL"
    empty = tmp_path / "empty.als"
    empty.write_text("sig A {}\n", encoding="utf-8")
    assert run_alloy.run(empty)["verdict"] == "FAIL"


@pytest.mark.skipif(not HAVE_ALLOY, reason="NOT_RUN: java or the pinned Alloy jar is absent")
def test_po_t5_a_wrong_expectation_is_fail_and_a_right_one_is_pass(tmp_path) -> None:
    good = tmp_path / "good.als"
    good.write_text("sig A { e: set A }\ncheck refl { all a: A | a in a.*e } for 4 expect 0\nrun { some e } for 3 expect 1\n", encoding="utf-8")
    assert run_alloy.run(good)["verdict"] == "PASS"
    bad = tmp_path / "bad.als"
    bad.write_text("sig A { e: set A }\ncheck sym { all a, b: A | a->b in e implies b->a in e } for 4 expect 0\n", encoding="utf-8")
    r = run_alloy.run(bad)
    assert r["verdict"] == "FAIL" and r["commands"][0]["instance_found"] is True


@pytest.mark.skipif(not HAVE_ALLOY, reason="NOT_RUN: java or the pinned Alloy jar is absent")
def test_po_g2_alloy_rule_pilot_holds() -> None:
    r = run_alloy.run(ALLOY / "rule_uncovered.als")
    assert r["verdict"] == "PASS" and r["sentinel"] == "ALLOY COMMANDS AS EXPECTED 3/3"


@pytest.mark.skipif(not HAVE_ALLOY, reason="NOT_RUN: java or the pinned Alloy jar is absent")
def test_po_g2_alloy_certificate_theorems_hold_within_scope_and_every_mutant_has_a_counterexample() -> None:
    r = run_alloy.run(ALLOY / "certificates.als", timeout=900)
    assert r["verdict"] == "PASS", r
    assert r["sentinel"] == "ALLOY COMMANDS AS EXPECTED 11/11"


# ---- drift between the Alloy models and the Python checkers -----------------------------------------------------

def test_po_x4_alloy_mutant_names_match_the_python_checker_mutants() -> None:
    text = (ALLOY / "certificates.als").read_text(encoding="utf-8")
    alloy_mutants = set(re.findall(r"^assert mutant_no_(\w+)", text, re.M))
    assert alloy_mutants == set(closure.MUTANTS)


def test_po_x4_alloy_conditions_and_python_conditions_carry_the_same_ids() -> None:
    als = (ALLOY / "certificates.als").read_text(encoding="utf-8")
    py = (FORMAL / "eijaref" / "closure.py").read_text(encoding="utf-8")
    for cond in ("a", "b1", "b2", "b3", "c"):
        assert re.search(rf"^pred {cond}\s", als, re.M), cond
    for token in ("a:roots-not-in-C", "b1:parent-edge-missing", "b2:parent-not-in-C", "b3:rank-not-decreasing", "c:not-forward-closed"):
        assert token in py, token
    order_py = (FORMAL / "eijaref" / "order.py").read_text(encoding="utf-8")
    for cond, token in (("s2", '"2:class-not-strongly-connected"'), ("s3", '"3:quotient-has-cycle"')):
        assert re.search(rf"^pred {cond}\s", als, re.M) and token in order_py


def test_po_x1_tools_lock_pins_alloy_by_sha256_and_size() -> None:
    lock = json.loads((FORMAL / "TOOLS.lock").read_text(encoding="utf-8"))
    assert re.fullmatch(r"[0-9a-f]{64}", lock["alloy"]["sha256"]) and lock["alloy"]["size"] == 21062377
    assert lock["alloy"]["release"] == "v6.2.0" and lock["clingo"]["release"] == "5.8.2"


def test_po_x3_the_binding_file_names_a_suite_and_obligations_for_every_entry() -> None:
    b = json.loads((FORMAL / "binding.json").read_text(encoding="utf-8"))["bindings"]
    for name, e in b.items():
        assert hasattr(suites, e["suite"]), name
        assert e["obligations"] and all(re.fullmatch(r"PO-[A-Z]\d+", o) for o in e["obligations"]), name
        assert re.fullmatch(r"[\w.]+:[\w]+", e["target"]), name


@pytest.mark.parametrize("name", sorted(json.loads((FORMAL / "binding.json").read_text(encoding="utf-8"))["bindings"]))
def test_po_x3_production_binding_runs_the_same_law_suite_or_reports_not_run(name) -> None:
    entry = json.loads((FORMAL / "binding.json").read_text(encoding="utf-8"))["bindings"][name]
    module_name, func = entry["target"].split(":")
    try:
        module = importlib.import_module(module_name)
        fn = getattr(module, func)
    except (ImportError, AttributeError):
        pytest.skip(f"NOT_RUN: {entry['target']} does not exist yet")
    if entry["suite"] == "suite_closure":
        assert suites.suite_closure(fn) == []
    elif entry["suite"] == "suite_canon":
        assert suites.suite_canon(fn) == []
    elif entry["suite"] == "suite_link_status":
        assert suites.suite_link_status(fn) == []
    else:
        pytest.skip(f"NOT_RUN: {entry['suite']} needs several bound functions; run by the lane that owns them")


# ---- hygiene of the files this lane owns -----------------------------------------------------------------------

OWNED = [*sorted(FORMAL.rglob("*.py")), *sorted(FORMAL.rglob("*.als")), *sorted(FORMAL.rglob("*.json")), FORMAL / "OBLIGATIONS.md",
         ROOT / "graph" / "bench" / "formal_checks.py", ROOT / "docs" / "weave" / "design" / "formal-verification-of-weave.md",
         ROOT / "docs" / "adr" / "0102-weave-formal-verification-of-weave.md", FORMAL / "TOOLS.lock"]


@pytest.mark.parametrize("path", [p for p in OWNED if p.exists()], ids=lambda p: str(p.relative_to(ROOT)))
def test_hygiene_owned_files_are_utf8_lf_without_bom_or_trailing_spaces(path: Path) -> None:
    data = path.read_bytes()
    assert b"\r" not in data and not data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8")
    assert text.endswith("\n") and not text.endswith("\n\n")
    if path.suffix in {".md"}:
        assert not re.search(r"[ \t]+\n", text.replace("  \n", "\n")), "trailing whitespace"


def test_hygiene_reference_package_is_stdlib_only_and_never_imports_the_production_packages() -> None:
    allowed_third_party = {"clingo"}
    stdlib = set(sys.stdlib_module_names)
    for py in sorted((FORMAL / "eijaref").glob("*.py")):
        for line in py.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*(?:from|import)\s+([A-Za-z_][\w]*)", line)
            if m and not line.strip().startswith("#"):
                top = m.group(1)
                assert top in stdlib or top in allowed_third_party or top == "eijaref" or line.strip().startswith("from ."), (py.name, line)
                assert top not in {"eijagraph", "eija_studio"}, (py.name, line)


def test_hygiene_no_wall_clock_or_randomness_in_the_reference_package() -> None:
    for py in sorted((FORMAL / "eijaref").glob("*.py")):
        text = py.read_text(encoding="utf-8")
        for banned in ("time.time", "datetime", "uuid4", "random.", "os.environ", "os.listdir", "glob("):
            assert banned not in text, (py.name, banned)


def test_hygiene_bench_report_is_byte_identical_between_two_runs_of_a_fast_subset() -> None:
    from conftest import load_bench
    b = load_bench()
    keys = ("F2", "F6", "F7", "F9")
    a = {k: b.CHECKS[k][1]() for k in keys if k != "F2"}
    c = {k: b.CHECKS[k][1]() for k in keys if k != "F2"}
    assert hashlib.sha256(json.dumps(a, sort_keys=True).encode()).hexdigest() == hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()
