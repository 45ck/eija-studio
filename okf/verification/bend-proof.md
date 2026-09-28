---
type: Verification Technique
title: Machine-checked laws
description: 'Planned (not implemented). Would establish: Laws hold for **all** action sequences of the model generated from code'
resource: repo://docs/adr/0018-formal-vv-portfolio.md#bend_proof
tags:
- verification
- planned
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0018-formal-vv-portfolio.md#bend_proof
  title: 0018-formal-vv-portfolio.md
  hash_method: md-table-row-v1
  sha256: df89b05c8c8eaa536add3a4158965a7d0a28a4b00933134e52275a10e5bae36d
notes_baseline: e8b4c7c46591a99cc89c9af5c9abe4ed23856d1e9ea567cfa9cc710fe0cd3d3a
---

# Machine-checked laws

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Evidence kind | `bend_proof` |
| Tool | [Bend 2](https://github.com/bendlang/bend) `LAWS.bend` / `PROOF.bend` |
| Source | `repo://docs/adr/0018-formal-vv-portfolio.md#bend_proof` |

## What it can establish

Laws hold for **all** action sequences of the model generated from code

**Status: planned, not implemented in the kernel.** The ADR names this technique; no code in this repository produces this evidence yet. The page is `draft` (unreviewed plan) whatever the ADR's own status becomes, and it is a distinct evidence kind that may never be relabelled as another.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Decision

* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
<!-- okf:generated:end links -->
