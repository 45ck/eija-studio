---
type: Architecture Decision Record
title: 'ADR-0019: Diagrams are generated projections of the executable model'
description: 'Reviewers need to see what a change, usually an agent''s change, does: state machines, sequences, classes, journeys and ripple effects.'
resource: repo://docs/adr/0019-diagrams-generated-from-executable-model.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0019-diagrams-generated-from-executable-model.md
  title: 0019-diagrams-generated-from-executable-model.md
  hash_method: lf-sha256-v1
  sha256: 9cf80356de6d49da520f05850113d8a1c096a61ccfbcea701bc0633039136c89
notes_baseline: 9fe885e4194dfba19f58d65a0e23a073f783ac6d368f96ae2ac387b72309096a
---

# ADR-0019: Diagrams are generated projections of the executable model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Source | `repo://docs/adr/0019-diagrams-generated-from-executable-model.md` |

## Decision outcome (verbatim)

> Every diagram is generated deterministically from the typed `Workflow` and the impact graph. Formats: [Mermaid](https://github.com/mermaid-js/mermaid) (rendered in the Studio and on GitHub), [PlantUML](https://github.com/plantuml/plantuml) and Graphviz DOT for export. A diff renders before, after and changed elements with a legend. Golden-file tests pin the generated text. Nobody edits a rendered diagram as a source of truth. Parts that are modelled rather than derived (the commit-protocol order, the DDD stereotypes) are pinned by tests and named as such in [ADR-0023](repo://docs/adr/0023-generated-uml-and-visual-diff.md); the aim is that a picture and the code cannot drift silently, not that a picture is proof.

## Sections

* Context and problem statement
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer](/adrs/0023-generated-uml-and-visual-diff.md) - ADR-0019 decided that diagrams are generated projections of the executable model.

## Referenced by

* [ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer](/adrs/0023-generated-uml-and-visual-diff.md) - ADR-0019 decided that diagrams are generated projections of the executable model.
* [ADR-0041: MCP server as the agent surface: propose and check, never decide](/adrs/0041-mcp-server-agent-surface.md) - People want their own agents (Claude Code, Codex, OpenCode, Gemini CLI) to use EIJA Studio.
* [ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site](/adrs/0043-readme-truthfulness-and-docs-site.md) - EIJA's promise is that what you see matches the code.
* [HCI-ADR-0061: Canvas and drag-and-drop UML editing as typed transactions on a generated picture](/adrs/0061-hci-canvas-uml.md) - HCI-ADR-0061: Canvas and drag-and-drop UML editing as typed transactions on a generated picture
* [HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple](/adrs/0062-hci-language-ddd-tree.md) - HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple
* [HCI-ADR-0063: Review an agent's change by meaning: operation list, ripple strip and an evidence rail with four-slot coverage](/adrs/0063-hci-evidence-change-review.md) - HCI-ADR-0063: Review an agent's change by meaning: operation list, ripple strip and an evidence rail with four-slot coverage
* [HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change](/adrs/0068-hci-design-system-architecture.md) - HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change
<!-- okf:generated:end links -->
