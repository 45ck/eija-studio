# Review workspace browser checks

Run from the repository root with the installed `hci` extra and Chromium:

```powershell
.\.venv\Scripts\python.exe tests/hci/ide_review_workspace.py --out reports/review-workspace-1
```

The output directory must be new. Python optimization (`-O`/`-OO`) is refused because it disables assertion oracles. Missing optional browser prerequisites are not a pass. On Calvin personal endpoints, complete the active browser-account-router device preflight before running. The script uses a fresh isolated browser context, its own temporary workspace/server and an in-memory test capability; it never uses personal browser profiles or a private owner launch token.

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
