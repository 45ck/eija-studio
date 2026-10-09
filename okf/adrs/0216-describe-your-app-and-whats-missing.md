---
type: Architecture Decision Record
title: 'ADR-0216: Describe your app, and what''s missing'
description: Until now a new system started from three sketch lines, a template or a UML file (ADR-0185, ADR-0190), and then grew in chat (ADR-0201, ADR-0202).
resource: repo://docs/adr/0216-describe-your-app-and-whats-missing.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0216-describe-your-app-and-whats-missing.md
  title: 0216-describe-your-app-and-whats-missing.md
  hash_method: lf-sha256-v1
  sha256: 9f89113cba342643147fc489edd49586e0cd904c25a74dc6ad25e645d05f0db1
notes_baseline: b03ca14c75199680c7e03cc7cc4c0c9ea693775982d04d4dbffcbe5ccc929aa0
---

# ADR-0216: Describe your app, and what's missing

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE. Owner, 9 October 2026: "it should start off like lovable or replit a box to type in than it makes all uml and u edit it etc or descirbe what needs to be changed or drag it like drawio and edit it etc. usually its a mix of both. and you work across all models and views to get it all ready, if something is missing it lets you know etc". |
| Source | `repo://docs/adr/0216-describe-your-app-and-whats-missing.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * **Describe it.** The New system dialog opens on "Describe your app" (also the "＋ New" button, and `/play?new=describe`).
>   * The description goes to a `SystemDescriber` (`application/ports.py`). The offline adapter, `adapters/system_describer.py`, picks the app shape whose keywords the description uses most. The shapes are data in `describe-shapes.json`, beside the shipped packs: orders, tickets, bookings, approvals, loans, hiring, deliveries, publishing and bugs, or a plain one.
>   * Role nouns from the description rename the shape's roles. "With …" and "has …" lists become fields: a name with "(a, b, c)" is a choice, price-like words are numbers, date-like words are dates, and anything else is text.
>   * The adapter says what it read and assumed, and that it is a fixed shape, not a live model.
> * **Every model and view.** `application/describe_system.describe_documents` builds the documents:
>   * `pack.json` and `data.json` exactly as a sketch's (`sketch_documents`), with the fields added to the record class;
>   * `scenarios.json`, with one test per end state (the shortest way there) and one refusal (the first step taken by a role that may not take it), each step written as what the kernel did (`record_steps`).
>
>   Every document passes the same checks as any new system (`checked_documents`). Use cases, screens, sequences, components and permissions are derived from these documents, as for any system. Before anything is created, the form says what each view will have. Nothing is written until Create and open.
> * **Kinds of actor (#156, ADR-0210).**
>   * The describer reads "an AI agent", "a timer", "a payment provider" and similar phrases from the data file. The verb after the phrase picks the transition that role takes.
>   * A sketch line `agents:`, `timers:`, `systems:` or `people:` gives a role its kind.
>   * In chat, `make <role> an AI agent|a timer|an external system|a person` reads as the same role-kind plan step the inspector's **Held by** makes (`data_steps.SetRoleKind`, ADR-0210). The laws about kinds judge the plan again with the kinds it leaves.
> * **The kernel's answer stays in view (#138).** The dialog's check result and its Create button sit right under the option being filled in (the description, the sketch, the UML file or the chosen template), so a refusal is never below the fold.
> * **No laws are generated.** What's missing says there are none, gives an example from the model ("Collected is final") and says laws are the person's to set.
> * **What's missing.** `POST /api/play/ready` returns a row per view: state machine, class diagram, use cases and permissions, screens, tests and sequences, and laws. Each row is either ready or lists what is missing or wrong, with where to fix it. It reads the work in progress: the plan's accepted steps when the policy allows them, previewed or not. The checks behind the rows are:
>   * a state nothing reaches;
>   * a record with only a title;

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
* `repo://tests/test_play_describe.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0185: Start, open and save your own system in PlayIDE](/adrs/0185-start-open-and-save-your-own-system.md) - PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA.
* [ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel](/adrs/0190-uml-import-and-export-through-the-kernel.md) - PlayIDE's users already know UML and already keep UML somewhere else: XMI in Enterprise Architect, Cameo, Papyrus or Visual Paradigm; PlantUML beside the code;…
* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).
* [ADR-0202: Grow the class diagram in chat](/adrs/0202-grow-the-class-diagram-in-chat.md) - ADR-0201 let a system started from a sketch grow its state machine round after round in chat.
* [ADR-0210: Actors that are not people: AI agents, timers and external systems in the model](/adrs/0210-actors-that-are-not-people.md) - Systems people design now have AI agents in them: a support bot that triages tickets and proposes refunds, a scheduled job that escalates what nobody handled,…
<!-- okf:generated:end links -->
