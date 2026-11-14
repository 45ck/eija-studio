---
description: "Integration review, 14 November 2026: main after the ten inspections of 13 November (#250-#261) reviewed as one change, with every tier run and every extra installed."
---

# Integration review of the 13 November fixes (14 November 2026)

On 13 November ten inspections merged about 90 fixes in PRs #250 to #261, each under auto-merge while the others
merged too. Each PR was reviewed alone. This review takes `main` at `41369a2` (after #261) as one change and asks
three questions:

1. Does all of it pass together, with nothing skipped?
2. Where do two of the day's fixes meet: the same code, the same behaviour, or the same documents?
3. Which fixes patched a symptom whose cause is structural?

The area threads ran a second pass of their own areas at the same time, and another thread reviewed #250-#261 PR by
PR, so this review stays at the level of the whole. The index of every inspection record is
[README.md](README.md).

## Method

* Every extra in `pyproject.toml` installed, so no test skips for a missing module: `smt` (z3), `mutation`
  (cosmic-ray), `graph`, `graph-formal`, `okf`, `hci`, `demos`, `visual`, `ux`, `dod`, `xuml`, `interop-api` and the
  rest. The Alloy and PlantUML jars at their pinned hashes and a Docker daemon, so the formal gates run instead of
  reporting NOT_RUN.
* `nox -t full`, then the release sessions that check the day's areas: `browser_suite` (`EIJA_BROWSER_TESTS=1`),
  `conformance_divergence_all`, `formal_bend`, `graph_formal_release` and `interop_plantuml`.
* The diffs of #250-#261 read for overlaps; every code a fix added traced through the layers that report it (policy,
  SMT encodings, legacy oracle, UML import and export, the generated app, PlayIDE's messages, docs).

## Findings

| ID | Kind | Where | Finding | Fix |
|---|---|---|---|---|
| I1 | Structural | `tests/conftest.py`; every `pytest.importorskip` | A test needing an extra skips without it and pytest exits 0. Local `nox -t fast` is the merge evidence while hosted CI cannot start, and contributors rarely install `smt`, so #258 merged two red z3-only tests and `main` stayed red until #261. #259 made hosted jobs fail on a skipped nox session, but not on a skipped test, and hosted jobs do not run. | New pytest plugin `tests/extras_guard.py`: every run ends with a "NOT_RUN for a missing extra" list grouped by module or extra, and `EIJA_REQUIRE_EXTRAS=1` makes such a skip fail the run. CONTRIBUTING and `docs/quality/gates.md` give it for merge evidence. The one test skipped even with every extra (`pyshacl`, a bench engine in no extra) now says so and is not counted. |
| I2 | Integration (red on `main`) | `quality/mutation/targets.py` | `nox -s mutation_quick` (full tier) was red on `main`: two survivors in `policy.lifecycle_conflicts`. #257 added `LINKED_LIFECYCLE_CONFLICT` with its test in a new file, `tests/test_merged_pr_inspection.py`, that never joined the policy module's mutation selection. The same gap held for `runtime.py`: the refusals of the 11-12 November kernel features (`ROLE_CANNOT_START`, `SEPARATION_DENIED`, `TIMER_NOT_DUE`, `VALUE_GUARD_DENIED`, `LINKED_OBJECT_REFUSED`, `SIGNAL_NOT_ACCEPTED`) were asserted only in files outside its selection. | The merged-PR tests join the `policy.py` and `models.py` selections; the six feature test files join `runtime.py`'s, with a `-k` expression (new `Target.keyword`) that leaves out their built-app and chart tests, so the selection stays at about five seconds. New `tests/test_mutation_selection.py`: every code literal a mutated module writes must appear in one of its selected test files, so a new rule and its test land in the selection together. |
| I3 | Design | `domain/policy.py` `_role_codes`; `verification/smt/{encoding,laws_gen,laws_gate}.py`; `tests/legacy_policy.py` | K1 (#258) named `UNDECLARED_ROLE` by transition id; every other catalog code names the action (`GUARD_POLICY:<action>`, `EFFECT_POLICY:<action>`). A role belongs to the action (ADR-0232), so an action from two states reported one refusal twice, and #261 had to map each pack's transition ids onto the SMT grammar's per-action slots (`_by_slot`, after Codex found the mismatch). | `UNDECLARED_ROLE:<action>` in the policy, the legacy oracle and both SMT encodings; `_by_slot` removed; snapshot hashes regenerated; ADR-0246 amended. Agreed with the kernel thread first. |
| I8 | Integration (red on `main`) | `tests/property/test_contract_schemas.py`, `tests/property/test_impact_closure.py` | `nox -s property` (full tier) was red on `main` with four failures. The contract test lists the cross-field rules JSON Schema cannot state; the linked-object rules (#245, ADR-0241) and the received-signal rule (#246, ADR-0242) were never added, so schema-valid instances were "wrongly" refused, and the near-miss workflow seeds no longer reached a single accepted instance. The impact property still expected no ripple without a changed action, though K7 (#258) made a change to how a record starts ripple through `record-start`. `tests/property` runs only in the full tier, so each PR's fast run was green. | The six rules are listed; a new test checks the other direction, that every `ValueError` a contract model raises is listed or excused, so a new validator cannot be forgotten again. Seed repair drops composites and linked objects (covered by their own tests) and deduplicates received signals. The impact property expects `record-start`, `review-packet` and `local-decision` exactly when how a record starts changed, and its independent oracle compares each action's transitions as a set: keyed by action alone it kept only the last transition of an action from several states (ADR-0232), so an edit to another one read as no change. That failure surfaced only once the first was fixed. |
| I4 | Documents | `docs/quality`, `docs/quality/inspections`, `docs/engineering`, `docs/hci` | The ten records were written in four folders under three naming schemes, with no list of them. | [README.md](README.md) in this folder lists every record with its PR, ADR and defect count, plus what the day left open, and is linked from the Quality lane page and the docs site navigation. Records stay where they are, because ADRs, OKF pages and the CHANGELOG link them. |
| I5 | Documents | `CLI-SERVER-INSPECTION.md` D10; `2026-11-13-tests-gates-docs.md` | Two records still said "left" or "passed on" for defects another thread fixed later the same day (the generated app's `Host` check in #260; the SMT-gated tests in #261). | Each now names the PR that fixed it. |
| I6 | Documents | `CHANGELOG.md` | Six of the ten inspections had a CHANGELOG section; chat plan mode (#253), diagram editing (#256), the merged-PR re-inspection (#257) and tests and gates (#259) had none. | One section covers the four. |
| I7 | Documents | `docs/ROADMAP.md`, issue #221 | The single list of current work did not mention the inspection day. | A line in both. |

## Checked and consistent

* #257 (M1) and #258 (K5) both fixed "another source for an existing action". Only one implementation is on `main`:
  `transactions._another_source`, which copies the action's shared shape; each PR's regression tests pass against
  it. `set_role`, `set_guards`, `set_effects` and retargeting a target change every transition of the action
  (`transactions._replace`), so no edit can split an action's shape.
* #258's `UNDECLARED_ROLE` reaches every layer that reports policy codes through `check_policy`: UML import (which also
  names an undeclared role at the arrow before the policy runs), plan preview and `plan_check`, the generated app's
  build, SCXML, the law proof and Simulate. PlayIDE shows policy codes as text, so it needs no new message.
* #252 (operation id), #257 (M3, `expected_version: 1.0`) and #260 (`Host` check, reads under the write lock) all
  changed the generated server's request handling; they compose (`server.py.tmpl` `do_POST`), and the generated
  conformance suite (20 tests) passes for every pack.
* #254 (the name of a set-aside draft) and #255 (`SYSTEM_CHANGED`, `:earlier[:n]` draft keys) touch neighbouring
  recovery code without overlap.
* #257 (M5) and #259 (DC-07) both corrected the stale `test.yml` header; one wording is on `main`.
* ADR numbers: 0244, 0245, 0246 and 0249 were used; 0247 and 0248 were left free on purpose. The kernel thread's
  second pass takes 0250. This review amends ADR-0246 rather than adding one.

## Gate results

See the pull request for the full table with before and after for each fix.
