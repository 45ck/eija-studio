---
type: Capability Lane
title: Agent providers (CLI adapters, contract suite)
description: Capability lane with ADR numbers 0021–0022 reserved.
resource: repo://docs/adr/README.md#0021-0022
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0021-0022
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: 55640142d7c9acb7247ce84344e4c87a16604021abd6920c80550f73627923f6
notes_baseline: 9c5147257589176d9b1d2f277ab64ff7c7d775703f32d28a0bc29a0e3666873a
---

# Agent providers (CLI adapters, contract suite)

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0021–0022 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0021-0022` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0021: Agent-CLI providers run in one isolated, bounded, tree-killing base class](/adrs/0021-cli-provider-isolation-and-process-tree-kill.md) - Codex, Claude Code, OpenCode and Gemini CLI are agents with shell and file tools.
* [ADR-0022: Live provider evidence is consent-gated, one call, and NOT_RUN when unproven](/adrs/0022-live-provider-evidence-and-not-run.md) - Mocked contract tests prove an adapter's handling of faked output.
<!-- okf:generated:end links -->
