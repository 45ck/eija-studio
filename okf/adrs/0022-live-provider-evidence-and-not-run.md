---
type: Architecture Decision Record
title: 'ADR-0022: Live provider evidence is consent-gated, one call, and NOT_RUN when unproven'
description: Mocked contract tests prove an adapter's handling of faked output.
resource: repo://docs/adr/0022-live-provider-evidence-and-not-run.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0022-live-provider-evidence-and-not-run.md
  title: 0022-live-provider-evidence-and-not-run.md
  hash_method: lf-sha256-v1
  sha256: 2d6ab8c858f0b731da1978f86a4daa37687dc51f07b274f0db32645c112425b5
notes_baseline: 209f4ce871a134bbec1a1d16058f99e0cbf667e07695cf039bee98cb9a3cb740
---

# ADR-0022: Live provider evidence is consent-gated, one call, and NOT_RUN when unproven

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | providers |
| Source | `repo://docs/adr/0022-live-provider-evidence-and-not-run.md` |

## Decision outcome (verbatim)

> Chosen option: "opt-in script", because it keeps live calls out of every automatic gate. `scripts/live_provider_smoke.py --provider X --consent` sends only the fixed synthetic request and baseline, refuses without `--consent`, caps the timeout at 180 s, and records status, CLI version, model when reported, latency, `schema_valid` and error class in `evidence/live-providers/<date>-<platform>.json`.
>
> * `PASS` means a live call returned a schema-valid Proposal. It does not measure interpretation quality.
> * `NOT_RUN` means a prerequisite is missing: the CLI is absent, `doctor()` reports not signed in, a key is absent, or the CLI itself reported an authentication error.
> * `FAIL` means a call was made and failed.
> * Gemini CLI has no official status command, so its login is `UNKNOWN`; the single call may return an auth error, which is recorded as `NOT_RUN`, not `FAIL`.
> * OpenCode with zero stored credentials is `NOT_RUN` even though it can reach free anonymous models: those are not an owner account and were not authorised.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [Agent providers (CLI adapters, contract suite)](/lanes/0021-agent-providers.md) - Capability lane with ADR numbers 0021–0022 reserved.
<!-- okf:generated:end links -->
