---
type: Architecture Decision Record
title: 'ADR-0017: Local quality gates with nox sessions and noslop enforcement'
description: Hosted CI is not currently available for this repository.
resource: repo://docs/adr/0017-local-quality-gates.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0017-local-quality-gates.md
  title: 0017-local-quality-gates.md
  hash_method: lf-sha256-v1
  sha256: 203666932a77afe16c9534f446fb156714ba271f9939229a06f4117a0e0d2559
---

# ADR-0017: Local quality gates with nox sessions and noslop enforcement

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Source | `repo://docs/adr/0017-local-quality-gates.md` |

## Decision outcome (verbatim)

> `noxfile.py` loads one module per gate family from `quality/sessions/`, tagged `fast`, `full` or `release`. [noslop](https://github.com/45ck/noslop) installs git hooks and agent guardrails that run those tiers and block `--no-verify`. Heavy sessions run serially. The GitHub workflow is kept, but it runs only on manual `workflow_dispatch` until hosted CI is enabled.

## Sections

* Context and problem statement
* Considered options
* Decision outcome

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://noxfile.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
