---
type: Capability Lane
title: 'Formal: TLA+/TLC specification and trace conformance'
description: Capability lane with ADR numbers 0027–0028 reserved.
resource: repo://docs/adr/README.md#0027-0028
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0027-0028
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: 244a51790fee13277da5fedb4b0715dec770ba74bfac1e041c31816ab2345ac2
notes_baseline: 591d8f285b7aced6595eb9e4e1aa23668189f1658f53b29ef98ef964d076b63b
---

# Formal: TLA+/TLC specification and trace conformance

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0027–0028 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0027-0028` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC](/adrs/0027-tla-plus-specification-and-model-checking.md) - The v0.2 runtime matrix checks one step from each state.
* [ADR-0028: Model-to-code conformance by exhaustive graph comparison and TLC trace validation](/adrs/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md) - A TLA+ proof about `Excursion.tla` is a proof about the model.
<!-- okf:generated:end links -->
