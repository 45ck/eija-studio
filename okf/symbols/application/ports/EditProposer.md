---
type: Class
title: application.ports.EditProposer
description: Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
resource: repo://src/eija_studio/application/ports.py#EditProposer
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#EditProposer
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: 447e3326016da1c8403976202f561b20056f15d25ec7fc3428f664f4553f134e
notes_baseline: 127275c283fe6a540ddea02c269632cc00d3cd901b8a82494e8a67c9d42785a8
---

# application.ports.EditProposer

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class EditProposer(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#EditProposer` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
~~~

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def propose(self, request: str, model: Workflow, choices: tuple[Transaction, ...]) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
