---
type: Architecture Decision Record
title: 'ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer'
description: ADR-0019 decided that diagrams are generated projections of the executable model.
resource: repo://docs/adr/0023-generated-uml-and-visual-diff.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0023-generated-uml-and-visual-diff.md
  title: 0023-generated-uml-and-visual-diff.md
  hash_method: lf-sha256-v1
  sha256: 02ddf88560aab29298294d2a056afc994bb40368a92ebbcef6174392fa31bb0a
notes_baseline: 780c2de62af25189824da4c7a93696906aed288068fc922fdc923f21d5dca740
---

# ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-29 |
| Lane | visual |
| Source | `repo://docs/adr/0023-generated-uml-and-visual-diff.md` |

## Decision outcome (verbatim)

> Chosen option: "Mermaid primary, PlantUML and DOT exports from one neutral model", because Mermaid renders in the Studio, in GitHub markdown and in a standalone HTML file with one vendored script, while PlantUML and DOT cover the toolchains reviewers already have.
>
> * `application/diagrams.py` builds a small format-neutral model (`Graph`, `Sequence`, `ClassModel`) from domain values only: state machine, baseline-vs-candidate diff, commit-protocol sequence per action, class diagram of the contracts, journey per role, and the ripple from `domain.impact.model_impact`.
> * `application/diagram_emitters.py` serialises it to Mermaid, PlantUML and DOT. State, diff, journey and impact are emitted in all three; sequence and class in Mermaid and PlantUML (DOT has no such diagram). Emitters escape every label, because `eija render --workflow` accepts an untrusted file.
> * `application/diagram_catalog.py` is the single entry for the CLI (`eija render`), the HTTP endpoint (`GET /api/cases/{id}/diagrams`) and the committed `docs/diagrams/*.md`.
> * Every diagram starts with a comment carrying the workflow `semantic_hash` it was generated from. The Studio compares it with the evidence subject of the review packet.
> * "Matches the code" is enforced by tests, not asserted: golden files pin the text; reordering states, transitions, guards and effects leaves the output identical; an independent reader of the emitted state diagram recovers exactly the workflow's transitions; every guard-failure code drawn in a sequence is a code the real runtime raises, and a guard the transition lacks is not drawn; the order of the sequence equals the order in which the real `execute` calls its unit-of-work port (a recording spy, so the order is hand-encoded but pinned, not derived); a policy-refused workflow is drawn with a POLICY BLOCKED marker; the class diagram is introspected, so a new model field appears without editing the generator; `docs/diagrams/*.md` must equal a fresh render (`nox` session `diagrams_drift`, fast and full).
> * Real renderers are exercised by the release session `diagrams_syntax`: the vendored Mermaid parses and renders every emitted diagram in Chrome, PlantUML `-syntax` checks the PlantUML output, pydot (and Graphviz `dot` when present) checks DOT. A missing prerequisite is `NOT_RUN` and fails the release session unless `EIJA_ALLOW_NOT_RUN=1`. PlantUML evaluates `%name(...)` preprocessor calls inside labels (verified: `%getenv` and `%load_json` with 1.2025.4), so the PlantUML emitter writes `%` as `<U+0025>` and the validator renders a hostile model with a secret in the environment.

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
* [ADR-0019: Diagrams are generated projections of the executable model](/adrs/0019-diagrams-generated-from-executable-model.md) - Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects.
* [ADR-0024: Render Mermaid in a sandboxed frame so the Studio page keeps its strict CSP](/adrs/0024-sandboxed-frame-for-mermaid-rendering.md) - The Studio page ships `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancest…

## Referenced by

* [ADR-0019: Diagrams are generated projections of the executable model](/adrs/0019-diagrams-generated-from-executable-model.md) - Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects.
* [ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site](/adrs/0043-readme-truthfulness-and-docs-site.md) - EIJA's promise is that what you see matches the code.
* [Visual model: UML/diagram generation and visual diff](/lanes/0023-visual-model-uml-diagram-generation.md) - Capability lane with ADR numbers 0023–0024 reserved.
<!-- okf:generated:end links -->
