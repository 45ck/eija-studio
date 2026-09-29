---
type: Architecture Decision Record
title: 'ADR-0034: What is mutated, how a score is defined, and the ratchet'
description: ADR-0033 picks the engine.
resource: repo://docs/adr/0034-mutation-measurement-and-ratchet.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0034-mutation-measurement-and-ratchet.md
  title: 0034-mutation-measurement-and-ratchet.md
  hash_method: lf-sha256-v1
  sha256: 089de066484fe57e1443ed35b4585bec455315ec47dd00a6edd4113fc588132a
notes_baseline: 82525a09648e354c117735d3595ec935a50c25b1a3f030ac12d041efbcfcf16e
---

# ADR-0034: What is mutated, how a score is defined, and the ratchet

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-29 |
| Lane | mutation |
| Source | `repo://docs/adr/0034-mutation-measurement-and-ratchet.md` |

## Decision outcome (verbatim)

> Chosen option: "curated operators, per-module test selection, per-module ratchet".
>
> **Targets.** `domain/{policy,models,impact,evidence}.py` and `application/{runtime,verifier}.py`: the modules that decide authority and compute evidence. Each has an explicit list of the test files allowed to kill its mutants (`quality/mutation/targets.py`).
>
> **Operators.** One operator per fault class relevant to guards: comparison boundary and negation, `and`/`or`, `not`, `True`/`False`, numbers, arithmetic sign, loop `continue`/`break`, exception type, zero-iteration loops, plus three EIJA operators (identifier-like string constants, return values, membership). The stock operators that only re-spell a fault (`+` to `**`, `<<`, `^`, ...) are excluded because a `TypeError` kills them and they inflate the score without testing anything. Prose strings (messages, docstrings) and `Literal[...]` type arguments are not mutated: their text is not behaviour.
>
> **Outcomes.**
>
> | Outcome | Meaning | In the score |
> |---|---|---|
> | killed | a selected test failed on the mutant | detected |
> | timeout | the selected tests hung on the mutant (for example an infinite loop) | detected, reported separately so an unusual count is visible |
> | survived | every selected test passed on the mutant | not detected |
> | incompetent | the mutant could not be exercised (collection or import failure, worker crash) | excluded, and the gate fails if more than 20% of a module's mutants are incompetent |
>
> `score = (killed + timeout) / (killed + timeout + survived)`, rounded **down** to four places so a stored floor never exceeds the measured value.
>
> **Ratchet.** `quality/mutation/baseline.json` stores one floor per module, from a full (unsampled) run. The gate fails when a module's score is below its floor, when a measured module has no floor, when no mutants were generated, or when a run is sampled (an estimate is never compared with a full-run floor). Floors move up freely with `--write-baseline`; lowering one requires `--allow-lower` and appears in review as a diff of a committed file. A measurement failure (red baseline, the scratch copy not being the code under test, the engine failing) exits with a different status from a ratchet failure and produces no score.
>
> **Equivalent mutants.** A survivor that cannot change behaviour is marked `# pragma: no mutate` on its line with a justification (cosmic-ray's own filter). This lane marked none: it adds tests instead and does not edit production code.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/TECHNICAL_LEAD_REVIEW.md`
* `repo://quality/mutation/targets.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows](/adrs/0033-mutation-tool-selection.md) - The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role o…

## Referenced by

* [Mutation analysis](/lanes/0033-mutation-analysis.md) - Capability lane with ADR numbers 0033–0034 reserved.
<!-- okf:generated:end links -->
