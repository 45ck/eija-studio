---
type: Capability Lane
title: 'Visual model: UML/diagram generation and visual diff'
description: Capability lane with ADR numbers 0023–0024 reserved.
resource: repo://docs/adr/README.md#0023-0024
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0023-0024
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: 30ae327286cb648277c6906e6a364ce5f1790412228f0c551881caf011aecb2a
notes_baseline: 98cc0db20d68fc4e91f4273033e446d8b1ef734192e3fb5cf506750fc6c08f43
---

# Visual model: UML/diagram generation and visual diff

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0023–0024 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0023-0024` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer](/adrs/0023-generated-uml-and-visual-diff.md) - ADR-0019 decided that diagrams are generated projections of the executable model.
* [ADR-0024: Render Mermaid in a sandboxed frame so the Studio page keeps its strict CSP](/adrs/0024-sandboxed-frame-for-mermaid-rendering.md) - The Studio page ships `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancest…
<!-- okf:generated:end links -->
