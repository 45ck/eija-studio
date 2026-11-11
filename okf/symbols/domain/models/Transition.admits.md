---
type: Method
title: domain.models.Transition.admits
description: The first condition these record values fail, or None when the transition's conditions all hold.
resource: repo://src/eija_studio/domain/models.py#Transition.admits
tags:
- symbol
- domain
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Transition.admits
  title: domain/models.py
  hash_method: ast-v2
  sha256: dfa1d5028c85cc9944910394e395b57410d574ae763e51bd9a44405593c9cac7
notes_baseline: 497180370149b93ace4d8176dce5ab4b99430dbaca6e9d56c2db19c13ee5bf4b
---

# domain.models.Transition.admits

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`domain/models`](/modules/domain/models.md) |
| Class | [`Transition`](/symbols/domain/models/Transition.md) |
| Signature | `def admits(self, values: dict[str, Any]) -> ValueGuard \| None` |
| Code | `repo://src/eija_studio/domain/models.py#Transition.admits` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The first condition these record values fail, or None when the transition's conditions all hold.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.ValueGuard](/symbols/domain/models/ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).
<!-- okf:generated:end links -->
