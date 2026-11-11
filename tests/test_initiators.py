"""Who may start a record (ADR-0231, issue #142).

A workflow may name its initiators. Empty (the default) keeps today's meaning, any active actor, and keeps every
existing model's bytes and hashes. When named, the runtime refuses anyone else with ROLE_CANNOT_START, the generated
app's conformance oracle checks it, and an undeclared role is a policy code.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application.appgen import generate, start_cases
from eija_studio.application.runtime import initialise
from eija_studio.application.simulation import simulate
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import check_policy
from eija_studio.interfaces.app_build import conformance
from eija_studio.interfaces.cli import main

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")


def with_initiators(model: Workflow, *roles: str) -> Workflow:
    return Workflow.model_validate(model.model_dump(mode="json") | {"initiators": list(roles)})


class _Session:
    def __init__(self):
        self.rows = []

    def create_instance(self, item):
        self.rows.append(item)


def test_a_model_without_initiators_keeps_its_bytes_and_hash():
    for pack_dir in sorted(p for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file()):
        raw = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))["model"]
        model = Workflow.model_validate(raw)
        assert "initiators" not in model.model_dump(mode="json"), pack_dir.name
        assert model.model_dump(mode="json") == Workflow.model_validate(raw).model_dump(mode="json")


def test_naming_initiators_changes_the_hash_and_round_trips():
    named = with_initiators(LOAN.model, "Member")
    assert named.semantic_hash != LOAN.model.semantic_hash
    assert Workflow.model_validate(named.model_dump(mode="json")) == named


def test_duplicate_initiators_are_invalid_and_an_undeclared_role_is_a_policy_code():
    with pytest.raises(ValueError):
        with_initiators(LOAN.model, "Member", "Member")
    assert "UNDECLARED_INITIATOR:Ghost" in check_policy(with_initiators(LOAN.model, "Ghost"), LOAN)
    assert not any(c.startswith("UNDECLARED_INITIATOR") for c in check_policy(with_initiators(LOAN.model, "Member"), LOAN))


def test_the_runtime_refuses_a_creator_outside_the_initiators():
    named = with_initiators(LOAN.model, "Member")
    session = _Session()
    assert initialise(session, "c", named, pack=LOAN, role="Member")["state"] == named.initial_state
    with pytest.raises(DomainError) as e:
        initialise(session, "c", named, pack=LOAN, role="Clerk")
    assert e.value.code == "ROLE_CANNOT_START" and e.value.details["refs"] == ["role:Member"]
    assert len(session.rows) == 1  # the refused start wrote nothing
    # An open model, and kernel-side starts with no creator role, are unchanged.
    assert initialise(_Session(), "c", LOAN.model, pack=LOAN, role="Clerk")
    assert initialise(_Session(), "c", named, pack=LOAN)


def test_the_oracle_lists_each_active_actor_only_when_initiators_are_named():
    assert start_cases(LOAN, LOAN.model) == []
    cases = {c["actor"]: c["expect"] for c in start_cases(LOAN, with_initiators(LOAN.model, "Member"))}
    assert cases["member-a"] == {"outcome": "CREATED"}
    assert cases["clerk"] == {"outcome": "REFUSED", "code": "ROLE_CANNOT_START"}
    assert "librarian-revoked" not in cases
    files, _ = generate(LOAN, LOAN.model)
    assert "start_cases" not in json.loads(files["tests/oracle.json"])


def _named_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "library-loan"
    shutil.copytree(ROOT / "packs" / "library-loan", pack_dir)
    doc = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    doc["model"]["initiators"] = ["Member"]
    (pack_dir / "pack.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    return pack_dir


def test_a_built_app_refuses_a_start_by_another_role_and_conformance_catches_an_app_that_does_not(tmp_path):
    pack_dir, out = _named_pack(tmp_path), tmp_path / "app"
    assert main(["build", "--pack", str(pack_dir), "--out", str(out)]) == 0
    manifest = json.loads((out / "BUILD.json").read_text(encoding="utf-8"))
    assert manifest["conformance"]["status"] == "PASS", manifest["conformance"]
    assert json.loads((out / "tests" / "oracle.json").read_text(encoding="utf-8"))["start_cases"]
    service = out / "app" / "service.py"
    text = service.read_text(encoding="utf-8")
    assert ', role=actor["role"])' in text
    service.write_text(text.replace(', role=actor["role"])', ")"), encoding="utf-8")  # negative control
    assert conformance(out)["status"] == "FAIL"


def test_a_simulated_crowd_only_starts_records_as_the_initiators():
    named = with_initiators(LOAN.model, "Member")
    run = simulate(LOAN, named, seed=3, steps=200)
    starters = {entry["role"] for entry in run["trace"] if entry["outcome"] == "CREATED"}
    assert starters == {"Member"}
    assert simulate(LOAN, LOAN.model, seed=3, steps=200) == simulate(LOAN, LOAN.model, seed=3, steps=200)


def test_the_order_initiators_are_named_in_is_not_semantic():
    assert with_initiators(LOAN.model, "Member", "Clerk").semantic_hash == with_initiators(LOAN.model, "Clerk", "Member").semantic_hash
