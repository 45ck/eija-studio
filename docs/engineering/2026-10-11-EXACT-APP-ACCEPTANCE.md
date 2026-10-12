# Exact generated-app approval checkpoint — 11 October 2026

This is an engineering checkpoint, **not release acceptance or legitimate owner
approval**. Exact generated-app review, a React frontend and standard record
navigation are implemented in the integration checkout. Focused core checks and
the React/responsive suite **PASS** within their recorded scopes; the final copy
change has separate passing checks. The fifth exact-app journey is now historical
because later frontend repairs changed its subject. On **12 October 2026**, the
eighth run passed both the exact-app and presentation-map browser tests on its
recorded subject. The later service-cohesion repair passed 70 focused checks and
changed the implementation identity, so that browser pass is now historical.
The ninth run passed both browser tests on the repaired implementation, and the
second full fast gate passed all 24 sessions. The release verification script's
tests passed, while its expected exit `2` preserves `SOURCE_REVIEW_REQUIRED`.
Legitimate source approval, clean wheel proof and new video remain open.
SD01–SD12 and UX01–UX08 remain open wherever their individual acceptance
observations have not been completed.

## Subject and scope

The Git baseline is `49a08ea` (`Make Play actions and trace inspection clearer`).
The new work is that revision **plus modified and untracked files**; the baseline
commit alone does not identify this tested implementation. Source changes were
held stable for the reported core run. Its retained text log does not include a
complete source hash manifest, so a final candidate manifest and final-tree gates
are still required. The later browser result has its own recorded build subject,
including historical implementation digest
`3addc01ed0da89e53708812e78d0ebc680d5e3fd310ba3767914d50c5890c151`;
it does not retroactively identify the earlier core run or the later React bundle.
The latest React evidence identifies JavaScript
`2b5beec9ac40d4cbb9dec1364d855a490026414d1a2616b185b2bc28e44dcab6` in
`outputs/react-browser-20261011/evidence.json`.
After the service-cohesion repair, the measured implementation is
`08d220be933c725a1e61bc9737af6da1eaa2475ac63d18535c77802b137dea65`.
Its retained source manifest is
`outputs/service-cohesion-final-source-20261012.json`, measured at
`2026-10-12T05:28:00.228813+00:00`; normal source trust remains false.

This record updates the implementation gap identified in the earlier
[integration checkpoint](2026-10-11-PLAYIDE-INTEGRATION.md): newly bound cases now
associate the generated build envelope and checker configuration with review.
That earlier checkpoint, its test counts, candidate wheel and recordings retain
their original subjects and do not become evidence for this later implementation.

| Implemented capability | Boundary |
|---|---|
| Exact generated-app selection | Owner-plan transfer sends an expected build digest; the server assembles and freezes its own matching candidate bundle. |
| Shared review identity | The optional versioned binding includes workflow, pack, data, screens, navigation, templates, React inputs/assets, installed implementation and checker configuration. Historical cases without it remain workflow-only. |
| Separate generated conformance | A sealed receipt records the generated checker's observed outcome. Kernel runtime checks and a submitted `PASS` label cannot replace that observation. |
| Explicit decision and atomic activation | Decisions bind case, baseline, decision kind, scope and complete subject. Active model, applied case and generated-app association commit together. |
| Freshness and recovery | Retained bytes and current identities are remeasured. Damaged captures are refused, not silently repaired. A failed check followed by a pass remains `CONFLICT`; recovery requires a new review case. |
| Generated React application | Bundled React/Mantine components call the generated app's API and EIJA runtime. Authored source, lockfile, licences, build manifest and emitted assets are retained. Running the packaged app does not require Node or a CDN. |
| Navigation and presentation map | Records, New record, record details and supported workflow actions derive from the existing contracts. The map is checked design. General record update/delete, arbitrary routes and production authentication remain unsupported. |

See [ADR-0224](../adr/0224-approve-the-exact-generated-application.md),
[ADR-0225](../adr/0225-react-for-generated-application-frontends.md),
[ADR-0226](../adr/0226-standard-record-navigation-and-presentation-map.md) and
the [architecture walkthrough](../architecture/PLAYIDE-EIJA-FLOW.md).

## Retained results

Paths beginning `outputs/` or `work/playide-design/` below are task-local evidence
under this chat's workspace, not files claimed to be distributed in the repository.
Separate runs are not added together into one passing suite.

| Observation | Result and evidence | Limit |
|---|---|---|
| Initial integrated focused run | **FAIL:** 197 passed, 2 failed, 1 deselected; `outputs/exact-app-core-focused-20261011.log` | A presentation test requested an interpretation its proposal had not supplied; the actual architecture-budget assertion also failed. The failed run remains retained. |
| Repaired focused core run | **PASS:** 94 passed, 1 deselected, 1 warning in 163.63 s; `outputs/exact-app-core-focused-final-20261011.log` | This later selected suite includes the repaired presentation/architecture checks and exact-app controls. It is not a rerun of all 199 initial tests or the complete release suite. Stronger presentation no-write assertions added afterward are covered by the separate 12-check result below. |
| Type checking | **PASS:** 152 source files; `outputs/exact-app-core-quality-final-20261011.log` | Static typing does not establish application behavior. |
| Architecture and complexity | **PASS:** 3 import contracts kept; xenon passed; 2,891 functions, 4 recorded debts and 0 ratchet violations; same quality log | The architecture-budget regression also needed its own test; import-contract success alone did not cover it. |
| Targeted Ruff | **PASS:** `outputs/exact-app-core-ruff-final-20261011.log` | Scoped lint, not whole-product acceptance. |
| Deliberately broken exact-app controls | **PASS within the 94:** 14 paired outcomes covering seven scenarios; [test source](../../tests/test_exact_app_mutations.py) | Seven real-implementation controls plus seven unsafe mutant detections, not fourteen distinct faults. Owner authority and runner observations are explicit synthetic fixtures; these tests exercise actual Studio/SQLite behavior. |
| Actual retained generated checker | **PASS within the 94:** [test source](../../tests/test_generated_app_approval.py) runs the generated unittest subprocess against the retained artifact, including a poisoned timestamp-valid bytecode cache | Actual subprocess evidence is separate from the mutation tests' synthetic runner observations. Owner approval in the test remains synthetic. |
| Current React static/controller/build checks | **PASS:** 32 Python checks, 5 deselected in 1.07 s; 16 Node checks; pinned build and `--check`; `outputs/react-browser-20261011/static-record-name.log`, `controller-record-name.log`, `build-record-name.log` | Current `2b5bee…` bundle. Static/controller checks are separate from rendered browser observations. |
| Initial React/responsive integration | **FAIL:** 32 passed, 3 failed in 174.72 s; `outputs/react-browser-20261011/combined-first.log` | Actual refusal-ARIA and typed-title defects, plus an outdated toolbar-overflow assumption. |
| Failed React repair attempt | **FAIL:** 1 passed, 2 failed in 79.71 s; `outputs/react-browser-20261011/targeted-repair.log` | `withAria=false` also removed the native control ID; this attempted repair remains a failure. |
| Native-control repair and complete scoped suite | **PASS:** targeted 3 in 19.86 s, then full 35 in 125.17 s; `outputs/react-browser-20261011/targeted-repair-2.log`, `combined-final.log` | Bundle `b12293…`: 24 generated-app browser cases, 8 workbench browser cases and 3 non-browser shell checks. There are 32 actual browser cases, not 35. |
| Final Record name copy change | **PASS:** 3 browser checks in 16.15 s; `outputs/react-browser-20261011/targeted-record-name-3.log` | Current `2b5bee…` bundle. This scoped delta confirmation does not relabel the preceding full-35 run as a run on the final bytes. |
| Combined browser attempt four | **FAIL:** 1 failed in 38.44 s; `outputs/raw/exact-app-browser-proof/exact-app-journey-fourth.log` | The final strict page-error assertion caught `The model changed since the page loaded; reload and try again`. Passing preceding steps do not turn this into an overall pass. |
| Repaired exact-app browser attempt five | **HISTORICAL PASS:** 1 passed in 35.41 s; `outputs/raw/exact-app-browser-proof/exact-app-journey-fifth.log`, `journey-result.json` and `final-manifest.json` in the same directory | Exact labels, negative controls, synthetic approval, activation, fresh-process reopen and React actions passed with zero errors/CSP. Later React repairs changed this subject; attempt eight provides fresh combined evidence. |
| Combined browser attempt six | **FAIL:** 1 passed, 1 failed in 58.14 s; `outputs/raw/exact-app-browser-proof/exact-app-and-map-sixth.log` | A string-evaluating test wait was correctly blocked by CSP. Retained console observations also exposed a real missing presentation-asset registration, producing 404/MIME errors. |
| Presentation asset and authority regressions | **PASS:** 12 checks in 2.66 s; [test source](../../tests/test_presentation.py) | Includes stronger denied-authority audit/outbox/operation count equality and exact HTTP asset body, MIME, nosniff, CSP and backup-name refusal checks. Separate from the earlier 94-check run. |
| Combined browser attempt seven | **FAIL:** 2 failed in 39.14 s; `outputs/raw/exact-app-browser-proof/exact-app-and-map-seventh.log` | The strict console oracle caught an incomplete Systems test fixture. The map test also misunderstood the canonical native accessible name around Mantine's decorative required asterisk. Both test defects were repaired without suppressing errors or weakening name assertions. |
| Combined browser attempt eight — 12 October | **HISTORICAL PASS:** 2 actual browser tests, 1 warning in 58.95 s; `outputs/raw/exact-app-browser-proof/exact-app-and-map-eighth.log`, `journey-result-eighth.json` and `final-manifest-eighth.json` | Implementation `329ce6…` and frontend `2b5bee…`; full exact-app journey and actual presentation map passed with zero page errors, all-frame CSP violations and unexpected console records. Three deliberate case-409 refusals remain recorded. The later service repair changed the implementation subject. Synthetic-owner mechanics, not legitimate owner approval. |
| Normal source authority | **OPEN:** `SOURCE_REVIEW_REQUIRED` remains enforced | No trusted-source fixture was restamped, no normal owner approval was fabricated, and synthetic fixtures do not authorize the checkout. |
| First aggregate fast gate — 12 October | **FAIL:** 24 sessions, 22 successful and 2 failed (`tests`, `diagrams_drift`); `outputs/exact-app-fast-final-20261012.log` | Default pytest: 4 failed, 3,324 passed, 219 skipped, 2 xfailed and 22 warnings in 334.13 s. Three failures were class-diagram drift; one was an actual maintainability-budget failure. |
| Reviewed class-diagram refresh | **PASS:** 98 diagram tests in 0.92 s; all 12 generated documentation files match; `outputs/class-diagram-refresh-20261012/` | Only the three affected class projections were regenerated after inspection. Implementation identity stayed `329ce6…`; this scoped repair does not clear the aggregate gate. |
| Service-cohesion repair | **PASS:** 70 focused checks, 1 warning in 158.23 s; `outputs/service-cohesion-core-final-20261012.log` | Implementation `08d220…`; structural measurement records service MI `20.394` against the unchanged minimum `20`. This focused run does not turn the failed first aggregate into a pass. |
| Current combined browser attempt nine — 12 October | **PASS:** 2 actual browser tests, 1 warning in 56.11 s; `outputs/raw/exact-app-browser-proof/exact-app-and-map-ninth.log`, `journey-result-ninth.json` and `final-manifest-ninth.json` | Implementation `08d220…`; fresh exact-app review/activation/restart/runtime and presentation-map checks passed. Zero page errors, all-frame CSP violations and unexpected console records; only three exact deliberate case-409 refusals. Synthetic-owner mechanics remain separate from legitimate owner approval. |
| Complete knowledge-file check | **PASS:** 1,002 pages, 0 stale source pages and 0 stale Notes pages; `outputs/okf-final-check-20261012.log` | Recorded trust tiers remain 47 machine-confirmed and 955 unverified, with 78 curated-Notes pages. Structural freshness does not establish source approval or application behavior. |
| Second aggregate fast gate — 12 October | **PASS:** all 24 sessions, exit `0`, approximately 8 minutes; `outputs/exact-app-fast-final-20261012-2.log` | Main pytest: 3,328 passed, 219 skipped, 2 xfailed and 22 warnings in 325.69 s. This is the current repaired implementation's fast gate; skipped and expected-failure cases are not counted as passes. The first failed run remains retained. |
| Release verification script — 12 October | **TESTS PASS / SOURCE REVIEW REQUIRED:** script exit `2`, `tests_exit_code: 0`; 3,328 passed, 219 skipped, 2 xfailed and 22 warnings in 317.01 s; `outputs/exact-app-release-final-20261012.log` | Exact implementation `08d220…`, `trusted_fixture: false`, `source_review: SOURCE_REVIEW_REQUIRED`; live providers `NOT_TESTED_BY_THIS_SCRIPT`. This is not full release acceptance or a run of the complete nox release session set. |
| Clean wheel and video | **PENDING** | Passing tests and the visible source-review block establish neither clean installation nor recording completion. Earlier isolated Windows-wheel results belong to earlier source. |

The core log retains a Starlette/AnyIO deprecation warning. Deselected, skipped or
unrun work is excluded from the passed-test count.

The 94-test command used the pinned capture-environment Python from the repository:

```text
../capture-env/Scripts/python.exe -u -m pytest -q tests/test_generated_app_approval.py tests/test_exact_app_mutations.py tests/test_build_subject.py tests/test_generated_subject_runtime.py tests/test_navigation.py tests/test_presentation.py tests/metrics/test_metrics_structure.py::test_architecture_budgets_pass_on_the_real_tree
```

The initial architecture failure was the actual `ARCH-03` stable-dependency
budget (`0.941 < 0.950`). Its repair injected the application-owned generation
and validation callbacks through bootstrap; the threshold was not relaxed.

The seven deliberate faults are: accepting the wrong inspected digest, accepting
a failed checker observation, reusing another case's signed decision, omitting the
post-seal payload check, omitting the post-seal measured-implementation check,
losing the atomic app association, and skipping retained-payload validation.
Each mutated callable must reach a specific unsafe approval, activation or stored
state before the independent behavioral assertion detects it. An unrelated
exception or source hash change cannot count as detection. This is a visible,
same-author fault set, not an independent hidden evaluation.

## Browser observations and repaired defects

The fourth and fifth browser attempts used the pinned capture environment:

```text
EIJA_BROWSER_TESTS=1
../capture-env/Scripts/python.exe -X utf8 -m pytest -o addopts= tests/test_exact_app_journey.py -q
```

Before the final failure, assertions passed for the unsafe-model refusal without
writes; an ordinary Renew edit and UML diff; exact build transfer; denied agent
approval and incorrect understanding answers; explicit synthetic owner approval;
tampered-bundle activation refusal without writes; exact-byte restoration,
recheck and reapproval; activation and duplicate refusal; and reopening the same
workspace in a new Python process with the same subject and `ACTIVE_APPROVED`.
The reopened React app then created a record and performed
CheckOut → MarkOverdue → Renew, with API version/history and live-trace agreement.
Observed CSP violation lists were empty across the page's frames.

After repair, attempt five repeated the full journey and passed its final strict
error/CSP checks. It also passed exact accessible-label selection for From, To,
Action and Who may take it, plus the Move Return/to state controls and their
ARIA-label equality checks. The retained result identifies two actual Python
processes (`41964` then `20204`), active revision `1`, and unchanged full app
subject `d86c3a96987b28d6775d4506fec8975d0015df74ae43f3059f28fc7ced3c04a8`.
Its final record is `OnLoan` at version `3`, with three matching committed trace
observations. The fifth manifest retains that outcome; `attempts.json` now
preserves all eight attempts, and earlier failures remain failures.
This passing fifth run remains historical after the subsequent React repairs.

Those are scoped observations from an **isolated synthetic-owner engineering
fixture**. The journey uses ordinary controls for the product flow, plus explicit
API assertions and deliberate disk mutation for negative checks. It is not a real
owner's approval, an installed-wheel browser test or production authentication.

The unhandled stale-model page error was a real product defect. Activation retired
the draft before installing the new base model; the resulting redraw requested
screens for the old model and left the server's correct `MODEL_CHANGED` refusal
uncaught. A separate real accessibility defect contaminated labels with wrapped
help/control text. The retained observation is
`outputs/raw/exact-app-browser-proof/exact-form-dom.json`. Both defects were
repaired and the fifth run confirmed the actual controls with the strict
no-page-error oracle retained. The first three attempts' stopping points also
involved test locator/selection defects; their logs remain in the same directory.

### Update — 12 October 2026

The eighth combined run began at `2026-10-12T05:02:44.3709986Z` and finished at
`2026-10-12T05:03:44.661393Z`, as retained in
`outputs/raw/exact-app-browser-proof/exact-app-and-map-eighth-times.json`.
It passed **two actual browser tests in 58.95 seconds**. The immutable
`final-manifest-eighth.json` records the dirty candidate above, implementation
`329ce60d20a49c85ca9590b906f4dd7fa614d15eecf65a52bb3d98b1ef098f84`,
frontend `2b5beec9ac40d4cbb9dec1364d855a490026414d1a2616b185b2bc28e44dcab6`
and exact generated-app subject
`a1aa0b9834655256cbdc724ea4c4bed75327d59c6dcee2d9ae87d5e694c34e6e`.
The observed Python process changed from `24504` to `33564`; active revision `1`
and the complete approved subject survived the reopen.

This run repeated exact typed-draft transfer, UML inspection, unsafe-model and
authority refusals without writes, retained-payload tamper refusal, exact-byte
restoration and reapproval, atomic activation and duplicate refusal. The reopened
React application created a record and committed CheckOut → MarkOverdue → Renew,
with record version, history and live traces agreeing. The actual presentation
map started collapsed, matched the running subject and linked its use case,
record class and design screen. Rendered field order, native input types, exact
accessible names, associated labels and required semantics matched the checked
design. Detail navigation was disabled without a record; New record focus and
the current navigation item were observed. Page errors, all-frame CSP violations
and unexpected console records were zero; three exact intentional case-409
refusal records were retained. Source approval remains synthetic.

The sixth and seventh failures explain the repairs this pass exercises. Attempt
six used a string-evaluating wait that normal CSP correctly refused; its replacement
uses a function predicate. It also exposed a real product delivery defect:
`play-presentation.js` and `play-presentation.css` were absent from the HTTP asset
allowlist. The repair registered only those exact assets, preserving CSP and
other response protections. Twelve separate non-browser checks passed, including
the new delivery/security regression and stronger authority no-write assertions.

In attempt seven, the stricter console oracle caught `/api/play/systems` returning
404 in the synthetic fixture. The normal CLI already wires the actual Systems
services; the fixture omitted them. The corrected fixture now uses that real
composition. A separate HTTP smoke check passed in 0.79 seconds, covering refused
unauthenticated access, current/template/draft listings and no durable domain
writes. The map's other failure was a test-oracle error around the required
asterisk: the corrected test checks canonical exact native accessible names,
label/control IDs and required semantics, respecting the decorative hidden mark.
It does not substitute fuzzy labels. The sixth/seventh logs and result JSON remain
unchanged; security settings and strict unexpected-console checks remain intact.

## React and responsive observations

`outputs/react-browser-20261011/evidence.json` retains the exact source, lock,
licence, build-manifest and asset hashes, separate result logs and 14 screenshots.
The full 35-check run used JavaScript
`b122933725ae72b8600a6ea87272ced3399563cca3ad6dddd7860b72981270ef`.
Generated-app browser contexts asserted zero page errors and CSP messages;
coverage included narrow/wide, dark/light and reduced-motion viewports, keyboard
focus/cancellation, stale/read recovery, record actions and no-write trace replay.
Viewport emulation does not establish physical-device or screen-reader usability.

The initial run found two actual defects: Mantine overrode the server-refusal
invalid-title ARIA association, and a typed attribute named `title` shared an
update path with display metadata. The first attempted ARIA repair disabled
native IDs with `withAria=false` and failed two targeted checks. The successful
repair preserved Mantine's native ID, label, required, disabled and error semantics,
overriding only the input description for the existing server-error notice.
Separate typed-field and metadata updates fixed the persisted-value collision.
The toolbar test was corrected to check fit at 1100 pixels and actual overflow
menu behavior at 760 pixels, rather than require overflow where the revised bar fit.

After that full pass, only generic metadata copy changed from Title to Record name
and its placeholder changed. Controller, CSS, APIs, policy and canonical typed-field
labels did not change. The current `2b5bee…` bundle passed three scoped browser
checks, 32 static checks, 16 controller checks and the pinned asset rebuild/check.
Two intervening selector failures remain in `targeted-record-name.log` and
`targeted-record-name-2.log` (each 2 passed, 1 failed): one included the decorative
required asterisk, and one guessed the wrong canonical field-label case.
The successful test uses actual accessible names and independently checks
distinct control IDs, native semantics, refusal recovery and persisted values.
The 14 retained screenshots belong to the preceding `b12293…` full-suite subject;
current-app footage is a separate pending artifact.

## First aggregate failure — 12 October 2026

The first final-candidate fast gate failed two of its 24 sessions: `tests` and
`diagrams_drift`. The default pytest run recorded **4 failed, 3,324 passed,
219 skipped, 2 xfailed and 22 warnings in 334.13 seconds**, preserved in
`outputs/exact-app-fast-final-20261012.log`.

Three failures were expected-artifact drift from the new optional
`ChangeCase.app_build` member. The class-only candidate diffs were reviewed before
regenerating the two class goldens and class documentation. The retained review,
diff and logs are in `outputs/class-diagram-refresh-20261012/`. All 98 diagram
tests then passed and all 12 generated documentation files matched. That
documentation-only repair retained implementation identity `329ce6…`; it neither
changed runtime meaning nor expanded the class projection's eight-contract scope.

The fourth failure was a real `MI-01` maintainability regression in
`application.service`: its index fell from `20.090` to `7.982`, below the required
`20`. The cyclomatic-complexity ratchet passed, but that separate result does not
clear the maintainability failure.

The subsequent service-cohesion repair extracted the read facade into
`StudioViews`, retaining command ownership and approval/application authority in
the service. The structural record in `outputs/service-cohesion-structural.json`
reports service MI **20.394** against the unchanged minimum **20**. No budget,
ignore or authority rule was relaxed. The focused post-repair run passed
**70 checks with 1 warning in 158.23 seconds**, retained in
`outputs/service-cohesion-core-final-20261012.log`. The new implementation identity
is `08d220be933c725a1e61bc9737af6da1eaa2475ac63d18535c77802b137dea65`.

The eighth browser pass remains evidence for its recorded `329ce6…` subject and
is now historical for this changed implementation. The ninth browser run passed
on the repaired implementation; neither that result nor the focused 70-check run
relabels the first failed aggregate. The second full fast gate subsequently passed,
as recorded below. Release verification's tests also passed, with source review
still required. Clean-install and new-video acceptance remain pending their own
results.

## Fresh browser proof after service repair — 12 October 2026

The ninth run passed **two actual browser tests in 56.11 seconds**, retaining one
Starlette/AnyIO deprecation warning. It ran from
`2026-10-12T05:33:40.1406334Z` to `2026-10-12T05:34:38.3222753Z` with exit code `0`.
Its immutable `outputs/raw/exact-app-browser-proof/final-manifest-ninth.json`
records implementation
`08d220be933c725a1e61bc9737af6da1eaa2475ac63d18535c77802b137dea65`,
unchanged frontend `2b5bee…` and exact generated-app subject
`69106fc191eb6abe5856bdf9928399f26e4390371b96ccc8a17451b44f9c341a`.
The actual Python process changed from `25680` to `45340`, preserving active
revision `1` and the complete reviewed app subject.

The run repeated the same exact-transfer, negative-authority, payload-tamper,
recovery, activation, duplicate-refusal, reopen and three-action runtime checks,
plus the actual presentation map's subject, navigation and native-control
contracts. Record state, version, history and live traces agreed. Page errors,
all-frame CSP messages/violations and unexpected console records were zero;
three exact deliberate case-409 refusal records remain visible. The Systems
fixture bytes were unchanged and the actual route produced no unexpected 404.
Its earlier standalone HTTP smoke remains historical rather than counted as a
new run. The manifest retains test/helper, service, read-facade and generated
frontend byte snapshots. `attempts.json` preserves all nine outcomes.

This is fresh local browser evidence under explicit synthetic-owner authority.
Normal `SOURCE_REVIEW_REQUIRED` remains enforced. It is not a recording,
clean-wheel proof, deployment or full SD/UX acceptance.

## Passing fast gate after repair — 12 October 2026

The complete second fast run passed **all 24 sessions** with exit code `0` in
approximately eight minutes. Its main pytest session recorded **3,328 passed,
219 skipped, 2 xfailed and 22 warnings in 325.69 seconds**. The full retained log is
`outputs/exact-app-fast-final-20261012-2.log`; it does not replace the first failed
log. The repaired diagram, architecture/maintainability and default-test gates
are included in this passing run.

This is the configured fast scope. Opt-in property and HCI/browser work, missing
optional formal tools, unavailable POSIX tooling and other skipped checks remain
excluded from its passing count. Documentation/demo-registry success and retained
historical HCI material do not establish new current-product browser observations;
those are recorded separately in the ninth browser manifest. Separate scoped
suite counts are not added to the main pytest count.

The release verification script subsequently completed using
`PYTEST_ADDOPTS='-n4 --dist loadfile'`. Its tests returned `0`, with **3,328 passed,
219 skipped, 2 xfailed and 22 warnings in 317.01 seconds**. The script itself
returned the expected exit code **2** because source review remains required;
that exit is not a test failure or full release approval. The retained output is
`outputs/exact-app-release-final-20261012.log`.

The report identifies implementation
`08d220be933c725a1e61bc9737af6da1eaa2475ac63d18535c77802b137dea65`,
`trusted_fixture: false`, `source_review: SOURCE_REVIEW_REQUIRED` and
`live_providers: NOT_TESTED_BY_THIS_SCRIPT`. No trusted fixture was stamped to
change that outcome. This script is distinct from the complete nox release
session set, which was not run here. These tests, the passing fast gate and the
separate browser runs retain their own scopes and counts.

## Acceptance still required

1. Complete legitimate owner source review and applicable remaining release,
   packaging and clean-install checks on the identified candidate. Keep the
   observed source-review gate separate from test
   failures. Preserve the eighth browser subject and all earlier outcomes; do not
   transfer approval/restart proof to later changed assets or substitute the
   earlier candidate wheel.
2. Complete and inspect a new actual-app recording for this exact-app/React slice.
   `outputs/16-play-polish.mp4` was shared for the earlier polish checkpoint and
   does not demonstrate this later approval or React implementation.
3. Complete the applicable [SD/UX acceptance rows](SELF-DOGFOOD-ACCEPTANCE.md),
   including keyboard and enlarged-text use, non-linear recovery, useful failure
   diagnosis and response times. Human comprehension and comparative builder
   performance remain unmeasured.

Structural links, model simulation, bounded conformance, observed browser
behavior and human understanding remain separate claims. No live provider,
external delivery/payment, migration, production deployment or legitimate owner
source approval is established by this checkpoint.

Recovery covers parseable but invalid active associations and missing, unselected
or mismatched cases. Arbitrarily corrupted SQLite/JSON bytes are not repaired and
may make a workspace unavailable; restore and physical-store repair are outside
this slice. Build identity is checked at capture, checking, approval, activation,
reopen/build and startup, rather than continuously against hostile filesystem
mutation. A malformed custom frontend manifest can also fail the read-only C4
projection; canonical generated manifests are the supported input here.
