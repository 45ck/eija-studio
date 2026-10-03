# Review workspace browser checks

Run from the repository root with the installed `hci` extra and Chromium:

```powershell
$env:PYTHONPATH = (Get-Location).Path + ';' + (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe tests/hci/ide_review_workspace.py --out reports/review-workspace-1
```

The standalone script imports the repository-owned `quality` package; the explicit
import path above includes this checkout and its source package.

The output directory must be new. Python optimization (`-O`/`-OO`) is refused because it disables assertion oracles. Missing optional browser prerequisites are not a pass. On Calvin personal endpoints, complete the active browser-account-router device preflight before running. The script uses a fresh isolated browser context, its own temporary workspace/server and an in-memory test capability; it never uses personal browser profiles or a private owner launch token.

To diagnose only source snapshot recovery, add `--scenario source-freshness` and
use a new output directory. This executes the same source fixture and marks the
main review journey `NOT_RUN`; its result must not be cited as ten review checks.

## What is checked

The main journey uses the real EIJA repository as a read-only source connection and the offline `eija-review-slice` pack. Normal UI controls create cases and submit permitted typed edits. Independent GET responses supply complete baseline/candidate models, history, evidence subjects, source snapshots and persisted runtime observations. The renderer supplies observations, never expected topology.

- Create a candidate, change the Save role and Verify source through server-listed affordances, and compare the full change inventory and exact fields.
- Check both actual painted graphs: state/transition membership, initial marker, labels, arrow resolution and endpoint contact against the correct state borders. Exercise parallel edges, a separate self-loop, absent-side elements, synchronized zoom and selection/case/revision identity.
- Follow the declared Verify binding to exact source lines and file/snippet/source/graph hashes, then return to the same selected change. Unmapped Save remains explicitly unknown.
- Compare visible evidence to the current packet; preserve the distinction between historical model preview and current evidence. Focus, reopen panes, fail one case refresh, retry through a real response, and restore normal preferences and visible keyboard focus.
- Switch between two cases with the same element IDs but different model facts. Run real synthetic Propose → SelectMeaning → Save and preserve its context across navigation.
- Use keyboard controls, measure desktop and 320-pixel layouts, and retain axe violations and incomplete checks. These are synthetic checks, not human usability or full accessibility evidence.

A separate source-coherence fixture copies one public Python source file into a temporary tracked Git repository. It changes only that disposable file, confirms stale source/impact requests fail closed, preserves the old caption/content truthfully, and explicitly refreshes the connection before comparing new source/impact identities. It does not claim full-repository semantic correctness.

Verification, owner approval, apply and export requests are blocked. No live provider is called. Runtime simulation uses its ordinary preview/execute controls; it does not apply source changes.

## Evidence and limits

Each run retains JSON outcomes, independent GET bodies, graph observations, exact script/helper/source hashes, screenshots, expected faults and browser/server cleanup. Any failed oracle keeps the run failed. Copied-observation negative controls and the temporary visibly wrong painted-path control test oracle sensitivity; they are not extra product stories.

The UI does not currently expose baseline-only removal or initial-state editing, so those browser scenarios remain uncovered. Human comprehension, real-user task success, live model quality, factory orchestration, owner authorization, source-code authoring and universal correctness are not measured. A passing run must be cited with its exact subject manifest and cannot be reused as evidence for changed bytes.

This guide defines the runnable scope. Execution status comes only from the named run's `result.json`; adding this file does not establish a pass.

## Ordinary semantic summary augmentation

The main replay has ten named checks after the ordinary-summary increment (the
previous nine-check records remain historical). The added check reuses the same
normal-identity server, cases, observations and cleanup; it is not a second app
or a fabricated case payload. Independent case GET snapshots determine every
changed field and exact old/new text. Each existing selection also checks the
summary's selected element, case and revision, including the existing case switch
and the two successive permitted edit revisions. Existing exact tables,
source/evidence/model navigation, graph membership and painted-endpoint oracles
remain unchanged.

The initial desktop selection checks actual text Range boxes against all clipping
ancestors and point hit testing. The 1280x800 and 320x800 observations resize an
explicitly reached selected summary; they do not claim mobile-first case creation
or an untouched entry viewport. The longer Added Save guard/effect values are
checked one field at a time with explicitly recorded scroll-to-view operations.
All field contents, at least 14px text, no page-wide horizontal overflow and
actual unclipped before/after text are required. Full long summaries need not fit
simultaneously. Raw observations retain the reached/reflow scope.

Whitespace checks use exact GET-derived multiline array text, computed white-space
and Range widths for literal space runs. Arbitrary whitespace-bearing scalar
names are not offered by this EIJA fixture; that distinct scalar case remains in
the comparison's Node tests, not claimed as an end-to-end browser observation.

Copied observation controls reject an omitted field, reversed values, a stale
revision and a wrong selection. A temporary hidden summary row must additionally
fail the actual painted-visibility oracle, then be restored and rechecked.
Authoritative case/evidence/history/runtime observations and write requests must
remain unchanged across these checks. `summary-observations.json` is saved as
observations are collected, including failures. These are sensitivity controls,
not additional product stories or a human-comprehension measurement.
