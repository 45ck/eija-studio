---
type: Architecture Decision Record
title: 'ADR-0249: Fixes from the inspection of the app generator'
description: The 13 November 2026 inspection (record) found ten defects in the generated app and its conformance suite.
resource: repo://docs/adr/0249-app-generator-inspection-fixes.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0249-app-generator-inspection-fixes.md
  title: 0249-app-generator-inspection-fixes.md
  hash_method: lf-sha256-v1
  sha256: 509dfc4a4fe32f127b744373b4221cec9325583a2c85a79711ba14a3b2cc0f6e
notes_baseline: d35dbb852257edcb0553347dd9e44d3d460c9220a9f485b688e6e2764d23b157
---

# ADR-0249: Fixes from the inspection of the app generator

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-13 |
| Lane | app generator (ADR-0150), issue #249 |
| Source | `repo://docs/adr/0249-app-generator-inspection-fixes.md` |

## Decision outcome (verbatim)

> Chosen option: fix each defect. The generated suite gains three tests (20 in all, `GENERATED_TESTS`): objects created through the app, a step restarting the record's clock, and the `Host` check. The oracle gains `object_cases` (only when an association is built, so other oracles keep their bytes) and, for signal cases, the stored values and the answer to the same signal under a new operation id. The page chooses a referenced object from the stored ones and can add one in place. Reads share the write lock. A stale record's options carry the code `act` will give.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0150: Build runnable apps from the model, checked against the kernel as oracle](/adrs/0150-build-apps-from-the-model-with-a-kernel-oracle.md) - The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".
* [ADR-0243: Conformance that catches a divergent app by behaviour](/adrs/0243-conformance-that-catches-divergence.md) - The pitch for `eija build` (ADR-0150) is that the generated app's conformance tests prove the app matches its model.

## Referenced by

* [ADR-0250: One status table, retryable creates and bounded requests in the generated app](/adrs/0250-app-generator-second-pass.md) - The second inspection of the app generator (record) found that the API contract and the server kept the status of each refusal in two copies that had drifted,…
<!-- okf:generated:end links -->
