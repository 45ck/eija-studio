# Property-based and model-based testing

Decision records: [ADR-0031](../adr/0031-property-based-testing-with-hypothesis.md) (Hypothesis, two profiles) and [ADR-0032](../adr/0032-stateful-differential-testing-and-negative-controls.md) (stateful differential test, negative controls).

Example tests say "this input behaves". These tests say "every input in this family behaves", using [Hypothesis](https://hypothesis.readthedocs.io/) to generate inputs and to shrink a failure to a minimal counterexample.

## Run it

```bash
pip install -e ".[dev,testing]"
nox -s property            # tier: full. ci profile, derandomized, ~2-3 min
nox -s property_deep       # tier: release. random seeds, 10x examples, saves failures to .hypothesis/
pytest tests/property      # the same suite without nox; a bare `pytest` skips it and says so
EIJA_HYPOTHESIS_PROFILE=deep pytest tests/property -k kernel_agrees
```

Reports are written to `reports/testing/property.json` (`property-deep.json` for the deep tier, both gitignored): profile, versions, platform, the number of examples Hypothesis generated per test, and the outcome histogram of the stateful test. A missing `hypothesis` install writes `"status": "NOT_RUN"` and skips the session; it never reports a pass.

| Profile | Seeds | Examples | Database | Use |
|---|---|---|---|---|
| `ci` (default) | fixed per test (`derandomize=True`) | base budget of each test | off | PR gate: the same examples everywhere, so a failure reproduces |
| `deep` | random | 10x | `.hypothesis/examples` | release tier: search harder; turn any failure into an `@example` or a named regression test |

## What is tested

| File | Property | What it establishes | What it does not |
|---|---|---|---|
| `test_runtime_differential.py` | Real `Studio` + SQLite equals an independent reference model after every step of random sequences | State, version, audit, outbox, operation and case-version equality; replay returns the original result without new effects; a conflicting binding is rejected; a revoked actor cannot replay; a crash after any commit step leaves no trace; edits make old instances stale unless the model is unchanged | Concurrency, crash during fsync, correctness of the specification, independence of the reference from its authors |
| `test_semantic_hash.py` | `Workflow.semantic_hash` equality coincides with an independent normal form | Invariant under permuting states, transitions, guards and effects; every semantic edit (rename, retarget, role, action, id, guard, effect, add/remove) changes it; last-writer-wins for typed edits | SHA-256 collision resistance; that the normal form is the right meaning |
| `test_impact_closure.py` | `closure` is reachability | Idempotent, monotone, distributes over union, contains roots, terminates on cycles; a budget never returns more than it, invents nothing, reports the exact unvisited frontier and `complete` iff nothing reachable was omitted; `model_impact` covers exactly the changed actions | That the projection graph covers every real-world consequence |
| `test_receipts.py` | Tampering with a sealed runtime-matrix receipt | Any single-field mutation breaks the HMAC seal; a key holder who re-seals is caught by the artifact hash; one who also recomputes the hash is caught by recomputation from raw observations; a stale technical subject is STALE; an asserted `status` is ignored | An attacker who forges a coherent matrix whose actual results equal the expected ones (the recorded same-author-oracle limit), or reads the local key |
| `test_contract_schemas.py` | `contracts/*.schema.json` versus the Pydantic models | Committed schemas equal the models' schemas; schema-generated instances are accepted (or refused only by a listed cross-field rule); everything the model accepts, built from the model side or after a near-miss mutation, satisfies the schema; both-or-neither agreement on near-misses | Cross-field rules JSON Schema cannot state (listed in `CROSS_FIELD`); other-language regex engines |
| `test_reference_detects_mutants.py`, `test_properties_detect_mutants.py` | Negative controls | Each property fails against a deliberately broken implementation (see below) | That the mutants cover every possible defect |

## The reference model

`tests/property/property_reference.py` is a deliberately naive second expression of the runtime rules, written from the specification text (ARCHITECTURE.md "Runtime commit sequence", ADR-007, ADR-011, the protected policy's published consequences), not from `application/runtime.py` or the verifier oracle. It has no SQL, no transactions and no Pydantic: dictionaries, dataclasses and a `predict` function whose checks follow the sequence in the specification.

The specification does not state where "is the action modelled?" is checked relative to the actor check. The reference puts it first, because role authority is only defined for a modelled action; the kernel does the same, and the test would flag a change.

It shares the policy vocabulary (state, role and effect names) with the kernel and was written in the same project, so it is a differential oracle. It is not a blinded holdout and reports never call it one.

## Generators

* `property_strategies.workflows()` builds structurally valid `Workflow` objects (unicode names, unique ids and actions, guard and effect sets, several roles). `reordered()` permutes every order-insensitive collection; `semantic_edits()` applies one of 16 edits. `normal_form()` is the test's own definition of workflow identity, written without `semantic_hash`.
* `test_receipts.py` obtains one genuine receipt from the real verifier and mutates one node at a time, choosing uniformly among five structural groups (envelope, subject, artifact fields, matrix, cells) so the ~3 000 cell leaves do not drown the few dozen fields that matter as much.
* `test_contract_schemas.py` uses `hypothesis-jsonschema` to generate from each committed schema, a small repair step to reach the model's cross-field rules (re-validated against the schema, so a repair cannot hide drift), and real Change Cases produced by the kernel at four stages as seeds for the nested aggregate.

## Negative controls (mutants)

A property suite is evidence only if it fails on a wrong kernel. The tests monkeypatch each of these into the running code, require the property to fail with an `AssertionError`, and undo the patch:

* Runtime: replay served before re-checking authority (ADR-007); operation-id conflict answered as replay; stale expected version ignored; assignment not required; revocation not checked.
* Hash: order-sensitive guards, states or transitions; ignoring forbidden effects, role, initial state or transition id.
* Closure: silent depth cap; budget off by one; `complete` always true; visited nodes in the frontier.
* Receipts: assessor that skips the artifact hash; trusts the matrix verdict; ignores the subject.
* Contracts: a schema that lost a length bound; a schema stricter than the model.

## Findings

* **Schema/model drift on integer fields (found by the `deep` profile, in part).** The three request/aggregate models disagree with their own schemas about what an "integer" is. `ExecuteCommand.expected_version` is `strict=True`: it refuses `1.0` (which JSON Schema, and Python's `json.dumps(1.0)`, treat as an integer) - fail-closed. `LayoutChange.x/y` and `ChangeCase.version` are Pydantic-lax: they accept `"1"` and `true` where the schema says `"type": "integer"` - fail-open on type. Recorded as five `xfail(strict=True)` cases of `test_integer_coercions_are_treated_alike_by_schema_and_model`; the other four combinations pass, so the strictness is inconsistent rather than uniformly wrong. Fix in a separate kernel change: `StrictInt` on integer fields of request models, or accept integral floats on `expected_version`.
* **Hash instability: duplicate forbidden effects (found by the `deep` profile, not by `ci`).** `Transition` rejects duplicate `required_effects` and duplicate guards but accepts duplicate `forbidden_effects`, and `semantic_hash` sorts without de-duplicating, so `["X"]` and `["X", "X"]` mean the same but hash differently. Evidence for one model is then spuriously STALE for the other (fail-safe, not a collision). Recorded as `xfail(strict=True)` in `test_semantic_hash.py::test_duplicate_forbidden_effect_is_not_a_semantic_difference`; the fix (reject the duplicate, or de-duplicate in the hash) is a separate kernel change because it touches protected `domain/models.py` and changes the implementation identity.
* **Documented non-findings.** Unknown extra keys in a receipt's `subject` (or, once the hash is recomputed, `artifact`) do not change the verdict because the assessor reads only named fields; the seal and hash bind them. `subject.presentation` is excluded from runtime applicability by design (ARCHITECTURE.md). Free-text `limitations` is prose.
* No other disagreement between the kernel and the reference or the schemas was found in the runs recorded in the PR.

## Adding a property

1. Write the oracle independently of the code under test (a plain reachability search, a normal form, a dictionary model).
2. State in the docstring what the property establishes and what it does not.
3. Scale its example budget with `property_support.examples(base)`.
4. Add a mutant that breaks the rule, and require the property to fail against it.
5. If it finds a real defect, commit an `xfail(strict=True)` with the reason and open a kernel change; do not weaken the property.

## Known limits

* `conftest.py` records example counts through Hypothesis' statistics collector, and the mutant tests use the per-test settings attribute that Hypothesis' own pytest plugin uses. Both are tied to the pinned version.
* The `deep` profile is not reproducible by design. Replay a failure with the printed `@reproduce_failure` blob or by adding an `@example`.
* Example counts are effort, not coverage of the state space.
