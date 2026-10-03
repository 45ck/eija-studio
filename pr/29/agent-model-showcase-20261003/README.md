# EIJA bounded showcase replay

Editable capture source for the Windows EIJA showcase. It drives the user's installed Chrome against a disposable local EIJA server. Requests use a visibly synthetic, deterministic offline proposer. The demonstrated edits affect the candidate model; repository source stays read-only. This is not live inference, arbitrary request understanding, owner approval, or evidence of user demand.

Use the existing EIJA test/capture environment with Chrome, Playwright, ffmpeg and ffprobe. Keep one capture active at a time. Set PYTHONDONTWRITEBYTECODE=1 and set TMPDIR, TEMP and TMP to a writable directory outside the source checkout.

```powershell
python capture.py --repo D:\path\to\eija-studio --describe-subject
python capture.py --repo D:\path\to\eija-studio --rehearse --story hero --expected-subject-sha256 <reported-hash> --out D:\Temp\eija-showcase-rehearsal
python capture.py --repo D:\path\to\eija-studio --record --story hero --expected-subject-sha256 <reported-hash> --out D:\Temp\eija-showcase-take
```

Output directories must be new. Rehearsal uses normal CSP and produces screenshots and task checks. Recording uses the existing recorder's cursor overlay, with that CSP exception disclosed in its result. The raw WebM, silent native-resolution MP4, scene timing, exact model/source checks and artifact hashes remain available. Cosmetic setup trimming is explicit; playback speed stays 1. The refined replay shortens cosmetic pauses and preserves the actual viewport after Undo; it does not substitute a recentered screenshot.

The record shows a supported request, before/proposed UML, an explicit candidate edit, native model selection, linked source, real endpoint dragging, undo and a protected-policy refusal. Recordly owns the editorial composition and narration. Production gates and human comprehension are separate from this bounded demonstration; no merge or release approval is implied.
