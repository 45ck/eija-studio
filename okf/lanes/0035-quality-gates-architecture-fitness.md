---
type: Capability Lane
title: Quality gates, architecture fitness functions and static analysis
description: Capability lane with ADR numbers 0035–0036 reserved.
resource: repo://docs/adr/README.md#0035-0036
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0035-0036
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: ee06eb02c9d6a7382e74040dc677809ede970d7c7b92613b0f19060792680066
notes_baseline: 01eb6e26687b032f1dcaf9109c5216976726167f889adf1b2fa7f0818f5e4567
---

# Quality gates, architecture fitness functions and static analysis

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0035–0036 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0035-0036` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets](/adrs/0035-static-analysis-and-architecture-fitness-functions.md) - The kernel's central claims (a vendor-free domain, authority checked before replay, computed evidence) hold only while the code keeps its shape.
* [ADR-0036: noslop guardrails adapted to run nox tiers; hook enablement is an explicit step](/adrs/0036-noslop-hooks-adapted-to-nox.md) - noslop installs git hooks and agent guardrails, but `noslop init` writes a generic Python pack: `black`, `ruff select=ALL`, `typos`, `mypy .`, plain `pytest`.
<!-- okf:generated:end links -->
