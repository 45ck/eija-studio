# EIJA Studio metrics snapshot

- Platform: **Windows 10.0.26200 / CPython 3.12.10** (win-amd64)
- Commit: `a5f5455e036969763c89ae5dde42f4a1340053e9`
- Profile: full
- Tools: coverage 7.16.2, fastapi 0.128.2, grimp 3.17, httpx 0.28.1, radon 6.0.1, uvicorn 0.48.0

> Sections `performance`, `scaling` and `verification_yield` contain wall-clock MEASUREMENTS taken on this platform under this load; they vary run to run. All other sections are deterministic functions of the source tree. The reported values are from the LAST of 2 runs (run 1: PERF-02, PERF-03; run 2: PERF-02, PERF-03).

## Budgets

| ID | Budget | Actual | Limit | Basis | Status |
|---|---|---|---|---|---|
| ARCH-01 | No dependency cycle between layers | 0 | == 0 | principled | PASS |
| ARCH-02 | No import cycle between modules | 0 | == 0 | principled | PASS |
| ARCH-03 | No Stable Dependencies Principle violation (a layer never depends on a less stable one) | 0 | == 0 | principled | PASS |
| ARCH-04 | Domain layer imports no other layer (Ce = 0) | 0 | == 0 | principled | PASS |
| ARCH-05 | Domain layer is maximally stable (I <= 0.1) | 0 | <= 0.1 | principled | PASS |
| ARCH-06 | Every non-domain layer lies within 0.5 of the main sequence (max D) | 0.43 | <= 0.5 | ratchet | PASS |
| ARCH-07 | Mean layer distance from the main sequence | 0.32 | <= 0.5 | ratchet | PASS |
| MI-01 | Lowest module maintainability index (radon MI, rank A >= 20) | 22.57 | >= 20 | ratchet | PASS |
| TEST-01 | Every domain/application/adapters/interfaces layer has a directly importing test (count of untested) | 0 | == 0 | principled | PASS |
| COV-01 | Line+branch coverage of src/eija_studio, percent (when reports/coverage exists) | 82.64 | >= 75 | ratchet | PASS |
| LANE-01 | No aggregated lane report is FAIL, UNKNOWN or UNREADABLE (a present report must say PASS or NOT_RUN) | n/a | == 0 | principled | NOT_RUN |
| PERF-01 | p95 of every read endpoint under 400 ms (TestClient) | 62.65 | < 400 | external | PASS |
| PERF-02 | p95 of every non-compute write endpoint under 400 ms (TestClient, durable SQLite) | 1,582 | < 400 | external | FAIL |
| PERF-03 | p95 of every read and write endpoint under 400 ms (real uvicorn, loopback) | 608.44 | < 400 | external | FAIL |
| PERF-04 | p95 of the verify compute endpoint under 10 s (long-running: needs a progress indication, see README) | 1,514 | < 10,000 | external | PASS |
| PERF-05 | Runtime verification time is near-linear in matrix size (R^2 of T = c0 + c1*cells >= 0.8; measured 0.896 to 0.99 run to run under load, so the limit keeps headroom; low power, see PERF-06) | 0.99 | >= 0.8 | ratchet | PASS |
| PERF-06 | Runtime verification: linear fit beats the quadratic alternative in cells (R^2 difference) | 0.05 | > 0 | principled | PASS |
| SCALE-01 | closure(): TWO-term fit T = c0 + cV*V + cE*E, R^2 (not the single V+E model; that is SCALE-04) | 0.95 | >= 0.9 | principled | PASS |
| SCALE-04 | closure(): the requested SINGLE-term fit T = c0 + c1*(V+E), R^2 (fits worse than two-term; limit has headroom) | 0.92 | >= 0.85 | ratchet | PASS |
| SCALE-02 | closure(): log-log exponent of time against V+E lies in [0.8, 1.2] | True | == True | principled | PASS |
| SCALE-03 | closure(): linear fit beats the quadratic alternative (R^2 difference) | 0.11 | > 0 | principled | PASS |

## Package metrics (Martin)

| Layer | Modules | Ca | Ce | I | A | D | Zone |
|---|---:|---:|---:|---:|---:|---:|---|
| __main__ | 1 | 0 | 1 | 1 | 0 | 0 | main sequence |
| adapters | 16 | 1 | 3 | 0.75 | 0.04 | 0.21 | main sequence |
| application | 8 | 9 | 5 | 0.36 | 0.21 | 0.43 | near main sequence |
| bootstrap | 1 | 1 | 5 | 0.83 | 0 | 0.17 | main sequence |
| domain | 5 | 20 | 0 | 0 | 0 | 1 | zone of pain (stable, concrete) |
| interfaces | 5 | 1 | 9 | 0.9 | 0 | 0.1 | main sequence |

SDP violations 0, layer cycles 0, module cycles 0.

## Complexity and maintainability

365 functions; mean CC 3.37, median 2, p90 7, max 45. Ranks: A=308, B=51, C=2, D=2, E=1, F=1. SLOC 3269, SLOC-weighted MI 44.45, lowest module MI 22.57.

| Hotspot | CC | Rank |
|---|---:|---|
| domain.evidence:assess_receipt | 45 | F |
| interfaces.cli:main | 31 | E |
| application.verifier:verify_runtime | 23 | D |
| domain.policy:check_policy | 21 | D |
| application.compiler:compile_case | 16 | C |
| application.runtime:execute | 16 | C |
| application.diagram_catalog:_diagram | 10 | B |
| application.diagram_catalog:case_diagrams | 10 | B |
| application.diagrams:journey_graph | 10 | B |
| domain.evidence:aggregate_status | 10 | B |

## Tests and coverage

504 tests statically (601 collected by pytest), 853 assertions, 90 raises-blocks.

| Layer | Test files (direct) | Tests (direct) | Tests (transitive) |
|---|---:|---:|---:|
| __main__ | 0 | 0 | 0 |
| adapters | 5 | 132 | 210 |
| application | 5 | 132 | 248 |
| bootstrap | 2 | 37 | 85 |
| domain | 13 | 314 | 326 |
| interfaces | 3 | 53 | 53 |

Coverage: 82.64% (2377/2806 statements, 537/720 branches).

| Layer | Statements | Line % | Branch % |
|---|---:|---:|---:|
| __main__ | 2 | 0 | n/a |
| adapters | 990 | 92.22 | 79.5 |
| application | 940 | 97.77 | 91.29 |
| bootstrap | 10 | 100 | n/a |
| domain | 289 | 93.77 | 83.93 |
| eija_studio | 1 | 100 | n/a |
| interfaces | 574 | 45.82 | 29.86 |

## HTTP latency (measured on Windows 10.0.26200 / CPython 3.12.10)

Thresholds: 100 ms instant, 400 ms Doherty. Milliseconds.

| Transport | Endpoint | Kind | n | p50 | p95 | p99 | Band |
|---|---|---|---:|---:|---:|---:|---|
| testclient | GET / | read | 120 | 2.4 | 2.85 | 2.91 | <=100 |
| testclient | GET /api/cases | read | 120 | 15.07 | 35.72 | 40.23 | <=100 |
| testclient | GET /api/cases/{id} | read | 30 | 45.89 | 62.65 | 112.61 | <=100 |
| testclient | GET /api/cases/{id}/export | read | 15 | 43.28 | 56.75 | 61.91 | <=100 |
| testclient | GET /api/doctor | read | 120 | 1.63 | 2.32 | 3.06 | <=100 |
| testclient | GET /api/status | read | 120 | 32.51 | 39.63 | 41.53 | <=100 |
| testclient | GET /assets/app.js | read | 120 | 2.48 | 2.88 | 3.17 | <=100 |
| testclient | POST /api/cases | write | 15 | 16.04 | 34.6 | 62.28 | <=100 |
| testclient | POST /api/cases/{id}/approve | write | 15 | 64.2 | 1,582 | 4,374 | over 400 |
| testclient | POST /api/cases/{id}/execute | write | 15 | 17.78 | 33.45 | 44.62 | <=100 |
| testclient | POST /api/cases/{id}/preview | write | 15 | 14.27 | 29.95 | 44.6 | <=100 |
| testclient | POST /api/cases/{id}/propose | write | 15 | 28.92 | 60.28 | 89.16 | <=100 |
| testclient | POST /api/cases/{id}/select | write | 15 | 15.11 | 54.72 | 67 | <=100 |
| testclient | POST /api/cases/{id}/verify | compute | 15 | 1,279 | 1,514 | 1,517 | over 400 |
| uvicorn | GET / | read | 120 | 4 | 6.65 | 8.36 | <=100 |
| uvicorn | GET /api/cases | read | 120 | 14.13 | 31.41 | 41.66 | <=100 |
| uvicorn | GET /api/cases/{id} | read | 30 | 45.61 | 51.96 | 52.63 | <=100 |
| uvicorn | GET /api/cases/{id}/export | read | 15 | 43.19 | 46.92 | 47.16 | <=100 |
| uvicorn | GET /api/doctor | read | 120 | 2.09 | 2.49 | 2.66 | <=100 |
| uvicorn | GET /api/status | read | 120 | 32.6 | 35.34 | 37.02 | <=100 |
| uvicorn | GET /assets/app.js | read | 120 | 3.27 | 3.78 | 4.07 | <=100 |
| uvicorn | POST /api/cases | write | 15 | 15.77 | 523.18 | 1,455 | over 400 |
| uvicorn | POST /api/cases/{id}/approve | write | 15 | 61.88 | 608.44 | 1,607 | over 400 |
| uvicorn | POST /api/cases/{id}/execute | write | 15 | 16.67 | 57.58 | 83.58 | <=100 |
| uvicorn | POST /api/cases/{id}/preview | write | 15 | 13.91 | 32.63 | 48.25 | <=100 |
| uvicorn | POST /api/cases/{id}/propose | write | 15 | 29.41 | 456.91 | 1,230 | over 400 |
| uvicorn | POST /api/cases/{id}/select | write | 15 | 16.46 | 28.87 | 41.66 | <=100 |
| uvicorn | POST /api/cases/{id}/verify | compute | 15 | 1,137 | 1,597 | 1,920 | over 400 |

verify_runtime: T = 20.34 + 7.274 * cells ms, R^2 = 0.99 over 10 matrix sizes (20 to 125 cells).

## closure() scaling (measured)

- T_ms = c0 + c1 * (V + E): c0 = -0.166 ms, c1 = 0.399 us per element, R^2 = 0.9151
- T_ms = c0 + cV * V + cE * E: cV = 1.065 us, cE = 0.291 us, R^2 = 0.9491
- log-log exponent 1.068 (R^2 0.952); quadratic alternative R^2 = 0.801
- 32 points, max |residual| 29.32 ms

Both models are linear in the graph size, so an exponent near 1 with a high R^2 is consistent with O(V+E) on this graph family; it is a measurement, not a proof. The single-coefficient V+E model fits less well than the two-term model because a visited node costs several times more than a scanned edge (queue and per-node sort overhead).

## Other lanes' reports

| Group | Lane | Status | Detail |
|---|---|---|---|
| formal | formal (Bend / TLA+ / Z3 / BMC) | NOT_RUN | no reports/formal/*.json (lane not run on this checkout) |
| hci | hci | NOT_RUN | no reports/hci/*.json (lane not run on this checkout) |
| mutation | mutation | NOT_RUN | no reports/mutation/summary.json (lane not run on this checkout) |
| testing | testing | NOT_RUN | no reports/testing/*.json (lane not run on this checkout) |

## Verification yield

| Technique | Source | States | Findings | Seconds | States/s |
|---|---|---:|---:|---:|---:|
| runtime_matrix (this kernel) | measured-here | 125 | 0 | 0.935 | 133.69 |
| impact_closure (this kernel) | measured-here | 20 | n/a | 6.66e-05 | 300,300 |

## What these numbers do not establish

| Scope | Not established |
|---|---|
| all | Latency and verify() timings use the offline provider; the identity is forced trusted_fixture=True (identity_source: metrics-harness) so a working tree that differs from the owner-stamped release can be measured. No kernel guard is changed, and this is not a measurement of the stamped release. |
| all | Verification yield: findings are oracle/runtime disagreements of a same-author oracle, not independent evidence, and counts are not comparable across techniques. |
| all | Timing budgets are advisory in the full gate and enforced in the release session; every timing value depends on the machine and its load at the time. |
| all | verify() fit: a negative intercept is a fit artefact from pooling matrices of different shape, and 20 to 125 cells cannot separate linear from mildly superlinear growth (see the quadratic comparison). |
| all | Martin metrics: single-module entry points (__main__, bootstrap) get D = 0 by degenerate I = 1, A = 0, and empty package __init__ modules show MI = 100; both pad the summaries. |
| all | Freshness: the drift check compares the martin and complexity sections with the source tree; the tests and coverage sections are not checked for freshness (coverage is bound to a tree hash when it is collected). |
| complexity | module-level statement complexity (radon omits it) |
| complexity | cognitive complexity |
| complexity | test-code complexity |
| coverage | whether covered lines are asserted on (mutation lane) |
| coverage | subprocess-only or browser-driven paths |
| lane_reports | the correctness of any lane's report (this module aggregates, it does not re-verify) |
| martin | class-level coupling |
| martin | runtime/dynamic imports |
| martin | third-party coupling (listed per layer) |
| martin | design quality: D is a balance heuristic, not a verdict |
| performance | browser rendering |
| performance | concurrent load |
| performance | live model provider |
| performance | other machines |
| scaling | asymptotic proof |
| scaling | other graph shapes |
| scaling | graph construction cost |
| scaling | other hardware |
| tests | test quality or fault-detection power (see the mutation lane) |
| tests | dynamic parametrisation beyond literals |
| tests | tests outside tests/ |
| verification_yield | independence of techniques |
| verification_yield | defect-finding power (findings are counts reported by each technique) |
