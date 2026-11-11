---
type: Architecture Decision Record
title: 'ADR-0229: Kernel-graded intent evals, and an OpenAI Responses API provider'
description: PlayIDE's pitch is that AI may propose a change and the kernel decides what it means.
resource: repo://docs/adr/0229-kernel-graded-intent-evals-and-openai-provider.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0229-kernel-graded-intent-evals-and-openai-provider.md
  title: 0229-kernel-graded-intent-evals-and-openai-provider.md
  hash_method: lf-sha256-v1
  sha256: 1a6f89523ba0cbea8e82e58ed7d7366b2e15995ea57e559e1f38fa35b8e3bc25
notes_baseline: f41926a0049a6696a49699051a1e5b6bd173e5ab6ee972655b3b8a6b7b861088
---

# ADR-0229: Kernel-graded intent evals, and an OpenAI Responses API provider

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-11 |
| Lane | providers / evals |
| Source | `repo://docs/adr/0229-kernel-graded-intent-evals-and-openai-provider.md` |

## Decision outcome (verbatim)

> **Cases.** `packs/intent-evals.json` holds pack data, so it lives with the packs (outside the vocabulary gate): a request, its pack, its kind (`example`, `paraphrase`, `unsafe`, `off_topic`) and the meaning it asked for. 32 cases over 11 packs to start.
>
> **Grader.** `quality/evals/intent.py` asks the provider for alternatives and takes the first as the meaning it would plan. Outcomes: `correct`; `substituted` (an unsafe meaning was asked for and a supported one answered); `wrong`; `invalid` (the provider failed or its reply failed validation, never repaired). The answered meaning is then planned through `propose_plan`; the kernel must allow a supported meaning and refuse an unsupported one, and any disagreement fails the run as a pack or kernel defect.
>
> **Running.** `python -m quality.evals.intent` runs the offline fixture (SYNTHETIC evidence). A networked provider needs `--allow-network` and `--consent`, and `--max-calls` stops the run (hard limit 200). The `intent_eval` nox session (fast and full tiers) runs only the offline harness tests, including a negative control: a provider that always answers with a safe meaning is caught on every unsafe case.
>
> **OpenAI provider.** `adapters/providers/openai_api.py` (`--provider openai`) calls `POST /v1/responses` with Structured Outputs in strict mode and `store: false`, the key from `OPENAI_API_KEY` or `--ask-key` held in memory, and a model the operator must name. No tools are sent; refusals, incomplete replies and tool calls fail closed; one attempt, no retry. It is contract-tested over a mock transport and is NOT live-verified until `scripts/live_provider_smoke.py` records a run.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://evidence/intent-eval/2026-11-11-offline-linux.json`
* `repo://packs/intent-evals.json`
* `repo://quality/evals/intent.py`
* `repo://scripts/live_provider_smoke.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter](/adrs/0020-multi-provider-agent-adapters.md) - People use different agent CLIs, often with subscription logins rather than API keys.
* [ADR-0021: Agent-CLI providers run in one isolated, bounded, tree-killing base class](/adrs/0021-cli-provider-isolation-and-process-tree-kill.md) - Codex, Claude Code, OpenCode and Gemini CLI are agents with shell and file tools.

## Referenced by

* [ADR-0230: Opt-in live plan mode, and a plan check for coding agents](/adrs/0230-opt-in-live-plan-mode-and-agent-plan-check.md) - On 2026-10-08 the owner kept PlayIDE's chat offline and synthetic: a phrase reader plus the pack's proposal rules, never a model.
<!-- okf:generated:end links -->
