---
type: Architecture Decision Record
title: 'ADR-0017: Local quality gates with nox sessions and noslop enforcement'
description: Hosted CI was not available for this repository when this was written (September 2026).
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
  sha256: d0c16f67a97cc56f0952619cafb544928bbb9d68a2bc7c31661d7fd5dcb15e25
notes_baseline: d411fd2b42132f918e070e7a24e3a6f820cfef9988cf352d1e9a41a5131ab775
---

# ADR-0017: Local quality gates with nox sessions and noslop enforcement

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted (its manual-dispatch-only part is superseded by [ADR-0228](0228-hosted-ci-on-pull-requests.md)) |
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
## Related decisions

* [ADR-0228: Hosted CI on pull requests, nightly full tier and auto-merge](/adrs/0228-hosted-ci-on-pull-requests.md) - ADR-0017 kept the GitHub workflows on manual `workflow_dispatch` because hosted CI was not available.

## Referenced by

* [ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets](/adrs/0035-static-analysis-and-architecture-fitness-functions.md) - The kernel's central claims (a vendor-free domain, authority checked before replay, computed evidence) hold only while the code keeps its shape.
* [ADR-0036: noslop guardrails adapted to run nox tiers; hook enablement is an explicit step](/adrs/0036-noslop-hooks-adapted-to-nox.md) - noslop installs git hooks and agent guardrails, but `noslop init` writes a generic Python pack: `black`, `ruff select=ALL`, `typos`, `mypy .`, plain `pytest`.
* [ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site](/adrs/0043-readme-truthfulness-and-docs-site.md) - EIJA's promise is that what you see matches the code.
* [HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change](/adrs/0068-hci-design-system-architecture.md) - HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change
* [ADR-0227: Search and generative-engine metadata for the repository and docs](/adrs/0227-search-and-generative-engine-metadata.md) - People and AI assistants find PlayIDE through GitHub, PyPI-style package metadata and the MkDocs site.
* [ADR-0228: Hosted CI on pull requests, nightly full tier and auto-merge](/adrs/0228-hosted-ci-on-pull-requests.md) - ADR-0017 kept the GitHub workflows on manual `workflow_dispatch` because hosted CI was not available.
<!-- okf:generated:end links -->
