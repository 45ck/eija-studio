# ADR-0047: Hand-authored scripted demo recordings, not demo-machine

* Status: accepted
* Date: 2026-09-29
* Lane: demos

## Context and problem statement

The owner wants live recordings — real cursor movement, real typing — that show a developer using EIJA Studio end to end: defining ubiquitous language into a DDD tree, drag-and-drop UML editing kept in sync with the executable model, image generation inside the app, generated e2e tests and personas/ICP alongside the running app and its UML, the formal V&V lanes, and how AI assists without holding authority. The owner owns [demo-machine](https://github.com/45ck/demo-machine) (YAML-spec-driven demo recorder) and first suggested reusing it, then explicitly said: *"dont need to use demo-machine can just use hard coded version"*.

## Considered options

* demo-machine: a YAML spec compiled into a recording. General-purpose, but its spec format is tuned for its own product demos; adopting it here means learning and fitting its schema for a one-off narrative walkthrough, and the owner declined it directly.
* A hand-authored (scripted) recorder: a small typed Python harness (Playwright) that a demo **scenario module** drives directly with normal function calls (`type_text(...)`, `move_to(...)`, `click(...)`, `caption(...)`). No spec compiler, no YAML layer.
* Manual screen recording: not reproducible, not reviewable as code, and it cannot be re-run against a changed UI or checked by a gate, so it goes stale silently. (This option involves no custom code, so the ADR-0016 OSS check does not apply to it; it is rejected on reproducibility grounds alone.)

## Decision outcome

A hand-authored scripted recorder. It is still engineered with the same rigor as every other lane: typed, tested (a scenario can run "dry": the same real clicks, form input and assertions with video, overlay and delays skipped, so a gate can check a scenario still works as the UI changes), reviewed, and documented — not a one-off script kept outside version control. Cursor motion is a smoothstep-eased loop of Playwright `mouse.move` steps that also moves a synthetic on-page cursor (Chromium does not render the OS pointer into recorded video); typing is `locator.press_sequentially` one character at a time with a seeded random pause between characters (`time.sleep`; the seed fixes only the typing cadence, so recordings are not otherwise repeatable). Video is Playwright's built-in capture, run against the **installed system Google Chrome** (`channel="chrome"`), so no browser is downloaded. Playwright is **not** a dependency of the kernel and was not declared anywhere on `main` before this lane (`scripts/browser_*smoke.py` import it lazily when present); this lane adds `playwright==1.63.0` to the new optional `demos` extra. When Playwright is not installed or Chrome cannot be launched, the CLI reports `NOT_RUN` (exit 3), never a pass.

### Consequences

* Good: no dependency on a second product's release cadence or schema; each scenario is plain, readable Python that is easy to keep truthful as the Studio's UI evolves.
* Good: a scenario's steps double as a scripted end-to-end UI check (`--dry-run`, no recording) usable in the `full` gate tier, because every step asserts text the Studio really renders.
* Bad: no reusable spec format for non-EIJA demos; this harness is intentionally narrow to this repository, not a general product.
* Revisit when: a second EIJA-adjacent repo wants the same harness — extract it then, not speculatively now.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| [demo-machine](https://github.com/45ck/demo-machine) | Owner directive: use a hand-authored version instead, not its YAML-spec compiler | If reconsidered later, this harness's scenario steps could be lowered into a demo-machine spec |
| Playwright (new optional dependency: the `demos` extra, pinned `playwright==1.63.0`) | Not insufficient — reused directly for input events and video capture; only the scenario narration is custom | — |
