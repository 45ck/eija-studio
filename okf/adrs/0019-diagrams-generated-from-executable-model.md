---
type: Architecture Decision Record
title: 'ADR-0019: Diagrams are generated projections of the executable model'
description: 'Reviewers need to see what a change, usually an agent''s change, does: state machines, sequences, classes, journeys and ripple effects.'
resource: repo://docs/adr/0019-diagrams-generated-from-executable-model.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0019-diagrams-generated-from-executable-model.md
  title: 0019-diagrams-generated-from-executable-model.md
  hash_method: lf-sha256-v1
  sha256: 45cddf16f44bcd58713eaa1025bf221c0571983d07c41e4af08cae5745a4b53c
---

# ADR-0019: Diagrams are generated projections of the executable model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-28 |
| Source | `repo://docs/adr/0019-diagrams-generated-from-executable-model.md` |

## Decision outcome (verbatim)

> Every diagram is generated deterministically from the typed `Workflow` and the impact graph. Formats: [Mermaid](https://github.com/mermaid-js/mermaid) (rendered in the Studio and on GitHub), [PlantUML](https://github.com/plantuml/plantuml) and Graphviz DOT for export. A diff renders before, after and changed elements with a legend. Golden-file tests pin the generated text. Nobody edits a rendered diagram as a source of truth. This is the "what you see matches the code" guarantee.

## Sections

* Context and problem statement
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
