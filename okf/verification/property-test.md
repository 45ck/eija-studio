---
type: Verification Technique
title: Model-based differential tests
description: 'Establishes: The runtime and SQLite agree with an independent reference model on generated sequences'
resource: repo://docs/adr/0018-formal-vv-portfolio.md#property_test
tags:
- verification
- planned
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0018-formal-vv-portfolio.md#property_test
  title: 0018-formal-vv-portfolio.md
  hash_method: md-table-row-v1
  sha256: 7902d2353ea36f67018e329f23e5fbf04cd9c525ac93ee2de69db9d143c8b080
---

# Model-based differential tests

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Evidence kind | `property_test` |
| Tool | [Hypothesis](https://github.com/HypothesisWorks/hypothesis) stateful testing |
| Source | `repo://docs/adr/0018-formal-vv-portfolio.md#property_test` |

## What it can establish

The runtime and SQLite agree with an independent reference model on generated sequences

This technique is planned by the ADR. The page stays `draft` until its lane lands and the ADR accepts it. It is a distinct evidence kind and may never be relabelled as another.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Decision

* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
<!-- okf:generated:end links -->
