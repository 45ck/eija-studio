# Generality audit: domain knowledge hardcoded outside a domain pack

The kernel is meant to work for any domain. This audit measures how far `main` is from that. The fix is designed in
[ADR-0153](../adr/0153-domain-agnostic-kernel.md).

| | |
|---|---|
| Commit audited | `origin/main` at `8712d6c` (2026-09-29) |
| In-flight lanes sampled | `lane/tla` (#22), `lane/property` (#24), read with `git show`; not merged, counted separately |
| Unit of count | **matching lines** (`rg -c`), not occurrences. A line with three domain terms counts once. |
| Excluded | `src/eija_studio/resources/web/vendor/**` (Mermaid bundle), `.tmp/` |
| Kind of result | MEASUREMENT for the counts; the classes are a judgement, with the rule below |

## 1. The reference domain's vocabulary

The vocabulary comes from the executable model (`src/eija_studio/domain/policy.py`, `examples/*.json`), not from guesses.

| Kind | Terms | Source |
|---|---|---|
| Workflow id | `excursion` | `domain/models.py:59` |
| States | `Draft`, `Submitted`, `Recommended`, `Approved`, `Rejected` | `domain/policy.py:32-38`, `:46` |
| Actions | `Submit`, `Recommend`, `Approve`, `Reject`, `Revise` | `domain/policy.py:7-13` |
| Roles | `Teacher`, `Registrar`, `Viewer` (fixture only) | `domain/policy.py:32-38`, `adapters/sqlite_store.py:22-25` |
| Effects | `Audit:ExcursionSubmitted` and four more `Audit:Excursion*`, `Notification:RegistrarQueued` | `domain/policy.py:7-13` |
| Forbidden effects | `PaymentCaptured`, `ParentDataExported` | `domain/policy.py:6` |
| Meanings | `recommend_only`, `final_approval`, `confirm_only` | `domain/models.py:89`, `domain/policy.py:14-23` |
| Change operations | `enable_recommendation`, `set_rejection_source`, `rejection_source` | `domain/models.py:113-114` |
| Actor fixtures | `teacher-assigned`, `teacher-unassigned`, `teacher-revoked`, `registrar`, `viewer` | `adapters/sqlite_store.py:22-25` |
| Request text | "Let teachers sign off excursions." | `interfaces/cli.py:202`, `resources/web/index.html:9` |

The search pattern is case-sensitive for identifiers, so the kernel's own words are not counted: the capability `approve`, the Change Case stages `DRAFT` and `APPROVED`, and the outcome `rejected`. The pattern is in [section 9](#9-reproduce).

## 2. Classes

| Class | Meaning | Rule used to assign it |
|---|---|---|
| **(a) fixture** | Legitimately domain data: examples, goldens, evidence snapshots, generated outputs, tests and docs of the reference domain | Everything under `examples/`, `tests/`, `docs/`, `evidence/`, generated `verification/**/*.json` and `verification/bend/main.bend`, and the root docs |
| **(b) leak** | Generic code holds a domain literal that could be **read from the pack** with no new abstraction: labels, prompts, seeds, demo text, defaults | `src/`, `quality/`, `demos/`, `scripts/`, and `domain/policy.py:1-38` (the pack's data living in the kernel package) |
| **(c) structural** | Code or schema **assumes this workflow's shape**. Fixing it needs something the schema cannot express today (authority laws, meanings, actor attributes) or a generator | `domain/models.py`, `domain/policy.py:39-111`, `domain/evidence.py`, `application/verifier.py`, `contracts/*.json`, hand-written formal code in `verification/` |

## 3. Counts

| Class | Lines | Files |
|---|---:|---:|
| (a) fixture | 3,005 | 91 |
| (b) leak into generic code | **136** | 21 |
| (c) structural assumption | **356** | 25 |
| Total | 3,497 | 136 (`domain/policy.py` is in both (b) and (c)) |

Lines of (b) and (c) inside the shipped package `src/eija_studio`: **99 lines in 15 files** (54 b, 45 c).

**Indirect coupling.** The search above cannot see this: 16 modules outside `domain/policy.py` import the excursion policy (`eija_studio.domain.policy`). Eight are in `src/` (`runtime`, `service`, `compiler`, `diagrams`, `diagram_catalog`, `cli`, `mcp_server`, `sqlite_store`), seven in `verification/` and one in `scripts/`. Three more files load `examples/excursion-*.json` or `examples/unsafe-teacher-final-approval.json` by path.

### By area

| Area | (a) | (b) | (c) |
|---|---:|---:|---:|
| `src/eija_studio/domain` | | 18 | 29 |
| `src/eija_studio/application` | | 9 | 16 |
| `src/eija_studio/adapters` | | 12 | |
| `src/eija_studio/interfaces` | | 3 | |
| `src/eija_studio/resources/web` | | 12 | |
| `contracts` | | | 34 |
| `verification/smt` | 151 | | 83 |
| `verification/bmc` | 50 | | 22 |
| `verification/bend` | 248 | | 172 |
| `quality` | | 18 | |
| `demos` | | 17 | |
| `scripts` | | 47 | |
| `tests/golden` | 368 | | |
| `tests` (other) | 194 | | |
| `examples` | 120 | | |
| `evidence` | 1,498 | | |
| `docs/diagrams` | 141 | | |
| `docs` (other) | 223 | | |
| root docs (`README.md`, `AGENTS.md`, `MANIFEST.json`) | 12 | | |
| **Total** | **3,005** | **136** | **356** |

### In-flight lanes (not on `main`; the plan must absorb them)

| Lane | Files with hits | Lines | Class | Note |
|---|---:|---:|---|---|
| `lane/tla` | 9 hand-written (`Excursion.tla`, `ExcursionTrace.tla`, `model.py`, `conformance.py`, …) | 66 | (c) | The transition table is generated, but the invariants `NoTeacherApproval` and `ApprovalRequiresRecommendation` are hand-written (`Excursion.tla:151-160`). `model.py:21` names `teacher-assigned`; `model.py:61-69` builds excursion-specific negative controls. |
| `lane/tla` | 17 generated `MC*_*.tla`/`.cfg`, plus `tests/test_tla_formal.py` | 117 + 28 | (a) | Generated from the Workflow; fine once the laws are generated too |
| `lane/property` | 7 test files | 44 | (a) | `tests/property/property_reference.py` is an independent oracle written from excursion prose (29 lines); it becomes a per-pack oracle in the plan |

## 4. Leaks into generic code (b)

| ID | Evidence (file:line) | What is hardcoded | Replacement from the pack |
|---|---|---|---|
| B1 | `domain/policy.py:6-38` | `FORBIDDEN`, `EFFECTS`, `CANONICAL_OPTIONS`, `baseline()`: the whole reference domain is Python constants in the kernel package | `packs/excursion/pack.json` (`model`, `protected.effects`, `protected.meanings`) |
| B2 | `adapters/sqlite_store.py:22-25`, `:87`, `:123-124` | Actor directory seed (5 excursion actors), outbox recipient `"registrar"`, baseline seed `baseline()` | `packs/<id>/fixtures/actors.json`; recipient from the effect declaration; seed from the active pack |
| B3 | `adapters/providers/_common.py:14-19` | Provider system prompt describes the excursion workflow and its three meanings | Prompt generated from the pack glossary and meanings, passed as delimited untrusted data |
| B4 | `adapters/providers/offline.py:12-17` | Offline provider routes by keyword (`"excursion" in request`, `"teacher"`); canned excursion alternatives. This is legacy keyword routing. | `packs/<id>/fixtures/proposals.json`; no keyword logic in the kernel |
| B5 | `interfaces/cli.py:202-205` | Demo request text and `recommend_only` selection | Pack `demo` block |
| B6 | `interfaces/http.py:28` | `Literal["recommend_only", "final_approval", "confirm_only", "unsupported"]` duplicated in the HTTP contract | Validate against the active pack's meaning ids at runtime |
| B7 | `resources/web/index.html:7,9,13,15` | "Synthetic excursion workflow", default request, rejection-source selects (`Recommended`/`Submitted`), actor options, try-it instructions | Rendered from the API (pack glossary, actors fixture, change-operation forms) |
| B8 | `resources/web/app.js:18,19,49` | `find(t=>t.action==="Reject")`, fixed action button list `["Submit","Recommend","Approve","Reject","Revise"]`, default sequence `"Recommend"` | Actions from `projections.rules`; typed edit forms from pack change operations |
| B9 | `domain/impact.py:46` | Ripple envelope text names "excursion" | Pack name in the envelope |
| B10 | `application/diagrams.py:152` | Legend "blocked by the protected excursion policy" | "blocked by the protected policy of pack `<id>`" |
| B11 | `application/diagram_catalog.py:27-30`, `:142-145` | `demo_pair()` = excursion baseline + `enable_recommendation`; page blurbs | Per-pack docs bundle from `packs/<id>/examples/` |
| B12 | `quality/hci/journey.py:7-8,104-105,124-158` | HCI journey clicks Submit/Recommend/Approve as teacher/registrar; answers `Registrar`/`Recommended` | Per-pack journey file; the excursion journey stays as the reference recording |
| B13 | `demos/scenarios/assurance_loop.py:27-95` | Scripted demo text and selectors | Legitimately excursion-specific. Moves to `packs/excursion/demos/`; the harness stays generic |
| B14 | `scripts/browser_smoke.py`, `browser_component_smoke.py`, `http_smoke.py`, `live_provider_smoke.py:29`, `wheel_smoke.py:31`, `capture_visual_screenshots.py` (47 lines in total) | Smoke scripts drive the excursion flow by name | Parameterise with `--pack`; the default is the reference pack |

## 5. Structural assumptions (c)

Ranked by risk, where risk means the chance the migration fails or silently weakens evidence.

| Rank | ID | Evidence (file:line) | Assumption | Why other domains cannot be expressed |
|---:|---|---|---|---|
| 1 | C1 | `domain/policy.py:41-78`; `verification/smt/encoding.py:137-161,204-258`; `verification/smt/differential.py:43-58`; `verification/bmc/spec.py:30-31,208-240`; `verification/bend/LAWS.bend:22-30,50-56`, `PROOF.bend` (32 lines name roles/states); `bend/bend_controls.py:92-140`; `lane/tla Excursion.tla:151-160` | **Authority laws are code, re-encoded by hand in five languages.** `check_policy` is a whitelist of the exact excursion shape (`UNSUPPORTED_WORKFLOW_SHAPE` when the action or state set differs, `:45-48`). Invariants such as `INV-TEACHER-NOT-DECIDER` are hand-written per backend. | The schema has no `laws` field. Any other domain fails `check_policy` outright and has zero formal coverage. Generating laws is the hardest part of the migration (Bend proofs in particular). |
| 2 | C2 | `domain/evidence.py:34-41,58`; `application/verifier.py:12-20,25-26,42-43,59` | **Evidence admissibility is pinned to the excursion matrix.** `assess_receipt` returns FAIL unless actors, actions and states equal the excursion sets. Effect deltas must be 0 or 1, so a transition with two audit effects would FAIL a correct receipt. The oracle is a fixed table. | A correct receipt for any other domain is judged FAIL. The kernel cannot say PASS for anything else. |
| 3 | C3 | `domain/models.py:89,113-114`; `application/service.py:100-102,111`; `domain/policy.py:80-94,105-111`; `contracts/proposal.schema.json`, `semantic-transaction.schema.json`, `change-case.schema.json` | **Closed change vocabulary.** Four interpretations, two semantic-transaction kinds; `select` accepts only `recommend_only`; three meaning questions with fixed answers (`"Registrar"`). | The agent cannot propose any change to an unknown domain, and the owner cannot select one. |
| 4 | C4 | `domain/models.py:30,57-72`; `adapters/sqlite_store.py:16`; `application/runtime.py:10-16` | **One entity, one state machine, globally unique action names, one role per transition, six fixed guards, global `assigned` flag.** `t.action in actions` (`:72`) forbids the same action from two states. Assignment is a column on the actor, not a relation to an instance. | No multi-entity models, no many-to-many relations, no per-instance assignment, no separation of duties, quorum, data conditions or timers. |
| 5 | C5 | `application/runtime.py:62-69`; `application/diagrams.py:377-399`; `verification/bmc/spec.py:208,231` | **Effects are typed by the string prefixes `Audit:` and `Notification:`,** with two adapters and forbidden effects matched by substring. | No other effect kind (deploy, share-with-consent, charge) can be declared. Substring matching over effect names is fragile under renaming. |
| 6 | C6 | `domain/models.py:59-60`; `contracts/workflow.schema.json:88-94`; `contracts/change-case.schema.json:177-183` | `Workflow.id: Literal["excursion"]`, `initial_state = "Draft"` | A second workflow cannot be constructed at all |
| 7 | C7 | `verification/smt/vocabulary.py:21-31`; `verification/bmc/explorer.py:36-50`; `verification/bend/bend_generate.py:37-63,275`; `verification/bend/main.bend:38-40` | Formal alphabets are fixed. `Model` has exactly the slots `Baseline` and `Candidate`; the Bend generator raises if `Recommended` is not declared; BMC toggles name actor ids. | Generation is partial: the tables are generated, but the vocabulary and the monitors are not |

## 6. Magic thresholds

| Where | Value | Tuned to excursion? | Disposition |
|---|---|---|---|
| `domain/models.py:36-39,61-62,127` | names ≤ 60 chars, ≤ 32 states, ≤ 64 transitions | No; they are kernel resource caps | Keep as kernel maxima; each pack declares its own limits under them (robustness) |
| `domain/models.py:94,98-100`; `application/service.py:44` | 1600-char texts, ≤ 4 alternatives, ≤ 10 unknowns, 6000-char request | No | Keep; document as kernel caps |
| `domain/models.py:119-120` | layout 0..2000 | No | Keep |
| `application/verifier.py:42-43`; `domain/evidence.py:58` | effect deltas ∈ {0, 1}; outbox = 1 only for `Recommend` | **Yes** | Expected deltas are computed from the transition's declared effects (C2) |
| `application/verifier.py:59` | `expected_cells = 5 actors × states × 5 actions` | **Yes** | Computed from the pack fixture directory and actions |
| `verification/bmc/__main__.py:19,29`; `verification/bmc/report.py:20` | depth 6, self-test depth 3, coverage enforced from depth 4 | **Yes** (5-state graph) | Derive from the state-graph diameter plus environment moves; report `exhausted` |
| `verification/bmc/report.py:22-23` | named model sets `candidate-reject-from-Recommended`, … | **Yes** | Enumerate the pack's examples |
| `verification/smt/prove.py:22` | Z3 timeout 60 s | No | Keep; a timeout gives UNKNOWN (it does already) |
| `quality/hci/budgets.json` (`klm.pointer_expert_time` 65 s) | modelled time of the excursion journey | **Yes** (a regression guard on this journey) | Budgets become per-journey, keyed by pack |
| `interfaces/agent_config.py:16` | 3 provider calls per MCP session | No | Keep |

## 7. MCP agent surface

| Tool | Generic? | Issue |
|---|---|---|
| `list_cases`, `create_case` | yes | None |
| `propose` | **no** | The provider prompt is excursion-only (B3); alternatives are limited to four interpretations (C3) |
| `view_case` | partly | The packet carries fixed meaning questions (C3) |
| `impact` | mostly | Envelope text (B9); the chain kinds are kernel concepts and fine |
| `verify` | **no** | Fixed oracle and admissibility (C2) |
| `render` | yes | Projections are generic but live in `domain/policy.py` (B1); diagram formats return `DIAGRAMS_NOT_AVAILABLE` until wired |
| resources | partly | `eija://language` is the kernel's language; no resource exposes a **domain** glossary, so an agent cannot learn an unknown domain from the server |

## 8. Fixtures (a): where they go

| Today | Lines | Disposition |
|---|---:|---|
| `examples/*.json` | 120 | `packs/excursion/examples/` |
| `tests/golden/*` | 368 | `tests/golden/excursion/*`, plus one golden set per held-out pack |
| `docs/diagrams/*` | 141 | `docs/packs/excursion/diagrams/`, generated per pack |
| `evidence/**`, `verification/bend/evidence/bend.json`, `accepted_set.json`, `expected_statistics.json` | 1,851 | Keyed by pack hash; regenerated evidence, not edited |
| `verification/bend/main.bend` (generated) | 96 | Regenerated from the pack; the only change is that the laws are generated too |
| `tests/*.py` | 194 | Parameterise over packs where the property is generic; keep excursion-specific assertions under `tests/packs/excursion/` |
| `docs/**` prose and snapshots | 223 | The reference-domain narrative stays; ADRs are immutable. New kernel docs use pack-neutral language. |
| Root docs (`README.md`, `AGENTS.md`, `MANIFEST.json`) | 12 | README keeps the excursion demo as the example and names the pack |
| **Total (a)** | **3,005** | |

## 9. Reproduce

```sh
V='(?i:excursion|teacher|registrar)|\b(Draft|Submitted|Recommended|Approved|Rejected|Submit|Recommend|Approve|Reject|Revise|Viewer)\b|recommend_only|final_approval|confirm_only|enable_recommendation|set_rejection_source|rejection_source|PaymentCaptured|ParentDataExported|RegistrarQueued|sign off'
rg -c --glob '!**/vendor/**' --glob '!.tmp/**' "$V" .              # per-file line counts (136 files, 3,497 lines)
rg -c "$V" src/eija_studio quality demos scripts contracts           # generic roots only
rg -l 'eija_studio\.domain\.policy import' src verification scripts  # indirect coupling (16 modules + policy.py itself)
```

The `domain_vocabulary` gate in ADR-0153 replaces this hand-written pattern. It extracts the vocabulary from every pack, so a new pack's terms are covered without anyone editing a regex.
