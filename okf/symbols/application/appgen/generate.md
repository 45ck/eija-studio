---
type: Function
title: application.appgen.generate
description: Return the per-model files and the build manifest (without file hashes or test results).
resource: repo://src/eija_studio/application/appgen.py#generate
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#generate
  title: application/appgen.py
  hash_method: ast-v2
  sha256: ebae93fe05dee0341aa385377baadb0d7c9e3a5049af99b58dfa2d27b435e20c
notes_baseline: bde870780d06c5f8dca31e976aabfb4720382d9bcd9a49c989b2bb3d5f999442
---

# application.appgen.generate

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def generate(pack: Pack, model: Workflow \| None=None) -> tuple[dict[str, str], dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/appgen.py#generate` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Return the per-model files and the build manifest (without file hashes or test results).

Refuses a model the protected policy blocks: an app is never built from a workflow the kernel would refuse.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.FORMAT](/symbols/application/appgen/FORMAT.md) - Constant `FORMAT` in `application/appgen`.
* [application.appgen.LIMITS](/symbols/application/appgen/LIMITS.md) - Constant `LIMITS` in `application/appgen`.
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int) -> str` in `application/appgen`.
* [application.appgen.spec_source](/symbols/application/appgen/spec_source.md) - `def spec_source(pack: Pack, model: Workflow) -> str` in `application/appgen`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
<!-- okf:generated:end links -->
