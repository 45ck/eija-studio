# Self-dogfood browser replay

Run the current EIJA IDE against its own checkout in an isolated Chromium context. This is a scripted functional replay, not a human usability study or evidence that the full implementation conforms to the reference journey.

From an EIJA checkout with Python 3.11 or newer, install the existing pinned browser dependencies and the isolated test browser once:

```console
python -m pip install -e ".[hci]"
python -m playwright install chromium
```

Then one command starts a new disposable workspace and loopback server, runs the browser checks, saves optional video, and shuts down the owned server:

```console
python tests/hci/self_dogfood_replay.py --record --out reports/self-dogfood-browser
```

Omit `--record` for a faster run. `--out` selects the evidence directory only. There is deliberately no server URL, owner capability, or existing workspace option. The server uses a random ephemeral session capability and normal source identity. It does not stamp release fixtures, connect to a provider, bypass CSP, reuse a Chrome profile, or call approval/apply endpoints. The connected checkout is inspected read-only through the production repository adapter. The new temporary workspace under `.tmp/` is removed after server shutdown; reports remain in the requested output directory. An interrupted process may leave its own temporary directory for inspection.

The replay uses Playwright's temporary browser profile, not your personal Chrome profiles. On managed personal endpoints, complete any required device/browser preflight and obtain authorization for an isolated test browser before running. `PLAYWRIGHT_BROWSERS_PATH`, if configured locally, can point to an existing Playwright browser cache.

## What the checks establish

- The full IDE opens with a model visible and the intent form closed; an offline request progresses through draft, proposal, and selected meaning.
- A domain term opens a captured source symbol with line numbers and source metadata. Declared intent, observed facts, and `Conformance: NOT_RUN` remain distinct.
- Zoom, pan, panel resizing, and baseline/history previews preserve the candidate. Historical and baseline views reject edits.
- A supported semantic edit changes the subject and revision. A forbidden approval-role edit is refused before an edit POST, preserving subject and revision. Undo/redo restore the expected semantic hashes, and reload retains the case.
- Changes opens after the accepted edit. The visual baseline/candidate pair and role difference are checked against the actual server response, then Inspect in model returns to the same candidate. Save is absent from this case's original baseline; its intermediate selected-candidate role changes from Owner to Agent. Both comparisons remain explicit in the retained response artifact.
- Keyboard navigation, command palette, tree, splitters, source-table focus, visible control names, and viewport containment are exercised.
- At 320x800 and 320x568 CSS pixels, the Intent, Rules, Run, Evidence, Repository, Source and Model tabs and readable-scale control remain clickable without forced clicks or body-level horizontal overflow. The 100% control must preserve the same minimum rendered label height used at desktop sizes, and its actual SVG screen scale must be 1 within 0.005. This checks reflow and scale consistency, not mobile task success.
- Readable 100% and whole-graph Overview are measured separately at 1600x1100 and 1280x800. Overview may shrink labels; use 100% plus pan to read details. The readable label-height threshold is a regression check, not a human comprehension result.
- Normal source identity preserves `SOURCE_REVIEW_REQUIRED`. Runtime verification refuses the changed implementation; approval/apply stay disabled. Human understanding stays `UNKNOWN`.
- Axe inspects four views for WCAG A/AA rules. Automatic violations fail the replay. All incomplete results are retained with `REVIEW_REQUIRED`, even when the scripted replay passes.

## Reading the results

`observations.json` contains each executed check, observed hashes and revisions, runtime errors, unexpected HTTP responses, owner-boundary observations, browser version, and the video path when recording. Screenshots show the tested states. `semantic-diff-response.json` retains the actual baseline/current/previous candidate models used by the visual comparison oracle. `axe.json` retains the raw automatic violations and incomplete findings. `accessibility-snapshot.txt` records the final accessibility tree.

`subject-manifest.json` records Git HEAD, dirty status, Python/dependency versions, and SHA-256 identities before and after the replay. Its scope is public regular files under `src/` and `packs/`, plus the replay and its subject-capture helper, including untracked source. Generated caches, private paths and key files are excluded with counts; their names and contents are not included. Vendored source is included. A byte change in this captured scope fails the replay; staging the same bytes does not. HEAD is only the base commit for a dirty checkout, not a claim that the tested bytes equal that commit. Root/applicable gate evidence remains separate.

Exit status 0 means the listed scripted checks passed. Status 1 means an executed check failed; later dependent checks are `NOT_RUN`. Status 2 means a prerequisite was missing or Python assertions were disabled. Do not run with `python -O`.

Zero automatic axe violations is not a complete accessibility result. Contrast in SVG and small glyphs can require manual review. Screen-reader use, forced colors, reduced motion, human task success, comprehension burden, and usefulness to engineers require separate evaluation. The recording demonstrates only the operations the script actually performs. This replay does not replace the full HCI suite or the repository release gates.
