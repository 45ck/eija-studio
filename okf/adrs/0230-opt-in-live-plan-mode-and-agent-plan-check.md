---
type: Architecture Decision Record
title: 'ADR-0230: Opt-in live plan mode, and a plan check for coding agents'
description: 'On 2026-10-08 the owner kept PlayIDE''s chat offline and synthetic: a phrase reader plus the pack''s proposal rules, never a model.'
resource: repo://docs/adr/0230-opt-in-live-plan-mode-and-agent-plan-check.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0230-opt-in-live-plan-mode-and-agent-plan-check.md
  title: 0230-opt-in-live-plan-mode-and-agent-plan-check.md
  hash_method: lf-sha256-v1
  sha256: 552559d68c5875205eb10f9f23d3912cc069c60876aede4a7d61f932e12d06f7
notes_baseline: 1e216dafb542b27314789d6c889b13dceaf9db2c09dda9bbd6273be1f7dc312b
---

# ADR-0230: Opt-in live plan mode, and a plan check for coding agents

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-11 |
| Lane | providers / agents / PlayIDE chat |
| Source | `repo://docs/adr/0230-opt-in-live-plan-mode-and-agent-plan-check.md` |

## Decision outcome (verbatim)

> **Live plan mode.** `adapters/live_plan_proposals.py` wraps the configured proposal provider. A request whose clauses are all exact phrases is planned offline and never sent. Otherwise the provider's first alternative must be a pack meaning with transactions; those transactions become the plan, and the kernel checks it as usual. An unsafe meaning is planned as asked and refused by its law (issue #152). A meaning with nothing to plan is refused with the model's explanation.
>
> It is wired only when the Studio's provider is networked. `/api/status` reports `live_plan` (true only with `--allow-network`), and `/api/play/plan` takes a strict boolean `consent`; consent without a live proposer or without network is refused with `EGRESS_CONSENT_REQUIRED`. The chat shows an "Ask <provider> for this request" box only when `live_plan` is true, and the box unticks after every send.
>
> **Plan check for agents.** The MCP tool `plan_check(steps)` dry-runs a plan of typed steps (the chat's step vocabulary) on the model in force, in order, and returns the same preview the chat shows: legal or not, each step's status, refusal codes and the laws they name. No case is needed; nothing is stored. It is read-only and listed in `AGENT_TOOLS`, the agent contract and both skill files.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/quality/inspections/2026-11-13-ai-chat-plan-mode.md`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0229: Kernel-graded intent evals, and an OpenAI Responses API provider](/adrs/0229-kernel-graded-intent-evals-and-openai-provider.md) - PlayIDE's pitch is that AI may propose a change and the kernel decides what it means.
<!-- okf:generated:end links -->
