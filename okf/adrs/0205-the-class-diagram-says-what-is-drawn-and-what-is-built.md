---
type: Architecture Decision Record
title: 'ADR-0205: The class diagram says what is drawn and what is built'
description: The built app stores records of the record class only (ADR-0150, ADR-0153).
resource: repo://docs/adr/0205-the-class-diagram-says-what-is-drawn-and-what-is-built.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0205-the-class-diagram-says-what-is-drawn-and-what-is-built.md
  title: 0205-the-class-diagram-says-what-is-drawn-and-what-is-built.md
  hash_method: lf-sha256-v1
  sha256: bb958a8c817a01b1bb12665995d0e9b34b3a88cb6209070997484f62adf92c31
notes_baseline: 80800ffe96258616ae616e5083e29f63e8aae28f2c1b7421562885bdf8074d8b
---

# ADR-0205: The class diagram says what is drawn and what is built

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE software architecture views (issue #145; follows ADR-0153 and ADR-0202) |
| Source | `repo://docs/adr/0205-the-class-diagram-says-what-is-drawn-and-what-is-built.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * `class_build` is pure and reads the data model only. A record attribute whose leading camelCase word names a class or role the record is associated with (`memberCard` beside `borrower: Member`) is `ATTRIBUTE_STANDS_IN_FOR_ASSOCIATION`, severity *consider*. The app checks the text, not that such a member exists.
> * `GET /api/play/data` returns the report as `build`. A previewed plan with data-model steps carries its own report as `class_build`.
> * On the class diagram, a class that is drawn only is grey, and an attribute that stands in for an association is amber. The hint under the diagram says that only the «record» class is built. The inspector says why and names the limit (#65).
> * The ripple (ADR-0158) lists a stand-in attribute that a change introduces under *Class diagram*, as a "To consider".

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
* [ADR-0153: Data models as UML class diagrams, checked in the built app](/adrs/0153-data-models-as-uml-class-diagrams.md) - Until now, records in a built app (ADR-0150) carried only a title, because the model had no data.
* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0202: Grow the class diagram in chat](/adrs/0202-grow-the-class-diagram-in-chat.md) - ADR-0201 let a system started from a sketch grow its state machine round after round in chat.
<!-- okf:generated:end links -->
