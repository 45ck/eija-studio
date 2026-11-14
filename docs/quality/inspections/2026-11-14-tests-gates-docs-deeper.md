---
description: "Second Fagan pass, 14 November 2026, over the tests, nox gates, hosted CI and docs: every skip traced to a tier, every optional tool that hid a gate, the nightly and release tiers run end to end."
---

# Inspection, second pass: tests, gates and docs (14 November 2026)

The [first pass](2026-11-13-tests-gates-docs.md) (#259) made the release tier run the 116 browser and slow tests, made
the hosted job fail on a skipped nox session, and corrected docs that called shipped features planned. This pass goes
where it did not: the tests that still skip and why, optional tools that hide a gate the way z3 did, tests that cannot
fail, flaky and order-dependent tests, the nightly and release tiers run end to end, and the docs checked against the
code after #250 to #269. The [integration review](2026-11-14-integration-review.md) (#270) ran at the same time and
found two of the same things; they are credited to it below and not fixed twice.

## Scope and method

* **Baseline:** `main` at `a389973` (after #262), rebased onto `a85b66e` (after #270) before the fixes were finished.
  Linux, CPython 3.13, 4 cores.
* **Environment:** every extra the hosted job installs, then each gate run with and without the jars and opt-in
  variables, so a skip could be traced to the thing that causes it.
* **Runs:** `pytest -rs` over the default selection with every extra (3,783 passed, 187 skipped, 1 xfailed); the same
  suite three times in random order (pytest-randomly, seeds 1234, 7 and 99, not committed); `nox -t full` session by
  session with `--report`; the release `mutation` session on every target; `verification.smt.laws` timed serially
  and in parallel.
* **Static checks:** an AST scan for tests with no assertion, for `pytest.importorskip` of first-party modules, and
  for tests whose only assertions sit in a loop; a script that resolves every path, test id and error code written in
  backticks in ADR-0228 to ADR-0254, the inspection records, `docs/quality/*.md`, the README, roadmap, CONTRIBUTING
  and CHANGELOG.
* **Severity:** major means a gate reports something false (a pass, a NOT_RUN or a failure) about the product; minor
  means it is wrong or weak but cannot hide a defect on its own.

### Checklist

| # | Question |
|---|---|
| S1 | For every skipped test: which tier runs it, and could any tier? |
| S2 | Which optional extra, jar or daemon makes a gate NOT_RUN on every machine that does not have it, the hosted runner included? |
| S3 | Which skips would hide a broken first-party import? |
| S4 | Is a new skip noticed by any gate? |
| T1 | Which tests cannot fail, or describe the code they test instead of the thing it reads? |
| T2 | Which tests depend on order or on another process? |
| R1 | Does the full tier pass, and does it fit the hosted job's 30-minute cap? |
| R2 | Can each release gate pass at all? |
| D1 | Do the paths, tests and codes the ADRs and records cite exist? |

## Defects

| ID | Sev | Where | Defect | Fix | Before → after |
|---|---|---|---|---|---|
| TD-01 | major | `quality/sessions/graph.py`, `quality/sessions/interop.py` | The Alloy jar (`graph/formal/TOOLS.lock`) and the PlantUML jar had only a manual `curl` in a docstring. `graph_formal_full` and `interop_plantuml` were NOT_RUN on every machine where nobody had run it by hand, the hosted nightly included (Java is there, the jars are not). `formal_tla` has always fetched its jar | New `quality/tools/pinned_jars.py` downloads each jar once into `.tmp/tools/`, checks its sha256 and never uses a jar that does not match; both sessions call it first. A failed download stays NOT_RUN | `graph_formal_full` skipped ("Alloy jar not found"), `interop_plantuml` skipped → both run and pass (3 min, 19 s); `tests/tools/test_pinned_jars.py` |
| TD-02 | major | `verification/smt/laws.py`, `formal_smt` | The full tier no longer fits the hosted job's `timeout-minutes: 30`. `formal_smt` took 18 minutes, 17.5 of them in the generated-law proof over the 11 packs, one at a time (`building-permit` alone 4 min 10 s, the same before #261). With `coverage`, `conformance_divergence`, `okf_tools` and `formal_tla` the nightly would be cancelled every night | The packs are proved in a process pool (4 by default, about 90 MB each; `EIJA_SERIAL=1` or `EIJA_SMT_WORKERS=N` as for pytest). Reports are written in pack order | 17 min 32 s → 5 min 18 s, reports byte-identical to a serial run; full tier measured below (R1) |
| TD-03 | major | `quality/metrics/aggregate.py` | Since 2026-10-09 the HCI journey writes `inspection_pass` in `reports/hci/trace.json`, and the metrics reader only accepted the three older keys. Every trace a real `nox -s hci` wrote read as UNKNOWN, so `metrics` failed LANE-01 after every full run with Chrome. The test fixture copied the reader's idea of the trace, not the writer's | The reader accepts `inspection_pass` (schema `eija.hci.inspection.v1`) and still refuses any other key. The new test reads the keys `quality.hci.journey.collect` returns from its source, so the two cannot drift again | `reports/hci/trace.json`: UNKNOWN → recognised as the raw trace; `test_the_trace_the_journey_really_writes_is_recognised` fails on `main` |
| TD-04 | major | `quality/mutation/baseline.json` | The release `mutation` gate could never pass: it fails any measured module with no floor, and 5 of its 8 targets had none (`models`, `impact`, `evidence`, `runtime`, `verifier`). Its message named a command that does not exist (`python -m quality.mutation baseline`) | Floors written from full runs (ratchet: they only go up from here). Message names `run --module M --write-baseline`. The low scores are filed as an issue rather than hidden | see "Mutation floors" below |
| TD-05 | major | `quality/sessions/tests.py` | A skipped test inside a green nox session is NOT_RUN that no gate sees. #270's `extras_guard` names a skip only when its reason mentions an extra or came from `importorskip`; TD-06 to TD-08 passed it | New `quality/tools/skip_ledger.py` with `skip_ledger.json`: the `tests` session writes junit and fails on any (file, reason) that skips more often than recorded. Fewer is fine; accepting a new skip is a reviewed `--update` diff. `EIJA_ALLOW_NOT_RUN=1` accepts the gap knowingly | a new skip passed every gate → `NEW SKIP: …` fails the fast tier (`tests/tools/test_skip_ledger.py` replays the z3 case) |
| TD-06 | minor | `pyproject.toml` `dev` | The four build-hook tests in `tests/test_pack_distribution.py` need setuptools; a venv on Python 3.12+ has none, so they ran in no tier | `setuptools==84.2.1` in `dev` | 4 skipped → 4 pass |
| TD-07 | minor | `.github/workflows/quality.yml` | `test_dot_validator_rejects_broken_dot_and_accepts_generated_text` needs pydot (`visual`). No gate environment had it, and `diagrams_syntax` selects only `-m browser` from that file | The hosted jobs and the documented install add `visual` | 1 skipped → 1 pass |
| TD-08 | minor | `pyproject.toml` `graph` | `test_shacl_agrees_with_the_other_engines_on_a_small_graph` needs pyshacl, which no extra installed (#270 relabelled the skip "installed by hand") | `pyshacl==0.40.2` in `graph` (test-time only; deptry DEP001 still says nothing shipped imports it) | 1 skipped → 1 pass (0.2 s) |
| TD-09 | minor | `.github/workflows/quality.yml` | The hosted jobs left out `metrics` (grimp came unpinned through import-linter) and `hci` (`test_axe_is_loaded_with_an_explicit_utf8_read` skipped) | Both added, with `visual` | hosted extras now equal the documented merge-evidence list |
| TD-10 | minor | `tests/test_value_guards.py`, `test_linked_objects.py`, `test_composite_states.py`, `test_time_events.py`, `test_pack.py`, `tests/graph/formal/test_formal_closure.py`, `test_formal_order_and_status.py` | Seven places skipped when a **first-party** module failed to import (`importorskip("verification.scxml.differential")`, `importorskip("eija_studio.domain.impact")`, a `kernel_present` flag). A renamed kernel function or a broken import in the differential would have turned these tests into NOT_RUN | Import the module; skip only on the third-party package (`z3`, `python-statemachine`) | a broken first-party import: skip → failure |
| TD-11 | minor | `tests/test_uml_actor_kinds.py` | Four permanent skips ("this pack has actors that are not people") used `skip` as a domain filter and padded every skip list | Parametrize over the packs in the domain; a new test keeps the domain non-empty and proper | 4 skips → 0 |
| TD-12 | minor | `docs/quality/gates.md` | `adapters/providers.py` (now a package); "`dev` and `lint` are enough for the fast tier"; the merge-evidence install line without `metrics`, `hci`, `visual` | Corrected; the ledger and the jar fetch documented | see the diff |

### Mutation floors

Full (unsampled) runs, cosmic-ray 8.7.0, with the selections #270 set:

| Module | Mutants | Killed | Survived | Score = floor |
|---|---|---|---|---|
| `domain/models.py` | 493 | 291 | 189 | 0.6062 |
| `domain/evidence.py` | 333 | 195 | 127 | 0.6055 |
| `domain/impact.py` | 125 | 88 | 36 | 0.7096 |
| `application/runtime.py` | 225 | 189 | 26 | 0.879 |
| `application/verifier.py` | 92 | 83 | 6 | 0.9325 |

Mutants include the ones accepted as equivalent (excluded from the score). Two runs, 7 and 18 minutes on 2 workers.
A floor is a ratchet, not a target: a module below it now fails, where before every module failed for want of one.
[#271](https://github.com/45ck/eija-studio/issues/271) tracks raising `models.py`, `evidence.py` and `impact.py`.

## Found here and fixed by the integration review (#270)

* `mutation_quick` red on `main`: `LINKED_LIFECYCLE_CONFLICT` (#257) and six runtime refusal codes outside their
  mutation selections (its I2). This pass found the same two survivors and a tripwire for the same thing; it dropped
  its own fix for #270's `tests/test_mutation_selection.py`.
* `property` red on `main` (its I8): seen here as LANE-01 reading `reports/testing/property.json` as FAIL.

## Not defects, or not fixed here

* **Random order.** Three random-order runs (seeds 1234, 7, 99) passed. One run started while `nox -t full` used the same
  checkout had one failure that three later runs did not reproduce; it is recorded, not explained.
* **xdist and `graph`.** Under `-n`, `from graph.formal import …` in a test can resolve to `tests/graph` instead of the
  repository's `graph/` (neither has an `__init__.py`). No committed test does it; this pass's own new test did, and
  reads the file instead.
* **Tests with no assertion.** 19 found; each asserts through a helper (`refused`, `_detect`, `check_laws_against_policy`)
  or is a "does not raise" check by design. The two "`true` and `1` are two guards" tests could also assert the count.
* **`hci`** fails on the two budgets #79 tracks (`klm.pointer_expert_time` 65.31 s against 65; `memory.max_chunks_viewport`
  52 against 27). Owner decision.
* **Skips that stay.** Counted in the ledger (17): the 8 bindings of the unbuilt `eijagraph` package, the TLA and Alloy
  jars before they are fetched (3 and 4), Docker for Bend (1), real-browser checks (3, run by `browser_suite` and
  `diagrams_syntax`) and the offline SARIF schema (1). Routed, not counted (158): the property suite (run by `property`)
  and the opt-in HCI browser tests (run by `hci`); their reasons name the session, so a new property test needs no
  ledger change.
* **Docs.** Every path, test id and error code cited in backticks in ADR-0228 to ADR-0254, the inspection records,
  `docs/quality/*.md`, the README, roadmap, CONTRIBUTING and CHANGELOG resolves, except TD-12's stale path.

## R1: the full tier

`nox -t full` on this branch, 4 cores, every hosted extra, the jars fetched by the sessions themselves, Chrome
present, no Docker: **43 min 2 s** wall clock; 41 sessions passed, 2 failed, 1 NOT_RUN.

* The two failures are the #79 budgets, not this pass: `hci` fails `memory.max_chunks_viewport` (52 against 27), and
  `metrics` fails LANE-01 because the HCI lane report says FAIL. Before TD-03 LANE-01 failed here too, but for an
  UNKNOWN trace; now it names the real failing lane.
* NOT_RUN: `formal_bend_quick` (no Docker daemon).
* Long poles: `conformance_divergence` 8 min, `okf_tools` 8, `formal_smt` 6 (18 before TD-02), `formal_tla` 6,
  `coverage` 5, `property` 2, `mutation_quick` 2. The rest take under a minute each.
* The hosted job's `timeout-minutes: 30` (its comment said "~13 min", measured on 31 October before the 11 to 14
  November gates) would cancel every nightly even with TD-02. It is now 60, with the measured time in the comment.
  Running sessions in parallel is the next step and is left for #206's long-pole item.
