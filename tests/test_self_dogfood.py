"""EIJA first: source observations and the synthetic reference model stay separate."""
from __future__ import annotations

from pathlib import Path

import eija_studio
import pytest
from eija_studio.adapters.self_facts import SOURCE_SYMBOLS, analyze_eija_source_files, source_profile
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import AGENT, OWNER, DomainError
from eija_studio.domain.pack import Pack, load_pack
from eija_studio.domain.policy import apply_transactions, check_policy
from eija_studio.domain.transactions import parse_transaction
from eija_studio.weave.codelink import AST_SYMBOL, digest, parse_uri, resolves
from kernel_support import harness_identity

ROOT = Path(eija_studio.__file__).resolve().parents[2]
PACK = Path(__file__).resolve().parents[1] / "packs/eija-review-slice"
SERVICE = "src/eija_studio/application/service.py"


@pytest.fixture
def source_files():
    return {path: (ROOT / path).read_bytes() for path in SOURCE_SYMBOLS}


def symbol(report, name):
    return next(item for item in report["symbols"] if item["ref"].endswith("#" + name))


def test_source_facts_are_deterministic_and_preserve_unknown_conformance(source_files):
    first = analyze_eija_source_files(source_files)
    assert first == analyze_eija_source_files(dict(reversed(list(source_files.items()))))
    assert first["extraction"]["status"] == "EXTRACTED"
    assert first["extraction"]["executes_target"] is False
    assert first["conformance"]["status"] == "NOT_RUN"
    assert first["declared_model"]["status"] == "UNBOUND"
    assert first["declared_model"]["pack_id"] is None
    require = symbol(first, "Studio.approve")
    assert require["ast_sha256"] == digest(ROOT, parse_uri(require["ref"]), AST_SYMBOL)
    assert any(fact["value"] == "principal.require('approve')" for fact in require["facts"])
    assert any(fact["kind"] == "unmodeled_predicate" for fact in require["facts"])
    assert all(item["line"] >= 1 and len(item["ast_sha256"]) == 64 for item in first["symbols"])
    names = symbol(first, "AGENT_TOOLS")["literal_names"]
    excluded = symbol(first, "OWNER_ONLY_OPERATIONS")["literal_names"]
    assert {"propose", "verify", "render"} <= set(names)
    assert not set(names) & set(excluded)


def test_missing_symbol_and_missing_file_are_visible_gaps(source_files):
    source_files[SERVICE] = source_files[SERVICE].replace(b"def approve(", b"def missing_approve(")
    del source_files["src/eija_studio/application/compiler.py"]
    report = analyze_eija_source_files(source_files)
    assert report["extraction"]["status"] == "PARTIAL"
    assert {item["reason"] for item in report["gaps"]} == {"SOURCE_NOT_IN_SNAPSHOT", "SYMBOL_MISSING"}
    assert symbol(report, "Studio.approve")["status"] == "UNRESOLVED"
    assert report["conformance"]["status"] == "NOT_RUN"


def test_changed_authority_gate_invalidates_source_and_symbol_identity(source_files):
    before = analyze_eija_source_files(source_files)
    source_files[SERVICE] = source_files[SERVICE].replace(
        b'principal.require("approve")', b'principal.require("view")',
    )
    after = analyze_eija_source_files(source_files)
    assert before["source_digest"] != after["source_digest"]
    assert symbol(before, "Studio.approve")["ast_sha256"] != symbol(after, "Studio.approve")["ast_sha256"]
    assert any(fact["value"] == "principal.require('view')" for fact in symbol(after, "Studio.approve")["facts"])
    assert after["conformance"]["status"] == "NOT_RUN"


def test_source_is_parsed_without_execution_and_formatting_is_distinguished(source_files):
    before = analyze_eija_source_files(source_files)
    source_files[SERVICE] += b'\nraise RuntimeError("must never execute target")\n'
    after = analyze_eija_source_files(source_files)
    assert after["extraction"]["status"] == "EXTRACTED"
    assert before["source_digest"] != after["source_digest"]
    assert symbol(before, "Studio.approve")["ast_sha256"] == symbol(after, "Studio.approve")["ast_sha256"]


def test_unparseable_and_dynamic_tool_declarations_never_report_complete(source_files):
    source_files[SERVICE] = b"broken syntax:"
    source_files["src/eija_studio/interfaces/mcp_server.py"] = (
        b"AGENT_TOOLS = build_tools()\nOWNER_ONLY_OPERATIONS = ('apply',)\n"
    )
    report = analyze_eija_source_files(source_files)
    assert report["extraction"]["status"] == "PARTIAL"
    assert {item["reason"] for item in report["gaps"]} == {
        "SOURCE_UNPARSEABLE", "NON_LITERAL_TOOL_DECLARATION",
    }


def test_declared_reference_pack_has_resolving_source_bindings_and_rejects_agent_approval():
    pack = load_pack(PACK)
    assert check_policy(pack.model, pack) == []
    assert all(resolves(ROOT, parse_uri(binding)) for term in pack.language.terms for binding in term.binds)
    meaning = pack.meaning("show_saved_path")
    assert meaning is not None
    candidate = apply_transactions(pack.model, meaning.transactions, pack)
    assert "SAVED" in candidate.states
    assert check_policy(candidate, pack) == []
    bad = parse_transaction({"kind": "set_role", "transition": "TR-APPROVE", "role": "Agent"})
    with pytest.raises(DomainError) as caught:
        apply_transactions(candidate, (bad,), pack)
    assert "REFERENCE_AUTHORITY:Approve" in caught.value.message


def test_self_reference_flow_keeps_real_agent_authority_boundary(tmp_path):
    pack = load_pack(PACK)
    studio = build_studio(tmp_path / "synthetic-self-workspace", pack=pack)
    studio.identity_provider = lambda: harness_identity(pack)
    case = studio.create(pack.fixtures.demo_request)
    case = studio.propose(case["id"], case["version"])
    with pytest.raises(DomainError, match="Capability required"):
        studio.select(case["id"], case["version"], "show_saved_path", AGENT)
    case = studio.select(case["id"], case["version"], "show_saved_path", OWNER)
    case = studio.verify(case["id"], case["version"])
    packet = studio.view(case["id"])["packet"]
    assert packet["technical_claims"]["runtime_matrix"] == "PASS"
    assert packet["human_understanding"] == "UNKNOWN"
    with pytest.raises(DomainError, match="Capability required"):
        studio.approve(case["id"], case["version"], packet["subject_hash"], {}, True, AGENT)
    with pytest.raises(DomainError, match="Capability required"):
        studio.apply(case["id"], case["version"], AGENT)
    with studio.store.transaction() as unit:
        assert unit.active()["version"] == 0



def test_source_profile_follows_bound_selectors_and_reports_the_actual_pack(source_files):
    pack = load_pack(PACK)
    reader = source_profile(pack)
    assert reader is not None
    observed = reader(source_files)
    assert observed["declared_model"]["pack_id"] == pack.id
    assert observed["declared_model"]["pack_digest"] == pack.digest
    assert observed["declared_model"]["status"] == "DECLARED_REFERENCE_JOURNEY"
    assert observed["conformance"]["status"] == "NOT_RUN"
    data = pack.model_dump(mode="json")
    data["pack"]["id"] = data["model"]["id"] = "alternate-review-reference"
    renamed = Pack.model_validate(data)
    reader = source_profile(renamed)
    assert reader is not None
    assert reader(source_files)["declared_model"]["pack_id"] == renamed.id


def test_source_profile_rejects_unrelated_or_incomplete_bindings():
    generic = load_pack(PACK.parent / "library-loan")
    assert source_profile(generic) is None
    data = load_pack(PACK).model_dump(mode="json")
    data["language"]["terms"] = []
    assert source_profile(Pack.model_validate(data)) is None


def test_bootstrap_composes_source_facts_only_for_a_supported_profile(tmp_path):
    supported = build_studio(tmp_path / "supported-workspace", pack=load_pack(PACK), repository_root=tmp_path)
    assert supported.repository is not None
    supported_facts = supported.repository._observed_facts({})
    assert supported_facts["extraction"]["status"] == "PARTIAL"
    assert supported_facts["declared_model"]["pack_id"] == load_pack(PACK).id
    generic = load_pack(PACK.parent / "library-loan")
    unsupported = build_studio(tmp_path / "generic-workspace", pack=generic, repository_root=tmp_path)
    assert unsupported.repository is not None
    assert unsupported.repository._observed_facts({})["extraction"]["status"] == "NOT_RUN"
