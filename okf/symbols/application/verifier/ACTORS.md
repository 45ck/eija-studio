---
type: Constant
title: application.verifier.ACTORS
description: Constant `ACTORS` in `application/verifier`.
resource: repo://src/eija_studio/application/verifier.py#ACTORS
tags:
- symbol
- application
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/verifier.py#ACTORS
  title: application/verifier.py
  hash_method: ast-v2
  sha256: 60f1d42e59bfc69407c1e96bafc9c813b2958f46d04570fd36a2150d0490205c
notes_baseline: 773c7a3de237c020a81b15a3812ae369c1601986779e03f1aaa1f980f4f6ae7e
---

# application.verifier.ACTORS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/verifier`](/modules/application/verifier.md) |
| Signature | `ACTORS = [('teacher-assigned', 'Teacher', True, True), ('teacher-unassigned', 'Teacher', True, False), ('teacher-revoked', 'Teacher', False, True), ('registrar…` |
| Code | `repo://src/eija_studio/application/verifier.py#ACTORS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier`.
<!-- okf:generated:end links -->
