---
type: Architecture Decision Record
title: 'HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change'
description: 'HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change'
resource: repo://docs/adr/0068-hci-design-system-architecture.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0068-hci-design-system-architecture.md
  title: 0068-hci-design-system-architecture.md
  hash_method: lf-sha256-v1
  sha256: d319edb8cc7ea155af20bbdf7b7fe515f76b681c70d9a56ead42cf8b258353fb
notes_baseline: c22582f955a59ec47594334e4ecbcba9011d1b40c90d263f02e4fd3fbf597bc7
---

# HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Source | `repo://docs/adr/0068-hci-design-system-architecture.md` |

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

* `repo://AGENTS.md`
* `repo://design/brief.json`
* `repo://design/fonts.lock.json`
* `repo://design/tokens/color.tokens.json`
* `repo://design/tokens/typography.tokens.json`
* `repo://docs/hci/design/accessibility.md`
* `repo://docs/hci/design/color-system.md`
* `repo://docs/hci/design/content-and-onboarding.md`
* `repo://docs/hci/design/layout-model.md`
* `repo://docs/hci/design/typography.md`
* `repo://docs/hci/personas-and-jtbd.md`
* `repo://docs/hci/research/PRINCIPLES.md`
* `repo://docs/hci/research/diagramming-and-uml-tools.md`
* `repo://docs/oss/REGISTER.md`
* `repo://pyproject.toml`
* `repo://src/eija_studio/adapters/identity.py`
* `repo://src/eija_studio/domain/evidence.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0000: v0.2 proof-of-concept decision log (ADR-001 … ADR-014)](/adrs/0000-poc-decision-log.md) - These fourteen decisions shipped with EIJA Studio 0.2.0 and are kept verbatim as one log.
* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0017: Local quality gates with nox sessions and noslop enforcement](/adrs/0017-local-quality-gates.md) - Hosted CI is not currently available for this repository.
* [ADR-0019: Diagrams are generated projections of the executable model](/adrs/0019-diagrams-generated-from-executable-model.md) - Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects.
* [HCI-ADR-0058: Screen layout model: five persistent regions, derived widths, no page scroll](/adrs/0058-hci-layout-model.md) - HCI-ADR-0058: Screen layout model: five persistent regions, derived widths, no page scroll
* [HCI-ADR-0065: Content, microcopy and sample-first onboarding for the Studio](/adrs/0065-hci-content-onboarding.md) - HCI-ADR-0065: Content, microcopy and sample-first onboarding for the Studio
* [HCI-ADR-0066: Motion, feedback and performance budgets with authority-honest optimism](/adrs/0066-hci-motion-performance.md) - HCI-ADR-0066: Motion, feedback and performance budgets with authority-honest optimism
* [HCI-ADR-0067: Accessibility architecture](/adrs/0067-hci-accessibility.md) - HCI-ADR-0067: Accessibility architecture

## Referenced by

* [HCI-ADRs: research-grounded UI/UX decisions (`ux`, `studio-ux`)](/lanes/0057-hci-adrs-research-grounded-ui-ux.md) - Capability lane with ADR numbers 0057–0088 reserved.
<!-- okf:generated:end links -->
