---
type: Method
title: application.service.Studio.view
description: '`def view(self, case_id: str, scope: str=''local-demo'') -> dict[str, Any]` in `application/service`.'
resource: repo://src/eija_studio/application/service.py#Studio.view
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.view
  title: application/service.py
  hash_method: ast-v2
  sha256: ff8a00028e8fa85fac47be7d038a08f1141c291fea4491951e71d197ac6a2299
notes_baseline: f9a53aa292dd41907d759bb6db492072e0ece272e7c5b508857845f48490d384
---

# application.service.Studio.view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [domain.policy.meaning_options](/symbols/domain/policy/meaning_options.md) - The pack's meanings as the review surface shows them: label, whether supported, consequences.
<!-- okf:generated:end links -->
