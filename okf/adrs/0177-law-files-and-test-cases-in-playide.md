---
type: Architecture Decision Record
title: 'ADR-0177: The law file and the test cases are files PlayIDE opens, edits as drafts and runs'
description: The owner asked where the formal law files and the test cases are.
resource: repo://docs/adr/0177-law-files-and-test-cases-in-playide.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0177-law-files-and-test-cases-in-playide.md
  title: 0177-law-files-and-test-cases-in-playide.md
  hash_method: lf-sha256-v1
  sha256: 90c96a2f1f26411348fab20c9f170cf7d23d9409ed4fbfbe93e09809cb8ed183
notes_baseline: 6b7675724d70b5abae1879c6462384ad96893afe03ebaaff4dab909418fa74d5
---

# ADR-0177: The law file and the test cases are files PlayIDE opens, edits as drafts and runs

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | executable UML (owner question, 8 October 2026: "formal law files and test cases etc?") |
| Source | `repo://docs/adr/0177-law-files-and-test-cases-in-playide.md` |

## Decision outcome (verbatim)

> Chosen option: the last one.
>
> 1. **`scenarios.json`** (`eija.scenarios.v1`, `domain/scenarios.py`) sits beside `pack.json`, as `screens.json` and `data.json` do. Each scenario has an id, a title, an optional start state and steps. Each step names a fixture actor, an action and `then`: either the state the record moves to, or the kernel's refusal code. All three packs ship with scenarios.
> 2. **`application/scenario_run.py`** runs each scenario on an in-memory session through `runtime.execute`. It stops at the first step whose outcome differs, marks the rest NOT_RUN, and names that step's diagram elements (its transition, the state it left and the state it reached). A model the policy refuses runs no scenario (REFUSED). `record_steps` returns what the kernel did for a list of steps, written as expectations: this is how a test is added.
> 3. **Surfaces.**
>    * `eija scenarios --pack P [--file DIR] [--workflow F]` exits 2 unless every scenario passes.
>    * `POST /api/play/tests` runs the pack's scenarios, or a draft, on the model on screen, with a previewed plan included.
>    * `POST /api/play/tests/try` records steps.
>    * PlayIDE's new **Tests** tab lists every scenario as Given/When/Then with pass or fail per step. **Show on diagram** paints the passing steps green and the failing one red. **New test** lets you pick who and what, one step at a time, and keep the result. **Edit scenarios.json** edits the file as JSON. A draft is marked "Edited, not saved" and can be downloaded.
> 4. **The law file in the Laws tab.**
>    * **Edit the law file** opens the laws exactly as `pack.json` holds them. **Prove the draft** checks the draft as the pack loader does (`law_proof.with_laws`, which calls `parse_pack`) and proves it over every run. It lists the laws added, changed and removed (`compare_laws`) and warns that removing or changing a law can loosen what the kernel refuses.
>    * The draft pack can be downloaded. Replacing `pack.json` with it stays the owner's reviewed step.
>    * **Formal checks for this pack** lists the pack's `verifiers`: how each checker covers it (the kernel, by hand, generated or not run) and why.
> 5. **Measured 2026-10-08, linux, Python 3.13.**
>    * Library-loan has 7 scenarios, excursion 6 and eija-review-slice 5. Every one passes.
>    * The negative controls:
>      * a kernel whose `check_actor` ignores roles fails "A member cannot check a book out to themselves" at step 1;
>      * a model without ReturnLate fails the overdue scenario at step 3 with ACTION_DENIED, while the others still pass;
>      * a wrong expectation fails at its own step and leaves the later steps NOT_RUN;
>      * a stricter draft law ("nothing leaves OnLoan") is reported BROKEN, and the model is REFUSED under it.

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
* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…
* [ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE](/adrs/0166-laws-proved-over-every-run-for-any-pack.md) - Every pack already states its laws as typed data in `pack.json` (`domain/laws.py`, twelve kinds): "only a librarian checks a loan out", "every path to Returned…

## Referenced by

* [ADR-0185: Start, open and save your own system in PlayIDE](/adrs/0185-start-open-and-save-your-own-system.md) - PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA.
* [ADR-0195: Sequence diagrams are the pack's scenarios, drawn in UML and checked by the kernel step by step](/adrs/0195-sequence-diagrams-the-kernel-checks.md) - Engineers who read UML expect sequence diagrams beside the state machine, class, use case and component diagrams.
<!-- okf:generated:end links -->
