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
  sha256: 24656d65f429f1ea6bc4ae25a303b37ca7d62394b15aa8a16039fe0eb9c35d14
notes_baseline: 9f3f75794cbc8ddafc11c9d990c276b47c580b91447c04b42d093be64945e665
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
