---
type: Function
title: application.formal.what_if_model
description: The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
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
  sha256: 017c4480f413c682a4412d7a00cc50305fcb247813f1de76f5693f2c0db36a2d
notes_baseline: 76ad1d31b071ee47b0cf57f40a24cd230da777de46dac10f47ecbdebe0db7087
---

# application.formal.what_if_model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def what_if_model(baseline: Workflow, interpretation: str, pack: Pack \| None=None) -> Workflow \| None` |
| Code | `repo://src/eija_studio/application/formal.py#what_if_model` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.what_if](/symbols/domain/policy/what_if.md) - What an UNSUPPORTED meaning would do to ``model`` (structure only, never a candidate), or None when it declares no transactions or they do not even apply struc…
<!-- okf:generated:end links -->
