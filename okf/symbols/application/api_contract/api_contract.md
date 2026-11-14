---
type: Function
title: application.api_contract.api_contract
description: The OpenAPI 3.1 document of the app this pack, model and data model build.
resource: repo://src/eija_studio/application/api_contract.py#api_contract
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/api_contract.py#api_contract
  title: application/api_contract.py
  hash_method: ast-v2
  sha256: 3e40bc452cbac1bf68a8a2c55d94e211d003ba574b249e844f790fcaa1f83565
notes_baseline: 5a1ad1947ac7e2a742b083e6bef4fd3cf51a2f6a44d2a8c96cc9a3f120d1d049
---

# application.api_contract.api_contract

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/api_contract`](/modules/application/api_contract.md) |
| Signature | `def api_contract(pack: Pack, model: Workflow, data: DataModel \| None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/api_contract.py#api_contract` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The OpenAPI 3.1 document of the app this pack, model and data model build.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.api_contract.FORMAT](/symbols/application/api_contract/FORMAT.md) - Constant `FORMAT` in `application/api_contract`.
* [application.api_contract.ONCE](/symbols/application/api_contract/ONCE.md) - Constant `ONCE` in `application/api_contract`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
