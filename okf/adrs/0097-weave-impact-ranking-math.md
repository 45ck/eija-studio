---
type: Architecture Decision Record
title: 'ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage'
description: 'The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-check, how should changes be queued for review, what is the s…'
resource: repo://docs/adr/0097-weave-impact-ranking-math.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0097-weave-impact-ranking-math.md
  title: 0097-weave-impact-ranking-math.md
  hash_method: lf-sha256-v1
  sha256: 18ebdcd15418ef9e2e20fc04fe12e4cfdc08c59ec09edf8a0bc919d71eeadb76
notes_baseline: 524a3cc1cdd2c39c98914fdbc6d1ac0f2c687989d697834290a38a4e4abc28d5
---

# ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Lane | weave (aspect impact-ranking-math; design in [docs/weave/design/impact-ranking-and-confidence.md](repo://docs/weave/design/impact-ranking-and-confidence.md), oracles in [graph/schema/math-oracles.md](repo://graph/schema/math-oracles.md)) |
| Source | `repo://docs/adr/0097-weave-impact-ranking-math.md` |

## Decision outcome (verbatim)

> Chosen option: "a thin stdlib layer with a reference implementation and hand-verified oracles", because it is the only option whose results are byte-reproducible on Windows and POSIX, whose every step has a witness or an error bound, and whose licence is unencumbered. Each decision has a section in the design document and an oracle in `math-oracles.md`.
>
> | Id | Decision | Guarantee and hypotheses | Oracle |
> |---|---|---|---|
> | IR-1 | Impact is the least fixed point of `X -> C U succ(X)` over typed arcs in three soundness tiers (must, may, heuristic), with tier, distance, lexicographically smallest shortest-path witness, kernel-compatible budget, `complete` and `frontier`, computed over the union of base and head arcs | Order-independent, terminates, tiers nest; equals the kernel on 300 seeded graphs, the SQL form equals it on the worked example and 200 seeded typed graphs, and it is the least pre-fixed point exhaustively on tiny graphs. Reach is over encoded arcs only | O1 |
> | IR-2 | Impact (structural, transitive) and suspicion (digest-driven, one hop, early cutoff) are separate; lint: every link type's flow covers its anchored direction, so stale nodes lie inside the impact set | Tested with a negative control | O1 |
> | IR-3 | SCC condensation with minimum-member labels, lexicographically smallest topological order, reach and exposure counts by bitset DP; betweenness not built | `O(V+E)` labels, `O(E V / w)` all-node counts; identical under shuffles | O2 |
> | IR-4 | Relevance is personalised PageRank in bit-exact fixed-point integers (`SCALE = 2^40`, floor split, remainder to sorted targets, `K` from `alpha` by integer inequality); default `alpha = 1/5`, impact-direction weight 2, reverse weight 1, hub damping optional and off; advisory only, never a gate | L1 error at most `2 SCALE beta^K + (arcs + 2 nodes + seeds)/alpha` units, checked against exact rational solutions; ordering certified when scores differ by more than twice that. Offline co-change study on two Python repositories: beats hop distance at recall@10 with paired 95% intervals excluding 0; ties path-prefix on one, beats it on the other. No agent or human effect is claimed | O3 |
> | IR-5 | `context(budget)` = pinned seeds, then density greedy with a best-single-item safeguard, budget in bytes of rendered pages, `BUDGET_TOO_SMALL` instead of truncation, and an `omitted` list in which every candidate not chosen carries a reason (`NOT_SELECTED_BUDGET`, `TOO_LARGE_FOR_ROOM`, `NON_POSITIVE_SCORE`, `NON_POSITIVE_COST`) | At least half the optimum when values are additive and each cost fits (candidates that cannot fit are in no feasible set); exhaustive check on 200 instances; chosen and omitted partition the candidates on 200 instances | O4 |
> | IR-6 | Test and evidence selection: a safe pool from coverage-derived `covers` edges (`NOT_RUN` without coverage data), then weighted greedy set cover of impacted obligations by exact cost per newly covered element; unreachable obligations are findings; fast tier only | `H(d)` approximation (Chvatal); greedy 3 against optimum 2 on the classic family; no better than about `ln n` in polynomial time unless P = NP | O5 |
> | IR-7 | Change risk is a vector of eight exact counts with a partial order and a lexicographic review order; gates are boolean policy rules, never thresholds | Order never puts a dominated change above its dominator | O9 |
> | IR-8 | Two status operators: replication join `A` over `UNKNOWN < STALE < {PASS, FAIL} < CONFLICT` for repeated observations of one check (the kernel's five values; empty fold `UNKNOWN`), and chain-minimum conjunction `B` with `PASS` on top for distinct checks; `NOT_RUN` lives only in `B`; the empty conjunction is `NOT_RUN`, never `PASS` | Laws checked exhaustively; `A` equals kernel `aggregate_status` on all 5460 flat sequences of length 1 to 6 and on the empty list, and composes where the kernel does not; `PASS` iff all `PASS` for every admissible chain. The order among non-`PASS` values stays an owner decision. Two representational differences from the formal aspect's `eijaref.status` are tested and left to the integrator with a recommendation | O7, O10 |
> | IR-9 | No confidence percentage in any gate, default view, agent result or OKF page. Print counts and ratios, exhaustive-domain statements, generator-relative miss bounds labelled conditional, mutation ratios with the fault model named, `pass^k` with `n`, and an evidence summary | Exact rationals only; demonstrations in the oracle file | O8 |
> | IR-10 | Evidence redundancy `k` (vertex-disjoint paths, cap 3) and the canonical source-side minimal cut; report only | Menger; cut brute-force checked | O6 |
> | IR-11 | Changeset overlap (direct, reaches, shared, by tier) as pre-merge conflict prediction, an early signal that complements the consistency aspect's post-merge check | Symmetric; equals the intersection of two tiered impact sets | O11 |
>
> Every function is a pure function of the canonical graph, recorded parameters and a change set, returns integers and sorted lists, and carries a `params` digest. A production implementation must reproduce the oracles byte for byte and is differential-tested against `graph/bench/impact_math_reference.py`.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://graph/bench/impact_math_reference.py`
* `repo://graph/schema/metamodel.json`
* `repo://graph/schema/views.md`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows](/adrs/0033-mutation-tool-selection.md) - The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role o…
* [ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets](/adrs/0035-static-analysis-and-architecture-fitness-functions.md) - The kernel's central claims (a vendor-free domain, authority checked before replay, computed evidence) hold only while the code keeps its shape.
* [ADR-0037: Measure design, performance and scaling with radon, grimp and coverage.py, and fit models rather than assert them](/adrs/0037-metrics-and-quantitative-models.md) - EIJA Studio claims a clean layered design (domain and application never import adapters), an O(V+E) impact closure and an interactive local UI.
* [ADR-0041: MCP server as the agent surface: propose and check, never decide](/adrs/0041-mcp-server-agent-surface.md) - People want their own agents (Claude Code, Codex, OpenCode, Gemini CLI) to use EIJA Studio.
* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](/adrs/0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.
* [ADR-0089: Weave metamodel and identity: a closed typed metamodel, canonical ids, an RFC 8785 subset and sorted-record hashing](/adrs/0089-weave-metamodel-identity.md) - EIJA Studio wants deterministic, machine-checkable links between code, UI, diagrams, ubiquitous language, requirements, tests, formal results, evidence, ADRs a…
* [ADR-0091: Storage and query: git files are the truth, a disposable SQLite index answers named queries](/adrs/0091-weave-storage-query.md) - Weave ties code, UI, diagrams, language, requirements, tests, proofs, evidence and decisions into one typed graph checked by a compiler-like rule set.
* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0095: The weave compiler and lint rules: violation queries over a typed graph, SARIF diagnostics, expiring suppressions](/adrs/0095-weave-lint-compile-rules.md) - EIJA wants deterministic, machine-checkable links between code, tests, requirements, the ubiquitous language, UI, diagrams, formal models, evidence and ADRs, a…
* [ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay](/adrs/0099-weave-agent-interface.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, with a checker that reports f…
* [ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture](/adrs/0105-weave-human-views.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce fi…

## Referenced by

* [ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture](/adrs/0105-weave-human-views.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce fi…
* [Weave: deterministic linked graph, compiler and linter (`weave`)](/lanes/0089-weave-deterministic-linked-graph.md) - Capability lane with ADR numbers 0089–0112 reserved.
<!-- okf:generated:end links -->
