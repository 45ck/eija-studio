---
type: Architecture Decision Record
title: 'ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture'
description: The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce findings.
resource: repo://docs/adr/0105-weave-human-views.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0105-weave-human-views.md
  title: 0105-weave-human-views.md
  hash_method: lf-sha256-v1
  sha256: 266ae51b9025fc2063a3cf8c381bfbb1d1562f4b355fdc041b08da59c55015f3
notes_baseline: d0f3eb226c120a6b28e1b505bc8e5e0fd94b2e40c21d95e42a0b654284539ee7
---

# ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Lane | weave (aspect human-views). Design, evidence and arithmetic: [docs/weave/design/human-comprehension-views.md](repo://docs/weave/design/human-comprehension-views.md). Definitions, slices, projections and budgets, machine-checked: [graph/schema/views.md](repo://graph/schema/views.md). Reproducible checks: `graph/bench/human_views_reference.py`, `graph/bench/human_views_budgets.py`, `tests/graph/test_human_views.py` (30 passed on 2026-09-29, revised after audit). |
| Source | `repo://docs/adr/0105-weave-human-views.md` |

## Decision outcome (verbatim)

> Chosen option: "B", because it is the only option that is deterministic, budgeted, checkable against the compiler, and consistent with the evidence that the task decides the form. The decisions, each detailed in the design document:
>
> 1. **Eight human views** (`HV-01` to `HV-08`): change digest, ripple, trace matrix, coverage map, language tree, diagnostics, explain, neighbourhood. Each is a pure function `view(snapshot, params) -> document`; it stores and edits nothing; it reuses the agent contract's `snapshot`, `bounds`, `Finding`, `Step` and `Text` definitions and the same server-side functions. The HCI lane renders; the agents lane serves the same documents read-only.
> 2. **Form follows the question**: outline for hierarchy, roll-ups and gaps; matrix for requirement-by-evidence enumeration (rows sorted by `(area, id)`, at most 7 columns, 25 rows per page); grouped list for findings; one witness chain for "why"; node-link only for a bounded neighbourhood (20 nodes default, 50 on expand, hard stop 100). A whole-graph picture is not a view.
> 3. **Budgets** (chunks, disclosure levels, depth, rows, matrix cells, neighbourhood nodes, out-degree, witness segments, closure budget, latency target) are declared in the definition block of views.md with a stated basis, all HYPOTHESES; overflow becomes exact counts plus "N more" by priority-then-cap; filters report hidden non-PASS counts; a change to a budget is a reviewed diff.
> 4. **Counts compose; one badge operator.** Semantic zoom is a fold of status-count vectors, a commutative monoid. A container's badge (and every cross-claim roll-up) is `fold_b`, the chain minimum with PASS on top and NOT_RUN for the empty set, computed from the statuses present in the counts; it is PASS if and only if every item is PASS. The weave join (`fold_a`) is used only for evidence about a single claim and never for a badge. The chain (`chain_worst_first`) is data, hashed into `definition_digest`, and also fixes which rows survive a cap; display order is applied after the cut and cannot change a byte of a document; laws C1 to C6 are tests (C1, C2, C4 and C5 run today; C3 and C6 wait for the implemented views). The kernel `aggregate_status` is not changed here (kernel changes need their own ADR).
> 5. **Non-PASS is level 0.** Every view shows counts by all six statuses, the gap count and the not-applicable count; NOT_RUN and UNKNOWN are never drawn as PASS or as "unaffected"; an empty tier states what was searched; `snapshot.dirty` and `snapshot.not_run` are shown.
> 6. **Ripple has tiers.** Sound, over-approximate, heuristic and not analysed, as nested closures whose tier equals a maximin path; direct and transitive counted apart. MEASUREMENT on this repo: the sound tier is empty and 22 of 28 requirements are reached from `domain/impact.py` only through import-derived edges.
> 7. **Explanations from provenance.** One canonical witness (lexicographically first shortest path) grouped into at most 4 segments, a contrast with the baseline, limits, a closed set of question kinds, no probabilities, owner actions as text with `applies: false`. Absence is answered by the closed-world scope searched, or UNKNOWN when the closure was incomplete.
> 8. **Change digest is the entry point.** Operations in at most 4 chunks; chapters computed from layer, truth class and `derived_from`; a null edit (file digest changed, normalised digest equal) is counted under its hash method, never hidden without the counter.
> 9. **Determinism.** Documents are RFC 8785 subset JSON with integers only, no percentages, no timestamps; identity by id; no force-directed layout in any artefact: the neighbourhood carries an integer `(rank, slot)` grid and a user's drag is a layout complement keyed by id.
> 10. **View mapping totality.** Every node type and link type of `metamodel.json` is shown by some view or listed as `not_shown` with a reason (rule WV-028 in miniature; `tests/graph/test_human_views.py`). Overlap agreement between views (X1 to X6) is a set of tests: X4 and X6 run today on the reference definitions; X1 to X3 and X5 wait for the implemented views.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/oss/REGISTER.md`
* `repo://docs/weave/ARCHITECTURE.md`
* `repo://graph/bench/human_views_budgets.py`
* `repo://graph/bench/human_views_reference.py`
* `repo://pyproject.toml`
* `repo://quality/tools/adr_index.py`
* `repo://tests/graph/test_human_views.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0040: HCI budgets are ratchets, browser tests are opt-in, and the journey runs under the harness identity](/adrs/0040-hci-budgets-as-ratchets-and-harness-identity.md) - The current UI already misses some HCI thresholds (for example moves above 4 bits, focus dropped after re-render, one serious axe rule).
* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay](/adrs/0099-weave-agent-interface.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, with a checker that reports f…

## Referenced by

* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [Weave: deterministic linked graph, compiler and linter (`weave`)](/lanes/0089-weave-deterministic-linked-graph.md) - Capability lane with ADR numbers 0089–0112 reserved.
<!-- okf:generated:end links -->
