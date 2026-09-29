---
type: Capability Lane
title: HCI laws and usability instrumentation
description: Capability lane with ADR numbers 0039–0040 reserved.
resource: repo://docs/adr/README.md#0039-0040
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0039-0040
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: e96faebb271cd31e9478cda37c55c3bd4b2be6cc1b93daaeb8c4ee1c9fe0f052
notes_baseline: fc55e8f5942fecabc1f845852b5b15f2a9c5140cc147f32adc4b93c9bc1ce0b5
---

# HCI laws and usability instrumentation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0039–0040 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0039-0040` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0039: Apply HCI laws to the Studio UI with Playwright, axe-core and pure formula modules](/adrs/0039-hci-law-instrumentation.md) - The Studio UI is the owner's only instrument for reviewing an AI-proposed change, yet its usability claims are unmeasured.
* [ADR-0040: HCI budgets are ratchets, browser tests are opt-in, and the journey runs under the harness identity](/adrs/0040-hci-budgets-as-ratchets-and-harness-identity.md) - The current UI already misses some HCI thresholds (for example moves above 4 bits, focus dropped after re-render, one serious axe rule).
<!-- okf:generated:end links -->
