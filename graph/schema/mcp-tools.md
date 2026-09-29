# Weave agent tool contract (`eija.weave.mcp.v1`)

Lane: weave. Date: 2026-09-29. Status: DESIGN (a contract, not code). Owner of this file: weave; owner of the server that serves it: agents lane (ADR-0041). Rationale, evidence and the evaluation design: [docs/weave/design/agent-interface-and-context-packs.md](../../docs/weave/design/agent-interface-and-context-packs.md) and [ADR-0099](../../docs/adr/0099-weave-agent-interface.md). Graph vocabulary: [docs/weave/ARCHITECTURE.md](../../docs/weave/ARCHITECTURE.md) and the maintained metamodel [graph/schema/metamodel.json](metamodel.json) (node types, link kinds, id scheme, digest format); the earlier summary [graph/brief.json](../brief.json) is superseded where they differ. Ranking, selection, impact, test selection and risk are the impact-ranking aspect's ([design](../../docs/weave/design/impact-ranking-and-confidence.md)); this contract only carries their results. Hashing follows the identity aspect ([identity-vectors.json](identity-vectors.json)).

This file is machine-checked. `tests/graph/test_agent_interface_contract.py` extracts every block preceded by a `<!-- schema: NAME -->` or `<!-- example: NAME -->` marker, checks that each schema is valid JSON Schema (draft 2020-12), that each example validates against its schema, that the node, edge, origin and provenance enums and the node-id pattern equal `graph/schema/metamodel.json`, that the tool index equals the tool blocks, and that no owner-only operation name is a tool.

Protocol basis (both pages opened 2026-09-29): MCP 2025-11-25 and 2026-07-28 `server/tools`. Facts used from them: `outputSchema` is optional and, when given, servers MUST return conforming structured results and clients SHOULD validate; a tool returning structured content SHOULD also return the serialized JSON in a TextContent block; tool annotations are untrusted unless the server is trusted; tool execution errors use `isError: true` and clients SHOULD show them to the model; servers MUST validate inputs, rate limit, sanitize outputs and implement access controls. The 2026-07-28 page adds: no protocol-level session (state is carried by explicit handles), and the tool list MUST NOT vary per connection and SHOULD be in a deterministic order. This contract needs only the intersection of both revisions. The MCP SDK version and negotiated protocol version are the agents lane's to pin and record (`header.client`).

## 1. Normative rules

| # | Rule | Why (evidence or design rule) |
|---|---|---|
| C-01 | Every tool result is one JSON object, the **envelope** (section 3). `structuredContent` is that object. The single `TextContent` block is its RFC 8785 subset serialisation, not a prose summary. | MCP SHOULD-serialise rule; byte-identical replay (D-02) |
| C-02 | The envelope carries `snapshot.graph_root`, `request_hash` and `response_hash`. Hashes use the identity aspect's convention `dhash(tag, value) = "sha256:" + SHA-256(ASCII tag, NUL, RFC 8785 bytes of value)`: `request_hash = dhash("eija.weave.mcp-request.v1", {tool, arguments (normalised), graph_root})` and `response_hash = dhash("eija.weave.mcp-response.v1", envelope without response_hash)`. The JSON value is self-delimiting, so no field-concatenation collision is possible (D-12). | Replay verification (section 7); D-12; identity-vectors.json |
| C-03 | Same (`graph_root`, tool, normalised arguments) gives byte-identical `structuredContent`. No wall clock, time zone, uuid, random, host name, absolute path, process id or environment value appears in any result. | D-04, D-05, D-07 |
| C-04 | Arguments are normalised before `request_hash`: arrays marked `"x-eija-set": true` are sorted (code-point order) and de-duplicated; omitted optional arguments are replaced by their schema defaults; `at` `WORKTREE` and `HEAD` are resolved to a `graph_root` and the resolved value is part of the hash. | Cache keys and replay; MCP 2026-07-28 statelessness |
| C-05 | Lists in results are sorted by a total key stated per tool. No result depends on hash-map or set iteration order. | D-01, D-07, D-09 |
| C-06 | Numbers are integers in the safe range (no floats). Ratios are integers in parts per million (`score_ppm`) or a pair of integers. | D-02, D-10 |
| C-07 | Sizes are counted in **cost units** = number of UTF-8 bytes of the RFC 8785 subset serialisation of the item being counted. No tokenizer is used because tokenizers are model-specific and change; the byte-to-token ratio is measured per model by the evaluation, not assumed. | Determinism; PREDICTION that bytes track tokens monotonically |
| C-08 | Every list tool is bounded. Defaults and caps are in section 2. A result that omits anything says so: `bounds.complete = false`, `bounds.truncated_by`, `bounds.frontier` (at most 50 ids) and `bounds.frontier_count`. Nothing is dropped silently. | Kernel `impact.closure` returns `complete` and `frontier` |
| C-09 | Cursors are stateless keyset cursors: the last sort key plus `graph_root` plus `request_hash` of the request without the cursor, in an opaque string. A cursor from another root gives `STALE_SNAPSHOT`. | No server session in MCP 2026-07-28 |
| C-10 | Errors are results with `isError: true`, `error` set and `result` null. Each error has a stable `code`, a `message_id`, integer/string `args` and up to five machine-actionable `next` calls. No traceback, no free-form advice. | MCP error rules; Anthropic tool-writing guidance (actionable errors) |
| C-11 | Free text that originates in a repository file (source slices, OKF page prose, comments, term definitions) appears only inside a `Text` object `{origin, untrusted: true, content}`. Nothing in a `Text` object is an instruction to the agent. | MCP "sanitize tool outputs"; indirect prompt injection is out of protocol scope |
| C-12 | The tool set is fixed at server start by the owner (`--graph-tools` set to `core` or `extended`) and never varies per connection or per call. Tools are listed in ascending name order. | MCP 2026-07-28 tools rules |
| C-13 | No tool takes consent, credentials, a status to trust, a digest to trust, or a path outside the repository. Digests, statuses and verdicts in a request are ignored or rejected; the checker recomputes them. | AGENTS.md; `assess_receipt` ignores a supplied status |
| C-14 | Owner-only operations are absent, not denied (section 9). Requests for them are protocol errors (unknown tool), not `OWNER_ONLY` results. | ADR-0041 (absence is stronger than denial and testable) |
| C-15 | Rate limiting is a per-run call quota (`--graph-quota`), counted in the run log, not a time-based limiter. Exceeding it gives `QUOTA_EXCEEDED` deterministically. | MCP "rate limit" MUST vs D-04 (no wall clock) |
| C-16 | Before sending, the server validates its own result against the tool's `outputSchema` and fails closed with `INTERNAL_SCHEMA_VIOLATION` (no partial data). | MCP: servers MUST conform |
| C-17 | Every tool description and schema is part of `tool_list_sha256`. Changing any of them changes the hash, fails the golden test and needs an ADR amendment. | ADR-0041: adding a tool name is a governance decision; descriptions are prompt content |
| C-18 | A missing prerequisite (extractor, tool, grammar, Chrome) is reported in `snapshot.not_run` and as `NOT_RUN`; it is never omitted and never PASS. `verdict` folds with NOT_RUN absorbing PASS. | AGENTS.md; D-15 |

## 2. Tool index

Class: `R` read-only query, `D` dry run (computes on an in-memory overlay, writes nothing), `P` proposal (writes one inert, content-addressed proposal record). Annotations are hints (untrusted by clients): all tools are `openWorldHint=false`; `R` and `D` are `readOnlyHint=true, destructiveHint=false, idempotentHint=true`; `P` is `readOnlyHint=false, destructiveHint=false, idempotentHint=true`. Default response cap 16384 cost units, hard cap 65536.

<!-- index -->
| Tool | Tier | Class | Purpose | Sort key of list results | Backing |
|---|---|---|---|---|---|
| `graph_status` | core | R | Snapshot descriptor, counts, verdict, NOT_RUN list, contract hashes | fixed keys | `eijagraph.store`, manifest |
| `graph_node` | core | R | One node: type, content hash, provenance, degree, findings count, optional source slice | edge type, then id | `eijagraph.store` |
| `graph_search` | core | R | Deterministic lexical lookup of nodes by id, path prefix, registered term form or name token | (match kind rank, id) | `eijagraph.store`, term registry |
| `graph_neighbors` | core | R | Typed edges of a node, filtered by edge type, direction, soundness class | (edge type, direction, other id) | `eijagraph.store` |
| `graph_impact` | core | R | Tiered closure with distance, relevance score and witness (the impact-ranking aspect's `eija.weave.impact.v1`), with `complete` and `frontier` in `bounds` | (tier, -score_ppm, distance, id) | `eijagraph.store`, `eijagraph.rank` (reference: kernel `impact.closure`) |
| `diagnostics_get` | core | R | Findings for a scope, optionally as a delta against an earlier root | (level rank, rule id, fingerprint) | `eijagraph.rules` |
| `context_pack` | core | R | Budgeted, ranked, hash-carrying slice of the graph for a task | pack order (design doc section 5) | `eijagraph.pack` |
| `edit_preview` | core | D | Apply an EditSet to an overlay: preconditions, findings delta, links that become SUSPECT, ripple | (level rank, rule id, fingerprint) | `eijagraph.overlay`, `eijagraph.editset` |
| `txn_dry_run` | core | D | Kernel semantic transaction on a base model: verdict, model delta, kernel impact, graph ripple | id | adapter (kernel domain functions) + `eijagraph.overlay` |
| `proposal_submit` | core | P | Submit a link, ack request, witness or rename record to the trusted checker | fixed keys | `eijagraph.proposals` |
| `graph_why` | extended | R | Derivation or witness for a reach, edge, finding or link | path order | `eijagraph.rules` |
| `select_tests` | extended | R | Weighted-set-cover choice of tests that observe each impacted obligation; obligations no test observes | (test id) | `eijagraph.rank` (impact-ranking aspect, section 7 there) |
| `change_risk` | extended | R | Change-risk vector of exact counts and its review-order key (no scalar score) | fixed keys | `eijagraph.rank` (section 9 there) |
| `link_status` | extended | R | Links with recomputed status and lifted evidence status | (link id) | `eijagraph.links` |
| `diagnostics_explain` | extended | R | Long-form explanation and remedy kinds for a rule | fixed keys | rule metadata |
| `language_lookup` | extended | R | Term entries per bounded context, bindings, ambiguity | (context, preferred name) | `eijagraph.language` |
| `evidence_get` | extended | R | Claim, label, trusted computing base, bounds, assumptions, recomputed status | claim id | `eijagraph.assure` |
| `pack_verify` | extended | R | Which items of a held pack changed, vanished or are unchanged | item id | `eijagraph.pack` |
| `snapshot_diff` | extended | R | Keyed semantic diff between two roots | id | `eijagraph.store` |
| `codemod_plan` | extended | D | Deterministic EditSet for a rename, term change, link declaration or regeneration | file path | `eijagraph.codemod` (LibCST, byte-range edits) |
<!-- /index -->

The impact-ranking aspect names the agent tools `impact`, `context`, `explain`, `select_tests` and `risk`; they are `graph_impact`, `context_pack`, `graph_why` and `diagnostics_explain`, `select_tests` and `change_risk` here. `ui_links` and `language.check` from ARCHITECTURE section 9 are not separate tools: UI links are `graph_neighbors` over the UI edge types (`exercised_by`, `names`, `styled_by`), and language checks are `diagnostics_get` with `rule_family: "language"`. Fewer tools were chosen on purpose; tool count is an ablation factor in the evaluation.

## 3. Common definitions

<!-- schema: common -->
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://eija.invalid/weave/mcp/v1/common",
  "$defs": {
    "Digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
    "KernelHash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "NodeId": {"type": "string", "pattern": "^repo://(?!\\.{1,2}(?:/|$))[A-Za-z0-9._-]+(?:/(?!\\.{1,2}(?:/|$))[A-Za-z0-9._-]+)*(#(?:[A-Za-z0-9._~:-]|%[0-9A-F]{2})+(/(?:[A-Za-z0-9._~:-]|%[0-9A-F]{2})+)*)?$", "maxLength": 512},
    "Selector": {"type": "string", "pattern": "^(WORKTREE|HEAD|[0-9a-f]{64})$", "default": "WORKTREE"},
    "Cursor": {"type": ["string", "null"], "maxLength": 1024, "default": null},
    "NodeType": {"enum": ["adr", "agent_run", "api_operation", "bounded_context", "claim", "component", "contract", "decision", "design_token", "diagram", "diagram_element", "document", "effect", "evidence", "formal_law", "formal_model", "gate", "guard", "invariant", "journey", "lane", "link_certificate", "module", "okf_page", "persona", "property", "requirement", "role", "state", "symbol", "term", "test", "tool", "transition", "ui_control", "ui_field", "ui_region", "ui_status", "ui_table", "ui_view", "witness", "workflow"]},
    "EdgeType": {"enum": ["attests", "calls", "checked_by", "conforms_to", "contains", "covers", "decides", "defeats", "depends_on", "derived_from", "documents", "exercised_by", "exposes", "flows_to", "formalises", "models", "motivates", "names", "proposes", "proves", "realises", "refines", "renamed_to", "satisfies", "serves", "styled_by", "supersedes", "supports", "verifies"]},
    "Level": {"enum": ["error", "warning", "note"]},
    "Soundness": {"enum": ["must", "may", "heuristic"]},
    "Origin": {"enum": ["declared", "derived", "evidence", "inferred"]},
    "ExtractorLabel": {"enum": ["exact", "syntactic", "candidate", "tool-resolved", "unresolved", "partial"]},
    "LinkStatus": {"enum": ["COVERED", "SUSPECT", "ORPHANED", "AMBIGUOUS", "UNWANTED", "UNRESOLVED"]},
    "EvidenceStatus": {"enum": ["PASS", "FAIL", "STALE", "UNKNOWN", "CONFLICT", "NOT_RUN"]},
    "Verdict": {"enum": ["FAIL", "NOT_RUN", "PASS"]},
    "Applicability": {"enum": ["machine_applicable", "has_placeholders", "maybe_incorrect", "unspecified"]},
    "Hash": {
      "type": "object",
      "properties": {"method": {"type": "string", "pattern": "^[a-z0-9-]+-v[0-9]+$"}, "value": {"$ref": "#/$defs/Digest"}},
      "required": ["method", "value"], "additionalProperties": false
    },
    "Text": {
      "type": "object",
      "properties": {"origin": {"$ref": "#/$defs/NodeId"}, "untrusted": {"const": true}, "content": {"type": "string", "maxLength": 32768}, "truncated": {"type": "boolean"}},
      "required": ["origin", "untrusted", "content", "truncated"], "additionalProperties": false
    },
    "Step": {
      "type": "object",
      "properties": {"from": {"$ref": "#/$defs/NodeId"}, "edge": {"$ref": "#/$defs/EdgeType"}, "to": {"$ref": "#/$defs/NodeId"}},
      "required": ["from", "edge", "to"], "additionalProperties": false
    },
    "Edge": {
      "type": "object",
      "properties": {
        "id": {"$ref": "#/$defs/Digest"}, "src": {"$ref": "#/$defs/NodeId"}, "type": {"$ref": "#/$defs/EdgeType"}, "dst": {"$ref": "#/$defs/NodeId"},
        "origin": {"$ref": "#/$defs/Origin"}, "soundness": {"$ref": "#/$defs/Soundness"},
        "link_status": {"anyOf": [{"$ref": "#/$defs/LinkStatus"}, {"type": "null"}]}
      },
      "required": ["id", "src", "type", "dst", "origin", "soundness", "link_status"], "additionalProperties": false
    },
    "Snapshot": {
      "type": "object",
      "properties": {
        "graph_root": {"$ref": "#/$defs/Digest"},
        "tree_hash": {"$ref": "#/$defs/Digest"},
        "base_commit": {"anyOf": [{"type": "string", "pattern": "^[0-9a-f]{40}$"}, {"type": "null"}]},
        "overlay_sha256": {"anyOf": [{"$ref": "#/$defs/Digest"}, {"type": "null"}]},
        "dirty": {"type": "boolean"},
        "extractor_pins_sha256": {"$ref": "#/$defs/Digest"},
        "not_run": {"type": "array", "items": {"type": "string", "pattern": "^[a-z0-9_.-]+$"}, "x-eija-set": true}
      },
      "required": ["graph_root", "tree_hash", "base_commit", "overlay_sha256", "dirty", "extractor_pins_sha256", "not_run"], "additionalProperties": false
    },
    "Bounds": {
      "type": "object",
      "properties": {
        "complete": {"type": "boolean"},
        "frontier": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}, "maxItems": 50},
        "frontier_count": {"type": "integer", "minimum": 0},
        "next_cursor": {"type": ["string", "null"]},
        "truncated_by": {"enum": [null, "limit", "budget", "hard_cap"]},
        "cost_units": {"type": "integer", "minimum": 0}
      },
      "required": ["complete", "frontier", "frontier_count", "next_cursor", "truncated_by", "cost_units"], "additionalProperties": false
    },
    "ErrorCode": {"enum": ["INVALID_ARGUMENT", "UNKNOWN_NODE", "AMBIGUOUS_TERM", "STALE_SNAPSHOT", "SNAPSHOT_UNAVAILABLE", "BUDGET_TOO_SMALL", "NOT_RUN", "PARTIAL_EXTRACTION", "PRECONDITION_MISMATCH", "PROTECTED_PATH", "KERNEL_REJECTED", "PROPOSAL_REJECTED", "UNSUPPORTED_KIND", "LIMIT_EXCEEDED", "QUOTA_EXCEEDED", "INTERNAL_SCHEMA_VIOLATION"]},
    "Error": {
      "type": "object",
      "properties": {
        "code": {"$ref": "#/$defs/ErrorCode"},
        "message_id": {"type": "string", "pattern": "^[a-z0-9_.]+$"},
        "args": {"type": "object", "additionalProperties": {"type": ["string", "integer", "boolean", "array"]}},
        "next": {"type": "array", "maxItems": 5, "items": {"type": "object", "properties": {"tool": {"type": "string"}, "arguments": {"type": "object"}}, "required": ["tool", "arguments"], "additionalProperties": false}},
        "retryable": {"type": "boolean"}
      },
      "required": ["code", "message_id", "args", "next", "retryable"], "additionalProperties": false
    },
    "Finding": {
      "type": "object",
      "properties": {
        "rule_id": {"type": "string", "pattern": "^WV-[0-9]{3}$"},
        "level": {"$ref": "#/$defs/Level"},
        "message_id": {"type": "string", "pattern": "^[a-z0-9_.]+$"},
        "args": {"type": "object", "additionalProperties": {"type": ["string", "integer", "boolean", "array"]}},
        "locations": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}, "maxItems": 20},
        "witness": {"type": "array", "items": {"$ref": "#/$defs/Step"}, "maxItems": 40},
        "fingerprint": {"$ref": "#/$defs/Digest"},
        "baseline_state": {"enum": ["new", "unchanged", "updated", "absent", null]},
        "fix": {"anyOf": [{"type": "object", "properties": {"editset_id": {"$ref": "#/$defs/Digest"}, "applicability": {"$ref": "#/$defs/Applicability"}}, "required": ["editset_id", "applicability"], "additionalProperties": false}, {"type": "null"}]}
      },
      "required": ["rule_id", "level", "message_id", "args", "locations", "witness", "fingerprint", "baseline_state", "fix"], "additionalProperties": false
    },
    "TextEdit": {
      "type": "object",
      "properties": {
        "start": {"type": "integer", "minimum": 0}, "end": {"type": "integer", "minimum": 0},
        "old_sha256": {"$ref": "#/$defs/Digest"}, "new_text": {"type": "string", "maxLength": 65536}
      },
      "required": ["start", "end", "old_sha256", "new_text"], "additionalProperties": false
    },
    "FileChange": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "pattern": "^[A-Za-z0-9._][A-Za-z0-9._/-]*$", "maxLength": 300},
        "precondition_sha256": {"anyOf": [{"$ref": "#/$defs/Digest"}, {"type": "null"}]},
        "postcondition_sha256": {"anyOf": [{"$ref": "#/$defs/Digest"}, {"type": "null"}]},
        "edits": {"type": "array", "items": {"$ref": "#/$defs/TextEdit"}, "minItems": 1, "maxItems": 500}
      },
      "required": ["path", "precondition_sha256", "postcondition_sha256", "edits"], "additionalProperties": false
    },
    "EditSet": {
      "type": "object",
      "properties": {
        "schema": {"const": "eija.weave.editset.v1"},
        "id": {"$ref": "#/$defs/Digest"},
        "base_root": {"$ref": "#/$defs/Digest"},
        "producer": {"type": "object", "properties": {"kind": {"enum": ["codemod", "rule_fix", "agent"]}, "id": {"type": "string", "pattern": "^[a-z0-9_.-]+$"}, "version": {"type": "integer", "minimum": 1}}, "required": ["kind", "id", "version"], "additionalProperties": false},
        "applicability": {"$ref": "#/$defs/Applicability"},
        "files": {"type": "array", "items": {"$ref": "#/$defs/FileChange"}, "minItems": 1, "maxItems": 200},
        "renames": {"type": "array", "items": {"type": "object", "properties": {"old_id": {"$ref": "#/$defs/NodeId"}, "new_id": {"$ref": "#/$defs/NodeId"}}, "required": ["old_id", "new_id"], "additionalProperties": false}},
        "commands": {"type": "array", "items": {"type": "object", "properties": {"generator_id": {"type": "string", "pattern": "^[a-z0-9_.-]+$"}, "args": {"type": "array", "items": {"type": "string"}}}, "required": ["generator_id", "args"], "additionalProperties": false}}
      },
      "required": ["schema", "id", "base_root", "producer", "applicability", "files", "renames", "commands"], "additionalProperties": false
    },
    "FindingsDelta": {
      "type": "object",
      "properties": {
        "new": {"type": "array", "items": {"$ref": "#/$defs/Finding"}},
        "absent": {"type": "array", "items": {"$ref": "#/$defs/Digest"}, "x-eija-set": true},
        "unchanged_count": {"type": "integer", "minimum": 0}
      },
      "required": ["new", "absent", "unchanged_count"], "additionalProperties": false
    },
    "Ripple": {
      "type": "object",
      "properties": {
        "roots": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}},
        "counts": {"type": "object", "properties": {"tier0": {"type": "integer", "minimum": 0}, "tier1": {"type": "integer", "minimum": 0}, "tier2": {"type": "integer", "minimum": 0}}, "required": ["tier0", "tier1", "tier2"], "additionalProperties": false},
        "affected": {"type": "array", "items": {"type": "object", "properties": {"id": {"$ref": "#/$defs/NodeId"}, "tier": {"enum": [0, 1, 2]}}, "required": ["id", "tier"], "additionalProperties": false}, "maxItems": 500},
        "complete": {"type": "boolean"},
        "envelope": {"const": "Covers the edges encoded in the graph; not every real-world consequence."}
      },
      "required": ["roots", "counts", "affected", "complete", "envelope"], "additionalProperties": false
    },
    "ImpactParams": {
      "type": "object",
      "properties": {
        "max_tier": {"enum": [0, 1, 2]},
        "budget": {"type": ["integer", "null"], "minimum": 0},
        "arc_set_sha256": {"$ref": "#/$defs/Digest"},
        "flow_table_sha256": {"$ref": "#/$defs/Digest"},
        "alpha": {"type": "array", "items": {"type": "integer", "minimum": 1}, "minItems": 2, "maxItems": 2},
        "iterations": {"type": "integer", "minimum": 1},
        "err_bound_units": {"type": "integer", "minimum": 0}
      },
      "required": ["max_tier", "budget", "arc_set_sha256", "flow_table_sha256", "alpha", "iterations", "err_bound_units"], "additionalProperties": false
    },
    "Envelope": {
      "type": "object",
      "properties": {
        "contract": {"const": "eija.weave.mcp.v1"},
        "tool": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
        "snapshot": {"$ref": "#/$defs/Snapshot"},
        "request_hash": {"$ref": "#/$defs/Digest"},
        "result": {"type": ["object", "null"]},
        "error": {"anyOf": [{"$ref": "#/$defs/Error"}, {"type": "null"}]},
        "bounds": {"$ref": "#/$defs/Bounds"},
        "response_hash": {"$ref": "#/$defs/Digest"}
      },
      "required": ["contract", "tool", "snapshot", "request_hash", "result", "error", "bounds", "response_hash"],
      "additionalProperties": false,
      "oneOf": [
        {"properties": {"result": {"type": "object"}, "error": {"type": "null"}}},
        {"properties": {"result": {"type": "null"}, "error": {"type": "object"}}}
      ]
    }
  }
}
```

Composition rule: the `outputSchema` of tool T is `{"$defs": <common $defs>, "allOf": [{"$ref": "#/$defs/Envelope"}, {"properties": {"result": {"anyOf": [{"type": "null"}, <T.result>]}}}]}`. The `inputSchema` of tool T is `{"$defs": <common $defs>, ...<T.input>}`. Both are generated, never hand-copied. All inputs use `additionalProperties: false`.

## 4. Read tools

### graph_status

<!-- schema: graph_status.input -->
```json
{"type": "object", "properties": {"at": {"$ref": "#/$defs/Selector"}, "refresh": {"type": "boolean", "default": false}}, "additionalProperties": false}
```

<!-- schema: graph_status.result -->
```json
{
  "type": "object",
  "properties": {
    "contract_sha256": {"$ref": "#/$defs/Digest"},
    "tool_list_sha256": {"$ref": "#/$defs/Digest"},
    "verdict": {"$ref": "#/$defs/Verdict"},
    "nodes_by_type": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
    "edges_by_type": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
    "findings_by_level": {"type": "object", "properties": {"error": {"type": "integer"}, "warning": {"type": "integer"}, "note": {"type": "integer"}}, "required": ["error", "warning", "note"], "additionalProperties": false},
    "not_run": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "reason_id": {"type": "string"}}, "required": ["id", "reason_id"], "additionalProperties": false}},
    "extractors": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "version": {"type": "string"}, "label": {"$ref": "#/$defs/ExtractorLabel"}}, "required": ["id", "version", "label"], "additionalProperties": false}}
  },
  "required": ["contract_sha256", "tool_list_sha256", "verdict", "nodes_by_type", "edges_by_type", "findings_by_level", "not_run", "extractors"],
  "additionalProperties": false
}
```

`refresh: true` rebuilds the worktree snapshot (incremental, verified equal to a clean build by the differential test) and returns the new root. `at: WORKTREE` without `refresh` uses the last root built for the current worktree tree hash, and rebuilds if the tree hash differs. `verdict` is `FAIL` if any error-level finding exists, else `NOT_RUN` if `not_run` is non-empty, else `PASS`.

### graph_node

<!-- schema: graph_node.input -->
```json
{"type": "object", "properties": {"at": {"$ref": "#/$defs/Selector"}, "id": {"$ref": "#/$defs/NodeId"}, "detail": {"enum": ["concise", "full"], "default": "concise"}}, "required": ["id"], "additionalProperties": false}
```

<!-- schema: graph_node.result -->
```json
{
  "type": "object",
  "properties": {
    "id": {"$ref": "#/$defs/NodeId"},
    "type": {"$ref": "#/$defs/NodeType"},
    "content_hash": {"$ref": "#/$defs/Hash"},
    "provenance": {"type": "object", "properties": {"origin": {"$ref": "#/$defs/Origin"}, "label": {"$ref": "#/$defs/ExtractorLabel"}}, "required": ["origin", "label"], "additionalProperties": false},
    "display_name": {"type": "string", "maxLength": 200},
    "degree": {"type": "object", "additionalProperties": {"type": "object", "properties": {"out": {"type": "integer", "minimum": 0}, "in": {"type": "integer", "minimum": 0}}, "required": ["out", "in"], "additionalProperties": false}},
    "link_status_counts": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
    "findings_by_level": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
    "source": {"anyOf": [{"type": "null"}, {"type": "object", "properties": {"path": {"type": "string"}, "sha256_lf": {"$ref": "#/$defs/Digest"}, "text": {"anyOf": [{"$ref": "#/$defs/Text"}, {"type": "null"}]}}, "required": ["path", "sha256_lf", "text"], "additionalProperties": false}]}
  },
  "required": ["id", "type", "content_hash", "provenance", "display_name", "degree", "link_status_counts", "findings_by_level", "source"],
  "additionalProperties": false
}
```

`concise` returns `source.text = null` (path and hash only); `full` returns the slice up to 32768 bytes with `truncated` set. An unknown id gives `UNKNOWN_NODE` with up to five `did_you_mean` ids in `args` (longest common prefix over the sorted id list, ties by id) and a `graph_search` call in `next`.

### graph_search

<!-- schema: graph_search.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "query": {"type": "string", "minLength": 1, "maxLength": 200},
    "types": {"type": "array", "items": {"$ref": "#/$defs/NodeType"}, "x-eija-set": true, "default": []},
    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
    "cursor": {"$ref": "#/$defs/Cursor"}
  },
  "required": ["query"], "additionalProperties": false
}
```

<!-- schema: graph_search.result -->
```json
{
  "type": "object",
  "properties": {
    "matches": {"type": "array", "items": {"type": "object", "properties": {"id": {"$ref": "#/$defs/NodeId"}, "type": {"$ref": "#/$defs/NodeType"}, "match_kind": {"enum": ["id_exact", "path_prefix", "term_form", "name_token"]}, "rank": {"type": "integer", "minimum": 1}}, "required": ["id", "type", "match_kind", "rank"], "additionalProperties": false}},
    "ambiguous": {"type": "boolean"}
  },
  "required": ["matches", "ambiguous"], "additionalProperties": false
}
```

Matching is exact and lexical: `id_exact`, then `path_prefix` on the repository path, then `term_form` (a registered form of a term after ASCII case fold), then `name_token` (identifier split by the registry splitter). No fuzzy, phonetic or embedding match, because their results depend on model or library versions. `ambiguous` is true when one query matches more than one node at the best match kind; the tool does not choose.

### graph_neighbors

<!-- schema: graph_neighbors.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "id": {"$ref": "#/$defs/NodeId"},
    "edge_types": {"type": "array", "items": {"$ref": "#/$defs/EdgeType"}, "x-eija-set": true, "default": []},
    "direction": {"enum": ["out", "in", "both"], "default": "both"},
    "classes": {"type": "array", "items": {"$ref": "#/$defs/Soundness"}, "x-eija-set": true, "default": []},
    "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
    "cursor": {"$ref": "#/$defs/Cursor"}
  },
  "required": ["id"], "additionalProperties": false
}
```

<!-- schema: graph_neighbors.result -->
```json
{"type": "object", "properties": {"edges": {"type": "array", "items": {"$ref": "#/$defs/Edge"}}}, "required": ["edges"], "additionalProperties": false}
```

An empty `edge_types` or `classes` means no filter. `link_status` in an `Edge` is set only for declared links.

### graph_impact

<!-- schema: graph_impact.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "roots": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}, "minItems": 1, "maxItems": 20, "x-eija-set": true},
    "max_tier": {"enum": [0, 1, 2], "default": 1},
    "edge_types": {"type": "array", "items": {"$ref": "#/$defs/EdgeType"}, "x-eija-set": true, "default": []},
    "max_nodes": {"type": "integer", "minimum": 1, "maximum": 2000, "default": 200},
    "witnesses": {"type": "boolean", "default": false}
  },
  "required": ["roots"], "additionalProperties": false
}
```

<!-- schema: graph_impact.result -->
```json
{
  "type": "object",
  "properties": {
    "schema": {"const": "eija.weave.impact.v1"},
    "roots": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}},
    "params": {"$ref": "#/$defs/ImpactParams"},
    "partial_extraction": {"type": "boolean"},
    "counts": {"type": "object", "properties": {"tier0": {"type": "integer", "minimum": 0}, "tier1": {"type": "integer", "minimum": 0}, "tier2": {"type": "integer", "minimum": 0}}, "required": ["tier0", "tier1", "tier2"], "additionalProperties": false},
    "affected": {"type": "array", "items": {"type": "object", "properties": {
      "id": {"$ref": "#/$defs/NodeId"}, "tier": {"enum": [0, 1, 2]}, "distance": {"type": "integer", "minimum": 0},
      "score_ppm": {"type": "integer", "minimum": 0, "maximum": 1000000},
      "witness": {"anyOf": [{"type": "null"}, {"type": "array", "items": {"$ref": "#/$defs/NodeId"}}]}
    }, "required": ["id", "tier", "distance", "score_ppm", "witness"], "additionalProperties": false}},
    "envelope": {"const": "Covers the edges encoded in the graph; not every real-world consequence."}
  },
  "required": ["schema", "roots", "params", "partial_extraction", "counts", "affected", "envelope"], "additionalProperties": false
}
```

The result is the impact-ranking aspect's `eija.weave.impact.v1` report (design section 2 there) with `complete` and `frontier` lifted into the envelope `bounds`, where every tool carries them. Tier 0, 1 and 2 are the soundness classes `must`, `may` and `heuristic` (tiers nest); `max_tier` bounds the arcs used and defaults to 1 so heuristic reach is shown only when asked. `affected` is sorted by `(tier, -score_ppm, distance, id)`; `score_ppm` is the advisory personalised-PageRank relevance (integer, bit-exact, section 5 there), never evidence. The witness of a node is the lexicographically smallest shortest path from any root, as node ids.

`max_nodes` has the kernel's `budget` meaning (`impact.closure`): traversal stops when that many nodes are visited and the remainder is reported as `bounds.frontier`; `bounds.complete` is true only when the frontier is empty. `affected` includes the roots (tier 0, distance 0). A report built from a partial extraction has `partial_extraction: true` and can never be complete.

### diagnostics_get

<!-- schema: diagnostics_get.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "scope": {
      "type": "object",
      "properties": {
        "ids": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}, "x-eija-set": true, "default": []},
        "paths": {"type": "array", "items": {"type": "string", "maxLength": 300}, "x-eija-set": true, "default": []},
        "rule_ids": {"type": "array", "items": {"type": "string", "pattern": "^WV-[0-9]{3}$"}, "x-eija-set": true, "default": []},
        "rule_family": {"enum": ["all", "links", "traceability", "language", "architecture", "views", "ui", "assurance", "hygiene"], "default": "all"}
      },
      "additionalProperties": false, "default": {}
    },
    "min_level": {"$ref": "#/$defs/Level"},
    "since": {"anyOf": [{"$ref": "#/$defs/Digest"}, {"type": "null"}], "default": null},
    "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
    "cursor": {"$ref": "#/$defs/Cursor"}
  },
  "additionalProperties": false
}
```

<!-- schema: diagnostics_get.result -->
```json
{
  "type": "object",
  "properties": {
    "verdict": {"$ref": "#/$defs/Verdict"},
    "by_level": {"type": "object", "properties": {"error": {"type": "integer"}, "warning": {"type": "integer"}, "note": {"type": "integer"}}, "required": ["error", "warning", "note"], "additionalProperties": false},
    "findings": {"type": "array", "items": {"$ref": "#/$defs/Finding"}}
  },
  "required": ["verdict", "by_level", "findings"], "additionalProperties": false
}
```

With `since` set to an earlier root, each finding carries `baseline_state` (`new`, `unchanged`, `updated`; SARIF `baselineState` vocabulary, SARIF 2.1.0 section 3.27.24) and findings present only in `since` are returned as `absent` with their fingerprint. Order is error before warning before note, then rule id, then fingerprint. `by_level` counts the whole scope, not the page, so an agent sees the size of what was truncated. A finding is never dropped to fit a cap: errors are listed first and a cap that would cut an error page-breaks with a cursor.

### context_pack

<!-- schema: context_pack.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "task": {
      "type": "object",
      "properties": {
        "intent": {"enum": ["understand", "modify", "rename", "diagnose", "review"]},
        "seeds": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}, "minItems": 1, "maxItems": 10, "x-eija-set": true},
        "seed_terms": {"type": "array", "items": {"type": "string", "maxLength": 100}, "maxItems": 10, "x-eija-set": true, "default": []}
      },
      "required": ["intent", "seeds"], "additionalProperties": false
    },
    "budget_units": {"type": "integer", "minimum": 512, "maximum": 65536, "default": 8192},
    "max_level": {"enum": ["handle", "summary", "slice"], "default": "slice"}
  },
  "required": ["task"], "additionalProperties": false
}
```

<!-- schema: context_pack.result -->
```json
{
  "type": "object",
  "properties": {
    "pack_id": {"$ref": "#/$defs/Digest"},
    "params": {"$ref": "#/$defs/ImpactParams"},
    "pack_policy_version": {"type": "integer", "minimum": 1},
    "budget_units": {"type": "integer"},
    "spent_units": {"type": "integer"},
    "obligations": {"type": "object", "properties": {"required": {"type": "integer", "minimum": 0}, "included": {"type": "integer", "minimum": 0}, "unresolved": {"type": "array", "items": {"type": "object", "properties": {"slot": {"type": "string"}, "reason_id": {"type": "string"}}, "required": ["slot", "reason_id"], "additionalProperties": false}}}, "required": ["required", "included", "unresolved"], "additionalProperties": false},
    "omitted": {"type": "object", "properties": {"by_budget": {"type": "integer", "minimum": 0}, "by_level_cap": {"type": "integer", "minimum": 0}, "by_hop_limit": {"type": "integer", "minimum": 0}}, "required": ["by_budget", "by_level_cap", "by_hop_limit"], "additionalProperties": false},
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"$ref": "#/$defs/NodeId"},
          "type": {"$ref": "#/$defs/NodeType"},
          "slot": {"enum": ["seed", "statement", "verifier", "term", "finding", "suspect", "governing", "ripple", "ranked"]},
          "level": {"enum": ["handle", "summary", "slice"]},
          "content_hash": {"$ref": "#/$defs/Hash"},
          "provenance": {"type": "object", "properties": {"origin": {"$ref": "#/$defs/Origin"}, "soundness": {"$ref": "#/$defs/Soundness"}, "label": {"$ref": "#/$defs/ExtractorLabel"}}, "required": ["origin", "soundness", "label"], "additionalProperties": false},
          "why": {"type": "array", "items": {"$ref": "#/$defs/Step"}, "maxItems": 6},
          "score_ppm": {"type": "integer", "minimum": 0, "maximum": 1000000},
          "cost_units": {"type": "integer", "minimum": 0},
          "text": {"anyOf": [{"$ref": "#/$defs/Text"}, {"type": "null"}]}
        },
        "required": ["id", "type", "slot", "level", "content_hash", "provenance", "why", "score_ppm", "cost_units", "text"],
        "additionalProperties": false
      }
    }
  },
  "required": ["pack_id", "params", "pack_policy_version", "budget_units", "spent_units", "obligations", "omitted", "items"],
  "additionalProperties": false
}
```

`bounds.complete` is true only when every required obligation is included and nothing eligible was omitted. If the mandatory items do not fit the budget the tool returns `BUDGET_TOO_SMALL` with `args.needed` and never drops an obligation to fit. `pack_id = dhash("eija.weave.pack.v1", {request (normalised), graph_root, params})`; the same inputs reproduce the same bytes. `params` are the ranking parameters (`alpha`, `iterations`, `err_bound_units`, arc-set and flow-table digests) exactly as the impact-ranking aspect reports them, plus the pack policy version. Slot semantics and the pack layer are in the design document, section 5; ranking (personalised PageRank in fixed-point integers) and the optional-tier selection are that aspect's `ppr_int` and `select_context`.

### edit_preview

<!-- schema: edit_preview.input -->
```json
{"type": "object", "properties": {"at": {"$ref": "#/$defs/Selector"}, "editset": {"$ref": "#/$defs/EditSet"}}, "required": ["editset"], "additionalProperties": false}
```

<!-- schema: edit_preview.result -->
```json
{
  "type": "object",
  "properties": {
    "applicable": {"type": "boolean"},
    "preconditions": {"type": "array", "items": {"type": "object", "properties": {"path": {"type": "string"}, "status": {"enum": ["OK", "ALREADY_APPLIED", "MISMATCH", "NOT_FOUND", "MIXED_EOL", "OVERLAP", "PROTECTED_PATH"]}}, "required": ["path", "status"], "additionalProperties": false}},
    "overlay_root": {"anyOf": [{"$ref": "#/$defs/Digest"}, {"type": "null"}]},
    "partial_extractions": {"type": "array", "items": {"type": "string"}},
    "findings_delta": {"anyOf": [{"$ref": "#/$defs/FindingsDelta"}, {"type": "null"}]},
    "links_becoming_suspect": {"type": "array", "items": {"$ref": "#/$defs/Digest"}, "x-eija-set": true},
    "ripple": {"anyOf": [{"$ref": "#/$defs/Ripple"}, {"type": "null"}]}
  },
  "required": ["applicable", "preconditions", "overlay_root", "partial_extractions", "findings_delta", "links_becoming_suspect", "ripple"],
  "additionalProperties": false
}
```

Nothing is written to the worktree. If any precondition is not `OK` or `ALREADY_APPLIED`, `applicable` is false and the analysis fields are null. A protected path (section 9) gives `PROTECTED_PATH` for that file. A file whose edited region parses with recovery is listed in `partial_extractions`; findings that depend on it are `NOT_RUN`, never PASS (D-14).

### txn_dry_run

<!-- schema: txn_dry_run.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "base": {"type": "object", "properties": {"workflow": {"$ref": "#/$defs/NodeId"}}, "required": ["workflow"], "additionalProperties": false},
    "transaction": {"$ref": "../../contracts/semantic-transaction.schema.json"}
  },
  "required": ["base", "transaction"], "additionalProperties": false
}
```

The `transaction` object is one transaction of the kernel's open change vocabulary (`src/eija_studio/domain/transactions.py`, WBS 1.3), by reference to the generated contract `contracts/semantic-transaction.schema.json`; the test `test_transaction_schema_matches_kernel` checks the reference and that the contract equals the kernel's schema, so the two cannot drift.

<!-- schema: txn_dry_run.result -->
```json
{
  "type": "object",
  "properties": {
    "verdict": {"enum": ["ACCEPTED", "REJECTED"]},
    "kernel_code": {"type": ["string", "null"]},
    "candidate_semantic_hash": {"anyOf": [{"$ref": "#/$defs/KernelHash"}, {"type": "null"}]},
    "base_semantic_hash": {"$ref": "#/$defs/KernelHash"},
    "model_delta": {"type": "object", "properties": {"changed_actions": {"type": "array", "items": {"type": "string"}}}, "required": ["changed_actions"], "additionalProperties": false},
    "kernel_impact": {"anyOf": [{"type": "null"}, {"type": "object", "properties": {"affected": {"type": "array", "items": {"type": "string"}}, "complete": {"type": "boolean"}, "envelope": {"type": "string"}}, "required": ["affected", "complete", "envelope"], "additionalProperties": false}]},
    "ripple": {"anyOf": [{"$ref": "#/$defs/Ripple"}, {"type": "null"}]},
    "findings_delta": {"anyOf": [{"$ref": "#/$defs/FindingsDelta"}, {"type": "null"}]},
    "links_becoming_suspect": {"type": "array", "items": {"$ref": "#/$defs/Digest"}, "x-eija-set": true},
    "label": {"const": "PREDICTION of a real change; the sets are computed over encoded edges and models, not observed."}
  },
  "required": ["verdict", "kernel_code", "candidate_semantic_hash", "base_semantic_hash", "model_delta", "kernel_impact", "ripple", "findings_delta", "links_becoming_suspect", "label"],
  "additionalProperties": false
}
```

`verdict`, `kernel_code`, `candidate_semantic_hash`, `model_delta` and `kernel_impact` come verbatim from the kernel's pure functions `apply_transaction` and `model_impact` (a `DomainError` becomes `REJECTED` with its `code`). `ripple`, `findings_delta` and `links_becoming_suspect` come from `eijagraph` run on an overlay in which the workflow file is replaced by the candidate; they are null when the transaction is rejected. Apply is not a tool (section 9).

### proposal_submit

<!-- schema: proposal_submit.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "proposal": {
      "oneOf": [
        {"type": "object", "properties": {"kind": {"const": "link"}, "link_kind": {"$ref": "#/$defs/EdgeType"}, "from": {"$ref": "#/$defs/NodeId"}, "to": {"$ref": "#/$defs/NodeId"}, "rationale": {"type": "string", "maxLength": 1000}}, "required": ["kind", "link_kind", "from", "to", "rationale"], "additionalProperties": false},
        {"type": "object", "properties": {"kind": {"const": "ack_request"}, "link_id": {"$ref": "#/$defs/Digest"}, "diff_summary": {"type": "string", "maxLength": 1000}}, "required": ["kind", "link_id", "diff_summary"], "additionalProperties": false},
        {"type": "object", "properties": {"kind": {"const": "witness"}, "claim": {"$ref": "#/$defs/NodeId"}, "artifact": {"$ref": "#/$defs/NodeId"}}, "required": ["kind", "claim", "artifact"], "additionalProperties": false},
        {"type": "object", "properties": {"kind": {"const": "rename_record"}, "old_id": {"$ref": "#/$defs/NodeId"}, "new_id": {"$ref": "#/$defs/NodeId"}}, "required": ["kind", "old_id", "new_id"], "additionalProperties": false}
      ]
    }
  },
  "required": ["proposal"], "additionalProperties": false
}
```

<!-- schema: proposal_submit.result -->
```json
{
  "type": "object",
  "properties": {
    "proposal_id": {"$ref": "#/$defs/Digest"},
    "status": {"const": "PROPOSED"},
    "applied": {"const": false},
    "checker_verdict": {"enum": ["ACCEPTABLE_FOR_REVIEW", "REJECTED"]},
    "reasons": {"type": "array", "items": {"type": "object", "properties": {"code": {"enum": ["OK", "ENDPOINT_MISSING", "SIGNATURE_VIOLATION", "METHOD_POLICY_MISMATCH", "UNRESOLVABLE_TARGET", "INFERRED_CANNOT_SATISFY_GATE", "OBLIGATION_REDUCED", "SAME_AUTHOR_EVIDENCE", "PROTECTED_SUBJECT", "NOT_RUN"]}, "args": {"type": "object", "additionalProperties": {"type": ["string", "integer", "boolean"]}}}, "required": ["code", "args"], "additionalProperties": false}},
    "recomputed": {"type": "object", "properties": {"method": {"type": ["string", "null"]}, "target_digest": {"anyOf": [{"$ref": "#/$defs/Digest"}, {"type": "null"}]}}, "required": ["method", "target_digest"], "additionalProperties": false},
    "owner_next": {"type": "string", "pattern": "^[a-z0-9_.]+$"}
  },
  "required": ["proposal_id", "status", "applied", "checker_verdict", "reasons", "recomputed", "owner_next"], "additionalProperties": false
}
```

`proposal_id` = SHA-256 of the normalised proposal and `graph_root`, so re-submitting is idempotent. The record is inert: it is stored under `.eija/proposals/` (gitignored) and appended to the run log; it changes no graph fact, clears no link and satisfies no gate. `recomputed.target_digest` is what the checker computed with the policy hash method for the link kind; an agent-supplied digest is not accepted (C-13). What the checker verifies is in the design document, section 8.

## 5. Extended read tools

### graph_why

<!-- schema: graph_why.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "fact": {
      "oneOf": [
        {"type": "object", "properties": {"kind": {"const": "reach"}, "from": {"$ref": "#/$defs/NodeId"}, "to": {"$ref": "#/$defs/NodeId"}}, "required": ["kind", "from", "to"], "additionalProperties": false},
        {"type": "object", "properties": {"kind": {"const": "finding"}, "fingerprint": {"$ref": "#/$defs/Digest"}}, "required": ["kind", "fingerprint"], "additionalProperties": false},
        {"type": "object", "properties": {"kind": {"const": "edge"}, "src": {"$ref": "#/$defs/NodeId"}, "type": {"$ref": "#/$defs/EdgeType"}, "dst": {"$ref": "#/$defs/NodeId"}}, "required": ["kind", "src", "type", "dst"], "additionalProperties": false}
      ]
    }
  },
  "required": ["fact"], "additionalProperties": false
}
```

<!-- schema: graph_why.result -->
```json
{
  "type": "object",
  "properties": {
    "holds": {"type": "boolean"},
    "rule_id": {"type": ["string", "null"]},
    "premises": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}},
    "witness": {"type": "array", "items": {"$ref": "#/$defs/Step"}},
    "searched_scope": {"type": ["string", "null"]},
    "rechecked": {"type": "boolean"}
  },
  "required": ["holds", "rule_id", "premises", "witness", "searched_scope", "rechecked"], "additionalProperties": false
}
```

For a positive fact the witness is the lexicographically first shortest path (or the recorded premises of a derived fact) and `rechecked` is true when the server re-derived the fact on the witness subgraph alone. For a negative answer (`holds: false`) the witness is empty and `searched_scope` names the closed-world scope that was searched (for example the edge types and node types examined), so absence is stated as "not found in this scope", never as a proof of non-existence.

### select_tests

<!-- schema: select_tests.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "base": {"$ref": "#/$defs/Selector"},
    "roots": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}, "maxItems": 50, "x-eija-set": true, "default": []}
  },
  "additionalProperties": false
}
```

<!-- schema: select_tests.result -->
```json
{
  "type": "object",
  "properties": {
    "params": {"$ref": "#/$defs/ImpactParams"},
    "pool_status": {"enum": ["OK", "NOT_RUN"]},
    "obligations": {"type": "integer", "minimum": 0},
    "chosen": {"type": "array", "items": {"type": "object", "properties": {"test": {"$ref": "#/$defs/NodeId"}, "cost": {"type": "integer", "minimum": 0}, "observes": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}}}, "required": ["test", "cost", "observes"], "additionalProperties": false}},
    "cost": {"type": "integer", "minimum": 0},
    "unreachable": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}},
    "claim": {"const": "Covers by declared or measured links; not fault detection. The fast tier is never a safety claim."}
  },
  "required": ["params", "pool_status", "obligations", "chosen", "cost", "unreachable", "claim"], "additionalProperties": false
}
```

`roots` empty means the changed nodes between `base` (default `HEAD`) and `at`. The result is the impact-ranking aspect's weighted-set-cover selection (section 7 there): obligations in the tier-1 impact that need executable evidence, tests that observe them, and `unreachable` obligations, which are findings ("impacted obligation with no test that observes the change"). Without coverage data the candidate pool is `NOT_RUN`, never "all tests pass".

### change_risk

<!-- schema: change_risk.input -->
```json
{"type": "object", "properties": {"at": {"$ref": "#/$defs/Selector"}, "base": {"$ref": "#/$defs/Selector"}}, "additionalProperties": false}
```

<!-- schema: change_risk.result -->
```json
{
  "type": "object",
  "properties": {
    "params": {"$ref": "#/$defs/ImpactParams"},
    "fields": {
      "type": "object",
      "properties": {
        "protected_paths_touched": {"type": "integer", "minimum": 0},
        "pinned_statements_changed": {"type": "integer", "minimum": 0},
        "impacted_obligations_without_observer": {"type": "integer", "minimum": 0},
        "suspect_links": {"type": "integer", "minimum": 0},
        "tier0_size": {"type": "integer", "minimum": 0},
        "tier1_size": {"type": "integer", "minimum": 0},
        "tier2_size": {"type": "integer", "minimum": 0},
        "changed_nodes": {"type": "integer", "minimum": 0}
      },
      "required": ["protected_paths_touched", "pinned_statements_changed", "impacted_obligations_without_observer", "suspect_links", "tier0_size", "tier1_size", "tier2_size", "changed_nodes"],
      "additionalProperties": false
    },
    "review_key": {"type": "array", "items": {"type": "integer", "minimum": 0}, "minItems": 8, "maxItems": 8},
    "claim": {"const": "A vector of exact counts. Not a defect probability and not a score."}
  },
  "required": ["params", "fields", "review_key", "claim"], "additionalProperties": false
}
```

The eight fields and their order are the impact-ranking aspect's change-risk vector (section 9 there); `review_key` is the field tuple in that order, larger first. No weighted score is computed. A non-zero `protected_paths_touched` or `pinned_statements_changed` requires an owner decision under existing policy; nothing else gates on a number.

### link_status

<!-- schema: link_status.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "node": {"anyOf": [{"$ref": "#/$defs/NodeId"}, {"type": "null"}], "default": null},
    "statuses": {"type": "array", "items": {"$ref": "#/$defs/LinkStatus"}, "x-eija-set": true, "default": []},
    "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
    "cursor": {"$ref": "#/$defs/Cursor"}
  },
  "additionalProperties": false
}
```

<!-- schema: link_status.result -->
```json
{
  "type": "object",
  "properties": {
    "links": {"type": "array", "items": {"type": "object", "properties": {
      "id": {"$ref": "#/$defs/Digest"}, "kind": {"$ref": "#/$defs/EdgeType"}, "from": {"$ref": "#/$defs/NodeId"}, "to": {"$ref": "#/$defs/NodeId"},
      "method": {"type": "string"}, "stored_digest": {"$ref": "#/$defs/Digest"}, "current_digest": {"anyOf": [{"$ref": "#/$defs/Digest"}, {"type": "null"}]},
      "status": {"$ref": "#/$defs/LinkStatus"}, "evidence_status": {"$ref": "#/$defs/EvidenceStatus"}, "baseline_entry": {"type": "string", "maxLength": 100}
    }, "required": ["id", "kind", "from", "to", "method", "stored_digest", "current_digest", "status", "evidence_status", "baseline_entry"], "additionalProperties": false}},
    "summary": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}}
  },
  "required": ["links", "summary"], "additionalProperties": false
}
```

Status is `link_status(link, current_digest, ledger)` recomputed on every call (ADR-0093). `SUSPECT` means the normalised target digest changed since the baseline, not that the link is false. The tool cannot clear a link.

### diagnostics_explain

<!-- schema: diagnostics_explain.input -->
```json
{"type": "object", "properties": {"rule_id": {"type": "string", "pattern": "^WV-[0-9]{3}$"}}, "required": ["rule_id"], "additionalProperties": false}
```

<!-- schema: diagnostics_explain.result -->
```json
{
  "type": "object",
  "properties": {
    "rule_id": {"type": "string"}, "name": {"type": "string"}, "version": {"type": "integer", "minimum": 1},
    "default_level": {"$ref": "#/$defs/Level"}, "stratum": {"type": "integer", "minimum": 0},
    "reads": {"type": "array", "items": {"type": "string"}},
    "explanation": {"$ref": "#/$defs/Text"},
    "remedy_kinds": {"type": "array", "items": {"enum": ["edit_text", "add_link", "ack_by_owner", "regenerate", "rename_with_map", "restore_obligation", "install_tool"]}}
  },
  "required": ["rule_id", "name", "version", "default_level", "stratum", "reads", "explanation", "remedy_kinds"], "additionalProperties": false
}
```

### language_lookup

<!-- schema: language_lookup.input -->
```json
{"type": "object", "properties": {"at": {"$ref": "#/$defs/Selector"}, "term": {"type": "string", "minLength": 1, "maxLength": 100}, "context": {"type": ["string", "null"], "default": null}}, "required": ["term"], "additionalProperties": false}
```

<!-- schema: language_lookup.result -->
```json
{
  "type": "object",
  "properties": {
    "entries": {"type": "array", "items": {"type": "object", "properties": {
      "context": {"type": "string"}, "preferred": {"type": "string"}, "forms": {"type": "array", "items": {"type": "string"}},
      "definition": {"$ref": "#/$defs/NodeId"}, "bindings": {"type": "array", "items": {"type": "object", "properties": {"surface": {"type": "string"}, "id": {"$ref": "#/$defs/NodeId"}}, "required": ["surface", "id"], "additionalProperties": false}}
    }, "required": ["context", "preferred", "forms", "definition", "bindings"], "additionalProperties": false}},
    "ambiguous": {"type": "boolean"},
    "unknown": {"type": "boolean"}
  },
  "required": ["entries", "ambiguous", "unknown"], "additionalProperties": false
}
```

A term that is not in the registry returns `unknown: true`; the tool never guesses a meaning (ADR-0106).

### evidence_get

<!-- schema: evidence_get.input -->
```json
{"type": "object", "properties": {"at": {"$ref": "#/$defs/Selector"}, "claim": {"$ref": "#/$defs/NodeId"}}, "required": ["claim"], "additionalProperties": false}
```

<!-- schema: evidence_get.result -->
```json
{
  "type": "object",
  "properties": {
    "claim": {"$ref": "#/$defs/NodeId"},
    "label": {"enum": ["GENERATED", "PROVED_IN_MODEL", "CHECKED_BOUNDED", "PROVED_MODULO_SOLVER", "SOLVER_TRUSTED", "CONFORMS_BOUNDED", "TESTED", "DECIDED"]},
    "status": {"$ref": "#/$defs/EvidenceStatus"},
    "tcb": {"type": "array", "items": {"type": "string"}},
    "bounds": {"type": "array", "items": {"type": "string"}},
    "assumptions": {"type": "array", "items": {"type": "string"}},
    "statement_digest": {"anyOf": [{"$ref": "#/$defs/Digest"}, {"type": "null"}]},
    "statement_approved_by_owner": {"type": "boolean"},
    "checker": {"type": "object", "properties": {"id": {"type": "string"}, "pin": {"type": "string"}}, "required": ["id", "pin"], "additionalProperties": false},
    "limitations": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["claim", "label", "status", "tcb", "bounds", "assumptions", "statement_digest", "statement_approved_by_owner", "checker", "limitations"], "additionalProperties": false
}
```

The status is recomputed by `assess_link` from the witness and pinned inputs; a supplied status is never read. A model-level label (`PROVED_IN_MODEL`, `CHECKED_BOUNDED`) is never phrased as code correctness; conformance is a separate claim with its own status.

### pack_verify

<!-- schema: pack_verify.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "items": {"type": "array", "minItems": 1, "maxItems": 200, "items": {"type": "object", "properties": {"id": {"$ref": "#/$defs/NodeId"}, "content_hash": {"$ref": "#/$defs/Hash"}}, "required": ["id", "content_hash"], "additionalProperties": false}}
  },
  "required": ["items"], "additionalProperties": false
}
```

<!-- schema: pack_verify.result -->
```json
{
  "type": "object",
  "properties": {
    "items": {"type": "array", "items": {"type": "object", "properties": {"id": {"$ref": "#/$defs/NodeId"}, "state": {"enum": ["unchanged", "changed", "removed", "renamed"]}, "current_hash": {"anyOf": [{"$ref": "#/$defs/Hash"}, {"type": "null"}]}, "renamed_to": {"anyOf": [{"$ref": "#/$defs/NodeId"}, {"type": "null"}]}}, "required": ["id", "state", "current_hash", "renamed_to"], "additionalProperties": false}},
    "all_unchanged": {"type": "boolean"}
  },
  "required": ["items", "all_unchanged"], "additionalProperties": false
}
```

The agent sends what it holds (id and hash); the server does not need to keep the pack. It is the freshness check for agent context: a hash comparison, no clock. `renamed` is reported only when a `renamed_to` record exists.

### snapshot_diff

<!-- schema: snapshot_diff.input -->
```json
{
  "type": "object",
  "properties": {
    "from": {"$ref": "#/$defs/Selector"},
    "to": {"$ref": "#/$defs/Selector"},
    "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 100},
    "cursor": {"$ref": "#/$defs/Cursor"}
  },
  "required": ["from", "to"], "additionalProperties": false
}
```

<!-- schema: snapshot_diff.result -->
```json
{
  "type": "object",
  "properties": {
    "nodes_added": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}},
    "nodes_removed": {"type": "array", "items": {"$ref": "#/$defs/NodeId"}},
    "nodes_changed": {"type": "array", "items": {"type": "object", "properties": {"id": {"$ref": "#/$defs/NodeId"}, "before": {"$ref": "#/$defs/Hash"}, "after": {"$ref": "#/$defs/Hash"}}, "required": ["id", "before", "after"], "additionalProperties": false}},
    "links_changed": {"type": "array", "items": {"type": "object", "properties": {"id": {"$ref": "#/$defs/Digest"}, "before": {"$ref": "#/$defs/LinkStatus"}, "after": {"$ref": "#/$defs/LinkStatus"}}, "required": ["id", "before", "after"], "additionalProperties": false}},
    "findings": {"$ref": "#/$defs/FindingsDelta"}
  },
  "required": ["nodes_added", "nodes_removed", "nodes_changed", "links_changed", "findings"], "additionalProperties": false
}
```

A keyed diff (set difference plus per-node content hash), so the same pair of roots always yields the same bytes. Ids removed without a `renamed_to` record are listed in `nodes_removed`; the rule WV-008 reports them separately.

### codemod_plan

<!-- schema: codemod_plan.input -->
```json
{
  "type": "object",
  "properties": {
    "at": {"$ref": "#/$defs/Selector"},
    "plan": {
      "oneOf": [
        {"type": "object", "properties": {"kind": {"const": "rename_symbol"}, "id": {"$ref": "#/$defs/NodeId"}, "new_name": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]{0,99}$"}}, "required": ["kind", "id", "new_name"], "additionalProperties": false},
        {"type": "object", "properties": {"kind": {"const": "rename_term"}, "term": {"$ref": "#/$defs/NodeId"}, "new_preferred": {"type": "string", "maxLength": 100}}, "required": ["kind", "term", "new_preferred"], "additionalProperties": false},
        {"type": "object", "properties": {"kind": {"const": "add_link_declaration"}, "link_kind": {"$ref": "#/$defs/EdgeType"}, "from": {"$ref": "#/$defs/NodeId"}, "to": {"$ref": "#/$defs/NodeId"}}, "required": ["kind", "link_kind", "from", "to"], "additionalProperties": false},
        {"type": "object", "properties": {"kind": {"const": "regenerate_view"}, "generated": {"$ref": "#/$defs/NodeId"}}, "required": ["kind", "generated"], "additionalProperties": false}
      ]
    }
  },
  "required": ["plan"], "additionalProperties": false
}
```

<!-- schema: codemod_plan.result -->
```json
{
  "type": "object",
  "properties": {
    "editset": {"anyOf": [{"$ref": "#/$defs/EditSet"}, {"type": "null"}]},
    "unresolved": {"type": "array", "items": {"type": "object", "properties": {"site": {"$ref": "#/$defs/NodeId"}, "reason_id": {"enum": ["dynamic_attribute", "string_reference", "ambiguous_resolution", "parse_error", "generated_file", "outside_repository", "protected_path"]}}, "required": ["site", "reason_id"], "additionalProperties": false}},
    "expected": {"anyOf": [{"$ref": "#/$defs/FindingsDelta"}, {"type": "null"}]}
  },
  "required": ["editset", "unresolved", "expected"], "additionalProperties": false
}
```

The tool returns a proposal. It edits nothing. Sites it cannot resolve syntactically or by scope are listed in `unresolved` and are never rewritten by guess. `regenerate_view` returns an `EditSet` with a `commands` entry (the pinned generator and its arguments) and no text edits for the generated file, because a generated view is a get-only projection: it is regenerated, not edited (ARCHITECTURE section 3; hand edits to generated views are rejected, not merged). `add_link_declaration` returns a `graph/links/*.jsonl` line whose digest the checker computed; the line has no `baseline_decision` and so is not COVERED until the owner records one.

## 6. Examples (validated by the test)

`graph_root` and other hashes below are placeholders written as repeated hex digits, except the kernel semantic hashes in the `txn_dry_run` example, which are the real values printed by `graph/bench/agent_interface_checks.py` for the shipped baseline.

<!-- example: graph_impact.response -->
```json
{
  "contract": "eija.weave.mcp.v1",
  "tool": "graph_impact",
  "snapshot": {"graph_root": "sha256:1111111111111111111111111111111111111111111111111111111111111111", "tree_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222", "base_commit": null, "overlay_sha256": null, "dirty": true, "extractor_pins_sha256": "sha256:3333333333333333333333333333333333333333333333333333333333333333", "not_run": ["scip-typescript"]},
  "request_hash": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
  "result": {
    "schema": "eija.weave.impact.v1",
    "roots": ["repo://src/eija_studio/domain/policy.py#apply_transaction"],
    "params": {"max_tier": 1, "budget": 200, "arc_set_sha256": "sha256:6666666666666666666666666666666666666666666666666666666666666666", "flow_table_sha256": "sha256:7777777777777777777777777777777777777777777777777777777777777777", "alpha": [1, 5], "iterations": 78, "err_bound_units": 62000},
    "partial_extraction": false,
    "counts": {"tier0": 1, "tier1": 1, "tier2": 0},
    "affected": [
      {"id": "repo://src/eija_studio/domain/policy.py#apply_transaction", "tier": 0, "distance": 0, "score_ppm": 412000, "witness": null},
      {"id": "repo://tests/test_policy.py#test_reject_requires_meaning", "tier": 1, "distance": 1, "score_ppm": 188000, "witness": null}
    ],
    "envelope": "Covers the edges encoded in the graph; not every real-world consequence."
  },
  "error": null,
  "bounds": {"complete": true, "frontier": [], "frontier_count": 0, "next_cursor": null, "truncated_by": null, "cost_units": 391},
  "response_hash": "sha256:5555555555555555555555555555555555555555555555555555555555555555"
}
```

<!-- example: txn_dry_run.response -->
```json
{
  "contract": "eija.weave.mcp.v1",
  "tool": "txn_dry_run",
  "snapshot": {"graph_root": "sha256:1111111111111111111111111111111111111111111111111111111111111111", "tree_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222", "base_commit": null, "overlay_sha256": null, "dirty": false, "extractor_pins_sha256": "sha256:3333333333333333333333333333333333333333333333333333333333333333", "not_run": []},
  "request_hash": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
  "result": {
    "verdict": "ACCEPTED",
    "kernel_code": null,
    "candidate_semantic_hash": "b26c9af5ae4cd958099956232721a70e73cb7e6efe1b213ff32417829b588e56",
    "base_semantic_hash": "5d3ef3a19c31d956a185b9c5ba4b1b79e651d0356e162436c5c67054d2ad4cdf",
    "model_delta": {"changed_actions": ["Approve", "Recommend", "Reject"]},
    "kernel_impact": {"affected": ["journey:Approve", "journey:Recommend", "journey:Reject", "local-decision", "obligation:Approve", "obligation:Recommend", "obligation:Reject", "receipt:Approve", "receipt:Recommend", "receipt:Reject", "review-packet", "rule:Approve", "rule:Recommend", "rule:Reject", "runtime:Approve", "runtime:Recommend", "runtime:Reject", "state-view:Approve", "state-view:Recommend", "state-view:Reject"], "complete": true, "envelope": "All dependencies encoded by this excursion projection mapping; not every real-world consequence."},
    "ripple": null,
    "findings_delta": null,
    "links_becoming_suspect": [],
    "label": "PREDICTION of a real change; the sets are computed over encoded edges and models, not observed."
  },
  "error": null,
  "bounds": {"complete": true, "frontier": [], "frontier_count": 0, "next_cursor": null, "truncated_by": null, "cost_units": 640},
  "response_hash": "sha256:5555555555555555555555555555555555555555555555555555555555555555"
}
```

`kernel_impact` is the kernel's `model_impact` output for this transaction (20 closure members, `complete: true`), reproduced by `graph/bench/agent_interface_checks.py`. `ripple` and `findings_delta` are null in this example only because no weave graph is attached to the illustrative snapshot.

<!-- example: txn_dry_run.rejected -->
```json
{
  "contract": "eija.weave.mcp.v1",
  "tool": "txn_dry_run",
  "snapshot": {"graph_root": "sha256:1111111111111111111111111111111111111111111111111111111111111111", "tree_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222", "base_commit": null, "overlay_sha256": null, "dirty": false, "extractor_pins_sha256": "sha256:3333333333333333333333333333333333333333333333333333333333333333", "not_run": []},
  "request_hash": "sha256:6666666666666666666666666666666666666666666666666666666666666666",
  "result": {
    "verdict": "REJECTED",
    "kernel_code": "POLICY_BLOCKED",
    "candidate_semantic_hash": null,
    "base_semantic_hash": "5d3ef3a19c31d956a185b9c5ba4b1b79e651d0356e162436c5c67054d2ad4cdf",
    "model_delta": {"changed_actions": []},
    "kernel_impact": null,
    "ripple": null,
    "findings_delta": null,
    "links_becoming_suspect": [],
    "label": "PREDICTION of a real change; the sets are computed over encoded edges and models, not observed."
  },
  "error": null,
  "bounds": {"complete": true, "frontier": [], "frontier_count": 0, "next_cursor": null, "truncated_by": null, "cost_units": 420},
  "response_hash": "sha256:7777777777777777777777777777777777777777777777777777777777777777"
}
```

A rejected transaction is a successful dry run (the tool worked and the kernel refused), so `error` is null. `error` is reserved for tool failures such as `UNKNOWN_NODE`.

<!-- example: error.unknown_node -->
```json
{
  "contract": "eija.weave.mcp.v1",
  "tool": "graph_node",
  "snapshot": {"graph_root": "sha256:1111111111111111111111111111111111111111111111111111111111111111", "tree_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222", "base_commit": null, "overlay_sha256": null, "dirty": false, "extractor_pins_sha256": "sha256:3333333333333333333333333333333333333333333333333333333333333333", "not_run": []},
  "request_hash": "sha256:8888888888888888888888888888888888888888888888888888888888888888",
  "result": null,
  "error": {
    "code": "UNKNOWN_NODE",
    "message_id": "node.unknown",
    "args": {"id": "repo://src/eija_studio/domain/polcy.py", "did_you_mean": ["repo://src/eija_studio/domain/policy.py"]},
    "next": [{"tool": "graph_search", "arguments": {"query": "polcy", "limit": 10}}],
    "retryable": false
  },
  "bounds": {"complete": true, "frontier": [], "frontier_count": 0, "next_cursor": null, "truncated_by": null, "cost_units": 210},
  "response_hash": "sha256:9999999999999999999999999999999999999999999999999999999999999999"
}
```

<!-- example: edit_preview.request -->
```json
{
  "editset": {
    "schema": "eija.weave.editset.v1",
    "id": "sha256:abababababababababababababababababababababababababababababababab",
    "base_root": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
    "producer": {"kind": "codemod", "id": "rename_symbol", "version": 1},
    "applicability": "machine_applicable",
    "files": [
      {"path": "src/eija_studio/domain/impact.py", "precondition_sha256": "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd", "postcondition_sha256": null,
       "edits": [{"start": 120, "end": 127, "old_sha256": "sha256:efefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefef", "new_text": "reach"}]}
    ],
    "renames": [{"old_id": "repo://src/eija_studio/domain/impact.py#closure", "new_id": "repo://src/eija_studio/domain/impact.py#reach"}],
    "commands": []
  }
}
```

Note: `old_sha256` is the SHA-256 of the exact bytes being replaced, so an edit that no longer matches its region fails closed even if the whole-file precondition was somehow bypassed.

<!-- example: context_pack.request -->
```json
{"task": {"intent": "modify", "seeds": ["repo://src/eija_studio/domain/policy.py#apply_transaction"], "seed_terms": ["Semantic Transaction"]}, "budget_units": 8192, "max_level": "slice"}
```

<!-- example: proposal_submit.request -->
```json
{"proposal": {"kind": "link", "link_kind": "verifies", "from": "repo://tests/test_policy.py#test_reject_requires_meaning", "to": "repo://docs/acceptance/matrix.csv#AC-014", "rationale": "The test asserts MEANING_REQUIRED for a rejection edit before the meaning is enabled."}}
```

## 7. Run log (`eija.agent-run.v1`)

One run is a directory `.eija/runs/<run_id>/` (gitignored) with `header.json`, `events.jsonl`, `blobs/<sha256>` and an optional `timing.jsonl` sidecar that is never hashed. `run_id` is the hash of the last event (a `sha256:` digest; the directory name uses its 64 hex digits). All hashed files are RFC 8785 subset JSON, UTF-8, LF, one event per line, no wall clock. An owner may export a redacted bundle into `evidence/agent-runs/<run_id>/`, which makes it an `agent_run` node (`repo://` id, `lf-sha256-v1`).

<!-- schema: run.header -->
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "schema": {"const": "eija.agent-run.v1"},
    "contract": {"const": "eija.weave.mcp.v1"},
    "tool_list_sha256": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
    "tier": {"enum": ["core", "extended"]},
    "trial": {"anyOf": [{"type": "null"}, {"type": "object", "properties": {"task_id": {"type": "string"}, "arm": {"type": "string"}, "index": {"type": "integer", "minimum": 0}}, "required": ["task_id", "arm", "index"], "additionalProperties": false}]},
    "client": {"type": "object", "properties": {"name": {"type": "string"}, "version": {"type": "string"}, "protocol_version": {"type": "string"}, "self_reported": {"const": true}}, "required": ["name", "version", "protocol_version", "self_reported"], "additionalProperties": false},
    "model": {"anyOf": [{"type": "null"}, {"type": "object", "properties": {"id": {"type": "string"}, "self_reported": {"const": true}}, "required": ["id", "self_reported"], "additionalProperties": false}]},
    "provider": {"type": "object", "properties": {"kind": {"enum": ["live", "mocked", "recorded"]}, "egress": {"type": "boolean"}}, "required": ["kind", "egress"], "additionalProperties": false},
    "base_commit": {"anyOf": [{"type": "string", "pattern": "^[0-9a-f]{40}$"}, {"type": "null"}]},
    "overlay_sha256": {"anyOf": [{"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"}, {"type": "null"}]},
    "graph_root0": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
    "extractor_pins_sha256": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
    "prompt_sha256": {"anyOf": [{"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"}, {"type": "null"}]},
    "quota_max_calls": {"type": "integer", "minimum": 1}
  },
  "required": ["schema", "contract", "tool_list_sha256", "tier", "trial", "client", "model", "provider", "base_commit", "overlay_sha256", "graph_root0", "extractor_pins_sha256", "prompt_sha256", "quota_max_calls"],
  "additionalProperties": false
}
```

<!-- schema: run.event -->
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "event": {
      "type": "object",
      "properties": {
        "seq": {"type": "integer", "minimum": 0},
        "kind": {"enum": ["tool_call", "tool_result", "worktree_observed", "model_message", "proposal", "session_close"]},
        "body": {"type": "object"}
      },
      "required": ["seq", "kind", "body"], "additionalProperties": false
    },
    "prev": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
    "hash": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"}
  },
  "required": ["event", "prev", "hash"], "additionalProperties": false
}
```

`hash = dhash("eija.weave.agent-run-event.v1", {"prev": prev, "event": event})` (identity aspect's convention: `"sha256:"` + SHA-256 over the ASCII tag, NUL and the RFC 8785 subset bytes); the first `prev` is `sha256:` followed by 64 zeros. Blob files are named by the 64 hex digits of their digest. Event bodies:

| kind | Body fields | Source of truth |
|---|---|---|
| `tool_call` | `tool`, `arguments` (as received), `request_hash` | server |
| `tool_result` | `request_hash`, `response_hash`, `graph_root`, `is_error`, `blob_sha256` (the full envelope) | server |
| `worktree_observed` | `tree_hash`, `changes[]` of `{path, before_sha256, after_sha256, blob_sha256}` computed at the next tool call after a change | server, from file contents |
| `model_message` | `role`, `blob_sha256`, `origin: "client_transcript_import"` | client transcript (self-reported, unverified) |
| `proposal` | `proposal_id`, `checker_verdict` | server |
| `session_close` | `final_tree_hash`, `final_graph_root`, `findings_digest`, `verdict`, `coverage` (always `tool_boundary_and_worktree_only`), `head_seal` (kernel receipt-signer HMAC over the head hash; an integrity seal, not institutional identity) | server |

The server can observe only its own tool traffic and the worktree; it cannot see model messages or edits made by other tools except through `worktree_observed`. That limit is stated in the design document, section 9.

## 8. Owner-set startup configuration (never tool arguments)

| Setting | Values | Default | Effect |
|---|---|---|---|
| `--graph-tools` | `core`, `extended` | `core` | Fixed tool set for the server process (C-12) |
| `--graph-run-log DIR` | path inside the workspace | `.eija/runs` | Where run logs are written; `off` disables and marks runs non-reproducible |
| `--graph-quota N` | integer | 500 | Maximum tool calls per run (C-15) |
| `--graph-snapshot-cache N` | integer | 8 | Snapshots kept in memory; older roots are rebuilt on demand from `base_commit` plus `overlay_sha256` or return `SNAPSHOT_UNAVAILABLE` |
| `--graph-sql` | flag | absent | Reserved. Would add one read-only SQL tool over the disposable index, opened with `mode=ro`, limited by SQLite virtual-machine instruction count (`set_progress_handler`) and a row cap, never by seconds. Not part of v1 |
| `--graph-worktree-writes` | flag | absent | Reserved. Would add `editset_apply`. Not part of v1; adding it is a governance decision (ADR-0041 precedent) |

## 9. Operations that are absent

None of the following is a tool, argument, resource or prompt on this server. The agents lane's existing test asserts absence of the first eleven for its own tools (ADR-0041); the weave additions extend the same test to the graph tools. Requests for them are protocol errors.

| Absent operation | Why | Where it lives |
|---|---|---|
| `select`, `select_meaning`, `edit`, `layout`, `approve`, `apply`, `discard`, `save`, `reset_preview`, `execute`, `export` | Owner capabilities (`OWNER_ONLY_OPERATIONS` in the agents lane) | Browser Studio, owner principal |
| `ledger_append`, `ack`, `clear_suspect` | Only a human clears a SUSPECT link (ADR-0093/0094) | `eija graph ack`, owner |
| `approve_statement`, `pin_statement` | Statement digests are owner-approved (ADR-0103) | Protected policy, owner |
| `edit_policy`, `edit_schema`, `disable_rule`, `add_suppression`, `grow_baseline`, `edit_checker_registry` | Would let an agent move the goalposts | Protected paths, file-diff gate |
| `mint_receipt`, `assess_override`, `set_status` | Statuses are recomputed, never supplied | Kernel |
| `grant_consent`, `set_egress`, `read_key`, `read_launch_token` | Consent and secrets are the owner's | Server start flags, owner |
| `graph_query` (free-form Cypher or SQL) | Text-to-query errors and unbounded cost; typed tools instead | Reserved flag, section 8 |
| `run_generator`, `run_tool` | The server executes no external process for an agent | Agent's own shell; kernel re-runs pinned tools when it checks |

Protected paths (the `PROTECTED_PATH` set, enforced by `edit_preview` and, independently, by the file-diff gate over the branch): `graph/ledger.jsonl`, `graph/schema/**`, the policy file that holds approved statement digests, `graph/rules/**` severity and enablement, the checker registry and `TOOLS.lock`, `src/eija_studio/resources/trusted_build.json`, `receipt.key`, `noxfile.py` and `quality/sessions/**`, `.github/**`. The exact list is a policy file owned by the owner and hashed into `tool_list_sha256`.

## 10. Change control and conformance

| Check | When | Status today |
|---|---|---|
| Schema validity, example validity, enum and node-id pattern equality with `graph/schema/metamodel.json` (status enums with `graph/brief.json`), index equals blocks, no owner-only tool name | `tests/graph/test_agent_interface_contract.py` (fast) | Implemented with this file |
| `SemanticTransaction` schema equals the kernel's | same test (skips as NOT_RUN if the kernel is not importable) | Implemented with this file |
| Golden `tools/list` and `tool_list_sha256` | agents lane test, after the tools exist | NOT_RUN (no implementation yet) |
| Permutation harness over each tool with a golden request (D-19) | `nox -s graph` full tier | NOT_RUN (no implementation yet) |
| Replay audit of a recorded run (section 7) | release tier | NOT_RUN (no implementation yet) |
| Windows and POSIX byte-identical goldens | release tier | NOT_RUN on POSIX |

Version rule: any change to a schema, description, default or cap changes `tool_list_sha256` and needs an ADR amendment. The `contract` constant changes (`eija.weave.mcp.v2`) only for a breaking change; additive changes keep `v1` and are visible through the hash.
