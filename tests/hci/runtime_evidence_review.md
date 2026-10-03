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

## Evidence triage keyboard check

The `triage` scenario is a new, separately source-bound group, also appended to `all`. At authoring it is **NOT_RUN**; earlier runtime and diagnostics records do not validate it. It uses the same normal-identity disposable server and existing UI/GET helpers:

```powershell
$env:PYTHONPATH = (Get-Location).Path + ';' + (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -u tests/hci/runtime_evidence_review.py --scenario triage --out reports/evidence-triage-keyboard-1
```

The explicit import path includes the checkout-owned `quality` package and `src`.

Setup creates and selects the real saved-path candidate using the ordinary offline controls. It runs no verification, runtime command or owner action. The independently fetched packet must actually report `SOURCE_REVIEW_REQUIRED` and `RUNTIME_EVIDENCE_UNKNOWN`; successful packet or evidence responses are never substituted. The current technical and formal records, their statuses, indices and order are taken from that packet.

At 1280×800 and 320×800, the scenario verifies the triage's exact blocker inventory/order and case/revision/subject. Starting at ordinary Evidence navigation, actual Tab presses must reach each native action; Enter must open Problems and focus its exact source restriction, or open/focus the existing runtime-matrix check. Each reached control and focused destination must show a focus outline and lie inside the actual ancestor-clipped viewport. The native **Exact blocker codes** disclosure is reached with Tab and opened with Enter before its visible text is compared with the server's exact codes. Horizontal page overflow is rejected.

The scenario keeps Model's Verify selection distinct from comparison's Save selection, preserves the case-wide scope and human UNKNOWN, and rechecks every reported technical/formal status plus the complete raw packet after navigation. Independent GETs compare the full case view, observations, packet and semantic history; no write beyond setup is allowed. Navigation/focus geometry, screenshots and independent oracles are retained alongside the existing source manifests and cleanup status.

This is a native keyboard/navigation and data-retention check, not a human comprehension study. It does not claim that every triage row fits simultaneously above the fold on narrow screens: entry screenshots retain that layout for inspection, while each action/destination must be genuinely visible when reached by keyboard. It adds no axe result; the separate opened-raw-diagnostics scenario retains that scope. Malformed packets, duplicate formal records, mismatched statuses and stale callback counterexamples remain explicitly Node-level coverage in `evidence-overview.test.cjs`, not browser fixtures in this group.

## Formal record inspection

These two separate scenarios are **NOT_RUN until executed on the integrated source**. They extend this
same replay, disposable server and isolated browser; neither is appended to `all` because their setup
and evidence claims differ. Run serially, using a fresh output directory for each:

```powershell
$env:PYTHONPATH = (Get-Location).Path + ';' + (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -u tests/hci/runtime_evidence_review.py --scenario formal-unavailable --out reports/formal-unavailable-1
.\.venv\Scripts\python.exe -u tests/hci/runtime_evidence_review.py --scenario formal-recorded --out reports/formal-recorded-1
```

`formal-unavailable` exercises the ordinary EIJA self-dogfood flow. It creates/selects the offline
candidate through existing controls, then inspects the actual server's UNKNOWN formal rows at
1280×800 and 320×800. No deciding receipts means no artifact or records: `NO_DECIDING_RECEIPT`
must remain visible, with `SOURCE_REVIEW_REQUIRED` unchanged. EIJA's declared `not_run` formal
verifiers are not promoted to passing results. No writes are permitted after candidate setup.

`formal-recorded` is an explicitly labelled **recorded excursion fixture inspection**, not EIJA
verification or an external-repository pilot. A callback runs only inside the fresh throw-away
workspace, before HTTP starts. It uses the normal identity, real `FormalReports` adapters and
`application.formal.attach` with the workspace signer's public method to seal the existing recorded
artifacts. It inserts two validated PREVIEW fixture cases: one with those receipts, one without.
It calls no verify/approve/apply/export endpoint, substitutes no identity/authenticator, inspects no
private launch token or receipt key, and runs no solver. The server then exposes those cases through
the ordinary API. Every observed browser request after setup must be GET.

The required recorded reports are:

- `verification/bend/evidence/bend.json`
- `reports/formal/smt.json`
- `reports/formal/bmc.json`

The Bend adapter also requires the existing `main.bend`, `LAWS.bend`, `PROOF.bend` and
`bend_generate.py` under `verification/bend`. These inputs are hashed before and after the run;
normalized artifact hashes and LF-normalized report hashes are retained in
`recorded-fixture-provenance.json`. Missing inputs or reports unreadable through their adapters
produce **NOT_RUN**, exit 2, before HTTP/browser startup. The replay never synthesizes replacement
reports. The SMT/BMC reports are generated prerequisites, so a fresh checkout without them cannot
claim this scenario passed. Preparing those reports belongs to their documented verification lanes.

The recorded reports inspected when writing this scenario contain passing positive results and
negative controls. Bend's first control is the recorded Teacher Submit → Recommend → Approve
sequence. SMT's first named control removes the Approve role restriction and retains its reduced
transition witness. This is not a supplied Workflow specimen; its model availability stays
`not_provided`. BMC's mutation controls retain only `mutant` and `detected`, with no recorded steps;
both searched models have empty counterexample lists. These controls must not be presented as a
failure of the current candidate, an executed current-model path, or fresh solver evidence.

Independent authenticated GETs supply the complete case, packet, original receipts and semantic
history. For every displayed item, the checker resolves its JSON Pointer directly into the deciding
receipt's artifact and compares raw JSON; it computes the expected control inventory directly from
that artifact and recomputes its hash. Review case/revision/scope, full subject and pack digest stay
separate from receipt identity. It compares every ordered step without guessing graph/source
references. No current-model or source navigation is admitted by this contract.

At both widths, actual Tab traversal reaches native summaries; Enter/Space opens and closes them.
The first item of each kind, complete artifact, and full review/receipt subjects are inspected via
focusable raw regions. PageDown is checked only where actual overflow exists, with forward and
reverse keyboard exit and unchanged JSON. Focus must be visible inside ancestor clipping and page
overflow is rejected. Case switching while an inspection is open must show the other case's genuine
absence, with no stale records or open inspection carried back. Full GET case/history/observations
and all original statuses stay unchanged. Screenshots, keyboard geometry, requests, original
report identities and GET oracles are retained with the existing source manifests and cleanup proof.

This covers recorded-artifact display, keyboard access and ordinary case isolation. Malformed or
mismatched inspection payloads remain Node-level counterexamples; this browser run does not fake
them. Fresh verification, a current-candidate failing trace, full mobile usability, axe/screen-reader
acceptance and reduced human comprehension burden remain untested by these scenarios.
