---
type: Method
title: domain.models.Workflow.receiving
description: The declaration that `signal` from `sender` starts a record here, if there is one (ADR-0242).
resource: repo://src/eija_studio/domain/models.py#Workflow.receiving
tags:
- symbol
- domain
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Workflow.receiving
  title: domain/models.py
  hash_method: ast-v2
  sha256: 109700d0f3ac9a6b813aa807bfedc2893f998caf51dc8889ed36b41e65716c61
notes_baseline: cccd86b73f580b5ea6d5afe53b1629532563502a22094e4c63f8d379669ad44f
---

# domain.models.Workflow.receiving

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`domain/models`](/modules/domain/models.md) |
| Class | [`Workflow`](/symbols/domain/models/Workflow.md) |
| Signature | `def receiving(self, signal: str, sender: str) -> Receive \| None` |
| Code | `repo://src/eija_studio/domain/models.py#Workflow.receiving` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The declaration that `signal` from `sender` starts a record here, if there is one (ADR-0242).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Receive](/symbols/domain/models/Receive.md) - A signal another workflow of the system sends that starts a record here (issue #93 item 5, ADR-0242): the signal effect `signal` declared by the pack `sender`.
<!-- okf:generated:end links -->
