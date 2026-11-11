---
type: Module
title: application.review
description: Review a model change in PlayIDE instead of a pull request (ADR-0175).
resource: repo://src/eija_studio/application/review.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/review.py
  title: application/review.py
  hash_method: ast-api-v1
  sha256: c1814206c35bf047dde46a164764e4916fb76840ab7670d34a5818c469c943ba
notes_baseline: f6ecb8a4edde8f8cf37a1a5420ff69663273c84ffd44998e425c2e983e634c35
---

# application.review

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/review.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Review a model change in PlayIDE instead of a pull request (ADR-0175).

A change is a pair of models: the one in force and the one the change would make. The review is built from three
readings of that pair, none of which the page computes:

* **What changed**, from `diff_summary`: every added, removed or changed state and transition, plus the knock-on
  effects nobody edited directly (a state that can no longer be reached, a state records can no longer leave). A
  state whose every transition and start now use a new name is read as renamed, so a rename is one low-risk change
  rather than a deleted state, an added one and every arrow that touches it.
* **How risky each change is**, by fixed rules that a reviewer can read: removing a path, changing who may act,
  dropping a guard or an effect are high; adding a path or moving one is medium; adding a state or a guard is low.
* **What it does when run.** Every fixture actor tries every action from every state on both models, and the kernel
  (`runtime.execute`) decides each attempt. Attempts whose outcome differs (allowed before and refused after, a new
  destination, different effects) are the behaviour diff. The same seeded simulation runs on both models too.

Each change that alters behaviour carries a question for the reviewer to answer before the kernel's answer is shown
(predict, then run). The review is read-only: it saves, approves and applies nothing.
~~~

## Public symbols

* [`CASE`](/symbols/application/review/CASE.md) (constant) - no docstring
* [`FIELD_LABEL`](/symbols/application/review/FIELD_LABEL.md) (constant) - no docstring
* [`RISK_ORDER`](/symbols/application/review/RISK_ORDER.md) (constant) - no docstring
* [`behaviour_diff`](/symbols/application/review/behaviour_diff.md) (function) - Every fixture actor tries every action from every state on both models; the attempts whose outcome differs.
* [`renames`](/symbols/application/review/renames.md) (function) - States the change renamed: a state that is gone, matched to the one new state that every transition and the start that…
* [`review_change`](/symbols/application/review/review_change.md) (function) - Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
* [`row_text`](/symbols/application/review/row_text.md) (function) - no docstring

## Internal imports

* [`application/diagrams`](/modules/application/diagrams.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`application/simulation`](/modules/application/simulation.md)
* [`domain/impact`](/modules/domain/impact.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.simulation](/modules/application/simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.review.CASE](/symbols/application/review/CASE.md) - Constant `CASE` in `application/review`.
* [application.review.FIELD_LABEL](/symbols/application/review/FIELD_LABEL.md) - Constant `FIELD_LABEL` in `application/review`.
* [application.review.RISK_ORDER](/symbols/application/review/RISK_ORDER.md) - Constant `RISK_ORDER` in `application/review`.
* [application.review.behaviour_diff](/symbols/application/review/behaviour_diff.md) - Every fixture actor tries every action from every state on both models; the attempts whose outcome differs.
* [application.review.renames](/symbols/application/review/renames.md) - States the change renamed: a state that is gone, matched to the one new state that every transition and the start that used it now use instead (counting only t…
* [application.review.review_change](/symbols/application/review/review_change.md) - Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
* [application.review.row_text](/symbols/application/review/row_text.md) - `def row_text(row: dict[str, Any]) -> str` in `application/review`.
<!-- okf:generated:end links -->
