"""The CLI surface: ``eija index | lint [--sarif] | impact``. Exit codes are 0 PASS, 1 FAIL, 2 NOT_RUN (or an error).

Dogfood: both real packs are linted against THIS repository (measured, not a fixture): no findings.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from weave_support import PACKS, ROOT, bound_term, read_pack, write_repo

from eija_studio.interfaces.cli import main
from eija_studio.weave.sarif import sarif_profile_problems


def run(capsys, *argv: str) -> tuple[int, str]:
    code = main(list(argv))
    return code, capsys.readouterr().out


def args(root: Path, pack_file: Path, *extra: str) -> list[str]:
    return [*extra, "--root", str(root), "--pack", str(pack_file)]


def test_lint_exit_codes_pass_fail_and_not_run(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.delenv("EIJA_ALLOW_NOT_RUN", raising=False)
    root, pack_file = write_repo(tmp_path / "ok", "excursion")
    code, out = run(capsys, "lint", *args(root, pack_file))
    assert code == 2 and json.loads(out)["verdicts"]["WV-005"] == "NOT_RUN"  # no baseline: NOT_RUN, never PASS
    monkeypatch.setenv("EIJA_ALLOW_NOT_RUN", "1")
    assert run(capsys, "lint", *args(root, pack_file))[0] == 0
    monkeypatch.delenv("EIJA_ALLOW_NOT_RUN")
    code, out = run(capsys, "index", *args(root, pack_file, "--write-baseline"))
    assert code == 0 and json.loads(out)["baseline"]["bindings"] >= 3
    assert run(capsys, "lint", *args(root, pack_file))[0] == 0  # the baseline is found at ROOT/.eija/weave-baseline.json
    doc = read_pack("excursion")
    bound_term(doc)["binds"].append("repo://src/missing.py#ghost")
    bad_root, bad_file = write_repo(tmp_path / "bad", "excursion", doc)
    assert run(capsys, "lint", *args(bad_root, bad_file))[0] == 1


def test_lint_sarif_and_impact_and_index_output(tmp_path: Path, capsys) -> None:
    root, pack_file = write_repo(tmp_path, "library-loan")
    code, out = run(capsys, "lint", *args(root, pack_file, "--sarif"))
    sarif = json.loads(out)
    assert code == 2 and sarif["version"] == "2.1.0" and sarif_profile_problems(sarif) == []
    code, out = run(capsys, "impact", *args(root, pack_file), "state:OnLoan")
    report = json.loads(out)
    assert code == 0 and report["certificate"] == "accepted" and report["count"] > 0
    code, out = run(capsys, "index", *args(root, pack_file))
    assert code == 0 and json.loads(out)["root_hash"].startswith("sha256:")
    assert run(capsys, "impact", *args(root, pack_file), "state:Nope")[0] == 2  # unknown target: an error, not an empty result


def test_a_broken_pack_is_diagnostics_not_a_crash(tmp_path: Path, capsys) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    pack_file.write_text("{not json", encoding="utf-8")
    code, out = run(capsys, "lint", *args(root, pack_file))
    assert code == 2 and json.loads(out)["error"] == "PACK_INVALID"


@pytest.mark.parametrize("name", PACKS)
def test_dogfood_this_repository_through_each_real_pack_has_no_findings(capsys, monkeypatch, name: str) -> None:
    monkeypatch.setenv("EIJA_ALLOW_NOT_RUN", "1")
    code, out = run(capsys, "lint", "--root", str(ROOT), "--pack", str(ROOT / "packs" / name))
    result = json.loads(out)
    assert code == 0 and result["findings"] == [] and result["extraction_gaps"] == []
    assert {r: v for r, v in result["verdicts"].items() if v != "PASS"} == {"WV-005": "NOT_RUN"}
