# Case navigation and runtime ownership regression

Run `case_preview_navigation.py` against this checkout using an installed EIJA development environment with the HCI extra and Playwright Chromium. It imports the existing normal-identity disposable CLI server, replay UI helpers and subject hashing helper. No new server or runtime engine is introduced.

```powershell
$priorPath = $env:PYTHONPATH
try {
  $env:PYTHONPATH = 'src;.'
  python tests/hci/case_preview_navigation.py --out reports/case-preview-navigation-new-run
  $runCode = $LASTEXITCODE
} finally {
  $env:PYTHONPATH = $priorPath
}
exit $runCode
```

The output directory must be new. Run browser checks serially. On a Calvin personal endpoint, complete the required browser-account-router preflight before browser execution. The script uses isolated Chromium, the real offline CLI, the default excursion pack and a newly created disposable workspace. It does not access an owner workspace or use a stamped test identity. The launch capability belongs only to this throwaway server and is not retained in evidence. Missing Python/browser prerequisites prevent the run; an absent run is NOT_RUN, never PASS. Python optimization (-O/-OO) is refused with NOT_RUN and exit code 2 before any server or browser starts, because these checks require assertion oracles.

## Five checks

1. Create a supported candidate through ordinary controls, start a preview and Submit as the assigned synthetic teacher. Refresh the same case through the command palette. Require a fresh actual case GET, unchanged persisted case/runtime/packet, and unchanged rendered Submitted preview/result.
2. Inject a single HTTP 503 on another case's detail GET, reached through the case list. Preserve current case identity, Submitted instance and result. Recommend must commit against that original instance and increment its version exactly once; the other case remains untouched.
3. Repeat through the dropdown and require its displayed selection to return to the retained case.
4. Hold the real diagnostics GET while the UI is busy, select another case and require no navigation or mutation. The dropdown must continue naming the retained case. Release the held GET with a synthetic 503, preserve the preview and successfully Recommend on the original instance.
5. Switch successfully to another case. Its preview must be Not started, runtime result empty and actions disabled. Both persisted cases remain untouched by navigation.

Only failed GET responses are fabricated. Successful API responses, models, instances and DOM state are real. Independent authenticated GETs inspect persisted instances, audit and outbox before and after navigation. Verify, approve, apply and export POSTs are blocked and the result requires zero attempts. Setup and runtime actions are synthetic local fixture operations, not human or institutional authorization.

## Evidence and limits

`result.json` records each completed check, real runtime responses, safe request paths, exactly three expected 503s, unexpected HTTP/JavaScript errors and cleanup status. `authoritative-get-oracles.json` contains the actual case/packet/observation responses. Screenshots capture retained Submitted state after failed navigation and while busy. Before/after source manifests include this script when run in the checkout; the result also names its exact SHA and reused helper hashes. Chromium and the server must close, and a socket probe confirms the server port no longer accepts connections. A failing sequential check stops the remainder; an unrun check is not a pass. The manifest identifies content, not correctness.

The initial work-only run passed refresh and both 503 switch checks, then stopped because its oracle incorrectly expected a semantic subject on an unselected DRAFT case. That case correctly exposes MEANING_REQUIRED. The corrected oracle compares the entire real packet, requires the refresh GET, rechecks destination isolation after execution and rejects cleanup exceptions. The busy check was added after an actual-handler unit regression exposed a busy dropdown identity discrepancy. Historical run evidence remains separate from later runs; consult each result and subject manifest before claiming a pass.

This is narrowly scoped runtime-navigation evidence. It does not run verification, owner review/apply, live inference or a human-comprehension study, nor establish production readiness. Creation/load failure is covered by `tests/test_case_navigation.py`, outside these five browser checks.
