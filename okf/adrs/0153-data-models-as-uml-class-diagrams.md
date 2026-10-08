---
type: Architecture Decision Record
title: 'ADR-0153: Data models as UML class diagrams, checked in the built app'
description: Until now, records in a built app (ADR-0150) carried only a title, because the model had no data.
resource: repo://docs/adr/0153-data-models-as-uml-class-diagrams.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0153-data-models-as-uml-class-diagrams.md
  title: 0153-data-models-as-uml-class-diagrams.md
  hash_method: lf-sha256-v1
  sha256: b8ba82011b54c187a5902fa337b90e892515ccbc9642dcfc75ce27f78217031b
notes_baseline: 9ad003814520813771ef5fe2d74e509ac14f8c2e1089787993957b809fc7c9c7
---

# ADR-0153: Data models as UML class diagrams, checked in the built app

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for record attributes; other classes are diagram-only |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0153-data-models-as-uml-class-diagrams.md` |

## Decision outcome (verbatim)

> Chosen option: an optional `data.json` per pack, `domain/data.py`.
>
> * `DataModel` (`eija.data.v1`) has entities (UpperCamelCase names, at most 40), typed attributes, associations and a `record` entity. Attribute types are text (with `max_length`), number, date, boolean, and choice (with literals). Associations are association, aggregation or composition, each with a role and two multiplicities from `0..1`, `1`, `0..*`, `1..*`. The validator refuses duplicates, an undeclared record entity and associations to undeclared entities. `parse_data` also refuses a data model that names a different pack (`DATA_PACK_MISMATCH`).
> * `check_values(entity, values)` is the only check of record values. It returns the clean values or refuses with `FIELD_REQUIRED`, `FIELD_TYPE`, `FIELD_TOO_LONG`, `FIELD_CHOICE` or `UNKNOWN_FIELD`.
> * `data_for(pack)` reads `data.json` from the directory the pack snapshot was loaded from (`pack.pack_directory`). The digests of packs and models are unchanged.
> * `eija build` writes `app/data.json` when the pack has one. The generated service calls `check_values` on create and stores the values in a `fields` column (added in place to an older build's database). The page renders a form from the record class. The oracle gains `data_cases`, each answered by `check_values`: a valid record, each required value missing, each wrong type, each text too long, an undeclared choice and an unknown field. The conformance suite runs every case through the app's own create. Two new negative controls must fail conformance: values stored unchecked, and a required attribute made optional in `app/data.json`.
> * PlayIDE gets a **Class diagram** tab and `GET /api/play/data`. Classes are maxGraph swimlanes with an attribute compartment written `name: Type [0..1]`, with choices as `{A, B}`. The record class is marked «record». Associations show role names and multiplicities at both ends, with hollow or filled diamonds for aggregation and composition. Selecting a class shows its attributes and associations in the inspector.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0150: Build runnable apps from the model, checked against the kernel as oracle](/adrs/0150-build-apps-from-the-model-with-a-kernel-oracle.md) - The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".
<!-- okf:generated:end links -->
