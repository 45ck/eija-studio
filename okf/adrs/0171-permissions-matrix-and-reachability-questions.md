---
type: Architecture Decision Record
title: 'ADR-0171: Who can do what, as a matrix the kernel checks, and reachability questions with a proof or a path'
description: 'Access rules are what AI-written apps most often get wrong, and they are what reviewers and auditors ask about first: who can do what, from which state, and can anything happen without the right person.'
resource: repo://docs/adr/0171-permissions-matrix-and-reachability-questions.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0171-permissions-matrix-and-reachability-questions.md
  title: 0171-permissions-matrix-and-reachability-questions.md
  hash_method: lf-sha256-v1
  sha256: 690782fde0c55fe3f6ed3a98971f73d74e7ebfb6d3a534e05792f61ead1a5352
notes_baseline: 075a6ea32c2b34c1f55ade834285070e1e0abfa8ed012eb32f20908e0d7aba79
---

# ADR-0171: Who can do what, as a matrix the kernel checks, and reachability questions with a proof or a path

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026: "UI, HCI, AHCI"; input from the "Who PlayIDE is for" research) |
| Source | `repo://docs/adr/0171-permissions-matrix-and-reachability-questions.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * `application/access.py`:
>   * `matrix(pack, model)` lists, for every state and every role in the pack, the actions that role may take from that state. It tries each one in the kernel with every fixture actor in that role, on a fresh record in that state, and records who was let through and the refusal code for the rest (`ASSIGNMENT_DENIED`, `ACTOR_REVOKED`, …).
>   * `access(pack, model, base)` adds the permissions a model adds and removes compared with `base`.
>   * `reach(pack, model, target, without)` asks whether a record can reach `target` with no step taken by role `without` (or at all). It answers with one of three outcomes:
>     * **UNREACHABLE.** No sequence of the model's transitions avoiding the role gets there. Guards can only refuse more, so this holds for every actor.
>     * **REACHABLE.** It searches the transitions some fixture actor can take in the kernel, then replays the shortest path on one record, step by step. The answer carries that path and the actors.
>     * **NOT_SHOWN.** The model has a path, but the fixture actors could not take it in the kernel. Other actors might.
> * `POST /api/play/access` and `POST /api/play/reach` take the same request as Build & run and Simulate. With accepted plan steps, they answer for the previewed candidate, recomputed on the server. `access` then flags the changes against the base model.
> * The **Permissions** tab (`play-access.js`, `play-access.css`) shows the question as a sentence ("Can a record reach [Overdue] without [a Clerk]? Ask the kernel"), the answer with its path (each step selects its transition on the state machine), the plan's permission changes, and the matrix. Added permissions are marked new; removed ones are struck through. A question once asked is asked again whenever a plan is previewed or left. The command palette (ADR-0170) has "Show who can do what".

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

* [ADR-0170: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review](/adrs/0170-playide-assist-ask-complete-palette-review.md) - PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157).

## Referenced by

* [ADR-0172: A read-only review view of PlayIDE for people who review the model](/adrs/0172-review-view-for-reading-the-model.md) - The owner set the audience as people who know UML, and noted that UML "is meant for non technical people to review it sometimes".
<!-- okf:generated:end links -->
