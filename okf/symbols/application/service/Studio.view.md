---
type: Method
title: application.service.Studio.view
description: '`def view(self, case_id: str, scope: str=''local-demo'') -> dict` in `application/service` (the source has no docstring).'
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
  hash_method: ast-v1
  sha256: 84ee6786aa886a91cac4314c1bf19834dcee0067cc79b309951e146e02460a33
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
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
* [domain.policy.CANONICAL_OPTIONS](/symbols/domain/policy/CANONICAL_OPTIONS.md) - `CANONICAL_OPTIONS = {'recommend_only': {'label': 'Teacher recommends; registrar decides', 'supported': True, 'consequences': ['Only active, assigned…` in `dom…
<!-- okf:generated:end links -->
