# ADR-0048: Demo scenarios are gated by their real dependencies, never faked

* Status: accepted
* Date: 2026-09-29
* Lane: demos

## Context and problem statement

The owner's full demo narrative (ubiquitous language → DDD tree, drag-and-drop UML kept in sync with the model, in-app image generation, e2e tests/personas/ICP alongside the running app and its UML, formal V&V, AI assisting throughout) spans capabilities that other lanes are still building. EIJA's own culture is evidence-honesty: a missing prerequisite reports `NOT_RUN`, never `PASS` ([ADR-0016](0016-oss-first-adapters-not-engines.md), `AGENTS.md`). A demo of a feature that does not exist yet would violate that as badly as a fake verification receipt.

## Decision outcome

`demos/scenarios/REGISTRY.md` lists every planned scenario with a `status` (`recorded`, `recorded-partial`, `scripted-not-recorded`, `blocked`) and the lane(s) it depends on. A scenario module only exists once its dependency has landed on `main`; until then it is a row in the registry with a `blocked` status and the lane(s) it waits for, not a stub Python file pretending to run. `demos/README.md` links to the generated `REGISTRY.md` instead of copying it, and any other place a recording is linked from (README.md, docs site) must do the same rather than carry a fixed list written once. Videos are large binaries and stay out of git (`demos/output/`, published as release assets); a `recorded` or `recorded-partial` status is instead backed by a small committed manifest under `demos/recordings/` (posix video path, video sha256 and size, platform, skipped acts, and the sha256 of the scenario module source at recording time; no commit hash or timestamp, so it does not churn). `recorded` means no act was skipped; a take in which any act could not run (for example verification blocked because the owner has not restamped the release fixture) is `recorded-partial`, and the gate checks the manifest agrees with the status. The `demos_registry` gate fails if a manifest is unreadable, is not a JSON object, lacks a required key or has a wrongly typed one (a `FAIL` line, never a traceback), or if `demos/output/<key>.webm` exists locally and its sha256 differs from the manifest (the video is gitignored, so its absence in a clean clone is fine). It only warns, without failing, when the scenario source has changed since the recording (`scenario_sha256` differs): the video then shows an earlier take and must be re-recorded before it is presented as current. It also fails if a `recorded` scenario has no manifest, if a `blocked` scenario has a module, if a non-blocked one lacks its module, or if the generated `REGISTRY.md` differs from `registry.py` — the registry and the code cannot drift apart.

One scenario — the core assurance loop (create case → interpretations → select `recommend_only` → Try flow across fixture actors → verify → acknowledge → approve → apply) — needs no other lane: it is exactly the v0.2 "First demonstration" walkthrough (`README.md`) that already ships and is already covered by `scripts/http_smoke.py` and `scripts/browser_smoke.py`. It is scaffolded first.

### Consequences

* Good: the demo roadmap is machine-checkable, not a claim in prose that can silently go stale.
* Good: reviewers and the owner can see real progress rather than an all-or-nothing deliverable. When this ADR was written the honest state was 1 of 10 scenarios recorded, and only in part (act 4 skipped); `REGISTRY.md` always shows the current counts.
* Bad: more bookkeeping (one registry row per scenario) than just writing scripts as capabilities land.
