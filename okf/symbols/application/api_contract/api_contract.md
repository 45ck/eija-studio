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
  sha256: af2c38c57a9bf2fd3c9b11cbe361de7bdbeec4885da5cee11895cb8be61de989
notes_baseline: bfedc2b7c06f91f17e568b3a61439a5193e7177e8264da73d4d28838258b6d0b
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
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
