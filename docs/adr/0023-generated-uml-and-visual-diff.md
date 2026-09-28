# ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer

* Status: accepted
* Date: 2026-09-29
* Lane: visual

## Context and problem statement

[ADR-0019](0019-diagrams-generated-from-executable-model.md) decided that diagrams are generated projections of the executable model. The owner wants to see what an agent's change does and how it ripples into other models, as UML, with a guarantee that the picture matches the code. We need to decide how the generators are structured, which formats they emit, how "matches the code" is enforced, and where the pictures appear.

## Decision drivers

* A diagram must be a pure function of domain values (`Workflow`, `model_impact`, the Pydantic contracts). No second source of truth, no hand-drawn element.
* Output must be deterministic: reordering the definition of the same workflow must not change a byte.
* OSS first ([ADR-0016](0016-oss-first-adapters-not-engines.md)): render with existing tools, write only generators.
* The Studio must render offline, with no CDN, under a strict Content-Security-Policy ([ADR-0024](0024-sandboxed-frame-for-mermaid-rendering.md)).
* Reviewers on GitHub see the same diagrams without running anything.

## Considered options

* Mermaid as the primary text format, PlantUML and Graphviz DOT as exports, all emitted from one neutral model.
* PlantUML only (needs Java and, for most diagram types, Graphviz at render time; not renderable in the browser or on GitHub).
* Graphviz DOT only (no sequence or class diagrams).
* Server-side SVG rendering (adds a heavy runtime dependency to a local tool).

## Decision outcome

Chosen option: "Mermaid primary, PlantUML and DOT exports from one neutral model", because Mermaid renders in the Studio, in GitHub markdown and in a standalone HTML file with one vendored script, while PlantUML and DOT cover the toolchains reviewers already have.

* `application/diagrams.py` builds a small format-neutral model (`Graph`, `Sequence`, `ClassModel`) from domain values only: state machine, baseline-vs-candidate diff, commit-protocol sequence per action, class diagram of the contracts, journey per role, and the ripple from `domain.impact.model_impact`.
* `application/diagram_emitters.py` serialises it to Mermaid, PlantUML and DOT. State, diff, journey and impact are emitted in all three; sequence and class in Mermaid and PlantUML (DOT has no such diagram). Emitters escape every label, because `eija render --model` accepts an untrusted file.
* `application/diagram_catalog.py` is the single entry for the CLI (`eija render`), the HTTP endpoint (`GET /api/cases/{id}/diagrams`) and the committed `docs/diagrams/*.md`.
* Every diagram starts with a comment carrying the workflow `semantic_hash` it was generated from. The Studio compares it with the evidence subject of the review packet.
* "Matches the code" is enforced by tests, not asserted: golden files pin the text; reordering states, transitions, guards and effects leaves the output identical; an independent reader of the emitted state diagram recovers exactly the workflow's transitions; every guard-failure code drawn in a sequence is a code the real runtime raises, and a guard the transition lacks is not drawn; the class diagram is introspected, so a new model field appears without editing the generator; `docs/diagrams/*.md` must equal a fresh render (`nox` session `diagrams_drift`, fast and full).
* Real renderers are exercised by the release session `diagrams_syntax`: the vendored Mermaid parses and renders every emitted diagram in Chrome, PlantUML `-syntax` checks the PlantUML output, pydot (and Graphviz `dot` when present) checks DOT. A missing prerequisite is `NOT_RUN`.

### Consequences

* Good: an agent's change is visible as a diff on a state machine and a ripple graph, generated from the same objects the kernel executes.
* Good: no diagram can drift silently; a policy change that alters a picture fails the drift gate until the docs are regenerated and reviewed.
* Bad: Mermaid cannot colour state-diagram edges, so edge status is a label prefix (`+`, `-`, `~`) and node colour. Layout is the renderer's, not ours.
* Bad: the DDD stereotypes on the class diagram (aggregate-root, value-object, command) are a curated map, not derived; a test only checks that each key is a real contract.
* Revisit when: a second workflow kind exists (the generators assume the `Workflow` contract), or diagrams exceed what Mermaid lays out legibly.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Mermaid 12 (vendored), PlantUML, Graphviz | They render text but know nothing of EIJA's `Workflow`, guards or impact closure | The emitters are a few hundred lines; any tool that accepts these three text languages can replace the renderer |
| Pydantic `model_fields` | Used as is for introspection | n/a |
| pydot, PlantUML `-syntax` | Used as is for validation | n/a |
