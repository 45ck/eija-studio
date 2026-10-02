# Runtime feedback browser replay

This replay uses the existing normal-identity, offline, disposable EIJA review-pack server and isolated Chromium. It never reads a private launch token or calls owner verify/approve/apply/export endpoints. Synthetic runtime commands use `/preview` and `/execute`; they do not approve or apply a real change.

Status, 3 October 2026: the original stale-success defect was reproduced and retained. The corrected seven-stage replay passed on isolated Chromium 153 on Windows, with normal source-review identity, captured source unchanged, and browser/server closed. An earlier expanded attempt stopped on a replay navigation error before exercising runtime commands; it remains a separate failed run. This is scoped engineering evidence, not full IDE or human-usability acceptance.

## Run

On a Calvin personal endpoint, require the current browser-account-router device-status preflight to return ready first. Run serially from the checkout with its development/HCI environment and installed Playwright Chromium. In PowerShell:

```powershell
$env:PYTHONPATH = "$PWD/tests/hci;$PWD/src;$PWD"
# Set this only when Chromium is in a custom cache; use your actual installed path.
$env:PLAYWRIGHT_BROWSERS_PATH = 'E:\.dev-cache\ms-playwright'
.\.venv\Scripts\python.exe -u tests/hci/runtime_evidence_review.py --scenario all --out reports/runtime-evidence-review-1
```

Use a new output directory per run. Omitting `--scenario all` runs only the denied-after-success case. Python `-O` is refused because it disables assertions. Missing imports or browser binaries must remain a prerequisite failure, not a passing result.

## Independent oracles

Seven stages cover:

1. One visible creation entry at desktop and 320 width, without opening the sidebar.
2. Allowed Agent Propose followed by wrong-role SelectMeaning: real 409 ROLE_DENIED, unchanged persisted case/instance/audit/outbox, truthful latest result and retained owned diagnostic. The complete audit remains reachable in its disclosure.
3. Aborted transport: the fixture forwards no command, but the UI must still report unknown outcome and avoid automatic retry.
4. Invalid response after a real commit: `route.fetch` executes the actual request once; only the browser response is replaced with invalid JSON. Independent GETs prove the commit while the UI truthfully retains an unknown outcome.
5. Acknowledged commit followed by one case GET 503: preserve acknowledged result/state/effects, show refresh failure, and recover using GET without executing again.
6. Same-case refresh, reset, candidate edit and case switch isolation; keyboard History undo from Run and redo from Evidence compare complete server candidates.
7. Held execute request plus second keyboard activation: one actual POST and one persisted audit effect set, with exact pending identity and reachable restored focus.

The server-returned candidate defines action, role, state and required effects. Independent case GETs expose actual instances, audit events and outbox. Operation IDs are compared between actual requests and persisted audit bodies; this is not a direct database operations-table read. No successful response or state is fabricated. Fault modes and original failures remain in output.

The result records source before/after manifests, replay bytes and hash, request inventory, controlled responses, server GET oracles, screenshots and cleanup status. `unknown` is distinct from refused, committed and duplicate. A retained prior acknowledgement cannot masquerade as the latest result. Live providers, actual owner decisions, full mobile use and human comprehension remain untested.


## Open raw diagnostics keyboard check

The `diagnostics` scenario (also appended to `all`) checks the opened Run audit, global raw error,
and Evidence raw packet at1440x900,1280x800 and320x800. Run it in a fresh output directory:

```powershell
.\.venv\Scripts\python.exe -u tests/hci/runtime_evidence_review.py --scenario diagnostics --out reports/raw-diagnostics-keyboard-1
```

The packet and audit come from actual disposable-server GETs after one real allowed runtime command.
The raw error is an explicitly labelled one-GET503 **synthetic oversized diagnostic** so all widths
exercise actual overflow without changing product dimensions or manufacturing a kernel decision.
The fixture body is retained in fault controls; exact UI JSON is compared with it. Independent GETs
confirm the case, packet and persisted audit stay unchanged while navigating.

Each region must be entered with Tab from its native summary, show the existing focus outline, scroll
with PageDown, wait for the native scroll-end event, permit forward Tab and reverse Shift+Tab exit, and retain the exact raw text. The checker
refuses to count a non-overflowing region as scroll coverage. A temporary `tabindex=-1` control must
exclude the packet from sequential navigation; the original attribute is restored and positive entry
is rechecked. This is a behavioral keyboard control, not a mirror of the markup implementation.

At 320px, the same native scrolling checks cover the actual overflowing status notice on Run and
Evidence. Real Tab navigation must reach the named status, its full text must remain unchanged,
and Tab/Shift+Tab must leave it. Navigating to New intent clears and hides the empty notice.

Axe runs with these disclosures open on Run and Evidence at every width; all violations and incomplete
checks remain in `axe-open-raw-diagnostics.json`. Viewport and keyboard observations are retained in
`raw-diagnostics-keyboard.json`. A prior seven-stage runtime result does not cover this added
scenario: use the fresh diagnostics result and its exact source manifest. An absent execution is
NOT_RUN; automated keyboard/axe observations do not establish human usability or screen-reader acceptance.
