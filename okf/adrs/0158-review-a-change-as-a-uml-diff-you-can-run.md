---
type: Architecture Decision Record
title: 'ADR-0158: Review a change as a UML diff you can run, not as a pull request'
description: The owner wants engineers to stop "reviewing changes in a GitHub PR when you can do it through the IDE in a much better, fun, quicker way that is more accurate".
resource: repo://docs/adr/0158-review-a-change-as-a-uml-diff-you-can-run.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0158-review-a-change-as-a-uml-diff-you-can-run.md
  title: 0158-review-a-change-as-a-uml-diff-you-can-run.md
  hash_method: lf-sha256-v1
  sha256: 294a941e7771d52ffc7a6dfc4af624e7fd05afb6a4791f652f82f7a8a42564e8
notes_baseline: 82e16e2f49ab7abfb65bb67de37eb4f490bb3c07f4703cfb7069a58054239252
---

# ADR-0158: Review a change as a UML diff you can run, not as a pull request

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0158-review-a-change-as-a-uml-diff-you-can-run.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * **`application/review.py`, `review_change(pack, before, after)`.** `before` is the model in force (the active baseline, or a case's baseline); `after` is the model shown (a case's candidate plus any accepted plan steps, recomputed by the server from the steps). It returns:
>   * **items**: every added, removed or changed state and transition from `diff_summary`, plus knock-on items nobody edited (a state that can no longer be reached, a state records can no longer leave), each with the element it is about and its reasons in words;
>   * **risk** by fixed rules: removing a path or a state, changing who may act or where records start, dropping a guard or an effect is high; adding or moving a path is medium; adding a state, a guard or a forbidden effect is low. Items are ordered high first;
>   * **behaviour**: every fixture actor tries every action from a fresh record in every state, on both models, through `runtime.execute` against an in-memory unit of work. Attempts whose outcome differs (allowed and now refused, a new destination, different effects) are rows, grouped by actor and linked to the items they explain;
>   * a **question** per item whose behaviour changed: one of its rows ("After this change, can a Librarian take ReturnLate on a record in Overdue?"), preferring one where allowed and refused swap, with the kernel's answer;
>   * the same seeded **simulation** (seed 1, 500 steps) on both models, with findings that appear or disappear.
> * **`POST /api/play/review`** takes the same request as Build & run and Simulate and is read-only.
> * **The Review tab** (`play-review.js`). Both models on one canvas: added in green, removed dashed in red, changed in amber, knock-on states in amber. Beside it, one card per item. **Show me** selects the element on the diagram. **Predict, then run** asks the question; only after an answer does the card show the kernel's answer and its behaviour rows. **Looks right** and **Needs a change** (with a note) unlock only after the item has been shown and its question answered. **Finish review** needs every item decided and produces a review note in Markdown, bound to both models' semantic hashes, to download. The plan card's **Review it** and the preview banner's **Review the change** open it; changing the plan re-runs the review for the new change.
> * **Points** (ADR-0157 rules): +1 for looking at a change on the diagram, +2 for predicting what the kernel does, +2 for finishing a review that decided every high-risk change. Approving earns nothing.

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

* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0157: Drawn edits join the plan, and a checks ring rewards checking](/adrs/0157-drawn-edits-and-checks-ring.md) - The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".
<!-- okf:generated:end links -->
