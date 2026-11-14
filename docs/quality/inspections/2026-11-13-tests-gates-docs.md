---
description: "Fagan inspection, 13 November 2026, of the things meant to catch defects (tests, nox gates, hosted CI) and of the claims the docs make about the product."
---

# Inspection: tests, gates and docs (13 November 2026)

One of ten inspections run on 13 November 2026. This one covers what is supposed to catch defects, and what the docs
claim. Product code belongs to the other inspections; product defects found here are listed at the end and passed on.

## Scope and method

* **Material:** `noxfile.py`, `quality/sessions/*.py`, `quality/tools/*.py`, `.github/workflows/*.yml`, the pytest
  configuration in `pyproject.toml`, the skip and xfail reasons of a full fast-tier run, `README.md`, `docs/ROADMAP.md`,
  `docs/sector-packs.md`, `docs/getting-started.md`, `docs/quality/gates.md`, ADR-0228 and ADR-0243.
* **Baseline:** `main` at 22298bc. `nox -t fast` green: 25 sessions, 3,563 passed, 220 skipped, 2 xfailed.
* **Method:** one reader with the checklist below. Each claim was checked by running something (a command, a test
  collection, a build), not by reading. Severity: **major** means a gate or a doc can report something false about the
  product; **minor** means it is wrong or weak but cannot hide a defect on its own.

### Checklist

| # | Question |
|---|---|
| G1 | Does every test run in some tier? Are marker descriptions true? |
| G2 | Can a gate pass because nothing ran (skips, missing extras, `session.skip()` exiting 0)? |
| G3 | Does the hosted workflow run the same gates a local run does? |
| G4 | Are thresholds at the ratchet floor the docs promise? |
| T1 | Which tests are skipped or xfailed for a reason that is no longer true? |
| T2 | Which tests cannot fail, or would go quiet when the code they guard arrives? |
| T3 | Which doc claims about tests are not pinned by a test? |
| D1 | Do the README, roadmap and guides call shipped features planned, or planned features shipped? |
| D2 | Do the documented commands and numbers match what the code does today? |
| D3 | Do ADRs describe the gates as they are? |

## Defects

| ID | Sev | Where | Defect | Fix | Before → after |
|---|---|---|---|---|---|
| TG-01 | major | `pyproject.toml` markers, `quality/sessions/` | No tier selected the `slow` or `browser` tests outside `tests/metrics` and `tests/test_syntax_validator.py`: 116 tests in 31 files (PlayIDE browser walks, the exact-app journey, 26 seeded conformance divergences). The marker text said `nox -s metrics` and `diagrams_syntax` ran them | New release session `browser_suite` (`quality/sessions/browser.py`); fails with NOT_RUN without Playwright; marker text corrected | `pytest --collect-only -m "slow or browser"` selected by 0 sessions → `nox -s browser_suite` runs them serially: 122 pass on `main` with #256 (the #225 placement fix) merged |
| TG-02 | major | `.github/workflows/quality.yml` | Hosted jobs installed fewer extras than a local run, and read only nox's exit code. nox exits 0 for `session.skip()`, so missing `smt`, `mutation`, `graph`, `graph-formal` turned the full-tier `formal_smt` and `mutation_quick` sessions and seven fast-tier graph tests into silent NOT_RUN | Both jobs install `graph,graph-formal,okf,interop-api,smt,mutation`; both write `nox --report`; new `quality/tools/nox_report.py` fails the fast job on any skipped session and lists NOT_RUN sessions in the nightly summary | CI extras, fast tier: 7 tests NOT_RUN (rfc8785, networkx, clingo), exit 0 → same extras as local, report check fails on any skip (`tests/tools/test_nox_report.py`) |
| TG-03 | major | `pyproject.toml` `fail_under` | Coverage floor 78 against a measured 93.78 %: the ratchet rule ("raise it whenever coverage rises") was not applied for six weeks, so a 15-point drop passed | `fail_under = 93` | floor 78 → 93 (`nox -s coverage`: 93.78 %) |
| TG-04 | minor | `graph/bench/metamodel_dogfood.py`, `graph/bench/consistency_checks.py` | Three tests looked for an `okf` sibling worktree from the lane era and skipped forever; the okf lane has been in this repository since then | Look in this repository first, sibling worktree second | 3 skipped (`okf worktree not found`) → 3 pass |
| TG-05 | minor | `tests/graph/formal/test_formal_tools_and_drift.py` | A binding whose target function is missing skipped. Once `eijagraph` exists, a renamed function would silently skip its law suite | Skip only while the whole package is absent; a missing function in an existing package fails | same 8 NOT_RUN today, with a reason that says why; a broken binding can no longer skip |
| TG-06 | minor | `tests/graph/formal/test_formal_hash_methods.py` | A strict xfail from 2026-09-29 said a lone surrogate "aborts a link check". It does not: `UnicodeEncodeError` is a `ValueError`, which every okf caller catches (`BROKEN_RESOURCE`), and the weave index falls back to a labelled digest | Replaced with a test of the real contract (typed refusal, caught by every caller) | 1 xfailed → 1 passed |
| TG-07 | minor | `tests/test_pack.py` | The schema test validated 2 of 11 packs | Parametrized over every `packs/*/pack.json` | 1 test, 2 packs → 11 tests |
| TG-08 | minor | `tests/test_sector_packs.py` | The guide said the test pinned conformance and Simulate; it pinned neither, nor the counts in the guide | Added a Simulate test per pack and a test that reads the guide's counts | new count test failed on the old guide (`'12 to 15 laws' not in guide`) → passes |
| DC-01 | major | `docs/sector-packs.md` | "11 to 14 laws" (12 to 15); "1,135 to 2,216 cases" (1,217 to 2,344); the gap table listed four kernel features as missing that shipped 11 and 12 November; "until the kernel has timers" | Counts corrected and pinned (TG-08); a status column on the gap table; timers sentence corrected | see TG-08; `eija build` on each pack: 1,408 / 1,697 / 1,697 / 1,217 / 2,344 cases |
| DC-02 | major | `README.md` "What you can do", "How close is it?" | Value guards called "planned"; relationships and signals "not implemented"; chat "an offline phrase reader" with no opt-in live mode; "value-driven actions remain unfinished" | Rows and sentence say what shipped (ADR-0230, 0234, 0235, 0242) and what is still next | see the diff |
| DC-03 | minor | `docs/ROADMAP.md` "What exists" | Same staleness in two rows | Rows updated | see the diff |
| DC-04 | minor | `docs/getting-started.md` | "three interchangeable proposal providers" (eight: `eija propose --help`); "There is no MCP server" (`eija mcp`) | Corrected | see the diff |
| DC-05 | minor | `docs/quality/gates.md` | `tests` listed as fast and full (fast only); no row for the new session or the report check | Corrected and added | see the diff |
| DC-06 | minor | ADR-0228, ADR-0243 | ADR-0228 said browser tests ran in the full tier; ADR-0243 said the fast tier ran every once-missed divergence (they are `slow`) | Amendment section on ADR-0228; ADR-0243 sentence corrected | see the diff |
| DC-07 | minor | `.github/workflows/test.yml` | Comment said hosted CI was unavailable (ADR-0017), superseded by ADR-0228 | Fixed on `main` by a parallel inspection while this one ran; its wording kept | stale comment → corrected on `main` |

## Product defects passed on

* **#225 (fixed by #256):** `test_play_place::test_a_state_lands_where_you_put_it_and_stays_there_in_a_real_browser` and
  `test_play_drop_place::test_a_state_lands_under_the_pointer_and_nothing_else_moves` failed on `main` (the plan banner
  pushed the canvas down 58 px). Passed to the diagram-editing inspection rather than deselected; its fix merged in #256,
  and `browser_suite` is green on top of it.
* **Parallel browsers:** under `-n 4`, `test_play_place::test_pick_then_click_double_click_and_edit_inline_in_a_real_browser`
  timed out (it passes alone). `browser_suite` therefore runs serially, one browser at a time, as CONTRIBUTING.md asks.

## Not defects

* `okf/adrs/0203-describe-…` and `okf/adrs/0237-conformance-…` look like duplicate ADR numbers, but they are pages for
  renumbered ADRs that the OKF generator keeps on purpose with `status: deprecated`.
* The `eijagraph` binding tests (TG-05) stay NOT_RUN: the package is planned, not built.
* `.gitattributes` exists but is `* -text`; #55 (LF normalisation) is still open, as #221 says.
