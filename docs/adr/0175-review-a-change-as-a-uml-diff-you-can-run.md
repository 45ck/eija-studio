# ADR-0175: Review a change as a UML diff you can run, not as a pull request

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner wants engineers to stop "reviewing changes in a GitHub PR when you can do it through the IDE in a much better, fun, quicker way that is more accurate". The positioning research behind PlayIDE found that AI-written pull requests are accepted far less often than human ones, and that reviewers who skim an AI's diff build up comprehension debt: the change lands, but nobody can say what it does. A text diff of a model file shows which lines moved, not what the system now allows or forbids.

PlayIDE already previews a change (chat plan mode, ADR-0156; drawn edits, ADR-0157) and a change case already holds a candidate model. What was missing is the review itself: going through each change, understanding what it does, and recording a decision, in a way that rewards checking rather than rubber-stamping.

## Decision drivers

* Review the meaning, not the text: every change is a UML element on the diagram, and a deleted path must be as visible as an added one.
* "More accurate" has to be measurable: what the change does is decided by the kernel, not by the reviewer reading code or by the page.
* Rewards go to checking and understanding (ADR-0157), never to approving or to producing output.
* One source of meaning: reuse `diff_summary`, the typed transactions, `runtime.execute` and `simulate`; no second interpreter in the page.
* A review never approves or applies. Those stay owner-only in the review workbench (and wait on issue #80 today).

## Considered options

* A Review tab that draws both models on one diagram, ranks changes by fixed risk rules, runs both models through the kernel for every fixture actor, and asks the reviewer to predict each changed outcome before showing it (chosen).
* Show the existing workbench compare view inside PlayIDE. Rejected: it shows the diff, but not what it does when run, and it has no per-change decision.
* A text or JSON diff of the model (jsdiff, GitHub's file view). Rejected: line-level, so a moved transition reads as a delete plus an add, and nothing says what behaviour changed.
* A model-diff engine (EMF Compare). Rejected: Eclipse/EMF-only, and EPL-2.0 is weak copyleft; `diff_summary` already gives a semantic diff of this model.
* Score reviews by how many changes were approved. Rejected: that rewards rubber-stamping, the failure the research warns about.

## Decision outcome

Chosen option.

* **`application/review.py`, `review_change(pack, before, after)`.** `before` is the model in force (the active baseline, or a case's baseline); `after` is the model shown (a case's candidate plus any accepted plan steps, recomputed by the server from the steps). It returns:
  * **items**: every added, removed or changed state and transition from `diff_summary`, plus knock-on items nobody edited (a state that can no longer be reached, a state records can no longer leave), each with the element it is about and its reasons in words;
  * **risk** by fixed rules: removing a path or a state, changing who may act or where records start, dropping a guard or an effect is high; adding or moving a path is medium; adding a state, a guard or a forbidden effect is low. Items are ordered high first;
  * **behaviour**: every fixture actor tries every action from a fresh record in every state, on both models, through `runtime.execute` against an in-memory unit of work. Attempts whose outcome differs (allowed and now refused, a new destination, different effects) are rows, grouped by actor and linked to the items they explain;
  * a **question** per item whose behaviour changed: one of its rows ("After this change, can a Librarian take ReturnLate on a record in Overdue?"), preferring one where allowed and refused swap, with the kernel's answer;
  * the same seeded **simulation** (seed 1, 500 steps) on both models, with findings that appear or disappear.
* **`POST /api/play/review`** takes the same request as Build & run and Simulate and is read-only.
* **The Review tab** (`play-review.js`). Both models on one canvas: added in green, removed dashed in red, changed in amber, knock-on states in amber. Beside it, one card per item. **Show me** selects the element on the diagram. **Predict, then run** asks the question; only after an answer does the card show the kernel's answer and its behaviour rows. **Looks right** and **Needs a change** (with a note) unlock only after the item has been shown and its question answered. **Finish review** needs every item decided and produces a review note in Markdown, bound to both models' semantic hashes, to download. The plan card's **Review it** and the preview banner's **Review the change** open it; changing the plan re-runs the review for the new change.
* **Points** (ADR-0157 rules): +1 for looking at a change on the diagram, +2 for predicting what the kernel does, +2 for finishing a review that decided every high-risk change. Approving earns nothing.

### Consequences

* Good: a reviewer sees what the change does, decided by the kernel for every fixture actor, and a wrong prediction is surfaced as a surprise to look at again, not lost in a skim.
* Good: the deleted path, the usual blind spot of a diff, is drawn and ranked first.
* Good: nothing new interprets the model: the review reuses the diff, the transactions, the kernel and the simulation.
* Bad: behaviour covers the fixture actors and one attempt per state and action from a fresh record. Guards that depend on data the fixtures do not vary are not exercised, and the review says so.
* Bad: risk rules are about the kind of change, not the domain. A low-risk change can still be wrong.
* Bad: the review note is a download, not stored evidence, and a review is not an approval. Storing reviews with a case, and letting the owner approve from it, wait on issue #80 (restamp) and issue #89 (saving free-form plans).
* Revisit when: reviews should be stored with a change case, the owner wants a review to gate approval, or fixtures gain data variation.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| GitHub and Gerrit review flow (per-file "viewed" and a final verdict) | A pattern, adopted: one decision per changed element and a verdict at the end | — |
| EMF Compare (EPL-2.0) | Eclipse/EMF models only; weak copyleft. `diff_summary` already diffs this model semantically | Export to an EMF model if one is needed |
| jsdiff (BSD-3-Clause) | Text diff; a moved transition reads as delete plus add, and behaviour is invisible | — |
| Predict–observe–explain (teaching method, White & Gunstone 1992) | A method, adopted as "Predict, then run" | — |
| Existing `diff_summary`, `runtime.execute`, `simulate`, maxGraph and Dagre | Adopted | — |
