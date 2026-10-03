---
type: Architecture Decision Record
title: 'ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay'
description: The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, with a checker that reports findings.
resource: repo://docs/adr/0099-weave-agent-interface.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0099-weave-agent-interface.md
  title: 0099-weave-agent-interface.md
  hash_method: lf-sha256-v1
  sha256: 4ededd95f84bbf3f81318d4488de10d853fea075632b31a1fdc5e9ddb9c71d5a
notes_baseline: 7ce04c387f24366640c02c2b70d409adacd4871ffde236251ad37e50af81bbfa
---

# ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Lane | weave (aspect: agent-interface). Number note: this record was assigned 0099; `docs/weave/ARCHITECTURE.md` section 11 and `graph/brief.json` allocate 0099 to the determinism doctrine and 0108 to the agent query set. The integrator must reconcile before merge (design document, open questions 1 and 13: every aspect currently writes its own numbers). References to "ADR-0093" and similar below use the ARCHITECTURE section 11 numbering. |
| Source | `repo://docs/adr/0099-weave-agent-interface.md` |

## Decision outcome (verbatim)

> Chosen options: A, E, H, L, O and S, because together they keep every agent-visible fact a recomputable function of (snapshot, request), keep decisions with the owner, and make the benefit claim falsifiable.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
* Interfaces and open questions

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/oss/REGISTER.md`
* `repo://docs/weave/ARCHITECTURE.md`
* `repo://docs/weave/design/impact-ranking-and-confidence.md`
* `repo://graph/bench/agent_interface_checks.py`
* `repo://graph/brief.json`
* `repo://graph/schema/metamodel.json`
* `repo://tests/graph/test_agent_interface_checks.py`
* `repo://tests/graph/test_agent_interface_contract.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0041: MCP server as the agent surface: propose and check, never decide](/adrs/0041-mcp-server-agent-surface.md) - People want their own agents (Claude Code, Codex, OpenCode, Gemini CLI) to use EIJA Studio.
* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.

## Referenced by

* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture](/adrs/0105-weave-human-views.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce fi…
* [Weave: deterministic linked graph, compiler and linter (`weave`)](/lanes/0089-weave-deterministic-linked-graph.md) - Capability lane with ADR numbers 0089–0112 reserved.
<!-- okf:generated:end links -->
