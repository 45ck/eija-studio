---
type: Function
title: application.generated_app.verify_app
description: Seal the observed checker artifact, without approving or writing the case.
resource: repo://src/eija_studio/application/generated_app.py#verify_app
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#verify_app
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: 5a105c51a911cd70a6b70ba7ad3745c622b75d6a9a3e7821a363ffbaaaa1ac0a
notes_baseline: c37e77601a15e1e55e079ef61c594628349e93517eddede19a687f08e1dbb7c7
---

# application.generated_app.verify_app

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def verify_app(case: ChangeCase, subject: dict[str, Any], apps: GeneratedApps \| None, identity_provider: IdentityProvider, seal: Callable[[dict[str, Any]], dict[str, Any]], stamp: Callable[[], str], new_id: Callable[[], str]) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/generated_app.py#verify_app` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Seal the observed checker artifact, without approving or writing the case.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.GeneratedApps](/symbols/application/ports/GeneratedApps.md) - Capture exact generated artifacts and observe the existing local conformance checker.
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
