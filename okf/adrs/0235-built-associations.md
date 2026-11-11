---
type: Architecture Decision Record
title: 'ADR-0235: Built associations as checked reference fields'
description: 'Issue #145, step 2.'
resource: repo://docs/adr/0235-built-associations.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0235-built-associations.md
  title: 0235-built-associations.md
  hash_method: lf-sha256-v1
  sha256: 50e8da456b9c28e1725ce7734591e7db95b92617e368db4febee33210ef7876a
notes_baseline: baf87eab89768f23f2d0e8eccb4fd8680f111c90d0afaf43007d986bb2719157
---

# ADR-0235: Built associations as checked reference fields

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-11 |
| Lane | kernel / executable UML |
| Source | `repo://docs/adr/0235-built-associations.md` |

## Decision outcome (verbatim)

> **The data model.** An association may set `built: true`. When it is false the field is left out of every dump, so the digest does not change. A built association must:
> * have the record class at one end and another class at the other;
> * link one record to at most one object (`1` or `0..1` at the other end);
> * have a role name that is a free attribute name of the record class.
>
> `DataModel` refuses anything else.
>
> **What a record holds.** `references(data)` lists the reference fields, named by the role. Such a field is required when the multiplicity is `1`. `record_fields(data)` lists the record's attributes followed by each reference field, typed as text of at most 32 characters. Screens, the API contract, the Studio's presentation and the generated form all read `record_fields`, so a reference appears wherever an attribute does.
>
> **The check.** `check_record(data, values, exists)` runs `check_values` on the attributes. It then checks each reference field:
> * it refuses a missing required reference with `FIELD_REQUIRED`;
> * it refuses a value that is not an id with `FIELD_TYPE`;
> * it refuses an id that names no stored object of the class with `REFERENCE_UNKNOWN`.
>
> **The built app.** The app stores objects of each referenced class in an `objects` table. `POST /api/objects/<Class>` checks the object's values against that class's attributes and returns a new id, and `GET /api/objects/<Class>` lists the stored objects. A class the app does not store answers `NOT_FOUND`. Record creation calls `check_record` with a lookup in the `objects` table. `REFERENCE_UNKNOWN` is a 400. The OpenAPI contract documents the objects route.
>
> **Conformance.** When a reference exists, the oracle gains `objects`: one sample object of each referenced class, which the conformance template stores before it creates records. The data cases add, for each reference, a missing value, a value that is not an id and an id that names nothing. An oracle without references is unchanged.
>
> **The class diagram report** (`class_build`) lists the stored classes as built and marks each built association. For a built association it says the app refuses an id that names nothing, instead of "drawn, not built".

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0205: The class diagram says what is drawn and what is built](/adrs/0205-the-class-diagram-says-what-is-drawn-and-what-is-built.md) - The built app stores records of the record class only (ADR-0150, ADR-0153).
<!-- okf:generated:end links -->
