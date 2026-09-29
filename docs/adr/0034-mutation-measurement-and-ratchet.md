# ADR-0034: What is mutated, how a score is defined, and the ratchet

* Status: accepted
* Date: 2026-09-29
* Lane: mutation

## Context and problem statement

[ADR-0033](0033-mutation-tool-selection.md) picks the engine. A mutation score is only meaningful if the fault model, the tests allowed to kill a mutant, and the meaning of each outcome are fixed and stated. Otherwise the number can be inflated (trivially killable mutants, hung tests counted as detections, a broken tool reading as "all killed") or gamed (deleting a hard mutant instead of testing it).

## Decision drivers

* The score must measure fault-detection power of the tests over *guard, authority and evidence* faults, not raw mutant volume.
* A tool failure must never look like a good score, and a missing engine must be `NOT_RUN`.
* The gate must be cheap enough for the `full` tier (a few minutes, two workers) and complete in the `release` tier.
* Production code is out of scope for this lane: findings become tests, not edits.

## Considered options

* All ~210 stock cosmic-ray operators, whole test suite per mutant.
* A curated operator set, per-module test selection, and a per-module ratchet floor (chosen).
* A single global score threshold.

## Decision outcome

Chosen option: "curated operators, per-module test selection, per-module ratchet".

**Targets.** `domain/{policy,models,impact,evidence}.py` and `application/{runtime,verifier}.py`: the modules that decide authority and compute evidence. Each has an explicit list of the test files allowed to kill its mutants (`quality/mutation/targets.py`).

**Operators.** One operator per fault class relevant to guards: comparison boundary and negation, `and`/`or`, `not`, `True`/`False`, numbers, arithmetic sign, loop `continue`/`break`, exception type, zero-iteration loops, plus three EIJA operators (identifier-like string constants, return values, membership). The stock operators that only re-spell a fault (`+` to `**`, `<<`, `^`, ...) are excluded because a `TypeError` kills them and they inflate the score without testing anything. Prose strings (messages, docstrings) and `Literal[...]` type arguments are not mutated: their text is not behaviour.

**Outcomes.**

| Outcome | Meaning | In the score |
|---|---|---|
| killed | a selected test failed on the mutant | detected |
| timeout | the selected tests hung on the mutant (for example an infinite loop) | detected, reported separately so an unusual count is visible |
| survived | every selected test passed on the mutant | not detected |
| incompetent | the mutant could not be exercised (collection or import failure, worker crash) | excluded, and the gate fails if more than 20% of a module's mutants are incompetent |

`score = (killed + timeout) / (killed + timeout + survived)`, rounded **down** to four places so a stored floor never exceeds the measured value.

**Ratchet.** `quality/mutation/baseline.json` stores one floor per module, from a full (unsampled) run. The gate fails when a module's score is below its floor, when a measured module has no floor, when no mutants were generated, or when a run is sampled (an estimate is never compared with a full-run floor). Floors move up freely with `--write-baseline`; lowering one requires `--allow-lower` and appears in review as a diff of a committed file. A measurement failure (red baseline, the scratch copy not being the code under test, the engine failing) exits with a different status from a ratchet failure and produces no score.

**Equivalent mutants.** A survivor that cannot change behaviour is marked `# pragma: no mutate` on its line with a justification (cosmic-ray's own filter). This lane marked none: it adds tests instead and does not edit production code.

**Limits, stated.** The score covers the curated fault model over six modules. The tests that raised it were written by the same author who read the survivors, so it is not an independent hidden-mutation evaluation (`docs/TECHNICAL_LEAD_REVIEW.md` recommends one). Mutation testing shows the tests notice these faults; it does not prove the kernel correct.

### Consequences

* Good: the number is comparable run to run, cannot be inflated by tool noise, and moves only with the tests or the code.
* Good: every survivor is a concrete, reviewable work item with a diff.
* Bad: per-module test selection can report a survivor that an unselected test would kill. The selections are deliberately generous for the authority modules; widen one in `targets.py` when a survivor is known to be covered elsewhere.
* Revisit when: a module is added to the authority core (add it to `TARGETS` and establish a floor), or timeouts exceed a few percent of mutants (the timeout multiplier is then too tight for the machine).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| cosmic-ray filters (`operators-filter`, `pragma-no-mutate`) | Adopted as is. They can exclude by regex but not include a curated list, so the configuration renders a negative-lookahead exclusion. | None needed. |
| cosmic-ray reporting (`cr-report`, `cr-rate`, `cr-html`) | Do not classify timeouts or collection failures separately, produce no ratchet, and print survivors without a suggested test. | `report.py` reads `cosmic-ray dump`, which is the stable interface. |
