---
type: Class
title: domain.models.Proposal
description: '`class Proposal(Contract)` in `domain/models`.'
resource: repo://src/eija_studio/domain/models.py#Proposal
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Proposal
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: f52d90722dc367fbff269ae62613a9931f3bbd6f10458ba5e40c7d601dbf2f2a
notes_baseline: fc8a816c4c13e706a2018218b2e79f3f4d68cceaba532aa66509470b2d38fa32
---

# domain.models.Proposal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Proposal(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Proposal` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `summary` | `str` | `Field(min_length=1, max_length=1600)` |
| `alternatives` | `tuple[Alternative, ...]` | `Field(min_length=1, max_length=4)` |
| `unknowns` | `tuple[str, ...]` | `Field(max_length=10)` |

## Methods

* [`unique`](/symbols/domain/models/Proposal.unique.md) - `def unique(self) -> Proposal`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Alternative](/symbols/domain/models/Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [application.ports.ProviderResult](/symbols/application/ports/ProviderResult.md) - `class ProviderResult` in `application/ports`.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.Proposal.unique](/symbols/domain/models/Proposal.unique.md) - `def unique(self) -> Proposal` in `domain/models`.
<!-- okf:generated:end links -->
