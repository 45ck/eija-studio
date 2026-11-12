---
type: Function
title: application.appgen.rules
description: 'The rule table the app shows: each action once, every state it leaves, where it leads and who takes it.'
resource: repo://src/eija_studio/application/appgen.py#rules
tags:
- symbol
- application
- function
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#rules
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 29499e56f44948295263425c213ef859e24b69cce9b7c20b9cc7384806a253f1
notes_baseline: 24b298a7c707c3cc6df161a949fcb0e8ffe1f80578f5760c9b5c8cc243c49910
---

# application.appgen.rules

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def rules(model: Workflow) -> dict[str, dict[str, str]]` |
| Code | `repo://src/eija_studio/application/appgen.py#rules` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The rule table the app shows: each action once, every state it leaves, where it leads and who takes it.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
