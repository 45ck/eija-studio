---
type: Function
title: application.generated_app.review_snapshot
description: Derive canonical contracts and the review binding through the shared pure assembler.
resource: repo://src/eija_studio/application/generated_app.py#review_snapshot
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#review_snapshot
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: 3b3f2cbdf113856948b5b354612b75d5f177370e663c8efbb88210536271dff3
notes_baseline: 1778b66845bff451ee2f6b904b232e201fa42868d864a83b179c1b73dcb29bdf
---

# application.generated_app.review_snapshot

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def review_snapshot(pack: Pack, model: Workflow, static: dict[str, str], identity: dict[str, Any], configuration: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any], GeneratedAppBinding]` |
| Code | `repo://src/eija_studio/application/generated_app.py#review_snapshot` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Derive canonical contracts and the review binding through the shared pure assembler.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.generated_app.assemble_app](/symbols/application/generated_app/assemble_app.md) - One generator and snapshot identity for previews and approved artifacts.
* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
<!-- okf:generated:end links -->
