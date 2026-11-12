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
  sha256: ea918ba1d81feaf03d10363c4d722c3e7346ae569d80ad4040ac9e752949997a
notes_baseline: 5b6d3f05aaaa995baed5d90b2b8d759d7a42679c359370e57802cd8b089dea63
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
> `DataModel` refuses anything else, and it refuses a record class whose attributes and reference fields together exceed 40, which is what one screen shows.
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
> **UML interchange.** PlantUML, Mermaid, XMI and draw.io have no way to say an association is built. An export lists the built associations under `not_carried`. On import, an association that the current model builds stays built if the file draws it with the same ends, multiplicities and role, and the report lists it as defaulted.
>

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

## Referenced by

* [ADR-0237: Verify value-guard representatives by property and mutation, and fix what that found](/adrs/0237-value-guard-representatives-verified.md) - ADR-0231 to ADR-0235 added initiators, one action from several states, separation of duties, guards over record values and built associations.
<!-- okf:generated:end links -->
