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
  sha256: de45d93747d978e4c8ff312c2575a4e090d2699b9f108d629580c89a8b1d1dbf
notes_baseline: 3f88851b7d29aa2836f96b48460282e6fa4805bcc9243c28b81523dfa2c54cd2
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
<!-- okf:generated:end links -->
