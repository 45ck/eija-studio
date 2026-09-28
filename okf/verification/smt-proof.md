---
type: Verification Technique
title: SMT policy soundness
description: 'Establishes: `check_policy` accepts only authority-preserving candidates across the whole transaction grammar'
resource: repo://docs/adr/0018-formal-vv-portfolio.md#smt_proof
tags:
- verification
- planned
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0018-formal-vv-portfolio.md#smt_proof
  title: 0018-formal-vv-portfolio.md
  hash_method: md-table-row-v1
  sha256: bc691c72de305603dcbef508c5d4960f3ddf412721fde702da950566b812d034
---

# SMT policy soundness

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Evidence kind | `smt_proof` |
| Tool | [Z3](https://github.com/Z3Prover/z3) |
| Source | `repo://docs/adr/0018-formal-vv-portfolio.md#smt_proof` |

## What it can establish

`check_policy` accepts only authority-preserving candidates across the whole transaction grammar

This technique is planned by the ADR. The page stays `draft` until its lane lands and the ADR accepts it. It is a distinct evidence kind and may never be relabelled as another.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Decision

* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
<!-- okf:generated:end links -->
