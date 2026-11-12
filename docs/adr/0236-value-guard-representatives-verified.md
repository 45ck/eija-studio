# ADR-0236: Verify value-guard representatives by property and mutation, and fix what that found

* Status: accepted
* Date: 2026-11-12
* Lane: kernel / verification (issue #221)

## Context and problem statement

ADR-0231 to ADR-0235 added initiators, one action from several states, separation of duties, guards over record values and built associations. Their tests were examples. The property suite (ADR-0031) and the mutation ratchet (ADR-0033, ADR-0034) predate them: the workflow generators never produced value guards or initiators, and `value_guards.py` and `laws.py` were not mutation targets.

The law proof, Simulate and the generated app's conformance oracle all rest on one claim in `domain/value_guards.py`: a finite set of values stands for every value a guard can tell apart. If some record value answers an attribute's guards in a pattern no representative produces, the proof never tries that record and can report HOLDS for a law the kernel breaks.

## Decision drivers

* A verdict is only as good as the values it tried. The claim must hold for every value a record can hold, not for the values an example happened to use.
* Fix the kernel, never the oracle: a counterexample is a defect until shown otherwise.
* Keep the fast tier fast (issue #206): Hypothesis stays in the full tier; each shrunk counterexample becomes a plain fast-tier regression test.
* Existing oracles, digests and recordings keep their bytes: representatives only change where the old ones were wrong.

## Considered options

* Extend the existing Hypothesis suite and cosmic-ray targets (chosen). Both are already adopted and registered.
* Add a second property tool (CrossHair, schemathesis) or mutation engine (mutmut). No gain over what is installed; mutmut 3 does not run on native Windows (ADR-0033).
* Prove the representative claim with Z3. The claim is about Python's int and float semantics (rounding near 2**53, overflow beyond 1.8e308), which an SMT encoding would have to model separately and could get wrong the same way.

## Decision outcome

**Property tests.** `tests/property/test_value_guards.py` states the claim for numbers (including integers beyond the float range and floats beyond 2**53), dates, text and true/false; that guards fail closed on missing, mistyped and non-finite values; that `combinations` is the full product or refuses; that siblings of one action share guards by literal; that the ripple reports a guard change exactly when the guards differ; and that `separation_breach` agrees with a naive reading of ADR-0233. The workflow generators now produce value guards and initiators, and the semantic-hash normal form and edits cover them.

**What they found, and the fixes.** Each has a fast-tier regression test in `tests/test_value_guard_edges.py`.

1. *Representatives collapsed at large constants.* For floats from 2**53 up, `c - 1 == c`, so the "below" point was the constant itself: no representative made `amount ≠ 9007199254740996.0` or `amount < c` true. `_numbers` now takes the first of `c ± 1`, the next float, or the next whole number that lies strictly on the right side.
2. *Overflow.* Two integer constants beyond the float range made `(a + b) / 2` raise `OverflowError`, crashing the law proof. `_between` now tries the midpoint, `a/2 + b/2`, the next float above `a` and the next whole number, skipping any that overflow, and invents no point between two adjacent floats.
3. *NaN and infinity.* `json.loads` accepts `NaN` and `Infinity`, and `check_values` accepted them as numbers. NaN satisfied every `≠` guard, a pattern no representative has. Records now refuse non-finite numbers (`FIELD_TYPE`), and a guard over one fails closed.
4. *`true` equalled `1`.* Pydantic equality compares `True == 1`, so `[paid = true]` and `[paid = 1]` were one guard: two transitions of one action with those guards passed the ADR-0232 shape rule though no value satisfies both, the pair was refused as a duplicate on one transition, and the ripple saw no change between them. Guards are now compared by their JSON (`models.guard_keys`), as the semantic hash already did.
5. *Duplicate forbidden effects* (a strict xfail since ADR-0031's deep profile): `['X', 'X']` and `['X']` meant the same but hashed differently. The contract now refuses the duplicate, as it does a duplicate required effect.

The property run also showed `test_mutations_are_refused_by_both_or_neither[workflow]` never saw an accepted near-miss once value guards were in the schema; its repair step now keeps only guards the contract accepts.

**Mutation.** `domain/value_guards.py` and `domain/laws.py` are mutation targets with floors in `quality/mutation/baseline.json`. First run: 432 mutants, 0 survivors (2 timeouts, counted as detected).

The same run showed the full-tier `mutation_quick` gate was red on main: three mutants of the ADR-0231 check `UNDECLARED_INITIATOR:<role>` in `policy.declared_codes` survived, because only `tests/test_initiators.py` asserted it and that file is not in the policy target's selection. `tests/test_policy_authority.py` now asserts the exact codes for declared and undeclared initiators; `policy.py` is back to 132 of 132 killed. All three floors were taken in one Linux run, so the baseline's platform is now Linux (CPython 3.13); the previous floor came from Windows.

### Consequences

* Good: the law proof's "every value was tried" now holds for every value a record can hold, and a counterexample to it is a full-tier failure.
* Good: the full-tier mutation gate is green again.
* Good: a pack that writes `[x = true]` on one transition and `[x = 1]` on its sibling is refused, as ADR-0232 intended.
* Bad: a record value of NaN or infinity, accepted before, is now refused. No shipped pack or recording holds one.
* Revisit when: a guard kind other than numbers, dates, text or true/false is added; it needs its own representative property here first.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Hypothesis 6.168.3 (MPL-2.0, already registered) | Used as is; only new strategies and properties | n/a |
| cosmic-ray 8.7.0 (MIT, already registered) | Used as is; two new targets | n/a |
