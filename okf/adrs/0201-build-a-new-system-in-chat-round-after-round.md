---
type: Architecture Decision Record
title: 'ADR-0201: Build a new system in chat, round after round'
description: The showcase changes a pack that already exists (Library loan).
resource: repo://docs/adr/0201-build-a-new-system-in-chat-round-after-round.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0201-build-a-new-system-in-chat-round-after-round.md
  title: 0201-build-a-new-system-in-chat-round-after-round.md
  hash_method: lf-sha256-v1
  sha256: c4c392d87b5fc66fca662b9652abd50b5c77aa0df6c58da97ed92852f38f172a
notes_baseline: 45d58ca6acc8c9b22c6a68052efa57357e722c08e08f182be4e4cfb899ccb8e3
---

# ADR-0201: Build a new system in chat, round after round

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for state-machine systems |
| Date | 2026-10-09 |
| Lane | PlayIDE (owner question, 9 October 2026: "what about a greenfield app that's being vibe coded and iterated on") |
| Source | `repo://docs/adr/0201-build-a-new-system-in-chat-round-after-round.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * **Rounds stack.** `POST /api/play/plan` takes the accepted steps so far (`plan`). On a system you started, the proposer plans on top of them and the answer says `on_top`. The page adds the new steps to the same plan as round N, moves the plan card under the latest ask, and heads each round with what was asked. Ticking, undo and redo, Save and reopen work across rounds; a saved step keeps its round and ask (`DraftStep.round`, `.request`). On a shipped pack a new plan still replaces the last, as before.
> * **The work in progress can be larger.** One proposal still has at most 12 steps (`MAX_STEPS`); the work in progress, every round together, has at most 64 (`MAX_DRAFT_STEPS`), the kernel's transition limit.
> * **The vocabulary grows on your own system.** `application/new_system.declare(pack, transactions)` returns the pack with every action and role the steps name but it does not declare, declared exactly as a sketch declares them: an action gets the base guards and one `Audit:<action>` entry, a role one active, assigned fixture user. The result is checked by `parse_pack` and held in memory; `domain/pack.derive` lets it read `data.json`, `screens.json` and `scenarios.json` from the system's folder, and `find_pack` cannot resolve it, so no change case or receipt can name it. Every PlayIDE route that runs a plan (preview, ripple, build, simulate, run, laws, tests, sequences, permissions, reach, review, export) runs it on that pack. "Your own system" is one in the systems home (`SystemLibrary.contains`). A new name must be one the built app can use (`[A-Za-z][A-Za-z0-9_]{0,39}`), and names that differ only in case are refused, as in a sketch.
> * **The offline proposer can say it.** On your own system, `add <action> from <A> to <B> for <role>` adds a state it names that does not exist yet as a step of its own before the transition, and names a new action or role as written. `remove state <S>` removes the transitions that still use it first, one step each. The step text says `(new action Cancel)` or `(new role Manager)`, and the verdict lists what the accepted steps declare.
> * **No follow-on is proposed that cannot apply.** A follow-on that adds a transition now uses only a declared action no transition uses yet; with none, there is no follow-on, rather than one the policy always refuses.
> * **Each round can be read on its own.** With more than one round, the Changes view has **Round N** and **All N rounds**. Round N sends `since`, the accepted steps of the earlier rounds, to `/api/play/diff` and `/api/play/ripple`, so the diagram, the change list and To consider read the last round against the system after the round before. The laws are proved on the whole plan either way, and the follow-ons are for the whole plan.

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

* `repo://tests/test_play_greenfield.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0176: How a UML change looks: one stable layout, removed parts kept as ghosts, and lenses](/adrs/0176-how-a-uml-change-looks.md) - The owner asked how a change can be reviewed as a UML change instead of a pull request, and "how you even view a UML change (ghost UI/UX?)".
* [ADR-0185: Start, open and save your own system in PlayIDE](/adrs/0185-start-open-and-save-your-own-system.md) - PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA.
* [ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel](/adrs/0190-uml-import-and-export-through-the-kernel.md) - PlayIDE's users already know UML and already keep UML somewhere else: XMI in Enterprise Architect, Cameo, Papyrus or Visual Paradigm; PlantUML beside the code;…
* [ADR-0198: Undo, redo and autosave of the edited document in PlayIDE](/adrs/0198-undo-redo-and-autosave-of-the-edited-document.md) - PlayIDE is meant to be more robust than the UML tools engineers already use, and every one of those has undo.
<!-- okf:generated:end links -->
