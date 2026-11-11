# ADR-0235: Built associations as checked reference fields

* Status: accepted
* Date: 2026-11-11
* Lane: kernel / executable UML

## Context and problem statement

Issue #145, step 2. ADR-0205 made the class diagram say which parts the built app enforces: the record class is built and checked, while every other class and association is drawn only. A loan's borrower was a plain `memberCard` text attribute. The app checked the text but never checked that such a member exists. Step 1 flagged that gap. Step 2 builds the simplest association that closes it.

## Decision drivers

* Every shipped data model, digest, oracle and recording keeps its exact bytes. Building is opt-in, per association.
* The data model's own check decides, in `eija_studio.domain.data`, and the built app calls it. A page or a template never decides.
* Conformance proves it: the oracle states which references are accepted, and the app must agree, case by case.
* One step at a time. Records of several classes, each with their own workflow, are #65 and stay out of scope.

## Considered options

* A built to-one association from the record class becomes a reference field that holds the id of a stored object of the other class (chosen).
* Build every association, including to-many ones and associations between two other classes. That needs collections in a record and objects that link to each other. Revisit with #65.
* Infer references from attribute names such as `memberCard`. That is a guess. ADR-0205 already flags these names as stand-ins instead.

## Decision outcome

**The data model.** An association may set `built: true`. When it is false the field is left out of every dump, so the digest does not change. A built association must:
* have the record class at one end and another class at the other;
* link one record to at most one object (`1` or `0..1` at the other end);
* have a role name that is a free attribute name of the record class.

`DataModel` refuses anything else, and it refuses a record class whose attributes and reference fields together exceed 40, which is what one screen shows.

**What a record holds.** `references(data)` lists the reference fields, named by the role. Such a field is required when the multiplicity is `1`. `record_fields(data)` lists the record's attributes followed by each reference field, typed as text of at most 32 characters. Screens, the API contract, the Studio's presentation and the generated form all read `record_fields`, so a reference appears wherever an attribute does.

**The check.** `check_record(data, values, exists)` runs `check_values` on the attributes. It then checks each reference field:
* it refuses a missing required reference with `FIELD_REQUIRED`;
* it refuses a value that is not an id with `FIELD_TYPE`;
* it refuses an id that names no stored object of the class with `REFERENCE_UNKNOWN`.

**The built app.** The app stores objects of each referenced class in an `objects` table. `POST /api/objects/<Class>` checks the object's values against that class's attributes and returns a new id, and `GET /api/objects/<Class>` lists the stored objects. A class the app does not store answers `NOT_FOUND`. Record creation calls `check_record` with a lookup in the `objects` table. `REFERENCE_UNKNOWN` is a 400. The OpenAPI contract documents the objects route.

**Conformance.** When a reference exists, the oracle gains `objects`: one sample object of each referenced class, which the conformance template stores before it creates records. The data cases add, for each reference, a missing value, a value that is not an id and an id that names nothing. An oracle without references is unchanged.

**UML interchange.** PlantUML, Mermaid, XMI and draw.io have no way to say an association is built. An export lists the built associations under `not_carried`. On import, an association that the current model builds stays built if the file draws it with the same ends, multiplicities and role, and the report lists it as defaulted.

**The class diagram report** (`class_build`) lists the stored classes as built and marks each built association. For a built association it says the app refuses an id that names nothing, instead of "drawn, not built".

### Consequences

* Good: "a loan's borrower is a member who exists" is checked by the app and proven by conformance.
* Good: nothing changes for a data model that builds nothing.
* Bad: only to-one references from the record. Collections, links between two other classes and multiplicity checks on the record's side remain drawn only.
* Bad: stored objects have no workflow, no edit and no delete, so a reference can never dangle because nothing removes an object.
* Revisit when: objects need their own workflow or deletion, which is #65, or a pack needs a to-many association built.
