# ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE

* Status: accepted for the current law kinds
* Date: 2026-10-08
* Lane: executable UML (owner direction, 8 October 2026: a place for the laws, "like a BEND.LAWS file", with formal V&V, "on top of UML")

## Context and problem statement

Every pack already states its laws as typed data in `pack.json` (`domain/laws.py`, twelve kinds): "only a librarian checks a loan out", "every path to Returned passes through OnLoan", "Returned is final". The protected policy judges them on the transition table and refuses a model or edit that breaks one. The formal lanes go further for one pack only. `verification/bend/LAWS.bend` states laws that `PROOF.bend` proves for all actors, states and command sequences. TLA+/TLC, Z3 and a bounded model check of the runtime are alongside it. All of that is written for the excursion pack.

The owner pictured exactly this, a laws file with formal verification and validation above the UML. Two things were missing. PlayIDE did not show the laws at all, so the layer that decides what the diagrams may never do was invisible. And no proof covered any pack other than excursion, or any model a person draws.

## Decision drivers

* Laws stay one source: the typed `laws` in `pack.json`, judged by `laws.evaluate_table` and `laws.evaluate_run`. Nothing may re-encode them.
* The kernel stays the only interpreter (ADR-0165). A proof about runs must ask `runtime.execute`, not a model of it.
* Any pack and any model a person draws or the AI proposes, with no per-pack hand-written spec and no JVM or Docker in the inner loop.
* Honest verdicts: a law that holds only because nothing reaches it must say so, a search that stops is UNKNOWN, and evidence laws are not judged by runs.
* OSS first (ADR-0016).

## Considered options

* **A. Generate a TLA+ specification per pack and run TLC or Apalache** (TLC is MIT and already used, see `verification/tla/`; Apalache is a symbolic checker for TLA+). Strong temporal logic, but it needs Java on every run, and it is a second encoding of the kernel and of each law kind, which `verification/tla` keeps in step for one pack with a drift gate.
* **B. Alloy 6** (MIT, already used by the weave lane). Good for relational invariants of the table, bounded for runs, JVM, and again a second encoding.
* **C. OCL constraints over a UML model** (Eclipse OCL, EPL-2.0, Java). The standard UML way to state invariants, but EIJA's laws are already typed records with stable codes. OCL would be a second law language with a Java evaluator (see `docs/weave/research/mde-metamodels-and-standards.md`).
* **D. Model check the SCXML export** (ADR-0165) by translating it to SPIN/Promela or UPPAAL. That is one step further from the kernel than the export itself, and it needs the laws written as temporal formulas.
* **E. Exhaustive explicit-state search that asks the kernel for every step and the law evaluator for every run** (chosen). No second encoding. The state space of one record is tiny: states x path-law waypoints passed.

## Decision outcome

Chosen option: **E**, because it proves the laws for any pack and any drawn model in milliseconds, using only the kernel and the laws' own evaluator. The heavy formal tools (Bend, TLA+, Z3, BMC) remain the deep, independent checks where they exist.

1. **`application/law_proof.py`** (pure) explores, breadth first, every configuration a new record can reach: its state plus the path-law waypoints it has passed. From each one, every action is tried by every actor class through `runtime.execute` on an in-memory session.
   * Actor classes: `check_actor` reads only `active`, `role` and `assigned`, so one actor per role per flag combination, plus one holding an undeclared role, stands for every actor.
   * Every committed run is judged by `laws.evaluate_run`.
   * A configuration is first reached by a shortest run, so a counterexample is the shortest run that breaks the law.
   * `LAW_HANDLING` says how each kind is judged: by runs, on the table (`closed_shape`, `action_requires_guard`), or by review evidence (`requires_evidence`). A test fails if a new kind is unclassified, because the configuration product is complete only for kinds that judge each step or the waypoints passed.
2. **Verdicts per law:**
   * HOLDS: no run breaks it, with the number of configurations searched.
   * BROKEN: with the shortest counterexample run.
   * VACUOUS: it holds only because its state is never reached or its action never commits.
   * INACTIVE: its `when` condition is false for this model.
   * EVIDENCE: judged by review evidence, not by runs.
   * UNKNOWN: the search stopped at 20,000 configurations.

   A model the policy refuses is REFUSED. The table verdicts are shown, and the search is NOT_RUN because the kernel would run nothing.
3. **Surfaces.** `eija laws --pack P [--workflow F] [--out F]` exits 2 unless the model holds. `POST /api/play/laws` returns the report for the model on screen, including a previewed plan. PlayIDE gets a **Laws** tab that lists every law in plain language with its verdict, and shows its subject or its counterexample run on the state machine.
4. **Measured 2026-10-08, linux, Python 3.13.** All three shipped packs hold. They use 4, 5 and 6 configurations, with 16, 16 and 12 actor classes, and every state is reached. On the excursion baseline, the recommendation laws are INACTIVE or VACUOUS. On the excursion candidate (`recommend_only`) they hold. Three negative controls must each find the broken law and its shortest run:
   * a kernel whose `check_actor` ignores roles: a one-step run by a non-librarian checking out;
   * with the policy guard off, a model where Return leaves Requested: the one-step run `Return`;
   * with the policy guard off, a model where Cancel leaves Returned: the run `CheckOut, Return, Cancel`.

### Consequences

* Good: the laws are visible where people design, and each verdict comes with its evidence or a counterexample a person can follow on the diagram.
* Good: any pack and any proposed change gets a proof over every run and every kind of actor, not only excursion's hand-written proofs.
* Good: vacuous laws are flagged. A law about a state nobody reaches is a design smell that a table check never shows.
* Bad: the proof is about one record at a time. Laws relating several records, time or data values need new law kinds and a larger configuration space (issue #93's operators).
* Bad: on a model the policy accepts, the search re-confirms what the table check already implies unless the kernel is wrong. Its value is as a check on the kernel (the negative controls) and on future run-level law kinds, and its vacuity and reachability findings. It is not a second opinion on the law evaluator. Bend, TLA+ and Z3 are those, for excursion.
* Revisit when: a law kind needs more history than the waypoints passed (extend the configuration and `LAW_HANDLING`), a pack exceeds the configuration cap, or a second, independent run-checker (TLC over a generated spec) is wanted for every pack.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| TLA+/TLC (MIT, used in `verification/tla`), Apalache | A second encoding of the kernel and every law kind per pack, and Java on every run | Generate a TLA+ spec from the pack beside this search, with the same counterexample format |
| Alloy 6 (MIT, used by the weave lane) | Bounded for runs, JVM, second encoding | — |
| Eclipse OCL (EPL-2.0) and OCL tools | A second law language and a Java evaluator; EIJA laws are typed records with stable refusal codes | Export laws as OCL for interchange if a UML tool needs them |
| SPIN/Promela or UPPAAL over the SCXML export | Further from the kernel than the export, and laws would have to be rewritten as temporal formulas | — |
| Existing `verification/bmc` explorer | Excursion-only and about runtime storage invariants (replays, CAS), not the pack's law set across every pack | Unchanged; it remains the storage-level check |
