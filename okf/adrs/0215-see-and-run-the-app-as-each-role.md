---
type: Architecture Decision Record
title: 'ADR-0215: See and run the app as each role'
description: 'PlayIDE already models the human side of a system: roles and fixture actors in the pack, a use case diagram (ADR-0154), one screen per use case, and a Permissions matrix the kernel fills (ADR-0171).'
resource: repo://docs/adr/0215-see-and-run-the-app-as-each-role.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0215-see-and-run-the-app-as-each-role.md
  title: 0215-see-and-run-the-app-as-each-role.md
  hash_method: lf-sha256-v1
  sha256: f49777d6aeece1e24cdf029b242b69b46354c8959e6973e97011f26401b85e00
notes_baseline: 4e7146c3dba11859fbaea2c20c55bedcdf05bd4a3523cb4d56cc4f7a92a8210c
---

# ADR-0215: See and run the app as each role

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE (owner direction, 9 October 2026: refine how humans and software are designed; thread "Humans, roles and screens") |
| Source | `repo://docs/adr/0215-see-and-run-the-app-as-each-role.md` |

## Decision outcome (verbatim)

> Chosen option: `resources/web/play-roles.js` and `play-roles.css`.
>
> * **An actor is selectable.** Choosing an actor on the use case diagram, a role in the outline, or a role's column heading on the Permissions tab selects `role:<id>`. The inspector shows the role's description (`pack_summary` now carries `role_notes`), the use cases the kernel lets its fixture actors take (from which states, and *assigned only* where a guard narrows it), the fixture actors who play it, and buttons to see their screens, to see who can do what, and to run the app as each actor. The run bar's breakpoint tool no longer appears for an actor.
> * **See the app as.** The Screens tab has a role bar above the designer. Choosing a role strikes through the screens it never sees, notes on the open screen whether the role sees it (and if not, which role does), and lists the role's screens in order, the ones it never sees, and **Run as** buttons. Starting a record counts for every role, because the kernel lets any active actor start one.
> * **Run as.** `PlayIDE.runAs(actor)` reuses the last build when it is of the model and screens on show and passed conformance, and builds otherwise. The running app opens at `#actor=<id>`.
> * **The built app puts the acting role first.** The generated page honours `#actor=<id>` (and later changes to it), shows the acting role beside the picker and flags an inactive actor, lists the acting role's actions first with the kernel's refusal where a guard applies, folds the other roles' actions under *For other roles*, and highlights the role's rows in the rules table. The screen's dismiss button says Close. The server still decides every option and every action.
>
> * **Actors that are not people** (amended 2026-10-09, after [ADR-0210](repo://docs/adr/0210-actors-that-are-not-people.md)). An AI agent, a timer or an external system has no screens. Choosing one in **See the app as** says so, strikes through every screen and lists the calls it makes as the built app's own endpoints (`POST /api/records/{id}/act` with its action and actor, and `POST /api/records` to start a record). The open screen says that the role takes that use case by an API call, and that the screen is what a person standing in for it sees. The inspector shows the kind («agent», «timer», «system») and the same calls. Its buttons say **Stand in for**, and the built app names the kind beside the picker (`describe()` now serves `kinds`).
> * **Run as after Stop.** Run as reuses the last build only while its app still runs in the frame. The run bar's Stop ends the process and blanks the frame, so the next Run as builds again rather than opening a dead address.
>
> * **Screen flow** (amended 2026-10-09). **Screen flow** on the Screens tab draws every screen as a wireframe and lays them out left to right in the order a record meets them. An arrow goes from a screen to each screen the record can reach next, labelled with the state it is then in, and an end state is an end node. The wireframe is drawn from the screen and the record class: the create screen shows an input per field, shaped by the attribute's type (a choice shows its first literal and ▾, a date shows dd/mm/yyyy) with * for required. Its tooltip gives the rule the server checks ("text, up to 120, required"). An action screen shows the values it displays. Nothing in it is drawn by hand: a transition added on the state machine adds an arrow, and an edit in the designer redraws the card. Under **See the app as**, the other roles' screens fade, so the hand-offs between roles show. Choosing a card opens that screen in the designer. The layout uses the vendored dagre, as the state machine does, and each card is measured before layout so a wrapped title keeps its room.

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

* [ADR-0154: Use case diagrams, and screens designed against the model](/adrs/0154-use-cases-and-screens-designed-against-the-model.md) - PlayIDE shows the workflow as a state machine (ADR-0151) and the data as a class diagram (ADR-0153).
* [ADR-0171: Who can do what, as a matrix the kernel checks, and reachability questions with a proof or a path](/adrs/0171-permissions-matrix-and-reachability-questions.md) - Access rules are what AI-written apps most often get wrong, and they are what reviewers and auditors ask about first: who can do what, from which state, and ca…
* [ADR-0210: Actors that are not people: AI agents, timers and external systems in the model](/adrs/0210-actors-that-are-not-people.md) - Systems people design now have AI agents in them: a support bot that triages tickets and proposes refunds, a scheduled job that escalates what nobody handled,…

## Referenced by

* [ADR-0218: An accessibility check on the generated screens](/adrs/0218-accessibility-check-on-the-generated-screens.md) - PlayIDE designs the screens of the app it builds (ADR-0154) and the role lens shows them as each role (ADR-0215).
<!-- okf:generated:end links -->
