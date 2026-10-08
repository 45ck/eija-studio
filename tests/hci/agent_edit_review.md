# Agent candidate-edit browser acceptance

This standalone replay uses the user's installed Chrome (`channel="chrome"`) with a fresh browser context and a disposable offline EIJA workspace. It records screenshots and JSON evidence; it has no recording option. Run it serially after the implementation and evidence helpers are frozen.

From the checkout root, using the project Python environment with Playwright, axe and the existing HCI dependencies installed:

```powershell
$env:PYTHONPATH = "$PWD\src;$PWD"
$replayTemp = 'D:\Temp\eija-agent-browser-temp'
New-Item -ItemType Directory -Path $replayTemp -Force | Out-Null
$env:TMPDIR = $env:TEMP = $env:TMP = $replayTemp
python tests/hci/agent_edit_review.py --out D:\Temp\eija-agent-edit-acceptance-20261003
```

Use a fresh output directory. Set all three temporary-directory variables before starting Python, to an existing directory outside the connected checkout. The source adapter refuses to build a mirror inside that checkout. This replay uses the in-process `self_dogfood_replay.disposable_server()` helper, so these process settings reach the source adapter; it does not call the CLI server helper that redirects temporary files inside the checkout. Its disposable workspace still uses an explicit directory under the checkout's `.tmp` and retains the existing cleanup. The result records the actual resolved temporary root; a nested temporary root is `NOT_RUN` before browser launch.

The replay also requires installed Chrome, readable repository Git metadata, permission to create the checkout's `.tmp` workspace and bind a loopback server, unoptimized Python, and at least 10 GiB free on C: on Windows. It creates its own disposable capability and does not read a personal launch token or receipt key. The installed-Chrome wrapper for older replays is unnecessary and does not allow this new filename.

The configured checkout is first opened in Repository and refreshed through the actual UI. A fresh independent GET must match the visible connection response, identify the exact checkout as connected and read-only, and match the real service file's SHA-256. Source and graph identities require the exact `sha256:` prefix; file, pack and snippet hashes use bare lowercase SHA-256 hex. The source identity is independently recomputed from the returned file manifest using its declared domain tag. The fixture setup is then visible: the normal UI creates an intent, the deterministic offline provider proposes the saved-path meaning, and an explicit owner selection creates a candidate. That setup is separate from the agent-edit proof:

1. Type `Move Verify source to SAVED`. Inspect the actual read-only `/edit/propose` response, its visible offline/synthetic origin, exact case/revision/semantic identity and full candidate. Proposing must not open the edit modal or mutate anything.
2. Open the real kernel preview, check both painted UML models against independent complete-model expectations, and close it. Complete case, history, runtime observations and edit POST count must remain unchanged.
3. Reopen and explicitly Apply edit. The actual acknowledgement and a fresh independent GET must equal the expected whole model. Exactly one transaction and one `SemanticEdited` event are added; the baseline and runtime remain unchanged. Before any tab navigation, assert that the visible saved-result status holds keyboard focus and capture its screenshot and focus observation.
4. Follow the applied proposal into Model, Changes and Rules. Verify `TR-VERIFY` remains the selected current transition. Follow its declared source binding and check actual displayed lines and hashes; this is read-only source navigation, not a source transformation.
5. Drag the visible Source handle from SAVED to PREVIEW using real pointer coordinates, observing the legal drop target and the painted guide after pointer movement. The guide must have positive length and stroke, and its screen endpoints must track the handle and pointer (within 2 CSS pixels for input/subpixel rounding). Dropping must remove the guide/drop hints and only open a preview. Apply explicitly, then undo twice: first restore the agent-edited SAVED candidate, then the original saved-path candidate.
6. Reject an unsupported request and inspect the protected Approve-role refusal without any model mutation. Hold one real proposal request, switch to another real candidate, and release the unchanged response; the old result must not appear or apply to the new case.
7. Retain normal `SOURCE_REVIEW_REQUIRED` and human comprehension `UNKNOWN`. Verify no owner verify/approve/baseline-apply/export attempts and unchanged source identity.

`result.json` reports each completed check, the failing stage, expected and unexpected HTTP failures, JavaScript errors, cleanup and source preservation. Console output contains concise check statuses and the result path. Separate files retain real proposer responses, complete expected/server models, painted-graph observations and negative controls, source bytes/hash checks, and actual pointer coordinates. The artifact manifest hashes the retained files. Missing prerequisites are `NOT_RUN`; failed behavior or incomplete cleanup is `FAIL`.

This demonstrates a bounded deterministic synthetic agent proposing a typed candidate edit. It does not establish live inference, arbitrary request interpretation, source rewriting, human usability or demand, baseline approval/application, or the separate same-case concurrent-revision race. Source-review status is not relabelled to make this replay pass.
