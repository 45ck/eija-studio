---
type: Architecture Decision Record
title: 'ADR-0202: Grow the class diagram in chat'
description: ADR-0201 let a system started from a sketch grow its state machine round after round in chat.
resource: repo://docs/adr/0202-grow-the-class-diagram-in-chat.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0202-grow-the-class-diagram-in-chat.md
  title: 0202-grow-the-class-diagram-in-chat.md
  hash_method: lf-sha256-v1
  sha256: b6d19226aac0e6904c53d9f5c957e942b8ec6dee0ef501708462f71531708a59
notes_baseline: 5db9a0647365d0a27981b775fdb4c0c8032b56f558ffccbeb8a05a56708537fb
---

# ADR-0202: Grow the class diagram in chat

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for systems started in PlayIDE |
| Date | 2026-10-09 |
| Lane | PlayIDE (follows ADR-0201; the owner's standing ask, 9 October 2026, to get the greenfield loop done) |
| Source | `repo://docs/adr/0202-grow-the-class-diagram-in-chat.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * **Three steps.** `add_attribute` (class, attribute as `domain.data.Attribute`), `remove_attribute` and `set_required` live in `application/data_steps.py`. `parse_step` reads a plan step as one of these, or else as a kernel transaction. They sit in the same plan list as the state-machine steps, so ticking, rounds, undo, Save and reopen all work across both.
> * **A draft holds its data model.** `domain.pack.hold(pack, "data.json", data)` returns a copy of the pack that holds the draft data model in memory. The pack document and digest are the same, and `domain.data.data_for` returns the held model. `derive` keeps what a draft holds. `application.data_steps.draft_pack` makes a plan's draft: ADR-0201's declared vocabulary plus the applied data steps. Every PlayIDE route that runs a plan uses it.
> * **Checked by the data model's contract.** Each step applies after the accepted data steps before it. A missing class or attribute, or a duplicate attribute, is `EDIT_INVALID`. The result is re-checked by `parse_data`. The state-machine steps still go through the policy as one change.
> * **Only on your own system.** On a shipped pack, a data step is `PLAN_DATA_FIXED`: the preview marks it as not applying, and every other route refuses it.
> * **The offline proposer can say it.** It understands three phrases: `add field size as choice Small, Medium, Large required`, `remove field notes` and `make notes required`. The type is text unless one is named.
> * **What you see.** A step reads `Add attribute size: one of Small, Medium, Large to Order, required`. The verdict and the preview banner add `Order gains size`. While a plan is previewed, the class diagram marks added rows with +, changed rows with ~, and removed rows as struck-through ghosts. "Show me" opens the class it changes. The ripple's class items list the attribute changes, per round with `since` as well.

## Sections

* Context and problem statement
* Decision drivers
* What existing tools do
* Considered options
* Decision outcome
* Verification
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://demos/scenarios/playide_greenfield.py`
* `repo://tests/test_play_data_steps.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0153: Data models as UML class diagrams, checked in the built app](/adrs/0153-data-models-as-uml-class-diagrams.md) - Until now, records in a built app (ADR-0150) carried only a title, because the model had no data.
* [ADR-0185: Start, open and save your own system in PlayIDE](/adrs/0185-start-open-and-save-your-own-system.md) - PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA.
* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).

## Referenced by

* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).
* [ADR-0203: A system landscape of the workflows that share classes](/adrs/0203-system-landscape-of-workflows-that-share-classes.md) - PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws.
<!-- okf:generated:end links -->
