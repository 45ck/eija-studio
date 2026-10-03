---
type: Verification Technique
title: Bounded exhaustive runtime
description: 'Planned (not implemented). Would establish: No reachable counterexample within depth *k*'
resource: repo://docs/adr/0018-formal-vv-portfolio.md#bounded_model_check
tags:
- verification
- planned
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0018-formal-vv-portfolio.md#bounded_model_check
  title: 0018-formal-vv-portfolio.md
  hash_method: md-table-row-v1
  sha256: 09bbf17b0f610d68de2697b8c065a6b38bb8cc8b4e781be041bef0d5edf5103d
notes_baseline: a52b555aa8f78d3e953def9e9e6ab334cb35c900b8433afd685c182594a595a9
---

# Bounded exhaustive runtime

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Evidence kind | `bounded_model_check` |
| Tool | explicit-state search over the real runtime |
| Source | `repo://docs/adr/0018-formal-vv-portfolio.md#bounded_model_check` |

## What it can establish

No reachable counterexample within depth *k*

**Status: planned, not implemented in the kernel.** The ADR names this technique; no code in this repository produces this evidence yet. The page is `draft` (unreviewed plan) whatever the ADR's own status becomes, and it is a distinct evidence kind that may never be relabelled as another.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Decision

* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
<!-- okf:generated:end links -->
