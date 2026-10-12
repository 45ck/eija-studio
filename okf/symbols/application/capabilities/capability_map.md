---
type: Function
title: application.capabilities.capability_map
description: The supported constructs, bounded to the current model, with no inferred readiness.
resource: repo://src/eija_studio/application/capabilities.py#capability_map
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/capabilities.py#capability_map
  title: application/capabilities.py
  hash_method: ast-v2
  sha256: f5ecb2a59514521c4014019ed747543123fd200b1be325f5cb27a52c56bcffba
notes_baseline: 25c7c8acdbef37fddede788971458a19316519c2463b664290f5c52c7e8d4768
---

# application.capabilities.capability_map

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/capabilities`](/modules/application/capabilities.md) |
| Signature | `def capability_map(pack: Pack, model: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/capabilities.py#capability_map` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The supported constructs, bounded to the current model, with no inferred readiness.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
