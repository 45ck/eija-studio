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
  sha256: aa6674e6f011054330a1d549ab222363a31f50ce94d9c55eac11f8d6bd7e8d07
notes_baseline: a7b774deff55954e40aae76f98a62af6643a23e7e56165680eaf2015a412d958
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
> * Each stored record keeps the digest of the data model that checked its values. A record from an earlier data model is not current and every action on it is refused with `STALE_DATA`, as an earlier workflow model's records are refused with `STALE_INSTANCE`. Choice literals are non-empty, because an empty value means "unset". No app is built when no fixture actor is active (`NO_ACTIVE_ACTOR`), since nobody could create a record. PlayIDE keys a built app by the model hash and the data model digest, so a changed data model never reuses the running process.
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

## Referenced by

* [ADR-0154: Use case diagrams, and screens designed against the model](/adrs/0154-use-cases-and-screens-designed-against-the-model.md) - PlayIDE shows the workflow as a state machine (ADR-0151) and the data as a class diagram (ADR-0153).
* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0176: How a UML change looks: one stable layout, removed parts kept as ghosts, and lenses](/adrs/0176-how-a-uml-change-looks.md) - The owner asked how a change can be reviewed as a UML change instead of a pull request, and "how you even view a UML change (ghost UI/UX?)".
<!-- okf:generated:end links -->
