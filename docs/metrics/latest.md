# EIJA Studio metrics snapshot

- Platform: **Windows 10.0.26200 / CPython 3.12.10** (win-amd64)
- Commit: `5f86d966411c8a60494c77a7846a5265f42621bf`
- Profile: full
- Tools: coverage 7.16.2, fastapi 0.128.2, grimp 3.17, httpx 0.28.1, radon 6.0.1, uvicorn 0.48.0

> Sections `performance`, `scaling` and `verification_yield` contain wall-clock MEASUREMENTS taken on this platform under this load; they vary run to run. All other sections are deterministic functions of the source tree. The reported values are from the LAST of 2 runs (run 1: PERF-02, PERF-05, PERF-06; run 2: no timing budget failed).

## Budgets

| ID | Budget | Actual | Limit | Basis | Status |
|---|---|---|---|---|---|
| ARCH-01 | No dependency cycle between layers | 0 | == 0 | principled | PASS |
| ARCH-02 | No import cycle between modules | 0 | == 0 | principled | PASS |
| ARCH-03 | No Stable Dependencies Principle violation (a layer never depends on a less stable one) | 0 | == 0 | principled | PASS |
| ARCH-04 | Domain layer imports no other layer (Ce = 0) | 0 | == 0 | principled | PASS |
| ARCH-05 | Domain layer is maximally stable (I <= 0.1) | 0 | <= 0.1 | principled | PASS |
| ARCH-06 | Every non-domain layer lies within 0.5 of the main sequence (max D) | 0.29 | <= 0.5 | ratchet | PASS |
| ARCH-07 | Mean layer distance from the main sequence | 0.31 | <= 0.5 | ratchet | PASS |
| MI-01 | Lowest module maintainability index (radon MI, rank A >= 20) | 27.44 | >= 20 | ratchet | PASS |
| TEST-01 | Every domain/application/adapters/interfaces layer has a directly importing test (count of untested) | 0 | == 0 | principled | PASS |
| COV-01 | Line+branch coverage of src/eija_studio, percent (when reports/coverage exists) | 78.72 | >= 75 | ratchet | PASS |
| LANE-01 | No aggregated lane report is FAIL, UNKNOWN or UNREADABLE (a present report must say PASS or NOT_RUN) | n/a | == 0 | principled | NOT_RUN |
| PERF-01 | p95 of every read endpoint under 400 ms (TestClient) | 37.58 | < 400 | external | PASS |
| PERF-02 | p95 of every non-compute write endpoint under 400 ms (TestClient, durable SQLite) | 76.59 | < 400 | external | PASS |
| PERF-03 | p95 of every read and write endpoint under 400 ms (real uvicorn, loopback) | 336.36 | < 400 | external | PASS |
| PERF-04 | p95 of the verify compute endpoint under 10 s (long-running: needs a progress indication, see README) | 1,570 | < 10,000 | external | PASS |
| PERF-05 | Runtime verification time is near-linear in matrix size (R^2 of T = c0 + c1*cells >= 0.8; measured 0.896 to 0.99 run to run under load, so the limit keeps headroom; low power, see PERF-06) | 0.98 | >= 0.8 | ratchet | PASS |
| PERF-06 | Runtime verification: linear fit beats the quadratic alternative in cells (R^2 difference) | 0.03 | > 0 | principled | PASS |
| SCALE-01 | closure(): TWO-term fit T = c0 + cV*V + cE*E, R^2 (not the single V+E model; that is SCALE-04) | 0.92 | >= 0.9 | principled | PASS |
| SCALE-04 | closure(): the requested SINGLE-term fit T = c0 + c1*(V+E), R^2 (fits worse than two-term; limit has headroom) | 0.91 | >= 0.85 | ratchet | PASS |
| SCALE-02 | closure(): log-log exponent of time against V+E lies in [0.8, 1.2] | True | == True | principled | PASS |
| SCALE-03 | closure(): linear fit beats the quadratic alternative (R^2 difference) | 0.02 | > 0 | principled | PASS |

## Package metrics (Martin)

| Layer | Modules | Ca | Ce | I | A | D | Zone |
|---|---:|---:|---:|---:|---:|---:|---|
| __main__ | 1 | 0 | 1 | 1 | 0 | 0 | main sequence |
| adapters | 4 | 1 | 3 | 0.75 | 0 | 0.25 | main sequence |
| application | 5 | 3 | 5 | 0.62 | 0.67 | 0.29 | near main sequence |
| bootstrap | 1 | 1 | 5 | 0.83 | 0 | 0.17 | main sequence |
| domain | 5 | 11 | 0 | 0 | 0 | 1 | zone of pain (stable, concrete) |
| interfaces | 2 | 1 | 7 | 0.88 | 0 | 0.12 | main sequence |

SDP violations 0, layer cycles 0, module cycles 0.

## Complexity and maintainability

136 functions; mean CC 3.54, median 2, p90 8, max 45. Ranks: A=116, B=13, C=3, D=2, E=1, F=1. SLOC 1365, SLOC-weighted MI 42.99, lowest module MI 27.44.

| Hotspot | CC | Rank |
|---|---:|---|
| domain.evidence:assess_receipt | 45 | F |
| interfaces.cli:main | 33 | E |
| application.verifier:verify_runtime | 23 | D |
| domain.policy:check_policy | 21 | D |
| adapters.providers:OpenRouterProvider.propose | 17 | C |
| application.compiler:compile_case | 16 | C |
| application.runtime:execute | 16 | C |
| adapters.providers:CodexProvider.propose | 10 | B |
| domain.evidence:aggregate_status | 10 | B |
| domain.impact:closure | 9 | B |

## Tests and coverage

270 tests statically (270 collected by pytest), 362 assertions, 41 raises-blocks.

| Layer | Test files (direct) | Tests (direct) | Tests (transitive) |
|---|---:|---:|---:|
| __main__ | 0 | 0 | 0 |
| adapters | 2 | 25 | 55 |
| application | 1 | 30 | 55 |
| bootstrap | 2 | 37 | 37 |
| domain | 5 | 86 | 98 |
| interfaces | 1 | 5 | 5 |

Coverage: 78.72% (967/1182 statements, 228/336 branches).

| Layer | Statements | Line % | Branch % |
|---|---:|---:|---:|
| __main__ | 2 | 0 | n/a |
| adapters | 302 | 85.43 | 68.52 |
| application | 336 | 94.05 | 79.81 |
| bootstrap | 12 | 91.67 | 50 |
| domain | 285 | 92.28 | 80.36 |
| eija_studio | 1 | 100 | n/a |
| interfaces | 244 | 48.36 | 26.56 |

## HTTP latency (measured on Windows 10.0.26200 / CPython 3.12.10)

Thresholds: 100 ms instant, 400 ms Doherty. Milliseconds.

| Transport | Endpoint | Kind | n | p50 | p95 | p99 | Band |
|---|---|---|---:|---:|---:|---:|---|
| testclient | GET / | read | 120 | 2.87 | 3.59 | 3.99 | <=100 |
| testclient | GET /api/cases | read | 120 | 16.42 | 37.58 | 46.37 | <=100 |
| testclient | GET /api/cases/{id} | read | 30 | 29.21 | 36.99 | 38.11 | <=100 |
| testclient | GET /api/cases/{id}/export | read | 15 | 29.33 | 30.19 | 30.61 | <=100 |
| testclient | GET /api/doctor | read | 120 | 1.76 | 2.53 | 5.7 | <=100 |
| testclient | GET /api/status | read | 120 | 19.53 | 33.71 | 52.66 | <=100 |
| testclient | GET /assets/app.js | read | 120 | 3.04 | 3.99 | 4.15 | <=100 |
| testclient | POST /api/cases | write | 15 | 17.75 | 24.85 | 27.39 | <=100 |
| testclient | POST /api/cases/{id}/approve | write | 15 | 56.26 | 76.59 | 93.46 | <=100 |
| testclient | POST /api/cases/{id}/execute | write | 15 | 18.06 | 24 | 24.18 | <=100 |
| testclient | POST /api/cases/{id}/preview | write | 15 | 15.27 | 20.07 | 20.34 | <=100 |
| testclient | POST /api/cases/{id}/propose | write | 15 | 33.34 | 43.27 | 47.97 | <=100 |
| testclient | POST /api/cases/{id}/select | write | 15 | 18.08 | 20.47 | 20.96 | <=100 |
| testclient | POST /api/cases/{id}/verify | compute | 15 | 1,388 | 1,570 | 1,590 | over 400 |
| uvicorn | GET / | read | 120 | 3.57 | 4.18 | 4.74 | <=100 |
| uvicorn | GET /api/cases | read | 120 | 15.54 | 34.22 | 40.01 | <=100 |
| uvicorn | GET /api/cases/{id} | read | 30 | 33.77 | 37.1 | 41.7 | <=100 |
| uvicorn | GET /api/cases/{id}/export | read | 15 | 29.2 | 33.14 | 34.52 | <=100 |
| uvicorn | GET /api/doctor | read | 120 | 2.41 | 2.91 | 3.81 | <=100 |
| uvicorn | GET /api/status | read | 120 | 18.76 | 21.24 | 22.46 | <=100 |
| uvicorn | GET /assets/app.js | read | 120 | 3.62 | 4.07 | 4.38 | <=100 |
| uvicorn | POST /api/cases | write | 15 | 17.62 | 113.64 | 229.34 | <=400 |
| uvicorn | POST /api/cases/{id}/approve | write | 15 | 51.31 | 134.25 | 248.21 | <=400 |
| uvicorn | POST /api/cases/{id}/execute | write | 15 | 17.98 | 336.36 | 914.34 | <=400 |
| uvicorn | POST /api/cases/{id}/preview | write | 15 | 17.27 | 46 | 67.42 | <=100 |
| uvicorn | POST /api/cases/{id}/propose | write | 15 | 34 | 103.08 | 219.8 | <=400 |
| uvicorn | POST /api/cases/{id}/select | write | 15 | 18.48 | 56.63 | 100.56 | <=100 |
| uvicorn | POST /api/cases/{id}/verify | compute | 15 | 1,222 | 2,497 | 3,714 | over 400 |

verify_runtime: T = -21.01 + 10.068 * cells ms, R^2 = 0.981 over 10 matrix sizes (20 to 125 cells).

## closure() scaling (measured)

- T_ms = c0 + c1 * (V + E): c0 = -0.081 ms, c1 = 0.385 us per element, R^2 = 0.9135
- T_ms = c0 + cV * V + cE * E: cV = 0.6 us, cE = 0.35 us, R^2 = 0.9173
- log-log exponent 0.949 (R^2 0.956); quadratic alternative R^2 = 0.892
- 32 points, max |residual| 31.11 ms

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
| runtime_matrix (this kernel) | measured-here | 125 | 0 | 1.258 | 99.4 |
| impact_closure (this kernel) | measured-here | 20 | n/a | 9.52e-05 | 210,084 |

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
