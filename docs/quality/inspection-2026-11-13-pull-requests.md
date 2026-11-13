# Inspection of open pull requests and recent merges, 13 November 2026

A Fagan-style inspection: each work product was read against its stated intent, its ADR and its tests, and every
defect is logged with a severity and a location. Severity: **major** changes behaviour a user or client can see;
**minor** is wording, naming or a doc slip.

## What was inspected

| Work product | Result |
|---|---|
| Open pull requests | None were open on 13 November 2026. |
| Remote branches not merged into `main` | One: `pr-media`. It is an orphan branch that only hosts PR GIFs for `demos/prgif` (`docs/engineering/PR-STANDARD.md`), so it is not unlanded work. The other 26 remote branches are all ancestors of `main`. A shallow clone shows them as unmerged with no merge base; fetch the full history before deciding a branch is stale. |
| Codex review threads on PRs #232 to #248 (16 threads) | All 16 are resolved, and each fix commit has a regression test. Codex did not re-review the fix commits, so they were read here. |
| The fix commits for those threads, and the code they touch | One major defect, D1 below. |

## Defect log

| ID | Severity | Location | Defect | Status |
|---|---|---|---|---|
| D1 | major | `src/eija_studio/resources/appgen/server.py.tmpl`, `POST /api/records/{id}/act` | Codex found on #246 that `/api/signals` defaulted a missing operation id to the shared id `missing` and cut a long one to 100 characters. That was fixed for signals only. The action route still did both. In a built app, a client that sent no operation id got its first action through, and every later action on any other record came back `409 OPERATION_CONFLICT`. Two different 101-character ids that shared their first 100 characters also collided. Reproduced on a built library-loan app. | Fixed: both routes now share `_operation`, which requires a string of 1 to 100 characters and never defaults it or cuts it short. Regression: `tests/test_appgen.py::test_an_action_needs_its_own_operation_id`, which fails on the old template. |
| D2 | minor | `src/eija_studio/resources/web/play-systems.js` (recovery message) | When a second unreadable draft is set aside it goes to `draft.unreadable-2.json`, but the chat message always names `draft.unreadable.json`. | Logged only. The message says the draft was set "beside it", so nothing is lost. |

## Checked and found correct

- #232 time events: ghost diff of `after`, and re-recording that keeps each step's wait.
- #234 set-aside drafts: numbered backups on disk and in browser storage.
- #237 access witnesses: solved per attribute, with choices limited to the declared ones.
- #238 mutation `--resume` fingerprint: covers nested tests.
- #239 composite states: one identifier map, and hoisting that keeps effect order.
- #245 linked objects: object states carried through the law proof, one object per class per transition, and differential moves taken from start states.
- #246 signals: the delivery binding includes the record's values, and the register row exists.
- #247 conformance: LF bytes on write, and a journey that starts with zero elapsed time.

ADR numbers 0230 to 0243 each appear once in `docs/adr`, and the code cites the renumbered ADRs correctly. #232's time
events were first written as ADR-0236 and now cite ADR-0237.
