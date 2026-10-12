---
type: Class
title: domain.generated_app.GeneratedAppBinding
description: '`class GeneratedAppBinding(Contract)` in `domain/generated_app`.'
resource: repo://src/eija_studio/domain/generated_app.py#GeneratedAppBinding
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/generated_app.py#GeneratedAppBinding
  title: domain/generated_app.py
  hash_method: ast-sig-v1
  sha256: 0e483293bf5f376ca96e230aa2f940df0d04548411378c0a8faee36f34d3590a
notes_baseline: 182826924b90573a7d62d0b14dc5af7b83a98e2ce7ca546b1593f1aa04afa295
---

# domain.generated_app.GeneratedAppBinding

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/generated_app`](/modules/domain/generated_app.md) |
| Signature | `class GeneratedAppBinding(Contract)` |
| Code | `repo://src/eija_studio/domain/generated_app.py#GeneratedAppBinding` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `format` | `Literal['eija.generated-app-review.v1']` |  |
| `subject` | `GeneratedBuildSubject` |  |
| `checker` | `GeneratedChecker` |  |
| `configuration` | `GeneratedCheckConfiguration` |  |
| `digest` | `Digest` |  |

## Methods

* [`consistent_digest`](/symbols/domain/generated_app/GeneratedAppBinding.consistent_digest.md) - `def consistent_digest(self) -> Self`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.generated_app.Digest](/symbols/domain/generated_app/Digest.md) - Type alias `Digest` in `domain/generated_app`.
* [domain.generated_app.GeneratedBuildSubject](/symbols/domain/generated_app/GeneratedBuildSubject.md) - `class GeneratedBuildSubject(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedCheckConfiguration](/symbols/domain/generated_app/GeneratedCheckConfiguration.md) - `class GeneratedCheckConfiguration(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedChecker](/symbols/domain/generated_app/GeneratedChecker.md) - `class GeneratedChecker(Contract)` in `domain/generated_app`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.generated_app.bind_subject](/symbols/application/generated_app/bind_subject.md) - `def bind_subject(subject: dict[str, Any], binding: GeneratedAppBinding | None) -> dict[str, Any]` in `application/generated_app`.
* [application.generated_app.review_snapshot](/symbols/application/generated_app/review_snapshot.md) - Derive canonical contracts and the review binding through the shared pure assembler.
* [application.generated_app.validate_review_payload](/symbols/application/generated_app/validate_review_payload.md) - The selected payload and installed implementation must satisfy the same build-subject contract.
* [application.ports.GeneratedApps](/symbols/application/ports/GeneratedApps.md) - Capture exact generated artifacts and observe the existing local conformance checker.
* [application.ports.GeneratedSnapshot](/symbols/application/ports/GeneratedSnapshot.md) - Type alias `GeneratedSnapshot` in `application/ports`.
* [application.ports.GeneratedSubjectValidator](/symbols/application/ports/GeneratedSubjectValidator.md) - Type alias `GeneratedSubjectValidator` in `application/ports`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.generated_app.GeneratedAppActivation](/symbols/domain/generated_app/GeneratedAppActivation.md) - `class GeneratedAppActivation(Contract)` in `domain/generated_app`.
* [domain.generated_app.GeneratedAppBinding.consistent_digest](/symbols/domain/generated_app/GeneratedAppBinding.consistent_digest.md) - `def consistent_digest(self) -> Self` in `domain/generated_app`.
* [domain.generated_app.generated_receipt_status](/symbols/domain/generated_app/generated_receipt_status.md) - Compute a scoped process observation, never trust its submitted status field.
<!-- okf:generated:end links -->
