# ADR-0249: Fixes from the inspection of the app generator

* Status: accepted
* Date: 2026-11-13
* Lane: app generator (ADR-0150), issue #249

## Context and problem statement

The 13 November 2026 inspection ([record](../quality/inspection-2026-11-13-app-generator.md)) found ten defects in the generated app and its conformance suite. The largest: a record that refers to another object could not be created from the page, and five seeded faults (objects, clocks, signals over HTTP) passed the generated suite.

## Decision drivers

* The generated suite must fail when the app stops matching its model (ADR-0243).
* The page must let a person do what the model allows, and not offer what the kernel will refuse.
* A local app must not answer a page from another origin (issue #249).

## Considered options

* Fix each defect in the templates and the oracle, and add a generated test for each gap.
* Leave the page as it is and document the reference field as an API-only feature.

## Decision outcome

Chosen option: fix each defect. The generated suite gains three tests (20 in all, `GENERATED_TESTS`): objects created through the app, a step restarting the record's clock, and the `Host` check. The oracle gains `object_cases` (only when an association is built, so other oracles keep their bytes) and, for signal cases, the stored values and the answer to the same signal under a new operation id. The page chooses a referenced object from the stored ones and can add one in place. Reads share the write lock. A stale record's options carry the code `act` will give.

### Consequences

* Good: the seven faults in the record's table are CAUGHT; ai-ops records can be made from the page.
* Bad: every generated app's files and build subject change, so earlier approved app builds are STALE and need a rebuild.
* Revisit when: an app needs concurrent readers at a scale where one lock matters.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Mantine `NativeSelect` (already a dependency) | Used as is for the object chooser | none |
