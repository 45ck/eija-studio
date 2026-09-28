# ADR-0040: HCI budgets are ratchets, browser tests are opt-in, and the journey runs under the harness identity

* Status: accepted
* Date: 2026-09-28
* Lane: hci

## Context and problem statement

The current UI already misses some HCI thresholds (for example moves above 4 bits, focus dropped after re-render, one serious axe rule). Budgets that fail today would block every PR; budgets that are only advisory would let regressions in. Separately, the approve and apply screens are unreachable on any lane branch because the Studio blocks approval (`SOURCE_REVIEW_REQUIRED`) whenever the running source differs from the owner-stamped fixture, and heavy browser tests must not slow or destabilise the default suite on a shared PC.

## Decision drivers

* A shortfall must never be shown as a pass; a regression must fail.
* Never weaken kernel guards or restamp `trusted_build.json` to make something pass.
* The default `pytest -q` stays fast (about 40 s) and browser-free.
* Approve/apply screens are part of the owner journey and must be measurable.

## Considered options

* Two-level budgets: `target` (the law's threshold) and `limit` (ratchet); PASS / GAP (xfail) / FAIL / NOT_RUN (chosen).
* Hard failure at the law thresholds now (blocks all work until the UI is fixed).
* Advisory report only (no regression protection).
* For the journey: (a) stop at verification and mark approve/apply NOT_RUN; (b) serve with the kernel-test harness identity; (c) restamp the fixture (forbidden).

## Decision outcome

Chosen: two-level budgets in `quality/hci/budgets.json` evaluated by pure code and asserted by pytest marker `hci` tests (GAP is `pytest.xfail`, so a gap is visible and never a pass). Browser tests are opt-in (`pytest -m hci`, `nox -s hci`, `EIJA_HCI=1`) and skip with `NOT_RUN: <reason>` when Chrome, Playwright or axe is unavailable; the drift check and formula tests always run.

For the journey, option (b): `quality/hci/serve_harness.py` serves through the same `create_app` and Uvicorn stack as `eija serve`, replacing only the identity provider with the harness identity that `tests/conftest.py` already uses for kernel tests. It changes no policy, guard or stamped file, and every report states `identity_source: pytest-harness`. `--identity release` runs the real `eija serve`; if the source is unstamped the run reports `NOT_RUN: ... SOURCE_REVIEW_REQUIRED ...` with exit code 3 (a missing prerequisite, never a pass and never a UI failure), and any other journey failure prints `FAIL:` with exit code 1. The scratch server directory, whose `server.log` holds the private launch token, is deleted even when the run fails. A test asserts that `serve_harness.harness_identity()` equals `tests/conftest.py`'s, so the two copies cannot drift silently, and the launcher banner states that approvals under it are not release approvals.

### Consequences

* Good: regressions fail today; documented gaps are xfail; tightening a limit is a reviewed one-line diff.
* Good: no kernel change, no shared-file edits beyond the lane extra.
* Good: the committed raw trace makes the fast drift check re-derive the snapshot under the current laws, analysis and budgets, so editing any of them without a refresh fails (a scratch experiment during review showed a `laws.py` constant, a `budgets.json` limit and `web/app.js` were all invisible to the earlier REPORT.md-only check; the first two are now caught, `web/app.js` is caught by the UI-hash rule below).
* Decision: a UI-hash mismatch between the snapshot and the current `web/*` is informational in the fast tier and a hard failure in the release tier (`nox -s hci_snapshot_fresh`, `python -m quality.hci check --strict`). The check cannot re-measure the UI; only the hash tells it the UI moved.
* Bad: geometry ratchets are specific to the Chrome build and fonts of the snapshot (`moves_over_4_bits` carries one bit of headroom for that reason); timing ratchets are generous and machine dependent; the KLM budget guards the journey definition, not a measurement.
* Bad: approve/apply timings and screens are measured under a harness identity, not a release identity; this is stated in the report's limitations.
* Bad: opt-in tests can rot unnoticed if nobody runs `nox -s hci`; it is tagged `full` and `release` so the PR gate runs it wherever Chrome exists.
* Revisit when: the visual lane brings limits to their targets (collapse target = limit), or a stamped build is available in CI (switch the default to `--identity release`).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| pytest markers/xfail (adopted) | n/a | n/a |
| pytest-playwright, pytest-benchmark | Fixture-per-test browsers and statistical benchmarks; we need one shared journey run and a law-based report | Could wrap the journey fixture later |
| `serve_harness.py` (custom, ~40 lines) | `eija serve` has no supported hook for a test identity | Retire once the CLI exposes an explicit, non-release test-identity option |
