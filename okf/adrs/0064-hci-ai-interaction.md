---
type: Architecture Decision Record
title: 'HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls'
description: 'HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls'
resource: repo://docs/adr/0064-hci-ai-interaction.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0064-hci-ai-interaction.md
  title: 0064-hci-ai-interaction.md
  hash_method: lf-sha256-v1
  sha256: 3506f8ed0f346219041c644f089d33d0ba3ca166b8da625a231a59e0b143a45a
notes_baseline: 4dbec7edef0bdc4c1f2fc530cb2932e04f43327460446234343dfd4612e0bb04
---

# HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Source | `repo://docs/adr/0064-hci-ai-interaction.md` |

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
* `repo://design/tasks/ai-flows.json`
* `repo://docs/hci/personas-and-jtbd.md`
* `repo://docs/hci/research/PRINCIPLES.md`
* `repo://docs/oss/REGISTER.md`
* `repo://src/eija_studio/interfaces/http.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0000: v0.2 proof-of-concept decision log (ADR-001 … ADR-014)](/adrs/0000-poc-decision-log.md) - These fourteen decisions shipped with EIJA Studio 0.2.0 and are kept verbatim as one log.
* [ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter](/adrs/0020-multi-provider-agent-adapters.md) - People use different agent CLIs, often with subscription logins rather than API keys.

## Referenced by

* [HCI-ADR-0057: Information architecture, navigation and command palette: three destinations, a stable frame, one palette, hash deep links](/adrs/0057-hci-ia-navigation.md) - HCI-ADR-0057: Information architecture, navigation and command palette: three destinations, a stable frame, one palette, hash deep links
* [HCI-ADR-0065: Content, microcopy and sample-first onboarding for the Studio](/adrs/0065-hci-content-onboarding.md) - HCI-ADR-0065: Content, microcopy and sample-first onboarding for the Studio
* [HCI-ADR-0067: Accessibility architecture](/adrs/0067-hci-accessibility.md) - HCI-ADR-0067: Accessibility architecture
* [ADR-0170: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review](/adrs/0170-playide-assist-ask-complete-palette-review.md) - PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157).
* [ADR-0172: A read-only review view of PlayIDE for people who review the model](/adrs/0172-review-view-for-reading-the-model.md) - The owner set the audience as people who know UML, and noted that UML "is meant for non technical people to review it sometimes".
* [HCI-ADRs: research-grounded UI/UX decisions (`ux`, `studio-ux`)](/lanes/0057-hci-adrs-research-grounded-ui-ux.md) - Capability lane with ADR numbers 0057–0088 reserved.
<!-- okf:generated:end links -->
