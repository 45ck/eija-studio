---
type: Capability Lane
title: 'Weave: deterministic linked graph, compiler and linter (`weave`)'
description: Capability lane with ADR numbers 0089–0112 reserved.
resource: repo://docs/adr/README.md#0089-0112
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0089-0112
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: 84fb510142bc0144f97fb562c8209dffc828e1783f0ab40b48bbfd0159cd6b7d
notes_baseline: 09c622ec2b7bc81943da705a07fb3700b05051a9d8081dacde25188113982972
---

# Weave: deterministic linked graph, compiler and linter (`weave`)

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0089–0112 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0089-0112` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0089: Weave metamodel and identity: a closed typed metamodel, canonical ids, an RFC 8785 subset and sorted-record hashing](/adrs/0089-weave-metamodel-identity.md) - EIJA Studio wants deterministic, machine-checkable links between code, UI, diagrams, ubiquitous language, requirements, tests, formal results, evidence, ADRs a…
* [ADR-0091: Storage and query: git files are the truth, a disposable SQLite index answers named queries](/adrs/0091-weave-storage-query.md) - Weave ties code, UI, diagrams, language, requirements, tests, proofs, evidence and decisions into one typed graph checked by a compiler-like rule set.
* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0095: The weave compiler and lint rules: violation queries over a typed graph, SARIF diagnostics, expiring suppressions](/adrs/0095-weave-lint-compile-rules.md) - EIJA wants deterministic, machine-checkable links between code, tests, requirements, the ubiquitous language, UI, diagrams, formal models, evidence and ADRs, a…
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay](/adrs/0099-weave-agent-interface.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, with a checker that reports f…
* [ADR-0102: Formal verification of the weave: a small trusted kernel, certificates, exhaustive small scope, Alloy for bounded statements, and drift guards](/adrs/0102-weave-formal-verification-of-weave.md) - The weave ties code, tests, requirements, UI, diagrams, the ubiquitous language, formal models and evidence into one typed, hash-anchored graph, and a rule set…
* [ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture](/adrs/0105-weave-human-views.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce fi…
<!-- okf:generated:end links -->
