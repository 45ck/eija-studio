# EIJA refined showcase replay

This editable capture records the actual bounded offline candidate-model journey in the user's installed Chrome. Product commit: `79ce22f78d649dd131561955e08044acbd60ffc9`. Captured source subject: `2010c846a8d6ae5b6afec180125336771c26c6019658c0dfac2d48d34b09b190`.

The exact driver passed a normal-CSP five-scene rehearsal and a separate recorded take on 2026-10-03. The export is 86.88 seconds, 1920 x 1080, H.264, normal speed and silent. Both browser and disposable server closed; source bytes were unchanged. Exported key frames were inspected; Recordly owns final narration, composition and full-speed/audio review.

## Replay

Use the project Python environment with Playwright/HCI dependencies, installed Chrome, Git and Node. Recording also needs ffmpeg and ffprobe on PATH. No dependency installation or paid provider call is performed. Keep source mirrors and browser temp files outside the checkout, and coordinate one browser/capture slot on this shared desktop.

```powershell
$captureRepo = 'D:\Temp\eija-ship-review-20261003'
$captureDriver = 'D:\Temp\eija-agent-polished-capture-20261003\capture.py'
$capturePython = 'C:\Dev\eija-wt\integrate\.venv\Scripts\python.exe'
$captureTemp = 'D:\Temp\eija-agent-browser-temp'
New-Item -ItemType Directory -Path $captureTemp -Force | Out-Null
$env:TEMP = $env:TMP = $env:TMPDIR = $captureTemp
$env:PYTHONPATH = "$captureRepo\src;$captureRepo;$captureRepo\tests\hci"
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONNOUSERSITE = '1'
& $capturePython $captureDriver --repo $captureRepo --describe-subject
$captureSubject = '2010c846a8d6ae5b6afec180125336771c26c6019658c0dfac2d48d34b09b190'
& $capturePython $captureDriver --repo $captureRepo --rehearse --story hero --expected-subject-sha256 $captureSubject --out D:\Temp\eija-refined-rehearsal-new
& $capturePython $captureDriver --repo $captureRepo --record --story hero --expected-subject-sha256 $captureSubject --out D:\Temp\eija-refined-take-new
```

Use new output directories. Rehearsal is headless with normal CSP and creates no media. Record mode is explicitly requested and uses the existing prgif recorder, with CSP bypass only for its real cursor overlay. Both modes require 10 GiB free on C:, reject a mismatched subject, enforce complete model/source oracles and close their own browser/server. Inspect the exported first/last frames and key transitions before use. Scene timestamps use the recorder actor clock and need frame-level confirmation at cuts.

## Story and scope

1. Exact supported request `Move Verify source to SAVED`, offline proposal and real kernel UML preview.
2. Explicit candidate Apply and actual persisted before/after UML.
3. Same transition through Model, baseline/working dropdown, Rules and declared read-only source.
4. Real Source endpoint drag to PREVIEW, unsubmitted preview, explicit candidate Apply, kernel Undo.
5. `Allow Agent to Approve` gets the actual protected-authority refusal with no edit submitted.

This is synthetic fixture behavior, not live inference, arbitrary request understanding, source rewriting, baseline approval, a production release or evidence of demand. SOURCE_REVIEW_REQUIRED remains visible and unchanged. Failed rehearsal-01 exposed a missing initial-state status badge; the product was fixed, the oracle retained, and rehearsal-02 plus the take passed. Earlier takes remain preserved.

`source.json` binds the replay to its product revision and recording facts. The local reproduction ZIP retains full observations and exported review frames. Raw footage is retained for Recordly; the review MP4 is not the final narrated film. The long real source-navigation wait can be shortened with a disclosed editorial cut. Do not fabricate product states or imply approval that did not occur.
