---
type: Method
title: application.service.Studio.view
description: '`def view(self, case_id: str, scope: str=''local-demo'') -> dict` in `application/service`.'
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
  sha256: b104cbb760ebc85dfd7cc2ec08500f1ba8d3c2e01263723f3cd10c0d10661726
notes_baseline: 2af7d65e720367af5e24f8fb980a0c95e22fdcca7d12674d265a6607e7a4073d
---

# application.service.Studio.view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def view(self, case_id: str, scope: str='local-demo') -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo…` in `application/compiler`.
* [domain.policy.CANONICAL_OPTIONS](/symbols/domain/policy/CANONICAL_OPTIONS.md) - Constant `CANONICAL_OPTIONS` in `domain/policy`.
<!-- okf:generated:end links -->
