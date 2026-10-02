# Prospective semantic-edit browser proof

This replay checks the real read-only edit preview and explicit Apply interaction in an isolated EIJA workspace. It uses normal source-review identity and CSP. It does not call owner verification, approval, baseline apply or live-provider endpoints. Each execution must retain its own source and replay identities, actual outcomes and cleanup observations. A passing static check is not a browser result, and this replay does not establish full US06 or human acceptance.

Run from a checkout containing the integrated preview backend, UI and replay helpers, using unoptimized Python. First complete the personal-endpoint `browser-account-router --device-status` preflight from the active Calvin Ops checkout; proceed only on `ready`. The browser is a fresh headless Playwright Chromium process, never a personal Chrome profile.

Environment conventions for the replay; each execution still requires its own preflight and retained receipt:

```powershell
Set-Location C:\Dev\eija-wt\integrate
$env:PYTHONPATH = 'C:/Dev/eija-wt/integrate/tests/hci;C:/Dev/eija-wt/integrate/src;C:/Dev/eija-wt/integrate'
$env:PLAYWRIGHT_BROWSERS_PATH = 'E:\.dev-cache\ms-playwright'
.\.venv\Scripts\python.exe -u tests/hci/prospective_edit_review.py --out reports/prospective-edit-1
```

Use a new output directory. Do not use `python -O`: it exits `NOT_RUN` instead of disabling assertion oracles. The normal project HCI/visual dependencies and cached Playwright browser must be available; import or launch failure is not a pass. Serialize this run with other browser/heavy gates on the reference PC.

| Stage | Authoritative expected behavior |
|---|---|
| Preview, Close and Escape | Three legal role/source/target proposals match independent complete expected candidates and real preview responses. Current/proposed graphs, all transition fields and hashes match. Closing preserves the entire case, packet, observations, history and edit-request count. Desktop entry followed by 1440/1280/320 viewport reflow stays within the viewport; this is not a complete mobile authoring journey. |
| Explicit Apply | Keyboard confirmation sends exactly the previewed transaction at the captured revision. The complete acknowledged candidate, semantic hashes, appended transaction, history cursor and one audit event match; prior observations remain intact. |
| Late read-only response | Close a held preview before switching case. Both real success and synthetic failure arriving later must leave both cases and the active UI unchanged. |
| Acknowledged edit, failed refresh | Hold an actual edit request, repeat activation/Escape, then hold and fail its GET refresh. Only one write occurs. The old runtime is invalidated; the committed reconciliation marker survives closing. Successful authoritative navigation back reconciles that case. |
| Unknown response | Forward an actual edit, replace only the browser's acknowledgement with malformed JSON, then reconcile by GET. The UI must say unknown, preserve its prior loaded model and block further editing until refresh. Refresh must not retry the write. |

The shared edge replay separately retains its two-page stale-version refusal: inspect a preview, let another ordinary page commit first, then explicitly Apply the stale proposal and expect `/edit` to refuse it without another mutation.

Server GETs and captured real preview/acknowledgement responses supply the model, packet, history and runtime facts. Expected candidate changes are constructed by changing only the selected field in the original full model. The existing painted-SVG oracle checks topology, labels, inventory, initial markers and arrow ownership. Its copied-observation negative controls reject missing nodes, duplicate edges, swapped endpoints, wrong labels and missing/moved initial labels; those controls are comparator sensitivity checks, not extra user journeys.

Outputs retain the executing script, before/after source manifests (including this replay and helper files), screenshots, actual requests and controlled faults, independent GETs, preview observations, graph measurements, acknowledgements, cleanup flags, actual failure and artifact hashes. Original failed runs must remain intact. Human usability, live inference, owner decision-making and complete mobile editing remain outside this proof.
