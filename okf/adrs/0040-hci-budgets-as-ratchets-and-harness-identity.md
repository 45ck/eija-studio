---
type: Architecture Decision Record
title: 'ADR-0040: HCI budgets are ratchets, browser tests are opt-in, and the journey runs under the harness identity'
description: The current UI already misses some HCI thresholds (for example moves above 4 bits, focus dropped after re-render, one serious axe rule).
resource: repo://docs/adr/0040-hci-budgets-as-ratchets-and-harness-identity.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0040-hci-budgets-as-ratchets-and-harness-identity.md
  title: 0040-hci-budgets-as-ratchets-and-harness-identity.md
  hash_method: lf-sha256-v1
  sha256: 49353423ae29bc401c8499d6f22d5c63a85bacb07d935e61effd43e63fdc3ac9
notes_baseline: dd10fe45662fb95f53cdcd126ffb45b736f6583c6e53f122d4a8b8a2feb65bc5
---

# ADR-0040: HCI budgets are ratchets, browser tests are opt-in, and the journey runs under the harness identity

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | hci |
| Source | `repo://docs/adr/0040-hci-budgets-as-ratchets-and-harness-identity.md` |

## Decision outcome (verbatim)

> Chosen: two-level budgets in `quality/hci/budgets.json` evaluated by pure code and asserted by pytest marker `hci` tests (GAP is `pytest.xfail`, so a gap is visible and never a pass). Browser tests are opt-in (`pytest -m hci`, `nox -s hci`, `EIJA_HCI=1`) and skip with `NOT_RUN: <reason>` when Chrome, Playwright or axe is unavailable; the drift check and formula tests always run.
>
> For the journey, option (b): `quality/hci/serve_harness.py` serves through the same `create_app` and Uvicorn stack as `eija serve`, replacing only the identity provider with the harness identity that `tests/conftest.py` already uses for kernel tests. It changes no policy, guard or stamped file, and every report states `identity_source: pytest-harness`. `--identity release` runs the real `eija serve`; if the source is unstamped the run reports `NOT_RUN: ... SOURCE_REVIEW_REQUIRED ...` with exit code 3 (a missing prerequisite, never a pass and never a UI failure), and any other journey failure prints `FAIL:` with exit code 1. The scratch server directory, whose `server.log` holds the private launch token, is deleted even when the run fails. A test asserts that `serve_harness.harness_identity()` equals `tests/conftest.py`'s, so the two copies cannot drift silently, and the launcher banner states that approvals under it are not release approvals. Nothing under `src/` names or accepts the harness (a test scans the package for it), the launcher refuses any workspace outside the checkout's `.tmp/hci/` so the stand-in can never open a real workspace, and the branch's `git diff origin/main -- src/` is empty.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://quality/hci/budgets.json`
* `repo://quality/hci/serve_harness.py`
* `repo://tests/conftest.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture](/adrs/0105-weave-human-views.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce fi…
* [HCI laws and usability instrumentation](/lanes/0039-hci-laws-and-usability-instrumentation.md) - Capability lane with ADR numbers 0039–0040 reserved.
<!-- okf:generated:end links -->
