---
type: Function
title: application.scxml.to_scxml
description: The model as an SCXML document.
resource: repo://src/eija_studio/application/scxml.py#to_scxml
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scxml.py#to_scxml
  title: application/scxml.py
  hash_method: ast-v2
  sha256: 6eab409668ea94c99bec3ffbd7ff67a4e739051215330428c96b815f9bd7666f
notes_baseline: d7ea9da138eabfd338874e511d1c927320a3a1c001ff36988e494889ce4028b6
---

# application.scxml.to_scxml

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scxml`](/modules/application/scxml.md) |
| Signature | `def to_scxml(pack: Pack, model: Workflow \| None=None) -> str` |
| Code | `repo://src/eija_studio/application/scxml.py#to_scxml` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The model as an SCXML document. Refuses a model the protected policy blocks, as `eija build` does.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.scxml.FORMAT](/symbols/application/scxml/FORMAT.md) - Constant `FORMAT` in `application/scxml`.
* [application.scxml.NAMESPACE](/symbols/application/scxml/NAMESPACE.md) - Constant `NAMESPACE` in `application/scxml`.
* [application.scxml.hoisted](/symbols/application/scxml/hoisted.md) - The transitions each state or composite carries in the chart.
* [application.scxml.scxml_id](/symbols/application/scxml/scxml_id.md) - An XML/SCXML-safe id for a state or event name.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
<!-- okf:generated:end links -->
