---
type: Architecture Decision Record
title: 'ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE'
description: 'Every pack already states its laws as typed data in `pack.json` (`domain/laws.py`, twelve kinds): "only a librarian checks a loan out", "every path to Returned passes through OnLoan", "Returned is final".'
resource: repo://docs/adr/0166-laws-proved-over-every-run-for-any-pack.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0166-laws-proved-over-every-run-for-any-pack.md
  title: 0166-laws-proved-over-every-run-for-any-pack.md
  hash_method: lf-sha256-v1
  sha256: ead9fd9126cbfa8b31369dda29484e562f8825c3fcfc80a761385f76c9f5d8b8
notes_baseline: a60156494c509de1e129a49bdc0ab5d87d6c55fa706468bd20f8b3831abed996
---

# ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for the current law kinds |
| Date | 2026-10-08 |
| Lane | executable UML (owner direction, 8 October 2026: a place for the laws, "like a BEND.LAWS file", with formal V&V, "on top of UML") |
| Source | `repo://docs/adr/0166-laws-proved-over-every-run-for-any-pack.md` |

## Decision outcome (verbatim)

> Chosen option: **E**, because it proves the laws for any pack and any drawn model in milliseconds, using only the kernel and the laws' own evaluator. The heavy formal tools (Bend, TLA+, Z3, BMC) remain the deep, independent checks where they exist.
>
> 1. **`application/law_proof.py`** (pure) explores, breadth first, every configuration a new record can reach: its state plus the path-law waypoints it has passed. From each one, every action is tried by every actor class through `runtime.execute` on an in-memory session.
>    * Actor classes: `check_actor` reads only `active`, `role` and `assigned`, so one actor per role per flag combination, plus one holding an undeclared role, stands for every actor.
>    * Every committed run is judged by `laws.evaluate_run`.
>    * A configuration is first reached by a shortest run, so a counterexample is the shortest run that breaks the law.
>    * `LAW_HANDLING` says how each kind is judged: by runs, on the table (`closed_shape`, `action_requires_guard`), or by review evidence (`requires_evidence`). A test fails if a new kind is unclassified, because the configuration product is complete only for kinds that judge each step or the waypoints passed.
> 2. **Verdicts per law:**
>    * HOLDS: no run breaks it, with the number of configurations searched.
>    * BROKEN: with the shortest counterexample run.
>    * VACUOUS: it holds only because its state is never reached or its action never commits.
>    * INACTIVE: its `when` condition is false for this model.
>    * EVIDENCE: judged by review evidence, not by runs.
>    * UNKNOWN: the search stopped at 20,000 configurations.
>
>    A model the policy refuses is REFUSED. The table verdicts are shown, and the search is NOT_RUN because the kernel would run nothing.
> 3. **Surfaces.** `eija laws --pack P [--workflow F] [--out F]` exits 2 unless the model holds. `POST /api/play/laws` returns the report for the model on screen, including a previewed plan. PlayIDE gets a **Laws** tab that lists every law in plain language with its verdict, and shows its subject or its counterexample run on the state machine.
> 4. **Measured 2026-10-08, linux, Python 3.13.** All three shipped packs hold. They use 4, 5 and 6 configurations, with 16, 16 and 12 actor classes, and every state is reached. On the excursion baseline, the recommendation laws are INACTIVE or VACUOUS. On the excursion candidate (`recommend_only`) they hold. Three negative controls must each find the broken law and its shortest run:
>    * a kernel whose `check_actor` ignores roles: a one-step run by a non-librarian checking out;
>    * with the policy guard off, a model where Return leaves Requested: the one-step run `Return`;

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/weave/research/mde-metamodels-and-standards.md`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…

## Referenced by

* [ADR-0176: How a UML change looks: one stable layout, removed parts kept as ghosts, and lenses](/adrs/0176-how-a-uml-change-looks.md) - The owner asked how a change can be reviewed as a UML change instead of a pull request, and "how you even view a UML change (ghost UI/UX?)".
* [ADR-0177: The law file and the test cases are files PlayIDE opens, edits as drafts and runs](/adrs/0177-law-files-and-test-cases-in-playide.md) - The owner asked where the formal law files and the test cases are.
* [ADR-0195: Sequence diagrams are the pack's scenarios, drawn in UML and checked by the kernel step by step](/adrs/0195-sequence-diagrams-the-kernel-checks.md) - Engineers who read UML expect sequence diagrams beside the state machine, class, use case and component diagrams.
<!-- okf:generated:end links -->
