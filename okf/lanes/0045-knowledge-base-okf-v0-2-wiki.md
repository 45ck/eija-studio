---
type: Capability Lane
title: 'Knowledge base: OKF v0.2 wiki deterministically linked to code'
description: Capability lane with ADR numbers 0045–0046 reserved.
resource: repo://docs/adr/README.md#0045-0046
tags:
- lane
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/README.md#0045-0046
  title: docs/adr/README.md
  hash_method: md-table-row-v1
  sha256: 2692b65d46d1f760fe1d5b0fe5c75d2a8fe639de6fe2f063f94425fc6c91f247
notes_baseline: ec3448c67f95273829e60ff32bacc8c7279b215bcd662a99ff1d74111a20ac19
---

# Knowledge base: OKF v0.2 wiki deterministically linked to code

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Reserved ADR numbers | 0045–0046 |
| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |
| Source | `repo://docs/adr/README.md#0045-0046` |

## Landed ADRs

Listed under the generated links below.
<!-- okf:generated:end facts -->

## Notes

This lane's gate is [nox -s okf](/gates/okf/okf.md). The generator and checker live in `repo://quality/okf/codelink.py` and its sibling modules.

<!-- okf:generated:begin links -->
## Landed ADRs

* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](/adrs/0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.
* [ADR-0046: Code-link hash methods and STALE semantics](/adrs/0046-code-link-hash-methods-and-stale-semantics.md) - ADR-0045 links wiki pages to code with content hashes.
<!-- okf:generated:end links -->
