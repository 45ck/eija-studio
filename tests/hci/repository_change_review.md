# Immutable code comparison browser proof

Run from an EIJA checkout with the `hci` and `source-analysis` extras installed,
Chromium available, and these two local commits retained:

```powershell
.\.venv\Scripts\python.exe tests/hci/repository_change_review.py --out reports/repository-change-review-1
```

The output directory must be new. The fixed pair is
`9c22d425ee33e52980a95b33330babec43c6aa59` to
`c666b6bb76905c0c9bd03e81cac0922136c4cf3e`. Missing commits or prerequisites
cannot produce a pass. Python optimization is refused because it disables the
assertion oracles. On Calvin personal endpoints, run the active
browser-account-router device preflight first and proceed only when ready.

The script reuses the existing disposable server, normal source-review identity,
CSP and isolated Chromium helpers. Every application request must be a GET. No
owner endpoint, provider, personal profile, live source execution, target-file
mutation, or private launch token is used. Its Git commands only inspect local
immutable objects; no checkout, hook or repository program executes.

## Checks and independent expectations

- Empty Code changes entry performs no automatic comparison and creates no case.
- The real comparison reconciles nine changed paths into eight public displayed
  paths and one excluded path, with exclusion reason counts. Excluded filenames
  and contents are not published. The file chooser matches the complete returned
  public inventory.
- Fixed Git objects independently establish four changed JavaScript syntax sites
  and the unchanged `task` function syntax. These observations are not a claim of
  behavioral equivalence. The partial capture and behavior `NOT_RUN` stay visible.
- Whole-file diff and selected `cases` excerpts match real GETs and independently
  read Git blobs, SHA-256 values, line ranges, snippet text and Git's unified diff.
  Before/After views display historical commit/blob identities and never call the
  live `repository/source` endpoint. Keyboard file/tab navigation includes a real
  added file's absent Before side.
- A deliberate isolated 503 preserves the last accepted comparison and source;
  a genuine retry accepts the reverse pair and clears the previous selection.
  A genuine delayed reverse response released after a newer accepted request
  cannot overwrite that newer subject.
- Wrong pair, blob and selected symbol range responses are deliberately injected
  from copied real responses. Each must be refused while preserving accepted
  data, then a genuine retry succeeds. Separate copied-observation mutations test
  the independent Git oracle. These are fault controls, not extra product stories.
- Populated historical-source views are checked at desktop, smaller desktop and
  320-pixel widths, with real keyboard tab activation and axe results retained.

## Evidence and limits

Each run keeps its result, exact source/helper/script manifest, independent GET
bodies, negative controls, screenshots, accessibility results, request log and
cleanup result. Assertion messages and sanitized traceback remain on failure.
Screenshots appear as each stage completes; a partial failed run is not relabeled
as a complete pass. Execution status comes from the named `result.json`, never
from this guide.

This is one bounded code-review workflow. It does not measure human comprehension,
behavioral correctness, all repositories/parsers, owner authorization, model
receipts, live providers, or source authoring. It does not mutate the live checkout
to test concurrent filesystem changes. Those claims require separate evidence.
