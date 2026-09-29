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
notes_baseline: d4ae5c69d86f7fcdd3692845ed27f1dbe173038ed9f047624ed492da8853cd6f
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
## Referenced by

* [ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets](/adrs/0035-static-analysis-and-architecture-fitness-functions.md) - The kernel's central claims (a vendor-free domain, authority checked before replay, computed evidence) hold only while the code keeps its shape.
* [ADR-0036: noslop guardrails adapted to run nox tiers; hook enablement is an explicit step](/adrs/0036-noslop-hooks-adapted-to-nox.md) - noslop installs git hooks and agent guardrails, but `noslop init` writes a generic Python pack: `black`, `ruff select=ALL`, `typos`, `mypy .`, plain `pytest`.
* [ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site](/adrs/0043-readme-truthfulness-and-docs-site.md) - EIJA's promise is that what you see matches the code.
* [HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change](/adrs/0068-hci-design-system-architecture.md) - HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change
<!-- okf:generated:end links -->
