---
type: Architecture Decision Record
title: 'ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows'
description: The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role or a weakened evidence check.
resource: repo://docs/adr/0033-mutation-tool-selection.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0033-mutation-tool-selection.md
  title: 0033-mutation-tool-selection.md
  hash_method: lf-sha256-v1
  sha256: f22eec4c9030073c5bbc8ac8a10b1605a5627c9d824d43370e956d65fa40dadb
notes_baseline: 37f62854f1a8939c17d0db1a2548d6c49c6fe7952f77c7966c522d67d7a52571
---

# ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-29 |
| Lane | mutation |
| Source | `repo://docs/adr/0033-mutation-tool-selection.md` |

## Decision outcome (verbatim)

> Chosen option: "cosmic-ray, natively", because it is the only maintained OSS mutation tool that runs on the reference platform without a second operating-system layer, and its plugin interface lets EIJA add the fault classes it lacks without forking it.
>
> EIJA-specific glue, in `quality/mutation/` (outside the shipped package):
>
> * `engine.py`: runs cosmic-ray inside a **scratch copy** of the repository under `<checkout>/.tmp/mutation/` so the real tree is never rewritten, proves the copy is the code under test before any mutant runs (import path probe and a green baseline), and turns `cosmic-ray dump` into typed records.
> * `eija_operators.py`: three operators that cosmic-ray lacks (identifier-like string constants, return values, membership tests). They are loaded through a dist-info written into the scratch copy, so nothing is installed.
> * `model.py`, `report.py`: classification, score, the ratchet and the survivor report.
> * `runner.py`: two workers maximum, each target split into two exact shards.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.

## Referenced by

* [ADR-0032: Stateful differential testing against a specification-derived reference, with mutant negative controls](/adrs/0032-stateful-differential-testing-and-negative-controls.md) - The runtime's promises are about *histories*: replay never repeats effects, a revoked actor cannot replay a cached success, a crash rolls back everything, an e…
* [ADR-0034: What is mutated, how a score is defined, and the ratchet](/adrs/0034-mutation-measurement-and-ratchet.md) - ADR-0033 picks the engine.
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [Mutation analysis](/lanes/0033-mutation-analysis.md) - Capability lane with ADR numbers 0033–0034 reserved.
<!-- okf:generated:end links -->
