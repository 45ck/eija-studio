---
type: Function
title: application.sequence_draft.outsider
description: 'Someone active in another role tries the first step: the kernel must refuse it.'
resource: repo://src/eija_studio/application/sequence_draft.py#outsider
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_draft.py#outsider
  title: application/sequence_draft.py
  hash_method: ast-v2
  sha256: b5a7a2c9f44ca59c26e3dad7f9245cad612a5221db22d50f6f108a587fe821fa
notes_baseline: 4a82378994f7d12d85aa1dab9c3dca24100eb4baf429cc052b6aadd34fcbc36f
---

# application.sequence_draft.outsider

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequence_draft`](/modules/application/sequence_draft.md) |
| Signature | `def outsider(pack: Pack, model: Workflow) -> tuple[str, str, list[tuple[str, str]]] \| None` |
| Code | `repo://src/eija_studio/application/sequence_draft.py#outsider` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Someone active in another role tries the first step: the kernel must refuse it.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.sequence_draft.draft_scenarios](/symbols/application/sequence_draft/draft_scenarios.md) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
<!-- okf:generated:end links -->
