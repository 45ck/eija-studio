---
type: Architecture Decision Record
title: 'ADR-0234: Guards over record values'
description: 'Issue #93, item 1.'
resource: repo://docs/adr/0234-guards-over-record-values.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0234-guards-over-record-values.md
  title: 0234-guards-over-record-values.md
  hash_method: lf-sha256-v1
  sha256: 90b0eb49e67ec42892175aad3f9bef31ac8cebb2c72e583925a990c6210e43b1
notes_baseline: 8d0588e5b34d70ade10686d47d92196f8dbda0813656b95d93b539abbca006b0
---

# ADR-0234: Guards over record values

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-11 |
| Lane | kernel / executable UML |
| Source | `repo://docs/adr/0234-guards-over-record-values.md` |

## Decision outcome (verbatim)

> **The model.** A transition may carry `conditions`, up to eight `{attribute, op, value}` guards that must all hold. `op` is one of `eq`, `ne`, `lt`, `le`, `gt` and `ge`.
> * The value is a number, a date (`YYYY-MM-DD`), text or true/false.
> * Ordering works on numbers and dates only. True/false is compared only with = or ≠.
> * When there are no conditions, the field is left out of every dump. That keeps the bytes and the semantic hash of every existing model. The semantic hash sorts conditions, because they are a set.
> * Every transition one action labels must carry the same conditions (ADR-0232).
>
> **The data model.** `value_guards.guard_problems` checks guards against the record class: the attribute exists, and the constant fits its type and its choices. `eija build` refuses a model whose guards do not fit, with `VALUE_GUARD_INVALID`.
>
> **The runtime.** After the state check, a transition with conditions reads the record's values through a new `UnitOfWork.values` port. Unless every guard holds, it refuses with `VALUE_GUARD_DENIED`, naming the transition and the attribute. A transition without conditions never calls the port. The Studio's preview records hold no values, so a guarded transition is always refused there. The generated app reads its record's checked `fields`.
>
> **Values that stand for all values.** A guard's truth depends only on which side of each constant a value falls, so `value_guards.points` picks a finite set that covers every region:
> * for numbers and dates: each constant, a point below the lowest, a point above the highest, and a point between each neighbouring pair;
> * for text and choices: each constant and one other value;
> * for true/false: both;
> * for every attribute: no value at all.
>
> `valuations` takes one point per guarded attribute, up to 256 combinations. Beyond that, the law proof reports UNKNOWN.
>
> **The checkers.**
> * **Law proof.** It runs one search per combination of values, since a record's values never change. It judges `can_reach_end` for each combination, so a record that some values strand is reported, together with those values.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* Amendment, 12 November 2026: tests and permissions give the record values
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0153: Data models as UML class diagrams, checked in the built app](/adrs/0153-data-models-as-uml-class-diagrams.md) - Until now, records in a built app (ADR-0150) carried only a title, because the model had no data.
* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.
* [ADR-0233: Separation of duties](/adrs/0233-separation-of-duties.md) - Issue #149.

## Referenced by

* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0175: Review a change as a UML diff you can run, not as a pull request](/adrs/0175-review-a-change-as-a-uml-diff-you-can-run.md) - The owner wants engineers to stop "reviewing changes in a GitHub PR when you can do it through the IDE in a much better, fun, quicker way that is more accurate…
* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.
* [ADR-0237: Time events on transitions](/adrs/0237-time-events.md) - Issue #93, item 2.
<!-- okf:generated:end links -->
