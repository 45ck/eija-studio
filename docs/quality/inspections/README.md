---
description: "Every inspection record in one list: what each one covered, where its log lives, the pull request and ADR that fixed it, and what it left open."
---

# Inspections

Start here to find an inspection record. The records stay where their threads wrote them, because ADRs, the OKF
pages and the CHANGELOG link to those paths. New records go in this folder, named `YYYY-MM-DD-<area>.md`, with images in
`assets/YYYY-MM-DD-<area>/`, and get a row below.

## 13 November 2026: ten Fagan inspections

Ten areas were inspected in parallel and fixed under auto-merge (PRs #250 to #261). Each record lists its checklist,
every defect with severity and location, and the regression tests that keep it fixed.

| Area | Record | Defects | Fixed in | Decision record |
|---|---|---|---|---|
| The `eija` command and local server | [CLI-SERVER-INSPECTION.md](../../engineering/CLI-SERVER-INSPECTION.md) | 10 (D1-D10) | #250; D10 in #260 | [ADR-0244](../../adr/0244-built-app-environment-and-bind-before-links.md) |
| Running and checking a design in place | [2026-11-13-INSPECTION-CHECK-IN-PLACE.md](../../engineering/2026-11-13-INSPECTION-CHECK-IN-PLACE.md) | 11 (D-01 to D-11) | #251 | none |
| Open pull requests and recent merges | [inspection-2026-11-13-pull-requests.md](../inspection-2026-11-13-pull-requests.md) | 2 (D1, D2) | #252, #254 | none |
| AI chat, plan mode and the proposer | [2026-11-13-ai-chat-plan-mode.md](2026-11-13-ai-chat-plan-mode.md) | 9, one withdrawn | #253 | [ADR-0230](../../adr/0230-opt-in-live-plan-mode-and-agent-plan-check.md) amendment |
| Saving, undo and UML import/export | [INSPECTION-SAVE-IMPORT.md](../../engineering/INSPECTION-SAVE-IMPORT.md) | 10 (D1-D10) | #255 | [ADR-0245](../../adr/0245-partial-reads-keep-and-saves-name-their-system.md) |
| Drawing and editing diagrams | [hci/inspection-2026-11-13](../../hci/inspection-2026-11-13/README.md) | 8 (D1-D8) | #256 | none |
| Pull requests merged since 11 November (#217-#252) | [inspection-2026-11-13-merged-prs.md](../inspection-2026-11-13-merged-prs.md) | 5 (M1-M5) | #257 | none |
| The kernel | [inspection-2026-11-13-kernel.md](../inspection-2026-11-13-kernel.md) | 8 (K1-K8) | #258, #261 | [ADR-0246](../../adr/0246-kernel-inspection-fixes.md) |
| Tests, gates, hosted CI and doc claims | [2026-11-13-tests-gates-docs.md](2026-11-13-tests-gates-docs.md) | 15 | #259 | none |
| The app generator | [inspection-2026-11-13-app-generator.md](../inspection-2026-11-13-app-generator.md) | 10 (G1-G10) | #260 | [ADR-0249](../../adr/0249-app-generator-inspection-fixes.md) |

ADR numbers 0247 and 0248 were left free by the app-generator thread for others that day; neither was used.

Before and after screenshots: `docs/assets/inspection-2026-11-13/` (check in place), `docs/hci/inspection-2026-11-13/`
(diagram editing), `docs/demos/assets/inspection-save-import-20261113/` (save and import),
`docs/quality/inspection-2026-11-13-app-generator/` (app generator) and `assets/2026-11-13-ai-chat/` (AI chat).

### Still open after the day

These were logged and deliberately not changed. Each record gives the reasoning.

* Kernel: the law proof checks separation of duties only where one listed action directly follows another; the
  kernel itself checks the whole history. `[x = 1]` and `[x = 1.0]` hash differently, so two transitions of one action
  written that way are refused as unalike.
* Command line: `eija lint` uses exit 2 for both NOT_RUN and a command error.
* Diagram editing: a class diagram wider than the canvas at the readable scale pans rather than shrinking below 0.8.
* Tests and gates: `.gitattributes` for LF line endings is still issue #55.

## 14 November 2026: second passes

Each area thread inspected its area again, deeper, and one thread reviewed #250-#261 PR by PR. Records as they merged:

| Area | Record | Fixed in | Decision record |
|---|---|---|---|
| AI chat, start flow and review view | [2026-11-14-ai-chat-deeper.md](2026-11-14-ai-chat-deeper.md) | #262 | ADR-0156, ADR-0216 amendments |
| The day's inspection PRs, one by one (N1-N3) | [inspection-2026-11-14-todays-prs.md](../inspection-2026-11-14-todays-prs.md) | #263 | [ADR-0246](../../adr/0246-kernel-inspection-fixes.md) amendment |
| The app generator | [inspection-2026-11-14-app-generator-pass-2.md](../inspection-2026-11-14-app-generator-pass-2.md) | #264 | [ADR-0254](../../adr/0254-app-generator-second-pass.md) |
| Running and checking a design in place | [2026-11-14-INSPECTION-CHECK-IN-PLACE-2.md](../../engineering/2026-11-14-INSPECTION-CHECK-IN-PLACE-2.md) | #265 | none |
| Saving and UML import | [INSPECTION-SAVE-IMPORT.md, second pass](../../engineering/INSPECTION-SAVE-IMPORT.md#second-pass-2026-11-14) | #266 | [ADR-0253](../../adr/0253-imports-match-names-and-tabs-keep-each-others-work.md) |
| The kernel | [inspection-2026-11-14-kernel.md](../inspection-2026-11-14-kernel.md) | #267 | [ADR-0250](../../adr/0250-kernel-second-inspection.md) |
| The `eija` command and local server | [CLI-SERVER-INSPECTION.md, second pass](../../engineering/CLI-SERVER-INSPECTION.md#second-pass-14-november-2026) | #268 | [ADR-0251](../../adr/0251-server-boundaries-second-inspection.md) |
| Drawing and editing diagrams (E1-E9) | [hci/inspection-2026-11-14](../../hci/inspection-2026-11-14/README.md) | #269 | none |

ADR-0252 was not used.

## 14 November 2026: integration review

[2026-11-14-integration-review.md](2026-11-14-integration-review.md) reviews `main` after #250-#261 as one change: every
tier run with every extra installed, the places where two of the day's fixes meet, and fixes whose cause is structural.
