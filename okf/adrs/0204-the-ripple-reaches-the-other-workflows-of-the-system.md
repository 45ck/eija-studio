---
type: Architecture Decision Record
title: 'ADR-0204: The ripple reaches the other workflows of the system'
description: The ripple (ADR-0158) shows what a change does to every diagram of one workflow.
resource: repo://docs/adr/0204-the-ripple-reaches-the-other-workflows-of-the-system.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0204-the-ripple-reaches-the-other-workflows-of-the-system.md
  title: 0204-the-ripple-reaches-the-other-workflows-of-the-system.md
  hash_method: lf-sha256-v1
  sha256: fba35f13d932547614f1b6447c3efa334545b5f2e321dfcc2408795f876ddc0f
notes_baseline: efd91e70c2daa867369577c1cf856b05e7f229faa5c5e709b6daad003c16bde2
---

# ADR-0204: The ripple reaches the other workflows of the system

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE software architecture views (issue #146; follows ADR-0158 and ADR-0203) |
| Source | `repo://docs/adr/0204-the-ripple-reaches-the-other-workflows-of-the-system.md` |

## Decision outcome (verbatim)

> Chosen option. The ripple gains `diagrams.system`, computed by `ripple._system_items` from two landscapes. The route passes the landscapes only when the open workflow has sibling packs.
>
> * A disagreement with another workflow that the change introduces (`CLASS_COPIES_DIFFER`, `ATTRIBUTE_NOT_ON_OWNER`, `RECORD_MOVED_TWICE`) is a **warning**. It is listed in the ripple's problems and counted on the checks ring, as other warnings are. The warning does not make the diagrams disagree, because each app still builds.
> * A «use» link from another workflow that the change breaks is a warning (`SYSTEM_LINK_BROKEN`).
> * A finding the change resolves, and a "to consider" it raises, are changes.
> * The plan's ripple list names them "System". The Components tab's badge counts them. Choosing one opens the Components tab on the System lens with the shape selected; an owned class is shown as its workflow. Checking it earns the checks-ring point that other ripple items earn. The Changes view's "Also changes" line links to it.

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

* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0202: Grow the class diagram in chat](/adrs/0202-grow-the-class-diagram-in-chat.md) - ADR-0201 let a system started from a sketch grow its state machine round after round in chat.
* [ADR-0203: A system landscape of the workflows that share classes](/adrs/0203-system-landscape-of-workflows-that-share-classes.md) - PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws.
<!-- okf:generated:end links -->
