---
type: Capability Lane
title: Mutation analysis
description: Capability lane with ADR numbers 0033–0034 reserved.
resource: repo://docs/adr/README.md#0033-0034
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0033-0034
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: 468139b0c572edba89761db31154bf27caa263d474f749bed94d4b9b26e84185
notes_baseline: 60d6a55d8291b6191773fc9d8fa24c9658b0907e23c41a5db0a5fcf53b086f1b
---

# Mutation analysis

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0033–0034 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0033-0034` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows](/adrs/0033-mutation-tool-selection.md) - The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role o…
* [ADR-0034: What is mutated, how a score is defined, and the ratchet](/adrs/0034-mutation-measurement-and-ratchet.md) - ADR-0033 picks the engine.
<!-- okf:generated:end links -->
