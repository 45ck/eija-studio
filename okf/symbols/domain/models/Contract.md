---
type: Class
title: domain.models.Contract
description: 'Base class for every domain contract: frozen and strict, unknown fields rejected.'
resource: repo://src/eija_studio/domain/models.py#Contract
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Contract
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 13c7cce1eef29efa373e8a053caddb16b9bab3cf15342d024340ed1379f4c73a
description_override: 'Base class for every domain contract: frozen and strict, unknown fields rejected.'
notes_baseline: 5053b280e054b67051413e1455ce4535d9f574101cd731628bcb0a4ce6eee0e0
---

# domain.models.Contract

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Contract(BaseModel)` |
| Code | `repo://src/eija_studio/domain/models.py#Contract` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The reason unknown fields and operators die at the boundary (acceptance [AC01](/requirements/ac01.md)). Contracts are immutable; a change produces a new value through validation, never `model_copy(update=...)`.

<!-- okf:generated:begin links -->
## Referenced by

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.Alternative](/symbols/domain/models/Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
