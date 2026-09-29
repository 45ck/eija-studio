---
type: Architecture Decision Record
title: 'ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter'
description: People use different agent CLIs, often with subscription logins rather than API keys.
resource: repo://docs/adr/0020-multi-provider-agent-adapters.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0020-multi-provider-agent-adapters.md
  title: 0020-multi-provider-agent-adapters.md
  hash_method: lf-sha256-v1
  sha256: 7da3ee4dd18e42989f382489367bb7e07a9a508aed76eccc58683663f3c20664
notes_baseline: 83f511f8a27b2afe496c1583b58f8ea8f5b67f853458e9f3ef1d2eb078ca8189
---

# ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
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
_No generated cross-references._
<!-- okf:generated:end links -->
