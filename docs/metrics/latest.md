# EIJA Studio metrics snapshot

- Platform: **Windows 11 / CPython 3.12.10** (AMD64)
- Commit: `15bdc83f4ff76a71cb39bc96854b162e5c39f081`
- Profile: full, generated 2026-09-28
- Tools: coverage 7.16.2, fastapi 0.128.2, grimp 3.17, httpx 0.28.1, radon 6.0.1, uvicorn 0.48.0

> Sections `performance`, `scaling` and `verification_yield` contain wall-clock MEASUREMENTS taken on this platform under this load; they vary run to run. All other sections are deterministic functions of the source tree.

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
| CX-01 | Largest function cyclomatic complexity | 45 | <= 50 | ratchet | PASS |
| CX-02 | Share of functions ranked A or B (CC <= 10) | 0.95 | >= 0.9 | ratchet | PASS |
| CX-03 | Lowest module maintainability index (radon MI, rank A >= 20) | 27.49 | >= 20 | ratchet | PASS |
| TEST-01 | Every domain/application/adapters/interfaces layer has a directly importing test (count of untested) | 0 | == 0 | principled | PASS |
| COV-01 | Line+branch coverage of src/eija_studio, percent (when reports/coverage exists) | 78.99 | >= 75 | ratchet | PASS |
| LANE-01 | No aggregated lane report has status FAIL | n/a | == 0 | principled | NOT_RUN |
| PERF-01 | p95 of every read endpoint under 400 ms (TestClient) | 38.53 | < 400 | external | PASS |
| PERF-02 | p95 of every non-compute write endpoint under 400 ms (TestClient, durable SQLite) | 54.55 | < 400 | external | PASS |
| PERF-03 | p95 of every read and write endpoint under 400 ms (real uvicorn, loopback) | 60.92 | < 400 | external | PASS |
| PERF-04 | p95 of the verify compute endpoint under 10 s (long-running: needs a progress indication, see README) | 3,333 | < 10,000 | external | PASS |
| PERF-05 | Runtime verification time is linear in matrix size (R^2 of T = c0 + c1*cells) | 0.62 | >= 0.9 | principled | FAIL |
| SCALE-01 | closure(): two-term linear fit T = c0 + cV*V + cE*E, R^2 | 0.99 | >= 0.9 | principled | PASS |
| SCALE-02 | closure(): log-log exponent of time against V+E lies in [0.8, 1.2] | True | == True | principled | PASS |
| SCALE-03 | closure(): linear fit beats the quadratic alternative (R^2 difference) | 0.2 | > 0 | principled | PASS |

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

136 functions; mean CC 3.54, median 2, p90 8, max 45. Ranks: A=116, B=13, C=3, D=2, E=1, F=1. SLOC 1348, SLOC-weighted MI 42.98, lowest module MI 27.49.

| Hotspot | CC | Rank |
|---|---:|---|
| domain.evidence:assess_receipt | 45 | F |
| interfaces.cli:main | 33 | E |
| application.verifier:verify_runtime | 22 | D |
| domain.policy:check_policy | 21 | D |
| adapters.providers:OpenRouterProvider.propose | 17 | C |
| application.compiler:compile_case | 16 | C |
| application.runtime:execute | 16 | C |
| adapters.providers:CodexProvider.propose | 10 | B |
| domain.evidence:aggregate_status | 10 | B |
| domain.impact:closure | 9 | B |

## Tests and coverage

151 tests statically (151 collected by pytest), 221 assertions, 36 raises-blocks.

| Layer | Test files (direct) | Tests (direct) | Tests (transitive) |
|---|---:|---:|---:|
| __main__ | 0 | 0 | 0 |
| adapters | 2 | 25 | 55 |
| application | 1 | 30 | 55 |
| bootstrap | 2 | 37 | 37 |
| domain | 5 | 86 | 98 |
| interfaces | 1 | 5 | 5 |

Coverage: 78.99% (964/1173 statements, 228/336 branches).

| Layer | Statements | Line % | Branch % |
|---|---:|---:|---:|
| __main__ | 2 | 0 | n/a |
| adapters | 302 | 86.42 | 68.52 |
| application | 331 | 93.96 | 79.81 |
| bootstrap | 12 | 91.67 | 50 |
| domain | 281 | 92.17 | 80.36 |
| eija_studio | 1 | 100 | n/a |
| interfaces | 244 | 49.59 | 26.56 |

## HTTP latency (measured on Windows 11 / CPython 3.12.10)

Thresholds: 100 ms instant, 400 ms Doherty. Milliseconds.

| Transport | Endpoint | Kind | n | p50 | p95 | p99 | Band |
|---|---|---|---:|---:|---:|---:|---|
| testclient | GET / | read | 120 | 2.75 | 3.52 | 4.26 | <=100 |
| testclient | GET /api/cases | read | 120 | 14.83 | 31.69 | 43.36 | <=100 |
| testclient | GET /api/cases/{id} | read | 30 | 28.3 | 38.53 | 40.14 | <=100 |
| testclient | GET /api/cases/{id}/export | read | 15 | 30.45 | 34.76 | 36.16 | <=100 |
| testclient | GET /api/doctor | read | 120 | 1.56 | 2.03 | 2.16 | <=100 |
| testclient | GET /api/status | read | 120 | 19.1 | 23.17 | 27.64 | <=100 |
| testclient | GET /assets/app.js | read | 120 | 2.73 | 3.6 | 3.79 | <=100 |
| testclient | POST /api/cases | write | 15 | 15.21 | 23.69 | 24.75 | <=100 |
| testclient | POST /api/cases/{id}/approve | write | 15 | 48.94 | 54.55 | 60.3 | <=100 |
| testclient | POST /api/cases/{id}/execute | write | 15 | 17.04 | 22.3 | 25.75 | <=100 |
| testclient | POST /api/cases/{id}/preview | write | 15 | 15.79 | 17.96 | 18.31 | <=100 |
| testclient | POST /api/cases/{id}/propose | write | 15 | 32.47 | 42.87 | 46.97 | <=100 |
| testclient | POST /api/cases/{id}/select | write | 15 | 17.47 | 19.74 | 21.5 | <=100 |
| testclient | POST /api/cases/{id}/verify | compute | 15 | 1,234 | 3,333 | 6,951 | over 400 |
| uvicorn | GET / | read | 120 | 4.01 | 4.74 | 5.81 | <=100 |
| uvicorn | GET /api/cases | read | 120 | 17.15 | 39.25 | 45.24 | <=100 |
| uvicorn | GET /api/cases/{id} | read | 30 | 28.87 | 38.06 | 39.2 | <=100 |
| uvicorn | GET /api/cases/{id}/export | read | 15 | 31.45 | 39.36 | 46.94 | <=100 |
| uvicorn | GET /api/doctor | read | 120 | 2.62 | 3.33 | 3.56 | <=100 |
| uvicorn | GET /api/status | read | 120 | 20.68 | 29.27 | 49.57 | <=100 |
| uvicorn | GET /assets/app.js | read | 120 | 4.18 | 5.25 | 5.93 | <=100 |
| uvicorn | POST /api/cases | write | 15 | 17.29 | 22.42 | 24.92 | <=100 |
| uvicorn | POST /api/cases/{id}/approve | write | 15 | 49.7 | 60.92 | 66.94 | <=100 |
| uvicorn | POST /api/cases/{id}/execute | write | 15 | 16.73 | 21.03 | 22.32 | <=100 |
| uvicorn | POST /api/cases/{id}/preview | write | 15 | 15.63 | 18.45 | 19.33 | <=100 |
| uvicorn | POST /api/cases/{id}/propose | write | 15 | 32.95 | 37.71 | 39.45 | <=100 |
| uvicorn | POST /api/cases/{id}/select | write | 15 | 17.45 | 21.11 | 22.15 | <=100 |
| uvicorn | POST /api/cases/{id}/verify | compute | 15 | 1,163 | 1,319 | 1,418 | over 400 |

verify_runtime: T = -35.12 + 12.678 * cells ms, R^2 = 0.621 over 10 matrix sizes (20 to 125 cells).

## closure() scaling (measured)

- T_ms = c0 + c1 * (V + E): c0 = 1.527 ms, c1 = 0.476 us per element, R^2 = 0.9063
- T_ms = c0 + cV * V + cE * E: cV = 1.691 us, cE = 0.279 us, R^2 = 0.9853
- log-log exponent 1.03 (R^2 0.956); quadratic alternative R^2 = 0.704
- 32 points, max |residual| 31.09 ms

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
| runtime_matrix (this kernel) | measured-here | 125 | 0 | 1.214 | 103.01 |
| impact_closure (this kernel) | measured-here | 20 | n/a | 0.00011 | 181,818 |
