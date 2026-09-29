---
type: Architecture Decision Record
title: 'ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter'
description: People use different agent CLIs, often with subscription logins rather than API keys.
resource: repo://docs/adr/0020-multi-provider-agent-adapters.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0020-multi-provider-agent-adapters.md
  title: 0020-multi-provider-agent-adapters.md
  hash_method: lf-sha256-v1
  sha256: 071e2de09b9d478723b109c83f0ed7d6c8f91ab3bca4915d1ee46f31666d0ef7
notes_baseline: 6bb3e2b555cdb73e789525b881e7c28e9f7bdd0f99773f92fc44b1115f40ae91
---

# ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Source | `repo://docs/adr/0020-multi-provider-agent-adapters.md` |

## Decision outcome (verbatim)

> One `CliProposalProvider` base class owns subprocess isolation: an empty working directory, an environment allow-list, structured output, a timeout, and killing the process tree on both Windows and POSIX. Each vendor is a thin adapter. Authentication is always delegated to the official CLI's own login, for example `codex login` or the `claude` subscription login. EIJA never reads token files and never turns a subscription into an API key.
>
> A shared contract test suite runs against every adapter with a mocked runner. Live smoke tests are opt-in, need owner consent, and record the CLI version. Providers stay proposal-only: they can never select meaning, mint receipts, approve or apply.

## Sections

* Context and problem statement
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0021: Agent-CLI providers run in one isolated, bounded, tree-killing base class](/adrs/0021-cli-provider-isolation-and-process-tree-kill.md) - Codex, Claude Code, OpenCode and Gemini CLI are agents with shell and file tools.
* [HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls](/adrs/0064-hci-ai-interaction.md) - HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls
<!-- okf:generated:end links -->
