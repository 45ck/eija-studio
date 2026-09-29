---
type: Class
title: domain.models.SemanticTransaction
description: 'One typed business-meaning edit: enable recommendation or set the registrar rejection source.'
resource: repo://src/eija_studio/domain/models.py#SemanticTransaction
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#SemanticTransaction
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 80ee1eb79fe0406b313022532eda971325cf6ee7629f09d77b7d6e7a48d40e37
description_override: 'One typed business-meaning edit: enable recommendation or set the registrar rejection source.'
notes_baseline: 071a13d59d33ca89c6b36f8c46aacca71735cc9802f310bc41bb35362c033771
---

# domain.models.SemanticTransaction

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class SemanticTransaction(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#SemanticTransaction` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['enable_recommendation', 'set_rejection_source']` |  |
| `rejection_source` | `Literal['Submitted', 'Recommended']` | `'Recommended'` |
<!-- okf:generated:end facts -->

## Notes

Rule-table and state-view commands produce this same shape ([Semantic Transaction](/language/semantic-transaction.md)); it is consumed only by [apply_transaction](/symbols/domain/policy/apply_transaction.md).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [Semantic Transaction](/language/semantic-transaction.md) - One typed business-meaning edit.
* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended).
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.formal.what_if_model](/symbols/application/formal/what_if_model.md) - The workflow an unsupported interpretation would produce (recommendation enabled, the fault applied), or None.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Legacy closed vocabulary (two kinds), kept until the open vocabulary of WBS 1.3 replaces it: the recommendation meaning of the default pack and a rejection-sou…
<!-- okf:generated:end links -->
