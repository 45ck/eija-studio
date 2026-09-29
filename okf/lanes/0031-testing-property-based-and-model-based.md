---
type: Capability Lane
title: 'Testing: property-based and model-based tests'
description: Capability lane with ADR numbers 0031–0032 reserved.
resource: repo://docs/adr/README.md#0031-0032
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0031-0032
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: 1f8a3e7a19765bd15ac13f46e2584ff584f7a09a548879d4b30f34152c5d7822
notes_baseline: 408fd136eb98403517832dc1bacd17c1343ebc534b9c30b39ddd01897eb2f853
---

# Testing: property-based and model-based tests

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0031–0032 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0031-0032` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0031: Property-based testing with Hypothesis, in two profiles](/adrs/0031-property-based-testing-with-hypothesis.md) - The kernel's guarantees are universally quantified: "every actor x state x action", "any order of definitions hashes the same", "any dependency graph closes to…
* [ADR-0032: Stateful differential testing against a specification-derived reference, with mutant negative controls](/adrs/0032-stateful-differential-testing-and-negative-controls.md) - The runtime's promises are about *histories*: replay never repeats effects, a revoked actor cannot replay a cached success, a crash rolls back everything, an e…
<!-- okf:generated:end links -->
