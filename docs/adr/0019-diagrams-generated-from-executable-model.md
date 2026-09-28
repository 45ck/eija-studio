# ADR-0019: Diagrams are generated projections of the executable model

* Status: proposed
* Date: 2026-09-28

## Context and problem statement

Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects. A hand-drawn diagram can disagree with the code.

## Decision outcome

Every diagram is generated deterministically from the typed `Workflow` and the impact graph. Formats: [Mermaid](https://github.com/mermaid-js/mermaid) (rendered in the Studio and on GitHub), [PlantUML](https://github.com/plantuml/plantuml) and Graphviz DOT for export. A diff renders before, after and changed elements with a legend. Golden-file tests pin the generated text. Nobody edits a rendered diagram as a source of truth. This is the "what you see matches the code" guarantee.
