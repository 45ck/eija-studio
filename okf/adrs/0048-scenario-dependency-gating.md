---
type: Architecture Decision Record
title: 'ADR-0048: Demo scenarios are gated by their real dependencies, never faked'
description: The owner's full demo narrative (ubiquitous language → DDD tree, drag-and-drop UML kept in sync with the model, in-app image generation, e2e tests/personas/ICP alongside the running app and its UML, formal V&V, AI assis…
resource: repo://docs/adr/0048-scenario-dependency-gating.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0048-scenario-dependency-gating.md
  title: 0048-scenario-dependency-gating.md
  hash_method: lf-sha256-v1
  sha256: e89b8bba906026a1e4952083e067922f6a4f05f36d0ac6dccf0d418e17c9ff68
notes_baseline: 1250ea85e6a71c1db7e28bcc2b8602ea95b94540d23d83968152b0bc05520982
---

# ADR-0048: Demo scenarios are gated by their real dependencies, never faked

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-29 |
| Lane | demos |
| Source | `repo://docs/adr/0048-scenario-dependency-gating.md` |

## Decision outcome (verbatim)

> `demos/scenarios/REGISTRY.md` lists every planned scenario with a `status` (`recorded`, `recorded-partial`, `scripted-not-recorded`, `unscripted`, `blocked`) and the lane(s) it depends on. A scenario waits only for lanes that have not landed (`LANDED_LANES` in `registry.py`): `blocked` means it still waits for one (today a wave-2 lane), `unscripted` means every lane it needs has landed and only the script is missing, so a landed lane is never listed as a blocker (a gate fails a `blocked` scenario that waits for nothing, and a ready one that still waits). A scenario module only exists once its dependency has landed on `main`; until then it is a row in the registry with a `blocked` status and the lane(s) it waits for, not a stub Python file pretending to run. `demos/README.md` links to the generated `REGISTRY.md` instead of copying it, and any other place a recording is linked from (README.md, docs site) must do the same rather than carry a fixed list written once. Videos are large binaries and stay out of git (`demos/output/`, published as release assets); a `recorded` or `recorded-partial` status is instead backed by a small committed manifest under `demos/recordings/` (posix video path, video sha256 and size, platform, skipped acts, and the sha256 of the scenario module source at recording time; no commit hash or timestamp, so it does not churn). `recorded` means no act was skipped; a take in which any act could not run (for example verification blocked because the owner has not restamped the release fixture) is `recorded-partial`, and the gate checks the manifest agrees with the status. The `demos_registry` gate fails if a manifest is unreadable, is not a JSON object, lacks a required key or has a wrongly typed one (a `FAIL` line, never a traceback), or if `demos/output/<key>.webm` exists locally and its sha256 differs from the manifest (the video is gitignored, so its absence in a clean clone is fine). It only warns, without failing, when the scenario source has changed since the recording (`scenario_sha256` differs): the video then shows an earlier take and must be re-recorded before it is presented as current. It also fails if a `recorded` scenario has no manifest, if a `blocked` or `unscripted` scenario has a module, if a scripted or recorded one lacks its module, or if the generated `REGISTRY.md` differs from `registry.py` — the registry and the code cannot drift apart.
>
> One scenario — the core assurance loop (create case → interpretations → select `recommend_only` → Try flow across fixture actors → verify → acknowledge → approve → apply) — needs no other lane: it is exactly the v0.2 "First demonstration" walkthrough (`README.md`) that already ships and is already covered by `scripts/http_smoke.py` and `scripts/browser_smoke.py`. It is scaffolded first.

## Sections

* Context and problem statement
* Decision outcome

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://AGENTS.md`
* `repo://README.md`
* `repo://demos/README.md`
* `repo://demos/scenarios/REGISTRY.md`
* `repo://scripts/browser_smoke.py`
* `repo://scripts/http_smoke.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.

## Referenced by

* [Demos: scripted live recordings, scenario dependency gating](/lanes/0047-demos-scripted-live-recordings-scenario.md) - Capability lane with ADR numbers 0047–0048 reserved.
<!-- okf:generated:end links -->
