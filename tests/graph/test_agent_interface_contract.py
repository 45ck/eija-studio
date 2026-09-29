"""Machine checks for graph/schema/mcp-tools.md (the weave agent tool contract).

The contract is a document, so the document is the thing under test: every schema block must be valid
JSON Schema 2020-12, every example must validate against the schema it claims, the node and edge enums
must equal graph/schema/metamodel.json (the maintained source, not the earlier brief), the tool index must equal the tool blocks, and no owner-only operation may be
a tool name. Missing optional prerequisites (jsonschema, the kernel) skip, which is the pytest spelling of
NOT_RUN; a skip is never a pass.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "graph" / "schema" / "mcp-tools.md"
METAMODEL = ROOT / "graph" / "schema" / "metamodel.json"

jsonschema = pytest.importorskip("jsonschema")

BLOCK = re.compile(r"<!--\s*(schema|example):\s*([\w.\-]+)\s*-->\s*```json\n(.*?)\n```", re.S)

#: Copy of the agents lane's OWNER_ONLY_OPERATIONS (interfaces/mcp_server.py, ADR-0041) plus weave additions.
OWNER_ONLY = {"select", "select_meaning", "edit", "layout", "approve", "apply", "discard", "save", "reset_preview",
              "execute", "export", "ledger_append", "ack", "clear_suspect", "approve_statement", "pin_statement",
              "edit_policy", "edit_schema", "disable_rule", "add_suppression", "grow_baseline",
              "edit_checker_registry", "mint_receipt", "assess_override", "set_status", "grant_consent",
              "set_egress", "read_key", "read_launch_token", "graph_query", "run_generator", "run_tool"}


@pytest.fixture(scope="module")
def blocks() -> dict[tuple[str, str], object]:
    text = DOC.read_text(encoding="utf-8")
    assert "\r" not in text, "LF line endings required"
    found = {}
    for kind, name, body in BLOCK.findall(text):
        assert (kind, name) not in found, f"duplicate block {kind}:{name}"
        found[(kind, name)] = json.loads(body)
    return found


@pytest.fixture(scope="module")
def defs(blocks) -> dict:
    return blocks[("schema", "common")]["$defs"]


def tools(blocks) -> list[str]:
    return sorted(n.rsplit(".", 1)[0] for k, n in blocks if k == "schema" and n.endswith(".input"))


def input_schema(blocks, defs, tool: str) -> dict:
    return {"$defs": defs, **blocks[("schema", f"{tool}.input")]}


def output_schema(blocks, defs, tool: str) -> dict:
    result = blocks[("schema", f"{tool}.result")]
    return {"$defs": defs, "allOf": [{"$ref": "#/$defs/Envelope"},
                                     {"properties": {"result": {"anyOf": [{"type": "null"}, result]}}}]}


def test_every_schema_block_is_valid_json_schema(blocks, defs) -> None:
    validator = jsonschema.Draft202012Validator
    validator.check_schema(blocks[("schema", "common")])
    for tool in tools(blocks):
        validator.check_schema(input_schema(blocks, defs, tool))
        validator.check_schema(output_schema(blocks, defs, tool))
    for name in ("run.header", "run.event"):
        validator.check_schema(blocks[("schema", name)])


def test_every_tool_has_input_and_result_and_a_valid_name(blocks) -> None:
    names = tools(blocks)
    assert len(names) == 20
    for tool in names:
        assert ("schema", f"{tool}.result") in blocks, tool
        assert re.fullmatch(r"[a-z][a-z0-9_]{0,63}", tool), tool
    assert not (set(names) & OWNER_ONLY)


def test_examples_validate_against_their_schemas(blocks, defs) -> None:
    checked = 0
    for (kind, name), instance in blocks.items():
        if kind != "example":
            continue
        if name.endswith(".request"):
            schema = input_schema(blocks, defs, name.split(".")[0])
        else:
            schema = output_schema(blocks, defs, instance["tool"])
        jsonschema.Draft202012Validator(schema).validate(instance)
        checked += 1
    assert checked >= 7


def test_negative_examples_are_rejected(blocks, defs) -> None:
    good = blocks[("example", "graph_impact.response")]
    validator = jsonschema.Draft202012Validator(output_schema(blocks, defs, "graph_impact"))
    assert validator.is_valid(good)
    bad_hash = json.loads(json.dumps(good))
    bad_hash["snapshot"]["graph_root"] = "not-hex"
    both = json.loads(json.dumps(good))
    both["error"] = blocks[("example", "error.unknown_node")]["error"]
    float_cost = json.loads(json.dumps(good))
    float_cost["bounds"]["cost_units"] = 1.5
    extra = json.loads(json.dumps(good))
    extra["generated_at"] = "2026-09-29T00:00:00Z"
    for bad in (bad_hash, both, float_cost, extra):
        assert not validator.is_valid(bad)


def test_enums_and_node_id_pattern_equal_the_metamodel(defs) -> None:
    if not METAMODEL.is_file():
        pytest.skip("NOT_RUN: graph/schema/metamodel.json not present")
    meta = json.loads(METAMODEL.read_text(encoding="utf-8"))
    assert defs["NodeType"]["enum"] == sorted(meta["node_types"])
    assert defs["EdgeType"]["enum"] == sorted(meta["link_types"])
    assert defs["Origin"]["enum"] == meta["classes"]
    assert defs["ExtractorLabel"]["enum"] == meta["provenance"]
    scheme = meta["id_scheme"]
    seg = scheme["fragment_segment"]
    assert defs["NodeId"]["pattern"] == "^repo://" + scheme["path"] + "(#" + seg + "(/" + seg + ")*)?$"
    assert defs["Digest"]["pattern"] == "^sha256:[0-9a-f]{64}$"
    assert meta["id_scheme"]["digest"] == "sha256:<64 lowercase hex>"


def test_status_enums_equal_the_brief(defs) -> None:
    brief = json.loads((ROOT / "graph" / "brief.json").read_text(encoding="utf-8"))
    assert defs["LinkStatus"]["enum"] == brief["link_status"]["values"]
    assert defs["EvidenceStatus"]["enum"] == brief["evidence_status"]["values"]


def test_index_equals_tool_blocks_and_tier_sizes(blocks) -> None:
    text = DOC.read_text(encoding="utf-8")
    table = text.split("<!-- index -->")[1].split("<!-- /index -->")[0]
    rows = [re.findall(r"^\| `([a-z_]+)` \| (core|extended) \| ([RDP]) \|", line) for line in table.splitlines()]
    rows = [r[0] for r in rows if r]
    assert sorted(n for n, _, _ in rows) == tools(blocks)
    assert sum(t == "core" for _, t, _ in rows) == 10
    assert sum(t == "extended" for _, t, _ in rows) == 10
    assert {n for n, _, c in rows if c == "P"} == {"proposal_submit"}
    assert {n for n, _, c in rows if c == "D"} == {"edit_preview", "txn_dry_run", "codemod_plan"}


def test_every_input_forbids_extra_properties_and_has_no_trusted_status_field(blocks) -> None:
    forbidden = {"status", "verdict", "digest", "consent", "approved", "sha256", "token", "key"}
    for tool in tools(blocks):
        schema = blocks[("schema", f"{tool}.input")]
        assert schema.get("additionalProperties") is False, tool
        assert not (set(schema.get("properties", {})) & forbidden), tool


def test_transaction_schema_matches_kernel(blocks) -> None:
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from eija_studio.domain.models import SemanticTransaction
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"NOT_RUN: kernel not importable ({exc})")
    kernel = SemanticTransaction.model_json_schema()
    ours = blocks[("schema", "txn_dry_run.input")]["properties"]["transaction"]
    assert ours["properties"]["kind"]["enum"] == kernel["properties"]["kind"]["enum"]
    assert ours["properties"]["rejection_source"]["enum"] == kernel["properties"]["rejection_source"]["enum"]
    assert ours["properties"]["rejection_source"]["default"] == kernel["properties"]["rejection_source"]["default"]
    assert ours["required"] == kernel["required"]
    assert ours["additionalProperties"] is False and kernel["additionalProperties"] is False


def test_real_kernel_hashes_in_the_dry_run_examples(blocks) -> None:
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from eija_studio.domain.impact import model_impact
        from eija_studio.domain.models import SemanticTransaction
        from eija_studio.domain.policy import apply_transaction, baseline
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"NOT_RUN: kernel not importable ({exc})")
    base = baseline()
    cand = apply_transaction(base, SemanticTransaction(kind="enable_recommendation"))
    impact = model_impact(base, cand)
    ok = blocks[("example", "txn_dry_run.response")]["result"]
    assert ok["base_semantic_hash"] == base.semantic_hash
    assert ok["candidate_semantic_hash"] == cand.semantic_hash
    assert ok["model_delta"]["changed_actions"] == impact["changed_actions"]
    assert ok["kernel_impact"]["affected"] == impact["affected"]
    assert ok["kernel_impact"]["envelope"] == impact["envelope"]
    rejected = blocks[("example", "txn_dry_run.rejected")]["result"]
    assert rejected["base_semantic_hash"] == base.semantic_hash
    assert rejected["kernel_code"] == "MEANING_REQUIRED"


def test_document_states_the_honest_limits() -> None:
    text = DOC.read_text(encoding="utf-8")
    for needle in ("PREDICTION of a real change", "not every real-world consequence", "NOT_RUN on POSIX",
                   "Owner-only operations are absent, not denied"):
        assert needle in text
