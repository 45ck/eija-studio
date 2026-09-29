# Human views: definitions, slices, projections and budgets

Lane: weave, aspect human-views. Date: 2026-09-29. Status: DESIGN (proposal for ADR-00101, see `docs/adr/00101-weave-human-views.md`). Rationale, evidence and worked numbers are in `docs/weave/design/human-comprehension-views.md`; this file is the definition. Nothing here is built except the executable reference definitions `graph/bench/human_views_reference.py`, the measurement script `graph/bench/human_views_budgets.py` and `tests/graph/test_human_views.py`, which check the definitions and measure sizes on this repository.

Labels: MEASUREMENT (a script ran, domain stated), PREDICTION (reasoned, not run), HYPOTHESIS (a starting value to be calibrated), DESIGN (a proposal of this lane). Every number in the `budgets` of section 8 is a HYPOTHESIS. The HCI lane implements the UI; a change to a budget is a reviewed diff of this file.

## 1. What a human view is

A human view is a pure function `view(snapshot, params) -> document`. It reads the canonical typed graph (facts, links, ledger, findings) at one Merkle root, applies a **slice** (which nodes and links), a **projection** (rows, columns, groups, order), and a **budget** (how much may be shown before counts replace items). It stores nothing, edits nothing, and never decides a status: statuses come from the weave status algebra (`fold_a`, the join, only for repeated observations of one claim by one check; `fold_b`, the chain minimum, for every roll-up across distinct items or claims; `LIFT` from link status; proposal in ADR-0101 of the allocation table). The HCI lane renders the document; the agents lane exposes the same document as a read-only tool result.

Two kinds of order are kept apart. **Data order** is part of the document and of `definition_digest`: total orders on ids, and the status chain `chain_worst_first` of section 8, which fixes the badge label and which rows survive a cap. **Display order** (which status is drawn first, colour, glyph, layout) is presentation and belongs to the HCI lane: it may reorder or restyle rows that are already in the document, and it never changes a byte of one. Anything that decides which rows or which badge are in the document is data, not display.

Data views versus human views. `metamodel.json` defines six *data views* (`assurance`, `governance`, `language`, `structure`, `trace`, `ui`): subsets of link types that get one Merkle root each. They are inputs here. The eight *human views* below (`HV-01` to `HV-08`) are what a person reads. Do not confuse them with the HCI lane's screens or with ProofMap Lite's model views.

## 2. Envelope common to all views

Human views reuse the conventions of the agent tool contract (`graph/schema/mcp-tools.md`, `eija.weave.mcp.v1`, section 3 and rules C-01 to C-18): the same `snapshot` and `bounds` objects, `Finding`, `Step` and `Text` definitions, integers only, sorted lists, untrusted repository prose only inside a `Text` object (HCI invariant I5). A view is not a second implementation: where an agent tool exists its result is the input, and the human document adds the projection (section 12).

```text
{ "schema": "eija.view.<name>/v1",
  "view": "HV-03",
  "snapshot": { "graph_root": hex64, "tree_hash": hex64, "base_commit": sha1|null, "overlay_sha256": hex64|null,
                "dirty": bool, "extractor_pins_sha256": hex64, "not_run": [ids, sorted] },      as mcp-tools.md "Snapshot"
  "base_snapshot": { ...same shape... } | null,      only views that compare two snapshots (HV-01, HV-02, HV-06, HV-07)
  "definition_digest": hex64,                       SHA-256 of the JCS form of the json block of section 8
  "bounds": { "complete": bool, "frontier": [ids, at most 50], "frontier_count": n, "next_cursor": null|opaque,
              "truncated_by": null|"limit"|"budget"|"hard_cap", "cost_units": n },           as mcp-tools.md "Bounds"
  "counts": { "in_scope": n, "by_status": {PASS,FAIL,CONFLICT,STALE,UNKNOWN,NOT_RUN}, "gap": n, "not_applicable": n },
  "overflow": [ { "group": id, "shown": n, "hidden": n, "hidden_by_status": {...} } ],   sorted by group
  "payload": { ... per view, section 6 }
}
```

`snapshot.dirty` is shown at L0: a view computed from an uncommitted worktree says so. `snapshot.not_run` names the extractors or tools that did not run; the reason text comes from the extractor record. Serialisation follows ADR-0091 (RFC 8785 subset): strings, safe integers, booleans, null; **no floats and no percentages**; keys sorted; no timestamps, GUIDs, absolute paths, or layout coordinates other than the integer grid of HV-08. `definition_digest` lets a consumer detect that a budget or mapping changed.

## 3. Counting model (the arithmetic every view shares)

**Item state.** An *item* is a node that an obligation applies to (for example a requirement under WV-010). Its state is a pair `(status, gap)` with `status` in the six evidence values and `gap` a boolean, or the marker `not_applicable` when policy exempts the item. `gap = true` means "a required link is absent"; the status of such an item is whatever the weave fold returns for an empty slot (proposal: see open question 2 of the design document). Views never invent this value.

**Counts vector.** For a set of items `I`, `c(I)` is the vector `(n_PASS, n_FAIL, n_CONFLICT, n_STALE, n_UNKNOWN, n_NOT_RUN)` of non-negative integers, plus `gap(I)` (items with `gap = true`, a subset of the items counted by status) and `na(I)` (not applicable items, outside the six).

**Laws** (they are what makes semantic zoom safe). Checked today by `tests/graph/test_human_views.py` on the reference definitions: C1, C2, C4, C5. C3 and C6 need the implemented views and are NOT_RUN:

| Id | Law | Why it matters |
|---|---|---|
| C1 | `c(A union B) = c(A) + c(B)` for disjoint `A`, `B` (vector addition) | a container's counts are the sum of its children's, at every zoom level |
| C2 | `sum(c(I)) + na(I) = |I in scope|` | nothing disappears; `not applicable` is visible, never silently dropped |
| C3 | `gap(I) <= n_UNKNOWN(I) + n_NOT_RUN(I)` under the current proposal for empty slots | a gap is never counted as PASS |
| C4 | The badge of a container is `fold_b` (chain minimum, `chain_worst_first`; empty is NOT_RUN) applied to the *set of statuses present* (support of `c`). It is PASS if and only if every item in the container is PASS. `fold_a` (the join) is never a badge operator: `join(PASS, NOT_RUN)` is PASS, so it would show a container holding an unrun item as green | one badge operator across items; a container cannot look green while an item is NOT_RUN, UNKNOWN, STALE, FAIL or CONFLICT. The badge is computed from counts, not from child badges, only so that an empty child container (NOT_RUN) does not lower a non-empty sibling |
| C5 | Every shown row count plus `overflow.hidden` equals the group size | "N more" is exact |
| C6 | Sum of the cells of HV-03 by status equals the L0 counts of HV-03, and equals the counts of the matching container rows of HV-04 | overlap agreement between views (section 9) |

C1 makes `c` a homomorphism from (multisets of items, union) to (vectors, addition), a commutative monoid: the result does not depend on grouping or order, which is also why it is deterministic.

## 4. Progressive disclosure levels

| Level | Meaning | Content rule |
|---|---|---|
| L0 | Always visible with the view | Counts by status, the gap count, `snapshot.not_run` with reasons, `snapshot.dirty`, `bounds.complete`, and the body at its default expansion. Non-PASS is never absent from L0. |
| L1 | One selection or expansion away | The inspector of one row or cell: links, tiers, evidence, first witness step. |
| L2 | Explicit "source" request | Raw fact JSON, hash method and digests, the full witness, the line or JSON diff. |

At most two levels after L0 (HCI principle P10, `NN/g` rule of thumb: no evidence base cited by the article). UNKNOWN, NOT_RUN, STALE, FAIL, CONFLICT and `not_run` reasons are L0.

## 5. Overflow, filters, hidden counters

**Priority-then-cap.** A list that exceeds its cap is ordered by the key `(severity rank, distance or depth, id)` *before* cutting, so the shown items are the worst ones, and `overflow` reports `hidden` and `hidden_by_status`. The severity rank is the position in `chain_worst_first` (section 8): it decides what is shown and what is hidden, so it is data and is covered by `definition_digest`; a renderer may reorder the shown rows for display but never chooses the cut. Trees and matrices do not cap: their order is structural (sibling order is model-derived, HCI decision D10) and they page or collapse instead.

**Filters.** Any filter a UI applies must report, for the rows it hides, the counts by status of every non-PASS state (HCI decision D7). The view document therefore always carries the unfiltered counts; the UI subtracts nothing from them.

**Empty states.** A view with no items states why: `roots equal` (no change), `no obligation applies`, `extractor not run` (with its reason), or `budget reached` with the frontier. It is never an empty pane.

## 6. The eight views

Machine-readable form: the JSON block in section 8. The table is the reading form.

| Id | Name | Question | Tasks (HCI ids) | Default form | Slice | Projection and order | Budget (see section 8) |
|---|---|---|---|---|---|---|---|
| HV-01 | change-digest | What did this change do, in the model's own terms? | T02 | grouped outline of operations | nodes and links whose canonical digest differs between `base_snapshot` and `snapshot`, plus `renamed_to` records | operation ADDED, MODIFIED, REMOVED, RENAMED; chapters core, consequences, glue; inside a chapter, dependency order (section 7.3), ties by id; null-edit counter; one line of the impact aspect's change-risk vector (exact counts, no score) | 4 top-level chunks |
| HV-02 | ripple | What does the change touch, how sure are we, and what was not analysed? | T03, T05, T12 | outline by tier then node type, with counts | closure of the impact flow (metamodel `affects`) from the changed nodes of HV-01, per soundness tier; not analysed = frontier plus NOT_RUN or partial extractors | tiers sound, over-approximate, heuristic, not analysed; inside a tier, node type; inside a type, `(severity, distance, id)` capped | 4 tier chunks, 5 rows per type |
| HV-03 | trace-matrix | For each requirement: satisfied and verified by which kinds of evidence, and is each link fresh? | T14, T06, T12 | matrix, rows requirement-like items sorted by `area` then id, columns evidence slots | metamodel data views `trace` and `assurance`; rows: `requirement`, `invariant`, `transition` that are targets of an obligation; columns: link kinds with `trace: true` or an evidence class, at most 7 | cell = fold of link statuses in the slot; rows sorted `(area, id)`, a group header only for an area of two or more rows (measured: 17 of 22 areas in this repo are singletons); columns in the fixed slot order of the coverage policy | 25 rows per page, 7 columns |
| HV-04 | coverage-map | Where are the gaps, by area? | T14, T12 | outline of containers with counts vectors | the `contains` hierarchy plus every metamodel obligation (WV-010, 011, 031, 037, 053, 054) | container row = counts vector of its subtree, gap and not-applicable counts, badge from C4; order structural | depth 4, 15 rows at default expansion |
| HV-05 | language-tree | What does the language mean and where is each term bound? | T05, T09 | tree | metamodel data view `language` plus the workflow layer (states, transitions, roles) | kind letter by `ddd_role` (section 7.6); own status by obligations; bindings with tier; homonym marks | depth 4, default expansion 2 levels |
| HV-06 | diagnostics | What is wrong or unproven, why, and what may I do? | T11, T12, T14, T06 | list grouped by rule | findings (rule id, level, args, locations, witness, fingerprint, baseline state, suppression) and `not_run` records | chunks error, warning, note, not run; inside: rule id, location, fingerprint; new-since-base first | 4 chunks, 5 rows per rule group |
| HV-07 | explain | Why is this here, or why not? | T03, T05, T11, T12 | one witness chain, a contrast, limits | provenance of one link, fact, status or finding (section 7.4) | at most 4 segments, then expand; closed set of question kinds | 4 segments, 12 hops listed |
| HV-08 | neighbourhood | How do these things connect? | T03, T12 | bounded node-link diagram plus an edge table | best-first expansion from a focus over chosen link kinds (section 7.5) | integer grid: rank by signed distance, slot by `(link kind, id)` | 20 nodes, 50 on expand, 100 hard stop |

Form follows the question class (design document, section 3): outline for hierarchy and gaps, matrix for exhaustive requirement-by-evidence enumeration, ordered list for findings, witness chain for "why", node-link only for bounded neighbourhoods and path questions.

## 7. Definitions used by the views

### 7.1 Tiers

Soundness classes come from the metamodel (`must`, `may`, `heuristic`). For a changed set `R` let `R_0 subset R_1 subset R_2` be the impact closures over links of class at most 0, 1, 2 (must; must and may; all). The **tier of a node** is the least `c` with the node in `R_c`, equivalently the best over all paths of the weakest link on the path (a maximin path). The tier is reported with the distance in that closure and the canonical witness of section 7.4. Direct = distance 1, transitive = distance 2 or more (OpenFastTrace vocabulary, own implementation).

### 7.2 Null edits and RENAMED

A node is a **null edit** in a change when the digest of its containing file under `lf-sha256-v1` differs between the two roots but its own digest under the node's hash method (metamodel `methods`, for example `ast-v1`) is equal. Null edits are counted per method and never listed unless the reader asks; the counter always names the method ("not compared under `ast-v1`") because a normaliser can hide a change that mattered (traceability dossier, section 2). A node has no null-edit notion under `lf-sha256-v1`. `RENAMED` comes from an explicit `renamed_to` record, never from similarity.

### 7.3 Chapters and order in HV-01

`chapter(x)`: `consequences` if the node's truth class is `evidence` (any layer), or its truth class is `derived` and its layer is `views` or `knowledge` (diagrams, generated pages), or `x` is reachable from another changed node by `derived_from` links (all `must`); otherwise `core` if its layer is `workflow`, `language` or `requirements`; otherwise `glue`. Layers and truth classes are the `layer` and `truth` fields of `metamodel.json`. Order inside a chapter: the lexicographically smallest topological order of the changed nodes under the `precedes` relation (`order_edges` in section 8) after collapsing strongly connected components labelled by their minimum member id; ties by `(type, id)`. Executable definitions: `graph/bench/human_views_reference.py` (`chapters`, `dependency_order`).

### 7.4 Witness and question kinds (HV-07)

Question kinds are a closed set: `why_affected`, `why_not_affected`, `why_status`, `why_link`, `why_finding`. The answer extends the agent contract's `graph_why` result (`holds`, `rule_id`, `premises`, `witness`, `searched_scope`, `rechecked`) with `{ sentence_id, args, truth_class, soundness, segments, contrast, limits, reproduce, actions }`.

* **Witness.** For a derived fact, the canonical minimal derivation: the lexicographically first shortest path over sorted neighbours, from a root to the subject, through the least tier that reaches it. For a declared link: the declaring file location, hash method, baseline digest and ledger sequence. For an inferred link: tool, model, version and the run that proposed it, labelled proposal. For a finding: the rule id and the rows that made the violation query non-empty.
* **Segments.** Consecutive hops with equal `(link kind, origin class, tier)` are one segment with a hop count. The default view shows at most 4 segments; expanding lists at most 12 hops; a longer path is listed by the reproduce command.
* **Selected cause.** One witness is shown, the count of other shortest paths is an integer (`n_paths`), and `path_rank` lets the reader ask for the next in deterministic order. No probabilities.
* **Contrast.** The foil is the baseline: what the status, digest or reach was in `base_snapshot`, and the first node and field that differs. For an absence (`why_not_affected`, a missing link) the contrast is the closed-world scope that was searched: relations, node count, and `complete`. If the closure is incomplete the answer is `UNKNOWN: not proven unaffected` with the frontier count.
* **Actions.** Proposals for the owner as text (`ack LINK --reason`, add a link, run a check). `applies` is always false; no view offers approve, apply, clear or edit, and no agent tool returns a command that does (invariant I4 of the HCI lane).

### 7.5 Neighbourhood selection (HV-08)

Best-first expansion from a focus `f` over the chosen link kinds (default: the metamodel data view `structure`), undirected for distance. Priority of a candidate `x` is the integer `DOI(x | f) = API(x) - D(f, x)`, where `D` is the shortest-path length from the focus in the undirected graph (breadth-first distances computed before selection, not the depth at which the expansion happened to reach `x`; the reference checks a case where the two differ) and `API(x) = w(type(x)) + 4 * [status(x) != PASS]` with `w` the type weights of section 8 (HYPOTHESIS; inspired by degree-of-interest functions in the literature, the weights are this lane's). Candidates are popped in order `(DOI descending, id ascending)` and a node is selectable only after its parent in the expansion tree was selected, so the result is connected. Stop at the node budget. Non-PASS nodes get a bonus so a problem is not crowded out by healthy neighbours. Complexity `O(E log V)`; integers only.

Deterministic layered grid (no force-directed layout, which uses floats and seeds): `rank(x)` is minus the distance for nodes first reached by an incoming link, plus the distance otherwise (ties go to the outgoing side); `slot(x)` is the index of `x` among nodes of equal rank sorted by `(link kind of the connecting link, id)`. The document carries `(rank, slot)` integers; drawing them as boxes and curves is the UI lane's job. A layout the user drags is a layout complement keyed by id (HCI principle P3), not part of the document.

### 7.6 Kind letters for the language tree (HV-05)

`bounded_context` is `C`; a `term` with `ddd_role` `aggregate` is `A`, `entity` is `E`, `value_object` is `V`, any other role or `concept` is `T`; an `invariant` is `I`. Workflow layer nodes (`state`, `transition`, `role`, `guard`, `effect`) appear as `T` children of the derived `Workflow Definition` aggregate, as the HCI lane specified for stage 1. Tiers of a binding: `kernel` = class `declared` or `derived` with soundness `must` or `tool-resolved` provenance; `text match` = class `derived`, soundness `heuristic`, provenance `syntactic` or `candidate`; `unknown` = extractor not run or unresolved. Inferred links (`proposes`) are shown only as proposals.

### 7.7 Optional L1 details (report only, never a gate)

* HV-02 `verification_cover`: the greedy weighted set cover (ties by `(cost, id)`) of the impacted obligations by the verifiers that cover them, with the harmonic bound of the greedy algorithm stated. It answers "which small set of verifiers covers what this change touches": minimum set cover is NP-hard, the greedy set is within a factor `H(n)` (the n-th harmonic number, n the largest number of obligations one verifier covers) of the minimum, and it is not claimed to be the minimum. Label: a `covers` or `verifies` link is not fault detection (mutation lane calibrates).
* HV-03 row `evidence_redundancy`: the number of vertex-disjoint evidence paths from the requirement, capped at 3, and the canonical minimum cut when it is 1 (single point of evidence, rule WV-014). A count, not a risk score.

## 8. Machine-readable definition

The block below is the single source for budgets and mappings. `tests/graph/test_human_views.py` parses it and checks the chunk budgets, the totality of the node and link mappings against `graph/schema/metamodel.json`, that no view offers an owner-only operation, and that the definition carries no float; the laws of section 3 are checked on the reference definitions. `graph/bench/human_views_budgets.py` reads the budgets and measures slice sizes on this repository.

```json views-definition
{
  "schema": "eija.weave.human-views/v1",
  "label": "DESIGN. Every number under budgets is a HYPOTHESIS to be calibrated by the hci lane; nothing here is a measured benefit.",
  "status_values": ["PASS", "FAIL", "CONFLICT", "STALE", "UNKNOWN", "NOT_RUN"],
  "chain_worst_first": ["FAIL", "CONFLICT", "STALE", "NOT_RUN", "UNKNOWN", "PASS"],
  "chain_note": "DATA order, hashed into definition_digest: the chain of the badge operator fold_b (worst first, PASS last) and the severity rank of priority-then-cap. PROPOSAL equal to eijaref.status DEFAULT_CHAIN; the order among non-PASS values awaits the status ADR. That a badge is PASS only if every item is PASS does not depend on it. The HCI display order is not in this block: it may reorder rows after the cut, never before.",
  "budgets": {
    "chunks_top_level_max": 4,
    "disclosure_levels_after_l0_max": 2,
    "tree_depth_max": 4,
    "l0_rows_max": 25,
    "rows_before_more": 5,
    "matrix_rows_per_page_max": 25,
    "matrix_columns_max": 7,
    "matrix_cells_max": 175,
    "coverage_default_rows_max": 15,
    "neighbourhood_nodes_default_max": 20,
    "neighbourhood_nodes_expanded_max": 50,
    "neighbourhood_nodes_hard_stop": 100,
    "out_degree_shown_max": 7,
    "witness_segments_default_max": 4,
    "witness_hops_listed_max": 12,
    "closure_node_budget_default": 2000,
    "document_latency_target_ms": 1000
  },
  "budget_basis": {
    "chunks_top_level_max": "HCI principle P4 (about 4 chunks per change); Cowan 2010 (3 to 5 chunks); HYPOTHESIS",
    "disclosure_levels_after_l0_max": "HCI principle P10; NN/g 2006 rule of thumb without cited evidence; HYPOTHESIS",
    "tree_depth_max": "HCI language-tree decision D1; HYPOTHESIS",
    "l0_rows_max": "HCI language-tree layout: 26 rows of 28 px fit in 748 px at 1440x900 (PREDICTION from layout); HYPOTHESIS",
    "rows_before_more": "HCI inspector chip list: at most 5 rows before scroll; HYPOTHESIS",
    "matrix_columns_max": "HCI hick.max_choices target 7; HYPOTHESIS",
    "neighbourhood_nodes_default_max": "Ghoniem, Fekete, Castagliola 2005: matrices outperform node-link beyond 20 vertices on most tasks (dense random graphs); Okoe et al. 2019 show sparse graphs of 258 to 332 nodes remain workable for topology tasks with interaction; HYPOTHESIS between the two",
    "neighbourhood_nodes_expanded_max": "Ghoniem et al. tested 20, 50 and 100 vertices; HYPOTHESIS",
    "out_degree_shown_max": "Ware et al. 2002: branches on the path raise path-following cost; HYPOTHESIS",
    "witness_segments_default_max": "same chunk budget as HV-01; HYPOTHESIS",
    "closure_node_budget_default": "equals the maximum of graph_impact.max_nodes in mcp-tools.md; impact.closure takes a node budget and reports complete and frontier; HYPOTHESIS for the value",
    "document_latency_target_ms": "HCI principle P7 latency class 1 s for a view switch; PREDICTION until measured"
  },
  "type_weights": {"requirement": 4, "invariant": 4, "transition": 4, "term": 4, "symbol": 3, "test": 3, "module": 2, "document": 2, "default": 1},
  "views": [
    {"id": "HV-01", "name": "change-digest", "tasks": ["T02"], "default_form": "outline", "alt_forms": ["keyed-diff-json", "line-diff"],
     "chunks": ["core", "consequences", "glue", "hidden_null_edits"], "compares_two_roots": true},
    {"id": "HV-02", "name": "ripple", "tasks": ["T03", "T05", "T12"], "default_form": "outline", "alt_forms": ["neighbourhood"],
     "chunks": ["sound", "over_approximate", "heuristic", "not_analysed"], "compares_two_roots": true},
    {"id": "HV-03", "name": "trace-matrix", "tasks": ["T14", "T06", "T12"], "default_form": "matrix", "alt_forms": ["outline"],
     "rows_per_page_max": 25, "columns_max": 7, "compares_two_roots": false},
    {"id": "HV-04", "name": "coverage-map", "tasks": ["T14", "T12"], "default_form": "outline", "alt_forms": ["matrix"],
     "depth_max": 4, "default_rows_max": 15, "compares_two_roots": false},
    {"id": "HV-05", "name": "language-tree", "tasks": ["T05", "T09"], "default_form": "tree", "alt_forms": ["matrix"],
     "depth_max": 4, "default_expansion_levels": 2, "compares_two_roots": false},
    {"id": "HV-06", "name": "diagnostics", "tasks": ["T11", "T12", "T14", "T06"], "default_form": "grouped-list", "alt_forms": ["sarif", "text"],
     "chunks": ["error", "warning", "note", "not_run"], "rows_per_group": 5, "compares_two_roots": true},
    {"id": "HV-07", "name": "explain", "tasks": ["T03", "T05", "T11", "T12"], "default_form": "witness-chain", "alt_forms": ["reproduce-command"],
     "segments_max": 4, "hops_listed_max": 12, "question_kinds": ["why_affected", "why_not_affected", "why_status", "why_link", "why_finding"], "compares_two_roots": true},
    {"id": "HV-08", "name": "neighbourhood", "tasks": ["T03", "T12"], "default_form": "node-link", "alt_forms": ["edge-table"],
     "nodes_default_max": 20, "nodes_expanded_max": 50, "nodes_hard_stop": 100, "compares_two_roots": false}
  ],
  "chapters": {
    "core_layers": ["workflow", "language", "requirements"],
    "consequence_truth": ["evidence"],
    "consequence_layers_derived": ["views", "knowledge"],
    "override": "reachable from another changed node by derived_from links: consequences"
  },
  "order_edges": {
    "note": "a precedes b in HV-01 when a is a definition or source of b; link kind, direction of precedence",
    "contains": "source_first",
    "derived_from": "target_first",
    "names": "target_first",
    "satisfies": "target_first",
    "verifies": "target_first",
    "depends_on": "target_first",
    "realises": "target_first",
    "refines": "target_first"
  },
  "node_type_views": {
    "module": ["HV-02", "HV-04", "HV-08"],
    "symbol": ["HV-02", "HV-08"],
    "contract": ["HV-02", "HV-08"],
    "api_operation": ["HV-02", "HV-08"],
    "workflow": ["HV-05"],
    "state": ["HV-05", "HV-02"],
    "transition": ["HV-05", "HV-03", "HV-02"],
    "role": ["HV-05"],
    "guard": ["HV-05"],
    "effect": ["HV-05"],
    "bounded_context": ["HV-05", "HV-04"],
    "term": ["HV-05", "HV-02"],
    "invariant": ["HV-05", "HV-03"],
    "requirement": ["HV-03", "HV-04"],
    "adr": ["HV-07"],
    "persona": ["HV-04"],
    "journey": ["HV-04", "HV-02"],
    "document": ["HV-06", "HV-07"],
    "lane": ["HV-04"],
    "gate": ["HV-06"],
    "test": ["HV-03", "HV-02"],
    "property": ["HV-03"],
    "formal_model": ["HV-03"],
    "formal_law": ["HV-03"],
    "witness": ["HV-03", "HV-07"],
    "tool": ["HV-06", "HV-07"],
    "evidence": ["HV-03", "HV-07"],
    "link_certificate": ["HV-07"],
    "claim": ["HV-04"],
    "decision": ["HV-06", "HV-07"],
    "agent_run": ["HV-07"],
    "ui_view": ["HV-04", "HV-08"],
    "ui_region": ["HV-04"],
    "ui_control": ["HV-04", "HV-03"],
    "ui_field": ["HV-04"],
    "ui_status": ["HV-04"],
    "ui_table": ["HV-04"],
    "design_token": ["HV-06"],
    "diagram": ["HV-06"],
    "diagram_element": ["HV-06"],
    "okf_page": ["HV-06", "HV-07"],
    "component": ["HV-04", "HV-08"]
  },
  "link_type_views": {
    "contains": ["HV-04", "HV-05"],
    "depends_on": ["HV-08", "HV-02"],
    "flows_to": ["HV-05", "HV-08"],
    "calls": ["HV-08", "HV-02"],
    "exposes": ["HV-08"],
    "realises": ["HV-05", "HV-03"],
    "satisfies": ["HV-03"],
    "verifies": ["HV-03"],
    "refines": ["HV-03", "HV-04"],
    "covers": ["HV-03", "HV-02"],
    "names": ["HV-05"],
    "documents": ["HV-07"],
    "motivates": ["HV-07"],
    "supersedes": ["HV-07"],
    "derived_from": ["HV-06", "HV-01"],
    "models": ["HV-03"],
    "conforms_to": ["HV-03"],
    "proves": ["HV-03"],
    "formalises": ["HV-03"],
    "exercised_by": ["HV-03", "HV-04"],
    "styled_by": ["HV-06"],
    "attests": ["HV-03", "HV-07"],
    "checked_by": ["HV-07"],
    "supports": ["HV-04"],
    "defeats": ["HV-04"],
    "decides": ["HV-07", "HV-06"],
    "renamed_to": ["HV-01"],
    "proposes": ["HV-01", "HV-07"],
    "serves": ["HV-04"]
  },
  "not_shown": {}
}
```

Any node type or link type that appears in `graph/schema/metamodel.json` and not in the two mappings is a `WV-028` style finding (view mapping totality): add it to a view or to `not_shown` with a reason. HV-01, HV-06 and HV-07 may additionally show any node type by id (as the subject of an operation, the location of a finding, a step of a witness); the mappings list the *primary* role only.

## 9. Overlap agreement between views

Views that share ids must agree on the shared facts; disagreement is a located finding, not a rendering choice. Checked today: X4 and X6 (reference definitions). X1 to X3 need the implemented views, and X5 needs the closure certificate checker wired to the views: NOT_RUN.

| Id | Statement | Check |
|---|---|---|
| X1 | Sum of HV-03 cells by status equals HV-03 `counts.by_status` | property test, seeded |
| X2 | HV-04 container counts equal the sum over its descendant items in HV-03 for obligations WV-010 and WV-011 | property test |
| X3 | Number of SUSPECT links in HV-06 (rule WV-005) equals the number of HV-03 cells with `suspect = true` | fixture |
| X4 | HV-02 tier 0 set is a subset of tier 1 set, which is a subset of tier 2 set | property test (nested closures) |
| X5 | Every node id in a HV-07 witness exists in the snapshot at `root`, and every hop is a link that exists | witness re-check (the closure certificate checker of the formal aspect) |
| X6 | HV-01 `MODIFIED` plus `ADDED` plus `REMOVED` plus `RENAMED` counts equal the keyed diff size, and null edits are disjoint from listed operations | property test |

## 10. Determinism checklist for a view builder

D-01 sorted by a total key at every step; D-02 JCS subset, integers only; D-04 no clock; D-05 repo-relative POSIX ids; D-07 no set iteration reaches output; D-09 no library default order (`nx.condensation`, `graphlib`); D-10 no floats: shares are printed as `n of m`; D-12 digests domain-separated; D-23 identity by id, never by label. Labels and prose are attributes; the only strings a person reads that are produced by the view are sentence templates identified by `sentence_id` with structured `args`, expanded by the renderer.

## 11. Text rendering

Every view has a lossless text form: the document rendered as UTF-8, LF, fixed column widths, statuses as words (not colour), one line per row, `n of m` for shares, the L0 line first: `14 PASS, 8 UNKNOWN (1 gap), 1 NOT_RUN, 0 FAIL, 0 CONFLICT, 0 STALE`. The text form is what a pull-request comment, a CLI, an OKF `facts` block and an agent read; it is golden-tested by the implementing lane. Not built in this lane.

## 12. Interface requirements on the store and the other aspects

Provider tool = the agent tool whose result a view projects (`graph/schema/mcp-tools.md`). The human document is computed server-side by the same functions with human budgets; agent caps (for example `limit`, `max_nodes`) do not apply to counts, only to lists.

| View | Provider tool or function | What the view adds | What is missing today (request to the owning aspect) |
|---|---|---|---|
| HV-01 | `snapshot_diff`; impact aspect risk vector (IR-7) | chapters, dependency order, null-edit counter | `snapshot_diff` reports a node only when its hash under the node's own method changed, so a null edit (file digest changed, node digest equal) is invisible; request: `null_edits_by_method` counts (and optionally ids) with file-level `lf-sha256-v1` before and after |
| HV-02 | `graph_impact` (`by_soundness.must`, `.may`, `.heuristic_only`, `witnesses`, `bounds`) | tiers named sound, over-approximate, heuristic; type grouping; direct vs transitive (needs distance); not analysed from `snapshot.not_run` and `bounds.frontier` | `distance` per node is in the reference (`tiered_impact`) but not in the tool result |
| HV-03 | `link_status`; `evidence_get`; metamodel `obligations` | cells, gap flags, totals, paging | no tool lists required slots per requirement; the builder reads `obligations` from the metamodel |
| HV-04 | store `contains` hierarchy; `diagnostics_get` for the gap rules (WV-010, 011, 031, 037, 053, 054) | counts vectors, badges | none beyond the store |
| HV-05 | `language_lookup`; `graph_neighbors` over `names`, `realises`, `contains` | tree, kind letters, tiers of bindings | term registry (language aspect) |
| HV-06 | `diagnostics_get` (`Finding`, `baseline_state`); `diagnostics_explain` | grouping, chunks, new-first order, NOT_RUN as findings of level `not run` | none |
| HV-07 | `graph_why` (`holds`, `rule_id`, `premises`, `witness`, `searched_scope`, `rechecked`) | segments, contrast, limits, actions text | `Step` has `from, edge, to` only; segments need `origin` and `soundness` per hop (the builder joins them from the store; request to extend `Step` if agents want the same segments) |
| HV-08 | `graph_neighbors` | best-first selection, integer grid | none |
| run report | defined in the agent-interface design (section 9.5, `eija graph run-report`) | not duplicated here; it follows this file's envelope, budgets and counting laws | |

Other needs: keyed diff and a store of link status and ledger sequence (ADR-0093 numbering of the allocation table), the status fold (`fold_a`, `fold_b`, `LIFT`, reference `graph/formal/eijaref/status.py`), the term registry, and the closure certificate checker (`check_certificate`, `check_unreachable`, reference `graph/formal/eijaref/closure.py`). Without a prerequisite a view reports NOT_RUN in `snapshot.not_run`; it never guesses.
