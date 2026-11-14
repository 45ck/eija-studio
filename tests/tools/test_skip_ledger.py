"""A skipped test inside a green nox session is NOT_RUN that nox cannot see; the skip ledger makes a new one fail."""
from __future__ import annotations

import json
from collections import Counter

import pytest

from quality.tools import skip_ledger


def _junit(tmp_path, *cases):
    rows = "".join(
        f'<testcase classname="{classname}" name="t{i}">'
        + (f'<skipped type="{kind}" message="{message}"/>' if kind else "") + "</testcase>"
        for i, (classname, kind, message) in enumerate(cases))
    path = tmp_path / "junit.xml"
    path.write_text(f'<?xml version="1.0"?><testsuites><testsuite name="pytest">{rows}</testsuite></testsuites>', encoding="utf-8")
    return path


Z3 = ("tests.test_pack", "pytest.skip", "z3-solver (extra `smt`) is not installed: NOT_RUN")
PROPERTY = ("tests.property.test_receipts", "pytest.skip", "property suite not requested")
TLA = ("tests.test_tla_formal", "pytest.skip", "NOT_RUN: tla2tools.jar is not in .cache/tla")


def test_skips_are_counted_per_file_and_reason_and_xfail_is_not_a_skip(tmp_path):
    path = _junit(tmp_path, PROPERTY, PROPERTY, ("tests.test_pack.TestSomething", "pytest.skip", "x"),
                  ("tests.test_pack", "pytest.xfail", "known"), ("tests.test_pack", None, None))
    assert skip_ledger.skips(path) == Counter({"tests/property/test_receipts.py: property suite not requested": 2,
                                               "tests/test_pack.py: x": 1})


def test_a_skip_the_ledger_does_not_record_fails_the_check(tmp_path, capsys, monkeypatch):
    """The 2026-11-13 case: without the `smt` extra two red tests skipped and every run looked green."""
    ledger = tmp_path / "ledger.json"
    skip_ledger.write(skip_ledger.skips(_junit(tmp_path, TLA)), ledger, {})
    monkeypatch.delenv("EIJA_ALLOW_NOT_RUN", raising=False)
    assert skip_ledger.main([str(_junit(tmp_path, TLA, Z3)), "--ledger", str(ledger)]) == 1
    assert "NEW SKIP: tests/test_pack.py: z3-solver" in capsys.readouterr().out
    monkeypatch.setenv("EIJA_ALLOW_NOT_RUN", "1")  # the accepted-gap escape hatch every NOT_RUN gate has
    assert skip_ledger.main([str(_junit(tmp_path, TLA, Z3)), "--ledger", str(ledger)]) == 0


def test_more_skips_of_a_recorded_reason_fail_and_fewer_pass_with_a_hint(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("EIJA_ALLOW_NOT_RUN", raising=False)
    ledger = tmp_path / "ledger.json"
    key = "tests/test_tla_formal.py: NOT_RUN: tla2tools.jar is not in .cache/tla"
    skip_ledger.write(Counter({key: 2}), ledger, {})
    assert skip_ledger.main([str(_junit(tmp_path, TLA, TLA, TLA)), "--ledger", str(ledger)]) == 1
    assert skip_ledger.main([str(_junit(tmp_path, TLA)), "--ledger", str(ledger)]) == 0
    assert "fewer skips than recorded" in capsys.readouterr().out
    assert skip_ledger.main([str(_junit(tmp_path, TLA)), "--ledger", str(ledger), "--update"]) == 0
    assert json.loads(ledger.read_text(encoding="utf-8"))["skips"] == {key: 1}


def test_a_skip_that_names_the_session_running_the_test_is_routed_not_counted(tmp_path, monkeypatch):
    """A new property test skips in the fast tier because `nox -s property` runs it: that needs no ledger change."""
    monkeypatch.delenv("EIJA_ALLOW_NOT_RUN", raising=False)
    ledger = tmp_path / "ledger.json"
    skip_ledger.write(Counter(), ledger, {"property suite not requested": "nox -s property"})
    assert skip_ledger.main([str(_junit(tmp_path, PROPERTY, PROPERTY, PROPERTY)), "--ledger", str(ledger)]) == 0
    assert skip_ledger.main([str(_junit(tmp_path, PROPERTY, Z3)), "--ledger", str(ledger)]) == 1
    assert json.loads(ledger.read_text(encoding="utf-8"))["routed"] == {"property suite not requested": "nox -s property"}


def test_the_committed_ledger_names_real_files_and_no_skip_that_hides_a_missing_extra():
    assert set(skip_ledger.routed()) == {"property suite not requested", "NOT_RUN: opt-in browser tests"}
    ledger = skip_ledger.load()
    for key in ledger:
        assert (skip_ledger.ROOT / key.split(": ", 1)[0]).is_file(), key
    # Extras every gate environment installs are never an accepted reason to skip.
    for extra in ("z3", "smt", "setuptools", "pyshacl", "pydot", "hypothesis", "networkx", "clingo", "rfc8785", "python-statemachine"):
        assert not [key for key in ledger if extra in key.split(": ", 1)[1]], extra


def test_a_ledger_of_another_schema_is_refused(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text('{"schema": "other", "skips": {}}', encoding="utf-8")
    with pytest.raises(SystemExit):
        skip_ledger.load(path)
