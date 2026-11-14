# Inspection: saving, undo and UML import/export (2026-11-13)

A Fagan-style inspection of everything in PlayIDE that keeps or moves a model. The hardening pass of 2026-11-12
([HOSTILE-INPUT](HOSTILE-INPUT.md)) fuzzed these paths for crashes. This one read them line by line for logic defects
that a fuzzer does not find. Decision record: [ADR-0245](../adr/0245-partial-reads-keep-and-saves-name-their-system.md).

## Scope

| Area | Code read |
|---|---|
| Undo, redo, browser autosave | `resources/web/play.js` (`commit`, `undo`, `redo`, `restore`, `persist`, `recover`, `draft`, `restoreDraft`) |
| Save, open, new system, recent | `interfaces/play_systems.py`, `adapters/system_library.py`, `resources/web/play-systems.js`, `application/new_system.py` |
| UML import and export | `application/interop/*` (readers, `mapping.py`, `several.py`, `start.py`), `interfaces/play_interop.py`, `interfaces/uml_interop.py`, `resources/web/play-interop.js` |

## Checklist

1. Data loss: can a step lose work that was saved, kept or drawn?
2. Round trip: does export then import give the same model, for every shipped pack and the kernel-feature fixture?
3. Partial writes: is every file write whole and atomic?
4. Undo stack: can an edit be missing from the history, or a restore be recorded as an edit?
5. Races: can an autosave, a save or a second tab act on the wrong document?
6. Silent drops on import: is every element of the file either read, kept or listed with a reason, and does a partial
   read remove nothing (issue #165)?
7. Protected files: does anything write law or test files without the person asking?

Items 2, 3 and 7 found nothing. All ten defects are fixed. Every shipped pack, and the fixture with every kernel feature
(`tests/test_play_kernel_features.py::kernel_loan`), round-trips CLEAN in all four formats. `draft.json`,
`recent.json` and new systems are written beside and renamed. Save writes only `draft.json` in the workspace; the tests
draft it holds is the Tests tab's draft, never `scenarios.json`.

## Defect log

| # | Severity | Where | Defect | Status |
|---|---|---|---|---|
| D1 | Major | `interop/mapping.py` `_partial`; `interop/textual.py`, `plantuml.py`, `mermaid.py`, `xmi_reader.py`, `drawio_reader.py` | An arrow the reader skipped (`-left[#red]->`, `<--`, `->>`), an XMI transition to a non-state, a labelled draw.io connector to another shape, or an extra XMI region did not count as unread, so the import planned `remove_transition` for a transition the file still draws (the dialog says it removes nothing). | Fixed |
| D2 | Major | `interop/mapping.py` `import_class_model` | An attribute the file has but PlayIDE cannot read (class-typed, collection) and an association with an unsupported end were deleted from the candidate `data.json`, which the dialog and `eija uml import --out-dir` offer. | Fixed: kept as the current model has it |
| D3 | Minor | `interop/mapping.py` `_changes`; `play-interop.js` | The class model changes ignored associations and the record class, so the dialog said "Classes reordered" (or nothing) when an association was added or dropped. | Fixed |
| D4 | Major | `interfaces/play_systems.py` `play_save_draft`, `play_clear_draft` | With two tabs, opening another system in one left the other tab on the old system; its Save wrote its work over the new system's `draft.json`, and Clear cleared it. | Fixed: `SYSTEM_CHANGED` |
| D5 | Major | `play.js` `recover` | A browser draft written on an earlier model was said to be "retained", but the first edit (or reopening the saved draft) wrote under the same key, so it was gone after a reload. | Fixed: kept under `:earlier` |
| D6 | Minor | `play-systems.js` `reopen` | When browser work was recovered, the saved-draft baseline left out each step's `round` and `request`, so identical work showed "Unsaved changes" and asked before leaving. | Fixed |
| D7 | Minor | `play.js` `restore` | Undo or redo that reset edited screens awaited the server with `restoring` still set, so an edit made in that wait was applied but not recorded in the history or the browser draft. | Fixed |
| D8 | Major | `interop/plantuml.py`, `mermaid.py` (pseudostate declarations), `interop/model.py` | A `<<choice>>` pseudostate became a real state once an arrow used it; the plan added the state and retargeted a transition to it, while the report said pseudostates are not imported. | Fixed: `Parsed.settle` |
| D9 | Minor | `interop/mapping.py`, `start.py`, the readers | Reasons said value guards and composite states "are planned (issue #93)"; both shipped (ADR-0234, ADR-0240) and #93 is closed. | Fixed |
| D10 | Minor | `play.js` `persist` | When storage could not hold even the current snapshot, the previous browser draft stayed under the key, so a reload brought that older work back as "your unsaved work". | Fixed: moved aside as an earlier draft, offered with Reopen |

Not defects, noted for later: the systems controls cache one studio per system for the life of the server; a template
copy of `eija-review-slice` leaves its `requirements.json` behind (its bindings are this repository's own); and a
pre-existing flaky browser test, `test_undo_redo_and_recovery_after_a_reload_in_a_real_browser`, fails about one run in
five when the whole file runs, on main as well.

## Regression tests

Every defect has a test that fails on main and passes with the fix (19 failed on main before the fix, then 0).

* `tests/test_save_import_inspection.py` (fast): D1, D2, D3, D4, D8, D9.
* `tests/test_play_history.py` (browser, opt-in): D5 `test_a_draft_kept_on_an_earlier_model_is_not_overwritten_by_the_next_edit`,
  D6 `test_recovered_work_that_matches_the_saved_draft_is_not_unsaved`, D7 `test_an_edit_made_while_undo_reloads_the_screens_is_kept`,
  D10 `test_an_outdated_browser_draft_is_not_recovered_as_the_latest_work_when_storage_is_full`.
* `tests/test_uml_interop.py`: the class model changes now include associations.

Before and after screenshots of each visible defect are in [`docs/demos/assets/inspection-save-import-20261113`](../demos/assets/inspection-save-import-20261113/).

Run the browser tests with `EIJA_BROWSER_TESTS=1 EIJA_CHROMIUM=<chromium> pytest tests/test_play_history.py -m "slow or not slow"`.

## Second pass (2026-11-14)

Decision record: [ADR-0253](../adr/0253-imports-match-names-and-tabs-keep-each-others-work.md). This pass went where the
first did not. It round-tripped every shipped pack in all four formats with the kernel features the packs use
(refund-desk's composite states and time event, ai-ops's linked object, library-fines's signal). Then it edited the
exported files as a person would, gave names and text a format writes differently, put two tabs on one system, and
read the folder lookup behind every file beside `pack.json`.

Unchanged files of every pack still come back CLEAN. Today's `UNDECLARED_ROLE` needs nothing from interchange: an
import already reports a role the pack does not declare as not imported, and never plans it.

| # | Severity | Where | Defect | Status |
|---|---|---|---|---|
| D11 | Major | `interop/mapping.py` `import_state_machine` | A state renamed in a file was planned as add, retarget and remove. It left its composite state, and the removal of a composite's initial state was refused, leaving the old state behind. | Fixed: `rename_state` when exactly one pair carries the same arrows (`interop/names.py`) |
| D12 | Major | `interop/plantuml.py` `_text`, `_alias` | PlantUML wrote `"` as `'`, so the import renamed the state; a state named `state` came back as a state named `-->`; a literal starting with `'` was read as a comment and lost. | Fixed: `<U+XXXX>` escapes, keywords by alias |
| D13 | Minor | every reader; `interop/mapping.py` | A name, description or literal with a tab, two spaces or a trailing space came back as a change (a state removed and re-added). | Fixed: matched and kept but for spacing |
| D14 | Major | `interop/mermaid.py`, `mapping.py` `import_class_model` | Mermaid's export says it does not carry attribute descriptions; its import of that same file deleted them from the candidate `data.json`. | Fixed: kept, listed under "Kept or filled in" |
| D15 | Major | `interfaces/play_systems.py` `play_save_draft`, `play_clear_draft` | Two tabs on one system: each Save replaced the other's `draft.json` unseen; the check and the write could also straddle a switch of system. | Fixed: `revision` and `DRAFT_CHANGED`, under the systems lock |
| D16 | Major | `play.js` `persist` | Two tabs on one system shared one browser key: the tab that wrote last replaced the other's kept work, and a tab undone to nothing deleted it. | Fixed: drafts name their tab; the other tab's work is kept under `:earlier:tab-<id>` |
| D17 | Major | `domain/pack.py` `load_pack`; `play_systems.templates`, `play.py` siblings | Opening the systems dialog read every shipped pack, which filed a matching snapshot under the shipped folder: a copy of a shipped pack with its own class model then read the shipped `data.json` (and screens, tests). | Fixed: `load_pack(..., claim=False)` for a look at a pack |

Noted, not changed: scenario steps accept only identifier-like state names (`^[A-Za-z][A-Za-z0-9_:-]{0,59}$`) while a
state may be named freely, so a state named `On loan` cannot be expected in a test. That is a kernel contract, passed to
the kernel owners.

Regression tests: `tests/test_save_import_second_pass.py` (D11 to D15, D17; 34 of its 44 tests fail on main, all pass here) and
`tests/test_play_history.py::test_two_tabs_on_one_system_keep_each_others_work` (D15 and D16 in a real browser).
Before and after screenshots are in [`docs/demos/assets/inspection-save-import-20261114`](../demos/assets/inspection-save-import-20261114/).
