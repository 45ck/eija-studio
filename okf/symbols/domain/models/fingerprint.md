---
type: Function
title: domain.models.fingerprint
description: 'SHA-256 of the canonical JSON of a value: the identity primitive used for models, subjects, artifacts and command bindings.'
resource: repo://src/eija_studio/domain/models.py#fingerprint
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#fingerprint
  title: domain/models.py
  hash_method: ast-v2
  sha256: a3e23680ee582029cc438029040fabdbf5ed8566fb83115adf4d04cd55e4b081
description_override: 'SHA-256 of the canonical JSON of a value: the identity primitive used for models, subjects, artifacts and command bindings.'
notes_baseline: bd96358d33c0feda44555c0a808ebf6ba0a2777dc0b1b6f7aaa194618b641eec
---

# domain.models.fingerprint

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `def fingerprint(value: Any) -> str` |
| Code | `repo://src/eija_studio/domain/models.py#fingerprint` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Deterministic because [canonical](/symbols/domain/models/canonical.md) sorts keys and forbids NaN. It detects change and corruption; it is not a proof of correctness and not a signature.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]` in `application/compiler`.
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.export](/symbols/application/service/Studio.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.propose](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` in `application/service`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
* [domain.data.DataModel.digest](/symbols/domain/data/DataModel.digest.md) - `def digest(self) -> str` in `domain/data`.
* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
* [domain.models.Workflow.semantic_hash](/symbols/domain/models/Workflow.semantic_hash.md) - `def semantic_hash(self) -> str` in `domain/models`.
* [domain.pack.Pack.digest](/symbols/domain/pack/Pack.digest.md) - `def digest(self) -> str` in `domain/pack`.
* [domain.scenarios.Scenarios.digest](/symbols/domain/scenarios/Scenarios.digest.md) - `def digest(self) -> str` in `domain/scenarios`.
* [domain.screens.Screens.digest](/symbols/domain/screens/Screens.digest.md) - `def digest(self) -> str` in `domain/screens`.
* [domain.sequences.Sequences.digest](/symbols/domain/sequences/Sequences.digest.md) - `def digest(self) -> str` in `domain/sequences`.
<!-- okf:generated:end links -->
