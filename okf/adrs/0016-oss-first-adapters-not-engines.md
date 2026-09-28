---
type: Architecture Decision Record
title: 'ADR-0016: OSS first: build adapters, not engines'
description: 'EIJA''s value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.'
resource: repo://docs/adr/0016-oss-first-adapters-not-engines.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0016-oss-first-adapters-not-engines.md
  title: 0016-oss-first-adapters-not-engines.md
  hash_method: lf-sha256-v1
  sha256: 76ece21c8e718003b8b3f1da32babb8bca1d9baa4c32fb42600d206cfbc7a7f4
---

# ADR-0016: OSS first: build adapters, not engines

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Source | `repo://docs/adr/0016-oss-first-adapters-not-engines.md` |

## Decision outcome (verbatim)

> Every capability first adopts existing open source (see [docs/oss/REGISTER.md](repo://docs/oss/REGISTER.md)). Custom code is limited to EIJA-specific glue:
>
> * **generators** that project the executable model into a tool's input format,
> * **adapters** that turn the tool's output into typed EIJA evidence, and
> * the **kernel** itself.
>
> This follows the ProofMap Lite doctrine (<https://github.com/45ck/proofmap-lite>). Each custom module records, in the register or its ADR, the OSS it checked, why adapter or dependency use was insufficient, and the path to replace or fork it.

## Sections

* Context and problem statement
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](/adrs/0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.
<!-- okf:generated:end links -->
