---
type: Function
title: domain.affordance.affordances
description: Every single-step retarget and role change of ``model``, each with its dry-run verdict.
resource: repo://src/eija_studio/domain/affordance.py#affordances
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/affordance.py#affordances
  title: domain/affordance.py
  hash_method: ast-v2
  sha256: 5d82b26f2235c6bc922e09aad2398badc8f6dfebeb958329eee1812c75030d4c
notes_baseline: 4e39fa01f52fd329a8bb996d960838b2a1de277790eda9b3f0f5599982e55b9f
---

# domain.affordance.affordances

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/affordance`](/modules/domain/affordance.md) |
| Signature | `def affordances(model: Workflow, pack: Pack) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/affordance.py#affordances` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every single-step retarget and role change of ``model``, each with its dry-run verdict.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.service.Studio.affordances](/symbols/application/service/Studio.affordances.md) - Which single edits of the case's working model the kernel would accept (read-only).
<!-- okf:generated:end links -->
