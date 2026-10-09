# ADR-0201: Build a new system in chat, round after round

* Status: accepted for state-machine systems
* Date: 2026-10-09
* Lane: PlayIDE (owner question, 9 October 2026: "what about a greenfield app that's being vibe coded and iterated on")

## Context and problem statement

The showcase changes a pack that already exists (Library loan). Building a new system the way people build apps with an AI, many small asks in a row, failed at the first ask. A session on a system started from a three-line sketch (Coffee orders: `Placed -> Brewing : Start [Barista]` and two more lines) found:

| Round | Ask | What happened |
|---|---|---|
| 1 | `add Cancel from Placed to Cancelled for Customer` | Refused: `PLAN_UNKNOWN_NAME: The pack declares no action Cancel`. The vocabulary is fixed when a system is created (ADR-0185), and the state had to be asked for separately. |
| 2 | `rename state Ready to AwaitingPickup` | Planned, but against the sketch, not round 1. |
| 3 | `add state Paid after Placed` | Planned, and round 2 was gone: every new plan replaced the last ("Replaced by the newer plan below"). Its follow-on, `Add Start: Placed → Paid`, was always refused, because every declared action was in use and each action labels one transition. |

So in chat, a person could make one change to a new system and then start again. The Changes view also always read a change against the model in force, which for a new system is the sketch: after five rounds everything is green and no single round can be read on its own.

## Decision drivers

* The kernel decides. A plan is untrusted; every step is still re-checked, and the accepted steps are still applied through the policy as one change.
* Saving is not applying (ADR-0185). A draft never writes `pack.json`, so it never changes the model in force or loosens a law.
* A greenfield system's vocabulary should grow the way it was first written: a sketch line declares its action and role, so a plan step may too, with the same rules.
* A shipped pack's vocabulary was written by its owner and stays fixed.
* Each round should be readable on its own, and the whole plan as well.

## What existing tools do

| Tool | How iteration works | What PlayIDE takes from it |
|---|---|---|
| Lovable, v0, bolt.new (proprietary) | Each chat message is applied on top of the last version; a version list lets you go back. | Asks stack on top of each other, and each round is listed with what was asked. |
| Cursor Composer / Claude Code checkpoints | Every turn is a checkpoint you can restore; the diff is shown per turn. | Undo and redo already restore any edit (ADR-0198); the Changes view gains a per-round diff. |
| [Stately](https://stately.ai) (statecharts, proprietary editor; XState is MIT) | AI suggestions are added to the current machine, and new events and states are created by naming them. | Naming a missing state or action in a step adds it, as a separate step the person can reject. |
| Git (GPL-2.0, reference only) | A series of commits, each diffable against its parent or against the start. | "Round N" against the rounds before it, or "All rounds" against the model in force. |

None of these is a library PlayIDE could adopt for this; the change is to how PlayIDE's own plan grows, so no dependency is added.

## Considered options

* **Each round's steps join the one plan, planned on top of the accepted steps; on your own system a step may name new states, actions and roles, declared as a sketch declares them, in the draft only** (chosen).
* **Write each round into `pack.json` ("keep").** The fastest loop, but it would change the model in force without review and break the workspace's binding to its pack digest. That is issue #89's decision (how a chat plan becomes a change case), still with the owner.
* **A "declare action" button that rewrites the system's vocabulary on disk.** Explicit, but it changes the pack digest, so the workspace no longer opens (`PACK_MISMATCH`), and it needs a migration path.
* **Let any pack's plan declare new actions.** Simpler, but it would let a chat plan widen a vocabulary its owner wrote.

## Decision outcome

Chosen option.

* **Rounds stack.** `POST /api/play/plan` takes the accepted steps so far (`plan`). On a system you started, the proposer plans on top of them and the answer says `on_top`. The page adds the new steps to the same plan as round N, moves the plan card under the latest ask, and heads each round with what was asked. Ticking, undo and redo, Save and reopen work across rounds; a saved step keeps its round and ask (`DraftStep.round`, `.request`). On a shipped pack a new plan still replaces the last, as before.
* **The work in progress can be larger.** One proposal still has at most 12 steps (`MAX_STEPS`); the work in progress, every round together, has at most 64 (`MAX_DRAFT_STEPS`), the kernel's transition limit.
* **The vocabulary grows on your own system.** `application/new_system.declare(pack, transactions)` returns the pack with every action and role the steps name but it does not declare, declared exactly as a sketch declares them: an action gets the base guards and one `Audit:<action>` entry, a role one active, assigned fixture user. The result is checked by `parse_pack` and held in memory; `domain/pack.derive` lets it read `data.json`, `screens.json` and `scenarios.json` from the system's folder, and `find_pack` cannot resolve it, so no change case or receipt can name it. Every PlayIDE route that runs a plan (preview, ripple, build, simulate, run, laws, tests, sequences, permissions, reach, review, export) runs it on that pack. "Your own system" is one in the systems home (`SystemLibrary.contains`). A new name must be one the built app can use (`[A-Za-z][A-Za-z0-9_]{0,39}`), and names that differ only in case are refused, as in a sketch.
* **The offline proposer can say it.** On your own system, `add <action> from <A> to <B> for <role>` adds a state it names that does not exist yet as a step of its own before the transition, and names a new action or role as written. `remove state <S>` removes the transitions that still use it first, one step each. The step text says `(new action Cancel)` or `(new role Manager)`, and the verdict lists what the accepted steps declare.
* **No follow-on is proposed that cannot apply.** A follow-on that adds a transition now uses only a declared action no transition uses yet; with none, there is no follow-on, rather than one the policy always refuses.
* **Each round can be read on its own.** With more than one round, the Changes view has **Round N** and **All N rounds**. Round N sends `since`, the accepted steps of the earlier rounds, to `/api/play/diff` and `/api/play/ripple`, so the diagram, the change list and To consider read the last round against the system after the round before. The laws are proved on the whole plan either way, and the follow-ons are for the whole plan.

### Consequences

* Good: a system can be built from a sketch in many small asks, and every ask is checked by the kernel, previewed, built and simulated with the earlier ones. The generated app passes conformance after each round (`tests/test_play_greenfield.py`).
* Good: nothing new is trusted. A grown action has exactly the guards and effects a sketch would give it, and the laws and tests are the pack's own.
* Bad: the draft is still not the model in force. A grown vocabulary lives only in the draft, so it cannot become a change case until #89 decides how a chat plan becomes one, and verify, approve and apply wait on #80.
* Bad: the data model is still the sketch's: the record has one attribute, `title`, and chat cannot add attributes. Drawing a transition on the canvas still offers only declared actions (the canvas belongs to the UX thread).
* Neutral: on a shipped pack nothing changes.
* Revisit when: #89 is decided (a round could become a change case), or chat can edit the data model.

## Verification

* `tests/test_play_greenfield.py`: three rounds on a sketched system (a new action with its state, a new role on what round one added, a state removed with its transitions), the preview of every round together, Build & run passing conformance and Simulate on the grown system, a saved draft keeping each round's ask, a shipped pack still refusing a new action, a bad or case-clashing new name refused, a grown pack that `find_pack` cannot resolve, and no follow-on when every action is in use.
* Manual run in Chromium against `eija serve --systems <tmp>`: five rounds on Coffee orders, the round headings in the plan card, and the Changes view's Round 3 and All 3 rounds.

## OSS check (required for any custom module)

No new module. `declare` reuses the sketch's own rules in `application/new_system.py`.

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| XState / Stately (MIT library) | A statechart runtime; PlayIDE's kernel is the interpreter, and a second one is ruled out | Export to XState stays possible through the UML export (ADR-0190) |
| jsondiffpatch (MIT) | A per-round diff is the existing ghost diff (ADR-0176) with another "before" model; a JSON diff would not draw UML | Use it if a round's diff ever has to cover non-UML documents |
