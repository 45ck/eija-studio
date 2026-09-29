---
type: Capability Lane
title: 'Formal: Z3 policy soundness and bounded model checking'
description: Capability lane with ADR numbers 0029–0030 reserved.
resource: repo://docs/adr/README.md#0029-0030
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0029-0030
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: 35e052005028e8d9b94347645f3b749a08d43d13dd67f43f7bdd6652ee50e377
notes_baseline: 0301d8c0de5b1a9bc938fed3d631137641b2e89336237904f5ea70799febd6bb
---

# Formal: Z3 policy soundness and bounded model checking

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0029–0030 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0029-0030` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates](/adrs/0029-z3-policy-soundness-proof.md) - `domain.policy.check_policy` is the gate between an AI-proposed candidate workflow and the local owner.
* [ADR-0030: Bounded model checking by explicit-state search over the real runtime](/adrs/0030-bounded-model-checking-of-the-real-runtime.md) - The runtime matrix in `application/verifier.py` is one-step: five actors times five states times five actions, each cell from a fresh instance.
<!-- okf:generated:end links -->
