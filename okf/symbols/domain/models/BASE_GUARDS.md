---
type: Constant
title: domain.models.BASE_GUARDS
description: Constant `BASE_GUARDS` in `domain/models`.
resource: repo://src/eija_studio/domain/models.py#BASE_GUARDS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#BASE_GUARDS
  title: domain/models.py
  hash_method: ast-v2
  sha256: 809e2c6774107af44fe8d37162c606af96c14dac8fbfa2260e6cee360a176136
notes_baseline: 9c20ab9250592c6eb59418688191691281b78cace0348d95b73a8c98e878e2a7
---

# domain.models.BASE_GUARDS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `BASE_GUARDS: tuple[Guard, ...] = ('actor_active', 'role_current', 'state_equals', 'expected_version', 'operation_binding')` |
| Code | `repo://src/eija_studio/domain/models.py#BASE_GUARDS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Guard](/symbols/domain/models/Guard.md) - Type alias `Guard` in `domain/models`.

## Referenced by

* [application.new_system.sketch_documents](/symbols/application/new_system/sketch_documents.md) - `pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
* [domain.models.Transition.guarded](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models`.
<!-- okf:generated:end links -->
