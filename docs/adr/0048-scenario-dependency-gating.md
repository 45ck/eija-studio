# ADR-0048: Demo scenarios are gated by their real dependencies, never faked

* Status: accepted
* Date: 2026-09-29
* Lane: demos

## Context and problem statement

The owner's full demo narrative (ubiquitous language → DDD tree, drag-and-drop UML kept in sync with the model, in-app image generation, e2e tests/personas/ICP alongside the running app and its UML, formal V&V, AI assisting throughout) spans capabilities that other lanes are still building. EIJA's own culture is evidence-honesty: a missing prerequisite reports `NOT_RUN`, never `PASS` ([ADR-0016](0016-oss-first-adapters-not-engines.md), `AGENTS.md`). A demo of a feature that does not exist yet would violate that as badly as a fake verification receipt.

## Decision outcome

`demos/scenarios/REGISTRY.md` lists every planned scenario with a `status` (`recorded`, `recorded-partial`, `scripted-not-recorded`, `blocked`) and the lane(s) it depends on. A scenario module only exists once its dependency has landed on `main`; until then it is a row in the registry with a `blocked` status and the tracking issue/PR, not a stub Python file pretending to run. `demos/README.md` and any place a recording is linked from (README.md, docs site) must show the registry's current state, not a fixed list written once. Videos are large binaries and stay out of git (`demos/output/`, published as release assets); a `recorded` or `recorded-partial` status is instead backed by a small committed manifest under `demos/recordings/` (video hash, size, platform, skipped acts). `recorded` means no act was skipped; a take in which any act could not run (for example verification blocked because the owner has not restamped the release fixture) is `recorded-partial`, and the gate checks the manifest agrees with the status. The `demos_registry` gate fails if a `recorded` scenario has no manifest, if a `blocked` scenario has a module, if a non-blocked one lacks its module, or if the generated `REGISTRY.md` differs from `registry.py` — the registry and the code cannot drift apart.

One scenario — the core assurance loop (create case → interpretations → select `recommend_only` → Try flow across fixture actors → verify → acknowledge → approve → apply) — needs no other lane: it is exactly the v0.2 "First demonstration" walkthrough (`README.md`) that already ships and is already covered by `scripts/http_smoke.py` and `scripts/browser_smoke.py`. It is scaffolded first.

### Consequences

* Good: the demo roadmap is machine-checkable, not a claim in prose that can silently go stale.
* Good: reviewers and the owner can see real progress (5 of N scenarios recorded) rather than an all-or-nothing deliverable.
* Bad: more bookkeeping (one registry row per scenario) than just writing scripts as capabilities land.
