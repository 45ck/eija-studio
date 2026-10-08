---
type: Architecture Decision Record
title: 'HCI-ADR-0061: Canvas and drag-and-drop UML editing as typed transactions on a generated picture'
description: 'HCI-ADR-0061: Canvas and drag-and-drop UML editing as typed transactions on a generated picture'
resource: repo://docs/adr/0061-hci-canvas-uml.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0061-hci-canvas-uml.md
  title: 0061-hci-canvas-uml.md
  hash_method: lf-sha256-v1
  sha256: 984ed5346e48bb31a8fe86def35de4c94937d46a4915fb147c969ffcd481df92
notes_baseline: 47bddccba9b4b320e495a32edcb18eb38f5b0028d146082b22ddd2f7d6479f58
---

# HCI-ADR-0061: Canvas and drag-and-drop UML editing as typed transactions on a generated picture

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed. **Owner decision point:** D-lite (release 1 without a MEANING drag) versus D (MEANING drag in release 1). D-lite deviates from the task definition of T04 in `design/brief.json` (see Problem); it needs the owner's sign-off before acceptance. |
| Date | 2026-09-29 |
| Source | `repo://docs/adr/0061-hci-canvas-uml.md` |

## Sections

* Status
* Problem and user goal
* Evidence
* Quantitative model
* Options considered
* Decision
* Anti-slop rubric check
* Accessibility check
* Validation plan
* Consequences
* Definition of ready

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://design/brief.json`
* `repo://design/layouts/current-impact.json`
* `repo://design/layouts/proposed-canvas.json`
* `repo://design/tasks/canvas-flows.json`
* `repo://docs/hci/research/PRINCIPLES.md`
* `repo://docs/oss/REGISTER.md`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0000: v0.2 proof-of-concept decision log (ADR-001 … ADR-014)](/adrs/0000-poc-decision-log.md) - These fourteen decisions shipped with EIJA Studio 0.2.0 and are kept verbatim as one log.
* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0019: Diagrams are generated projections of the executable model](/adrs/0019-diagrams-generated-from-executable-model.md) - Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects.
* [HCI-ADR-0066: Motion, feedback and performance budgets with authority-honest optimism](/adrs/0066-hci-motion-performance.md) - HCI-ADR-0066: Motion, feedback and performance budgets with authority-honest optimism

## Referenced by

* [HCI-ADRs: research-grounded UI/UX decisions (`ux`, `studio-ux`)](/lanes/0057-hci-adrs-research-grounded-ui-ux.md) - Capability lane with ADR numbers 0057–0088 reserved.
<!-- okf:generated:end links -->
