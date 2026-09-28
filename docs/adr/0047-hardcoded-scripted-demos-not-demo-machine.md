# ADR-0047: Hand-authored scripted demo recordings, not demo-machine

* Status: accepted
* Date: 2026-09-29
* Lane: demos

## Context and problem statement

The owner wants live recordings — real cursor movement, real typing — that show a developer using EIJA Studio end to end: defining ubiquitous language into a DDD tree, drag-and-drop UML editing kept in sync with the executable model, image generation inside the app, generated e2e tests and personas/ICP alongside the running app and its UML, the formal V&V lanes, and how AI assists without holding authority. The owner owns [demo-machine](https://github.com/45ck/demo-machine) (YAML-spec-driven demo recorder) and first suggested reusing it, then explicitly said: *"dont need to use demo-machine can just use hard coded version"*.

## Considered options

* demo-machine: a YAML spec compiled into a recording. General-purpose, but its spec format is tuned for its own product demos; adopting it here means learning and fitting its schema for a one-off narrative walkthrough, and the owner declined it directly.
* A hand-authored (scripted) recorder: a small typed Python harness (Playwright) that a demo **scenario module** drives directly with normal function calls (`type_text(...)`, `move_to(...)`, `click(...)`, `caption(...)`). No spec compiler, no YAML layer.
* Manual screen recording: not reproducible, not reviewable as code, fails ADR-0016 (OSS-first still means keeping engineering artefacts, not producing throwaway media).

## Decision outcome

A hand-authored scripted recorder. It is still engineered with the same rigor as every other lane: typed, tested (a scenario can run "dry": the same real clicks, form input and assertions with video, overlay and delays skipped, so a gate can check a scenario still works as the UI changes), reviewed, and documented — not a one-off script kept outside version control. Cursor motion and typing use Playwright's real input events (`mouse.move` with interpolated waypoints, `keyboard.type` with per-character delay), recorded via Playwright's built-in video capture (Chromium, already a project dependency for the HCI and visual lanes — no new capture tool).

### Consequences

* Good: no dependency on a second product's release cadence or schema; each scenario is plain, readable Python that is easy to keep truthful as the Studio's UI evolves.
* Good: a scenario's steps double as a scripted end-to-end UI check (`--dry-run`, no recording) usable in the `full` gate tier, because every step asserts text the Studio really renders.
* Bad: no reusable spec format for non-EIJA demos; this harness is intentionally narrow to this repository, not a general product.
* Revisit when: a second EIJA-adjacent repo wants the same harness — extract it then, not speculatively now.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| [demo-machine](https://github.com/45ck/demo-machine) | Owner directive: use a hand-authored version instead, not its YAML-spec compiler | If reconsidered later, this harness's scenario steps could be lowered into a demo-machine spec |
| Playwright (already an EIJA dependency: visual/HCI lanes) | Not insufficient — reused directly for input events and video capture; only the scenario narration is custom | — |
