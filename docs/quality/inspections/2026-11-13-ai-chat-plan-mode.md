# Fagan inspection: AI chat, plan mode and the proposer (2026-11-13)

* Scope: the PlayIDE chat in plan mode (ADR-0156, ADR-0201), the offline and opt-in live plan proposers (ADR-0230),
  the OpenAI provider and the shared provider plumbing (ADR-0229), `plan_check` for agents, plan preview, accept and
  reject, owner selection of a plan (`/api/cases/from-plan`), "Describe your app" and "Update the tests" (ADR-0216),
  and the read-only review view (ADR-0172).
* Material read line by line: `adapters/live_plan_proposals.py`, `adapters/plan_proposals.py`,
  `adapters/providers/{_common,_http,openai_api,registry}.py`, `application/plan.py`, `application/owner_plan.py`,
  `application/describe_system.py`, `application/service_views.py` (`plan_check`), `interfaces/play.py` (plan routes),
  `interfaces/mcp_server.py` (`plan_check`), and the chat half of `resources/web/play.js`.
* Method: Fagan-style. Each item of the checklist below was traced through the code, each suspected defect was
  reproduced with a script or a test before it was logged, and each fixed defect has a regression test that fails on
  the code before the fix.

## Checklist

| Item | Result |
| --- | --- |
| A plan applied without passing checks | Pass. `from_plan` re-applies the exact steps through the policy and refuses `CANDIDATE_CHANGED` unless the reviewed candidate hash is reproduced. |
| Partial apply | Pass. The accepted steps are applied as one change (`apply_transactions`); a step that does not apply blocks the whole preview. |
| Reject not restoring state | Pass. Preview is never persisted; leaving it redraws the model in force; unticking re-runs the server preview. |
| Provider errors and timeouts | Pass. One bounded attempt, no redirect, capped body; failures map to stable codes without the response body. |
| Key handling and leakage | Pass. Keys come from the environment or memory, travel only in a header, are never stored or echoed; `store: false`. |
| Live mode switching on without opt-in | Pass. Live needs a networked provider, `--allow-network` and a strict boolean `consent`; the box unticks after each send. |
| Preview differing from what was asked | **Fail**, defect 1. |
| One provider call at a time | **Fail**, defect 2. |
| Plan size bounds hold across rounds | **Fail**, defect 3. |
| Provenance shown is true for every step | **Fail**, defect 4. |
| Review view cannot change the model | Pass. The chat is closed and its commands are filtered out in `?view=review`. |

## Defects

Severity: Major (wrong result a person may act on), Minor (wrong but visible or recoverable), Trivial.

| # | Severity | Where | Defect | Status |
| --- | --- | --- | --- | --- |
| 1 | Major | `adapters/live_plan_proposals.py`, `propose` | A live request that mixes exact phrases with prose ("add state Archived after Approved then let a supervisor take over...") was sent whole to the model, which plans one meaning, so the exact clause was silently dropped from the plan. The offline reader is careful never to drop a clause it read. | Fixed: refused before anything is sent, `PLAN_REQUEST_MIXED`. |
| 2 | Minor | `adapters/live_plan_proposals.py` | The chat's live path had no single-flight guard, unlike `Studio.propose` (`PROVIDER_BUSY`), so two tabs or a double send could make two billed calls. | Fixed: one live call at a time; a second is refused and never sent. |
| 3 | Minor | `interfaces/play.py` `play_plan`; `resources/web/play.js` `addRound`, `addStep` | Rounds on a system you started stack without a bound. A round that takes the plan past `MAX_DRAFT_STEPS` (64) was planned and added, and every preview after it failed validation, leaving a plan that can no longer be checked. | Fixed: the server refuses `PLAN_TOO_LONG`; the page also counts rejected steps, which the server cannot see. |
| 4 | Minor | `resources/web/play.js` `addRound`, `planCard` | The plan card's provenance line took the latest round's provider for the whole plan, so steps a live model wrote were labelled "offline fixture, not a live model" after an offline round, and the reverse. | Fixed: each AI step keeps its provider; the card names every one and says when the plan is mixed. |
| 5 | Minor | `adapters/live_plan_proposals.py` | A request shaped like an exact phrase but with a wrong name ("add state Archived after Nowhere") falls through to the live provider (with consent) and comes back as an unrelated meaning instead of the phrase reader's "no state Nowhere". | Logged. Refusing it would also block paraphrases that happen to match a phrase shape ("let supervisors approve"); needs a product call. |
| 6 | Minor | `interfaces/play.py`, live plan path | A live chat call leaves no audit event. `Studio.propose` records `ProviderCallStarted` and `ProviderCallNotAccepted` (request hash, billing UNKNOWN); the chat's live calls are invisible in observations. | Logged. |
| 7 | Minor | `application/service_views.py` `plan_check` | `plan_check` always previews as a shipped pack (`grows=False`), so on a system you started a plan naming a new action or role is refused although the chat accepts it. | Logged. |
| 8 | Minor | `application/describe_system.py` `update_tests` | A failing refusal test ("Customer cannot Start") is dropped, not recorded again, because only end-state journeys are re-recorded. It is listed as "removed", but the behaviour change it caught loses its test. | Logged. |
| 9 | Trivial | `application/describe_system.py` `_slug` | Two end states whose names differ only in underscores (`Paid_Out`, `Paid__Out`) slug to the same test id, and the description is refused. | Logged. |

## Regression tests

* `tests/test_live_plan.py::test_a_request_that_is_partly_exact_phrases_is_refused_before_anything_is_sent`
* `tests/test_live_plan.py::test_a_second_live_request_while_one_runs_is_refused_and_never_sent`
* `tests/test_play_greenfield.py::test_a_round_that_would_take_the_plan_past_one_preview_is_refused`

All three fail on `main` before the fix and pass after. Defect 4 was checked in Chromium (the card's provenance line)
and by the chat browser tests in `test_play_diff.py`, `test_play_history.py` and `test_play_game.py`.
