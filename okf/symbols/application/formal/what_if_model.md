---
type: Function
title: application.formal.what_if_model
description: The workflow an unsupported interpretation would produce (recommendation enabled, the fault applied), or None.
resource: repo://src/eija_studio/application/formal.py#what_if_model
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/formal.py#what_if_model
  title: application/formal.py
  hash_method: ast-v2
  sha256: 1d4135ec8fa9acd15d2aac4ba3751faccdd58b5ad3539e37d75f0c20bbcd3a4c
notes_baseline: 2de743125748fd1798eb1c585adafa490825bf2198543a4bf2e56f197b0aa0ea
---

# application.formal.what_if_model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def what_if_model(baseline: Workflow, interpretation: str) -> Workflow \| None` |
| Code | `repo://src/eija_studio/application/formal.py#what_if_model` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The workflow an unsupported interpretation would produce (recommendation enabled, the fault applied), or None.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.formal.WHAT_IF_FAULTS](/symbols/application/formal/WHAT_IF_FAULTS.md) - Constant `WHAT_IF_FAULTS` in `application/formal`.
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Legacy closed vocabulary (two kinds), kept until the open vocabulary of WBS 1.3 replaces it: the recommendation meaning of the default pack and a rejection-sou…
<!-- okf:generated:end links -->
