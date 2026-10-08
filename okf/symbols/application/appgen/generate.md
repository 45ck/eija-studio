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
  sha256: c7cc4c89651c33a86ff1a4b30077cace453744e0dac7d7350a4fd5ba8111867f
notes_baseline: 0024b0d38e1a5e0e0867a79b6b20ef72619c348f8a96c1725f7cd5d7057e599f
---

# application.appgen.generate

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def generate(pack: Pack, model: Workflow \| None=None, data: DataModel \| None=None) -> tuple[dict[str, str], dict[str, Any]]` |
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
* [application.appgen.app_limits](/symbols/application/appgen/app_limits.md) - `def app_limits(data: DataModel | None) -> list[str]` in `application/appgen`.
* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_values`' answer for each: a valid record, then each required value missing, each value of the wrong type, each text on…
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
<!-- okf:generated:end links -->
