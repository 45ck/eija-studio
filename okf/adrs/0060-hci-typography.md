---
type: Architecture Decision Record
title: 'HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio'
description: 'HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio'
resource: repo://docs/adr/0060-hci-typography.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0060-hci-typography.md
  title: 0060-hci-typography.md
  hash_method: lf-sha256-v1
  sha256: b096ace527fa0b911c81cea65b7bae8092ceb2295bee29cb73ace608528888a1
notes_baseline: 9308c6f6f3990a8bc86e825a80aefe46eb84b434d8213487cbf984f27a0e7567
---

# HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 (revised after audit, 2026-09-29) |
| Source | `repo://docs/adr/0060-hci-typography.md` |

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
* `repo://MANIFEST.json`
* `repo://NOTICE.md`
* `repo://README.md`
* `repo://design/brief.json`
* `repo://design/fonts.lock.json`
* `repo://design/tokens/typography.tokens.json`
* `repo://docs/hci/research/PRINCIPLES.md`
* `repo://docs/oss/REGISTER.md`
* `repo://examples/excursion-baseline.json`
* `repo://pyproject.toml`
* `repo://src/eija_studio/interfaces/http.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.

## Referenced by

* [HCI-ADR-0058: Screen layout model: five persistent regions, derived widths, no page scroll](/adrs/0058-hci-layout-model.md) - HCI-ADR-0058: Screen layout model: five persistent regions, derived widths, no page scroll
* [HCI-ADR-0059: Colour system: OKLCH role tokens, redundant status coding, diff and categorical colour for the Studio](/adrs/0059-hci-color-system.md) - HCI-ADR-0059: Colour system: OKLCH role tokens, redundant status coding, diff and categorical colour for the Studio
* [HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple](/adrs/0062-hci-language-ddd-tree.md) - HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple
* [HCI-ADR-0067: Accessibility architecture](/adrs/0067-hci-accessibility.md) - HCI-ADR-0067: Accessibility architecture
* [HCI-ADRs: research-grounded UI/UX decisions (`ux`, `studio-ux`)](/lanes/0057-hci-adrs-research-grounded-ui-ux.md) - Capability lane with ADR numbers 0057–0088 reserved.
<!-- okf:generated:end links -->
