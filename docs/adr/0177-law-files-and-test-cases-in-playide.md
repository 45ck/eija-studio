# ADR-0177: The law file and the test cases are files PlayIDE opens, edits as drafts and runs

* Status: accepted
* Date: 2026-10-08
* Lane: executable UML (owner question, 8 October 2026: "formal law files and test cases etc?")

## Context and problem statement

The owner asked where the formal law files and the test cases are. Some of each existed:

* **Laws.** The typed `laws` in each pack's `pack.json`, judged on the table by the protected policy and proved over every run by the Laws tab (ADR-0166). `verification/bend/LAWS.bend` states the excursion pack's laws for Bend, and TLA+, Z3 and a bounded model check cover excursion. Each pack's `verifiers` list says which of these checkers cover it.
* **Tests.** The built app's conformance cases (`appgen.oracle_cases`): every state × action × fixture actor × version, 240 to 360 per pack, generated and run by `eija build`. The SCXML differential replays them on a second engine (ADR-0165). Each pack also has fixture actors, a negative variant (`variants/`) and comprehension questions (`journey`).

Two gaps remained. In PlayIDE the law file was read-only, and you could not see the formal checks that cover a pack. And none of those tests is a test case a person wrote. The oracle cases are one step each and generated. Nothing records a story such as "a librarian lends a book, a clerk marks it overdue, the librarian takes it back late" and checks that it still works after a change.

## Decision drivers

* One source for laws: the `laws` in `pack.json`. There is no second law file or law language (AGENTS.md: no parallel rule sources).
* A test case runs on the kernel and on nothing else. A test that re-encoded the rules would be a second interpreter.
* People who use PlayIDE write tests in their IDE today. A test should read like a story, and adding one should take a few clicks.
* PlayIDE saves nothing (ADR-0156). Laws are protected policy: AI proposals cannot change them, and loosening one must stay a reviewed act by the owner.
* A failing test must show where it fails on the diagram.

## Considered options

* **Gherkin `.feature` files** (Cucumber's format; `gherkin-official` is MIT) run by behave or pytest-bdd. This is the most familiar story format. But its steps are free text matched by regular expressions, so a typo becomes an undefined step rather than a schema error. It also needs a step library and a test runner. The kernel's vocabulary has three facts per step (who, what action, what must happen), which typed JSON states exactly. PlayIDE shows each scenario as Given/When/Then anyway.
* **Make the generated oracle cases editable.** They are exhaustive and generated, so editing them would hide behaviour the generator decides, and they are one step each.
* **Let PlayIDE write `pack.json` and `scenarios.json`.** This is the most direct option. It is rejected for laws because a removed or loosened law would land without review. It is rejected for both files because PlayIDE never writes the repository, and no IDE route writes files.
* **Typed scenarios beside `pack.json`, run by the kernel, edited and run as drafts in PlayIDE, downloaded to keep** (chosen).

## Decision outcome

Chosen option: the last one.

1. **`scenarios.json`** (`eija.scenarios.v1`, `domain/scenarios.py`) sits beside `pack.json`, as `screens.json` and `data.json` do. Each scenario has an id, a title, an optional start state and steps. Each step names a fixture actor, an action and `then`: either the state the record moves to, or the kernel's refusal code. All three packs ship with scenarios.
2. **`application/scenario_run.py`** runs each scenario on an in-memory session through `runtime.execute`. It stops at the first step whose outcome differs, marks the rest NOT_RUN, and names that step's diagram elements (its transition, the state it left and the state it reached). A model the policy refuses runs no scenario (REFUSED). `record_steps` returns what the kernel did for a list of steps, written as expectations: this is how a test is added.
3. **Surfaces.**
   * `eija scenarios --pack P [--file DIR] [--workflow F]` exits 2 unless every scenario passes.
   * `POST /api/play/tests` runs the pack's scenarios, or a draft, on the model on screen, with a previewed plan included.
   * `POST /api/play/tests/try` records steps.
   * PlayIDE's new **Tests** tab lists every scenario as Given/When/Then with pass or fail per step. **Show on diagram** paints the passing steps green and the failing one red. **New test** lets you pick who and what, one step at a time, and keep the result. **Edit scenarios.json** edits the file as JSON. A draft is marked "Edited, not saved" and can be downloaded.
4. **The law file in the Laws tab.**
   * **Edit the law file** opens the laws exactly as `pack.json` holds them. **Prove the draft** checks the draft as the pack loader does (`law_proof.with_laws`, which calls `parse_pack`) and proves it over every run. It lists the laws added, changed and removed (`compare_laws`) and warns that removing or changing a law can loosen what the kernel refuses.
   * The draft pack can be downloaded. Replacing `pack.json` with it stays the owner's reviewed step.
   * **Formal checks for this pack** lists the pack's `verifiers`: how each checker covers it (the kernel, by hand, generated or not run) and why.
5. **Measured 2026-10-08, linux, Python 3.13.**
   * Library-loan has 7 scenarios, excursion 6 and eija-review-slice 5. Every one passes.
   * The negative controls:
     * a kernel whose `check_actor` ignores roles fails "A member cannot check a book out to themselves" at step 1;
     * a model without ReturnLate fails the overdue scenario at step 3 with ACTION_DENIED, while the others still pass;
     * a wrong expectation fails at its own step and leaves the later steps NOT_RUN;
     * a stricter draft law ("nothing leaves OnLoan") is reported BROKEN, and the model is REFUSED under it.

### Consequences

* Good: laws and tests are files a person can read, edit and run next to the UML, and a change that alters behaviour shows up as a failing test drawn on the diagram.
* Good: a scenario cannot drift from the kernel, because it states outcomes and the kernel decides them.
* Bad: keeping a draft needs a download and a commit. Once a reviewed path for writing pack files exists, it should replace the download.
* Bad: a scenario covers one record and the fixture actors. Data values, time and several records need new step kinds (issue #93's operators).
* Revisit when: an owner-approved write path for pack files lands, or people ask to read scenarios as Gherkin (an export is straightforward).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Gherkin (`gherkin-official`, MIT), behave (BSD-2), pytest-bdd (MIT) | Free-text steps bound by regular expressions, a step library and a runner, where three typed facts per step say the same and are schema-checked | Export scenarios as `.feature` files if a team wants Cucumber reports |
| Hypothesis stateful testing (MPL-2.0) | Generates runs rather than recording intended stories; the law proof (ADR-0166) already covers every run | — |
| Existing `appgen.oracle_cases` | Generated and one step each; they stay the built app's conformance suite | Unchanged |
