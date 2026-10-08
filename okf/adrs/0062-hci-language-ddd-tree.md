---
type: Architecture Decision Record
title: 'HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple'
description: 'HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple'
resource: repo://docs/adr/0062-hci-language-ddd-tree.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0062-hci-language-ddd-tree.md
  title: 0062-hci-language-ddd-tree.md
  hash_method: lf-sha256-v1
  sha256: df3e4b73c9760bdf482b828bc17e6004267961e13ab8e4afdf07b08e02eae40a
notes_baseline: 8f8aec618166382b412fc50d5565acb18276931a99857cc22531149720dc76a9
---

# HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed (revision 3, after audits of revisions 1 and 2; changes are listed in section 10 of the design document) |
| Date | 2026-09-29 |
| Source | `repo://docs/adr/0062-hci-language-ddd-tree.md` |

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

* `repo://design/layouts/proposed-language.json`
* `repo://design/tasks/language-flows.json`
* `repo://docs/architecture/ARCHITECTURE.md`
* `repo://docs/hci/design/typography.md`
* `repo://docs/oss/REGISTER.md`
* `repo://docs/verification/ACCEPTANCE_MATRIX.csv`
* `repo://docs/verification/VERIFICATION.md`
* `repo://src/eija_studio/domain/evidence.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0000: v0.2 proof-of-concept decision log (ADR-001 … ADR-014)](/adrs/0000-poc-decision-log.md) - These fourteen decisions shipped with EIJA Studio 0.2.0 and are kept verbatim as one log.
* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0019: Diagrams are generated projections of the executable model](/adrs/0019-diagrams-generated-from-executable-model.md) - Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects.
* [HCI-ADR-0057: Information architecture, navigation and command palette: three destinations, a stable frame, one palette, hash deep links](/adrs/0057-hci-ia-navigation.md) - HCI-ADR-0057: Information architecture, navigation and command palette: three destinations, a stable frame, one palette, hash deep links
* [HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio](/adrs/0060-hci-typography.md) - HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio
* [HCI-ADR-0063: Review an agent's change by meaning: operation list, ripple strip and an evidence rail with four-slot coverage](/adrs/0063-hci-evidence-change-review.md) - HCI-ADR-0063: Review an agent's change by meaning: operation list, ripple strip and an evidence rail with four-slot coverage

## Referenced by

* [HCI-ADR-0057: Information architecture, navigation and command palette: three destinations, a stable frame, one palette, hash deep links](/adrs/0057-hci-ia-navigation.md) - HCI-ADR-0057: Information architecture, navigation and command palette: three destinations, a stable frame, one palette, hash deep links
* [HCI-ADRs: research-grounded UI/UX decisions (`ux`, `studio-ux`)](/lanes/0057-hci-adrs-research-grounded-ui-ux.md) - Capability lane with ADR numbers 0057–0088 reserved.
<!-- okf:generated:end links -->
