# ADR-0153: Data models as UML class diagrams, checked in the built app

* Status: accepted for record attributes; other classes are diagram-only
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

Until now, records in a built app ([ADR-0150](0150-build-apps-from-the-model-with-a-kernel-oracle.md)) carried only a title, because the model had no data. The owner's audience is engineers who know UML. They expect class diagrams for data, and expect the app built from the model to hold real data.

## Decision drivers

* One source per fact. The data model is its own document, read by the diagram, the built app and its oracle alike.
* Pack digests, and every receipt and fixture over them, must not change for packs that gain no data model.
* Record values are checked in exactly one place, which the built app calls. There is no second reading of the rules.
* Proper UML class notation.

## Considered options

* An optional `data.json` beside `pack.json`, validated by a Pydantic contract `DataModel` with its own digest (chosen).
* A new `data` section inside the pack. Rejected: any new field changes every pack's digest, including the owner-stamped fixture's.
* JSON Schema as the data model, validated with `jsonschema`. It covers values well but has no notion of classes, associations or multiplicities to draw. It is also only a test and graph dependency today.
* LinkML (CC0 metamodel, Apache-2.0 tools). It fits the problem but brings a large toolchain and its own YAML metamodel next to the existing contracts.

## Decision outcome

Chosen option: an optional `data.json` per pack, `domain/data.py`.

* `DataModel` (`eija.data.v1`) has entities (UpperCamelCase names, at most 40), typed attributes, associations and a `record` entity. Attribute types are text (with `max_length`), number, date, boolean, and choice (with literals). Associations are association, aggregation or composition, each with a role and two multiplicities from `0..1`, `1`, `0..*`, `1..*`. The validator refuses duplicates, an undeclared record entity and associations to undeclared entities. `parse_data` also refuses a data model that names a different pack (`DATA_PACK_MISMATCH`).
* `check_values(entity, values)` is the only check of record values. It returns the clean values or refuses with `FIELD_REQUIRED`, `FIELD_TYPE`, `FIELD_TOO_LONG`, `FIELD_CHOICE` or `UNKNOWN_FIELD`.
* `data_for(pack)` reads `data.json` from the directory the pack snapshot was loaded from (`pack.pack_directory`). The digests of packs and models are unchanged.
* `eija build` writes `app/data.json` when the pack has one. The generated service calls `check_values` on create and stores the values in a `fields` column (added in place to an older build's database). The page renders a form from the record class. The oracle gains `data_cases`, each answered by `check_values`: a valid record, each required value missing, each wrong type, each text too long, an undeclared choice and an unknown field. The conformance suite runs every case through the app's own create. Two new negative controls must fail conformance: values stored unchecked, and a required attribute made optional in `app/data.json`.
* PlayIDE gets a **Class diagram** tab and `GET /api/play/data`. Classes are maxGraph swimlanes with an attribute compartment written `name: Type [0..1]`, with choices as `{A, B}`. The record class is marked «record». Associations show role names and multiplicities at both ends, with hollow or filled diamonds for aggregation and composition. Selecting a class shows its attributes and associations in the inspector.

### Consequences

* Good: built apps hold real, typed data, and the check is exhaustive over the oracle's value cases.
* Good: packs without a data model are byte-for-byte unaffected.
* Bad: only the record class is stored. Other classes and associations are drawn but not stored or navigable in the app yet.
* Bad: the class diagram is view-only; editing it through typed transactions comes with the drag-and-drop palettes.
* Revisit when: associated classes need storage (the next data step), or when export to JSON Schema or LinkML is wanted for interchange.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| JSON Schema (`jsonschema`) | Values only, no classes, associations or multiplicities to draw; a runtime dependency for five checks | Export `DataModel` to JSON Schema for interchange |
| LinkML | Right shape, but a large toolchain and a second metamodel beside the Pydantic contracts | Adopt if data models need to interoperate with other tools |
| Pydantic `create_model` per entity | Error messages and codes are Pydantic's, not stable refusal codes the oracle can compare | — |
| maxGraph swimlane | Adopted for the class shape | — |
