---
type: Verification Technique
title: Temporal model checking
description: 'Planned (not implemented). Would establish: Safety invariants of the workflow and the commit protocol (replay, CAS, authority), up to declared bounds'
resource: repo://docs/adr/0018-formal-vv-portfolio.md#tlc_model_check
tags:
- verification
- planned
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0018-formal-vv-portfolio.md#tlc_model_check
  title: 0018-formal-vv-portfolio.md
  hash_method: md-table-row-v1
  sha256: fcd972a905bc5c8627c03fa518f1fba366bbd46b6a9dce221670f5623f868d82
notes_baseline: f6e58a7be5bdb3d211813133f04022d39b4f2565a9f6744b4312016b92a978bd
---

# Temporal model checking

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Evidence kind | `tlc_model_check` |
| Tool | [TLA+](https://github.com/tlaplus/tlaplus) with TLC |
| Source | `repo://docs/adr/0018-formal-vv-portfolio.md#tlc_model_check` |

## What it can establish

Safety invariants of the workflow and the commit protocol (replay, CAS, authority), up to declared bounds

**Status: planned, not implemented in the kernel.** The ADR names this technique; no code in this repository produces this evidence yet. The page is `draft` (unreviewed plan) whatever the ADR's own status becomes, and it is a distinct evidence kind that may never be relabelled as another.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Decision

* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
<!-- okf:generated:end links -->
