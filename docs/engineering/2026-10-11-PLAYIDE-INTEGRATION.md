# PlayIDE integration checkpoint — 11 October 2026

This is an in-progress engineering record, not release acceptance. It covers the
local activation, design, generated-build identity, live-action trace and C4 work
being integrated under the [delivery contract](PLAYIDE-DELIVERY.md). The
[self-dogfood contract](SELF-DOGFOOD-ACCEPTANCE.md) remains the authority for
SD01–SD12 and UX01–UX08; those rows have not all been re-exercised here.

## Subject and environment

- Git baseline: `87dc953b222878f95453092ddafb88ff1cf67cfd`.
- Subject: that baseline **plus staged, unstaged and untracked changes** in the
  integration checkout. These changes are not represented by the baseline commit.
  Other contributors' pre-existing changes remain in the checkout.
- The final implementation is now retained in commit
  `01b959b512cec71fa20b55ded9bd7710b4b3b5c0`; the isolated installation probes are
  retained in `9b4d31cf48d02955ccbbfa562f8126d95e64c3d3`. The final tests below
  measured implementation `640a2f78ddff5838e9fd5e8cc9a3c20e638cf01da371b31202656fca214b295a`.
  Earlier recordings still identify their own pre-commit subjects.
- Exercised environment: Windows, Python 3.12.10, Playwright 1.63.0 and Chrome
  154.0.8037.99. Browser runs use fresh unsigned contexts, loopback applications,
  the normal CSP and synthetic fixture actors.
- Logs and capture records named below are retained in the task's
  `work/playide-design` evidence directory, outside the repository. A portable
  release evidence archive is still required; these names are not public links.

Each run has its own subject. For example, the failed capture preflight
`raw/15-live-c4-readme-sanity/20261011T063256707182Z` retains a source manifest
with implementation digest
`138068a19d829d0b276ad84678fe0d0b7f7ffb4884acf57b10c40da60ab2f6ae`
and generated-template digest
`fa73637049c953e6225b03d1083836e863cd1e843a73b51aa8b3e73ff0aa552f`.
It is **FAIL**, not demo evidence. Neither digest identifies subsequent edits or
a frozen release candidate. Freeze and retain the final dirty-content manifest
before recording or claiming integrated release results.

The later accepted demo is a separate, retained subject. Its
[public manifest](../demos/assets/playide-live-20261011/manifest.json) records
implementation
`a1529ef54662bcfb01e73818f94cc7a55ffdc89bc28f1e6f1c2eab7caed1c818`
and generated build
`ead8ab7e8bcbc1164aef969f6d426bd064894048b2ff8d2cf15fc30307f226d2`.
Source stayed unchanged during that capture. It remains a dirty-tree subject,
not evidence that the baseline commit alone contains these capabilities.
The subsequent dependency-direction repair changes implementation bytes again.
The accepted video remains valid for its named earlier subject; it is not a
recording of that later repair or a current release verification result.

## Progress by outcome

| Outcome | Implemented | Integrated | Exercised | Release-ready |
|---|---|---|---|---|
| M0: exact workflow draft transfer and activation contracts | Owner-plan selection, identities, service checks and review UI exist | Present in the working tree | Direct-service, SQLite and fault controls have dedicated evidence; see [activation evidence](PLAYIDE-ACTIVATION-EVIDENCE.md) | No: source review and final integrated acceptance remain open |
| M0: generated-build and evidence identity | Build subject includes generated contracts/payload and templates; measured implementation includes appgen templates | Connected to generation, startup and conformance, with independent before/after checks | Focused identity/C4 checks, final fast tier and release-script tests pass; substitution controls are scoped below | Frozen candidate measured; release script exits 2 for SOURCE_REVIEW_REQUIRED; owner source review open |
| M1: shared review/build association | Exact workflow review and generated-build identities both exist | **PARTIAL:** review does not reference the generated build subject | Identity tests exercise their respective boundaries; no unified review/build association is established | Pending forward-compatible association and its checks |
| M1: Design + Play and shared generated-app craft | Paired/stacked layout, readable rules, focus, busy/refusal and explicit read recovery | Existing kernel and shared templates reused | Generated-app and shell browser checks; earlier design capture retains its own revision | Final whole-workbench UX acceptance pending |
| M1: actual local actions on the diagram | Confirmed app observations, selected-record trace and local replay controls | Generated app and parent workbench connected | Two repaired real-browser journeys pass; sender/receiver negative controls and inspected demo retained | Scoped demo accepted; final gates and whole-workbench acceptance pending |
| M1: C4 alongside UML and domain meaning | Generated architecture view and subject-bound structural response | Native tab binding repaired; API/view connected | Native-tab browser regression passes; inspected demo drills through all three C4 views | Scoped demo accepted; full M1 and release acceptance remain open |
| M1: task continuity and failed-request recovery | Presentation restoration and explicit editing of a failed request | Existing draft history and composer reused | Three focused browser recovery tests pass after harness repair | Does not close all SD/UX rows |
| Candidate distribution on Windows | Authored packs and required resources bundled; isolated installation probe | Wheel built from the measured source | Fresh Python 3.12.10 environment, offline installation and bounded HTTP/application checks pass | Windows candidate-install scope only; installed browser, other platforms and strict release probe remain NOT_RUN |

Capabilities remain bounded. Workflow actions execute; C4 and domain vocabulary
describe known structure. Requirement prose, schema, law and screen drafts do
not silently become active policy. Current local apps have fixture role pickers;
timer, agent and payment names do not establish real clocks, agents or payments.
Typed action inputs, record updates, value conditions, relationships, external
delivery, production operations and broad source transformation require later
semantics and evidence.

The review subject still binds implementation, policy, environment, harness,
workflow semantics and layout. Owner-plan selection additionally retains pack,
baseline, candidate and command identities. Generated build/C4/runtime identity
uses `eija.build-subject.v1`, including data, screens and generated payload. The
review packet does **not** currently reference that build digest. Including
templates in implementation freshness improves the existing review gate; it does
not make these two subject contracts identical. M1 therefore provides exact
workflow review alongside generated-build observations, with their shared
association **PARTIAL**. Any later association must be forward-compatible and
preserve historical receipts, decisions and replay.

## Retained observations

| Record | Observed result | Interpretation |
|---|---|---|
| `implementation-browser-integration.log` | 42 passed, 33 deselected | Non-browser subset: default pytest addopts excluded browser tests despite the browser environment flag |
| `implementation-browser-all.log` | 70 passed, 5 failed | Two live-trace journeys and three new recovery tests failed; retained rather than replaced |
| `live-frame-regression-before.log` | 20 passed, 1 failed | Receiver regression reproduced before repair |
| `live-frame-regression-after.log` | 32 passed | Sender/receiver unit checks after repair; isolated doubles do not establish browser/SQLite behavior |
| `live-frame-browser-after.log` | 2 passed | Re-exercised the two failed real-browser live-trace journeys after repair |
| `recovery-browser-repair.log` | 3 passed | Re-exercised the three recovery tests after correcting Playwright handler registration |
| `runtime-sender-light-checks.log` | 10 Node tests and 21 Python tests passed; 1 deselected | Sender/template and static-check scope only; earlier two synchronization failures retained in the record |
| `generated-browser-confirmation.log` | 21 passed, 20 deselected | Earlier shared-template design pass, including the existing accessibility audit; not a fresh pass for all later changes |
| `implementation-fast-baseline.log` | Fast tier failed; unit session: 7 failed, 3,214 passed, 219 skipped, 2 xfailed, 1 error | Lint, architecture, complexity and test failures were observed during integration. Repairs require their own current-tree confirmation |
| `implementation-fast-frozen.log` | **FAIL**: 23 of 24 sessions passed; test session: 3,251 passed, 219 skipped, 2 xfailed, 1 failed | The remaining failure is `tests/metrics/test_metrics_structure.py::test_architecture_budgets_pass_on_the_real_tree`; the separate import-contract session passed |
| `implementation-fast-final.log` | **PASS**: all 24 fast-tier sessions; test session: 3,252 passed, 219 skipped, 2 xfailed, 22 warnings, 284.99 seconds | Fresh frozen implementation `640a2f78ddff5838e9fd5e8cc9a3c20e638cf01da371b31202656fca214b295a`; earlier failed runs remain retained |
| `implementation-browser-final.log` | **PASS**: 3 passed, 1 warning, 26.23 seconds | Actual-browser checkpoint on the post-refactor source; not installed-wheel browser acceptance or all SD/UX journeys |
| `verify-release.log` | 3,202 passed, 219 skipped, 95 deselected, 2 xfailed; `SOURCE_REVIEW_REQUIRED` | Earlier implementation `04bc2ae7b9cc5faf6ee646bb72f51aac46b6d5eace086fb78c2a085d84dc9edb`; not release verification of the later integrated tree |
| `verify-release-final.log` and [last verification](../../evidence/last-verification.json) | Tests **PASS**: 3,252 passed, 219 skipped, 2 xfailed, 22 warnings, 290.84 seconds; `tests_exit_code: 0`; script exit **2** | Frozen implementation `640a2f78ddff5838e9fd5e8cc9a3c20e638cf01da371b31202656fca214b295a`; only exit reason is SOURCE_REVIEW_REQUIRED, not functional test failure |
| `raw/15-live-c4-readme-sanity/20261011T064028932578Z/verification.json` | **FAIL** overall; 13 recorded steps passed before the C4 tab step | Actual local record, seven workflow commits, pause/inspection and recorded replay passed; native C4 tab was not bound. This is a failed sanity run, not an accepted demo |
| `c4-tab-browser-regression.log` | 1 passed, 1 warning, 8.65 seconds | `test_c4_tab_click_loads_current_structure_and_drills_without_claiming_runtime` uses the ordinary browser controls |
| [Live/C4 demo manifest](../demos/assets/playide-live-20261011/manifest.json), run `20261011T064943643243Z` | **PASS**, **INSPECTED**, 63.28 seconds | Seven actual local commits; recorded replay makes zero mutation requests and leaves the database unchanged; native C4 tabs drill through three structural views |

The repair runs cover the five named failures from the 70-pass run. They do not
turn those separate executions into a new single 75-pass run or establish that
unrelated final-tree gates pass. The Starlette deprecation warning remains in
these browser logs. Skips, deselections and expected failures remain outside
the passed-test claim.

The identity/C4 worker subsequently reported the following directly observed
tool outcomes. Separate log files were **not retained** for these focused runs;
the tool observations are identified here rather than presented as archived logs:

| Command using the pinned capture-environment Python | Result |
|---|---|
| `python -X utf8 -m pytest tests/test_generated_subject_runtime.py tests/test_build_subject.py tests/test_c4.py -q` | 35 passed, 1 Starlette deprecation warning, 15.50 seconds |
| `python -X utf8 -m ruff check src/eija_studio/application/build_subject.py src/eija_studio/interfaces/app_build.py tests/test_build_subject.py tests/test_generated_subject_runtime.py` | All checked files passed |
| `python -X utf8 -m mypy src/eija_studio/application/build_subject.py src/eija_studio/interfaces/app_build.py` | No issues in the 2 checked source files |
| `python -X utf8 -m nox -s architecture complexity` | Both sessions passed; 3 architecture contracts kept, 0 broken; 2,837 functions, 4 recorded complexity debts, 0 violations |

These results close the focused identity/conformance regression and the named
architecture/complexity sessions at that observation. They are not a new complete
fast-tier pass, a candidate installation pass or release verification.

After the frozen fast run exposed the stable-dependency failure, the worker
reported these additional observed commands, again without separate retained log
files:

| Command using the pinned capture-environment Python | Result |
|---|---|
| `python -X utf8 -m pytest tests/metrics/test_metrics_structure.py::test_architecture_budgets_pass_on_the_real_tree tests/test_build_subject.py tests/test_generated_subject_runtime.py tests/test_c4.py -q` | 36 passed, 8.05 seconds |
| `python -X utf8 -m pytest tests/test_appgen.py tests/test_play.py tests/test_components.py tests/test_deployment.py tests/test_api_contract.py tests/test_ripple.py tests/test_kernel_memo.py -q` | 78 passed, 39.24 seconds |
| `python -X utf8 -m mypy src/eija_studio/interfaces/app_build.py src/eija_studio/interfaces/c4.py src/eija_studio/interfaces/play.py` | No issues in the 3 checked source files |
| `python -X utf8 -m nox -s architecture complexity` | Both sessions passed; 3 architecture contracts kept and no complexity violations |

The metrics and broader caller checks pass after dependency inversion. They do
not replace the failed complete fast-tier record. The separate fresh aggregate
run now passes all 24 fast-tier sessions, and the final three-browser checkpoint
passes. Those later observations establish their own current-tree outcomes.

The first integration command was:

```powershell
python -m pytest tests/test_play.py tests/test_build_subject.py tests/test_c4.py tests/test_play_shell.py tests/test_generated_app_design.py tests/test_play_history.py tests/test_play_assist.py -q
```

The 70-pass/5-fail run used the same module list with `python -X utf8`,
`-o addopts=` and `EIJA_BROWSER_TESTS=1`, so the browser tests actually ran.
The two repaired live tests were
`test_actual_owned_draft_action_and_role_trace_the_same_generated_build_vocabulary`
and `test_actual_local_actions_reach_the_model_and_replay_without_writing_to_the_app`.
The three repaired recovery tests were
`test_navigation_recovers_without_an_edit_and_rejects_stale_or_foreign_selection`,
`test_navigation_is_restored_after_the_draft_model_is_checked`, and
`test_a_failed_request_can_be_edited_without_losing_the_plan_or_newer_composer_text`.

Additional reproduction entry points are the retained test modules:

```text
tests/test_build_subject.py
tests/test_template_evidence_identity.py
tests/test_generated_subject_runtime.py
tests/test_c4.py
tests/test_play_shell.py
tests/test_play_history.py
tests/test_play_assist.py
tests/test_generated_runtime_surface.py
tests/web/generated-runtime.test.cjs
tests/web/play-live.test.cjs
```

Browser tests require the documented browser environment and opt-in flags.
Ordinary pytest defaults deliberately skip some of them. Exact selectors and
the final integration commands must accompany the portable evidence archive.

## Problems found and what the checks establish

- Generated-template bytes previously lay outside measured implementation
  identity. The new contract includes them. Disposable tests change only a
  template and check that real review evidence becomes stale, approval/apply are
  blocked, the active baseline is unchanged, and historical receipts remain
  authentic and inspectable after reopening.
- A generated app must not retain one build label while importing a different
  installed kernel. The generated startup test supplies different measured
  implementation identities and expects `BUILD_IMPLEMENTATION_MISMATCH` before
  the server describes or serves the mismatched build. Those identities are
  synthetic test inputs, not a cross-version installation proof.
- Build-subject tests substitute pack, data, screens, templates and extra payload;
  reject missing/cross-pack subjects; remeasure cached generation; and refuse a
  source change during generation. A stable workflow hash alone is insufficient.
- Review found that generated conformance imported the service directly and
  bypassed the server's new startup identity check. A shared generated identity
  helper now checks payload and installed implementation before and after the
  generated suite. Independently, `build_into` checks the captured payload and
  implementation around the test runner and records its exact subject digest.
  Before/after tampering and implementation substitution produce **FAIL**, even
  when a substituted test runner returns PASS. This closes the identified path;
  it does not establish every possible concurrent filesystem interleaving.
- A real trace animation could receive a frame timestamp earlier than the
  observation, calculate an invalid path index and throw. That exact receiver
  regression fails before repair and passes afterward; the two actual-browser
  journeys now pass. Replay must remain inspection: it cannot
  issue another domain action or create a second database event.
- New recovery tests initially failed because a built-in handler could not carry
  Playwright's wrapper attribute. Corrected handlers allow the actual recovery
  assertions to run; all three targeted tests pass. This was a harness defect,
  not proof that the previous product behavior was correct.
- The later actual-app capture reached seven recorded commits and replay without
  extra domain requests, then found the ordinary C4 tab did not open its panel.
  The missing native-tab binding was repaired; its dedicated browser regression
  now passes, and the subsequent accepted demo uses the native tab and drilldown.
  A working API or programmatic view call did not establish that the advertised
  button worked. The failed take remains retained; the later successful run does
  not change that take's overall FAIL.
- The frozen fast run exposed the `ARCH-03` stable-dependency budget through the
  new `app_build` import of bootstrap and its adapter dependencies. The separate
  architecture import contracts passed, so their result did not cover this
  metrics invariant. The repair passes the existing `IdentityProvider` callback
  through generation, `build_into`, C4 and `AppRunner` instead of importing the
  concrete wiring from the build module. No budget or threshold was changed.
  Focused metrics/identity and broader caller verification now pass; another
  complete frozen fast-tier run subsequently passed all 24 sessions.
- Earlier design checks found stale actions after a failed read, narrow rules
  breaking words into fragments, and lost task focus. The shared templates gained
  freshness/race guards, compact labelled rules and focus recovery. Separate
  harness waits were repaired without weakening the CSP.

The existing activation checker additionally uses seven deliberately broken
local callables: missing owner capabilities, missing exact-subject/evidence
checks, and missing SQL version protection. A fault counts as detected only
through its concrete unsafe behavior, not an unrelated crash or changed hash.
See the separate [method and limits](PLAYIDE-ACTIVATION-EVIDENCE.md). This visible,
same-authorship fault set is not an independent hidden evaluation.

## Windows candidate installation

The retained `outputs/install-2026-10-11/20261011-173503-184` task evidence contains
`candidate-proof-summary.json` and `candidate-install-repaired.json`, both
**PASS**. The wheel digest is
`06d763387bf070b9b09e8eaa6f39ddba3c1047eb312f62fc31c2a822b5b21cef`;
installed implementation is
`640a2f78ddff5838e9fd5e8cc9a3c20e638cf01da371b31202656fca214b295a`.
The 263-file product-source manifest stayed unchanged; its digest is
`72cf7b96d7a576a0ea822488d949dd697a9a5a6cfd35a7b8e8c9db1282fc63e7`.

The probe used Windows 11 and Python 3.12.10 in a fresh virtual environment
outside the repository, in a path containing spaces, without inherited system
packages. Dependencies installed offline from the prepared wheelhouse, and
`pip check` passed. Installed imports and all declared runtime packs resolved
inside the target. Missing/configuration-invalid bundles failed closed;
installed HTTP assets and session protection, an exact offline proposal and a
protected refusal without writes passed. No live provider calls occurred.

The first `candidate-install.json` remains **FAIL**. Its historical three-pack
expected inventory omitted eight already-authored bundled packs. The probe was
corrected to an explicit list of eleven authored IDs, preserving exact equality;
it did not derive its expectation from installed output or change the package.
The same wheel then passed. The passing report preserves that correction.

This establishes the bounded Windows candidate installation. Browser interaction
in the newly installed environment, Linux/macOS installation, strict release
probe, owner approval/apply and public package publication remain **NOT_RUN**.
`SOURCE_REVIEW_REQUIRED` remains visible.

## Remaining handoff

The second frozen fast run passes all 24 sessions after the dependency-direction
repair, and the final three-browser checkpoint passes. Windows candidate
installation passes within the scope above. Required `scripts/verify_release.py`
completed on the same implementation, with the command-scoped
`PYTEST_ADDOPTS='-n 4 --dist loadfile'`; its output is retained in
`verify-release-final.log`. Its tests passed with exit code 0, and the script
returned 2 solely for the observed `SOURCE_REVIEW_REQUIRED` restriction. The
measured harness is
`3ff915896e7cac2498435d0dc3d0402cc4c580c2233274b7857d654cd9491efb`;
live providers are `NOT_TESTED_BY_THIS_SCRIPT`. This is a passing functional
result with an open legitimate source-review gate, not unrestricted release
approval. Earlier failed runs remain unchanged.

1. Preserve the passing current-tree fast, browser and release-script test
   records. Keep the source-review restriction visible until legitimate owner
   review; do not restamp or turn synthetic test authority into approval.
2. Preserve the passing Windows candidate installation and its failed first
   attempt, along with the isolated builder and 16 resolved runtime wheels'
   pins/hashes. The earlier preparation record remains preparation-only; the
   later candidate reports establish installation. Complete separately claimed
   installed-browser/platform/release checks rather than inferring them from
   Windows success or workflow files. The capture environment was not modified.
3. Preserve the accepted 63.28-second [actual-app recording](../demos/assets/playide-live-20261011/playide-live-c4.mp4)
   and its manifest alongside failed preflights. Inspection used video-derived
   timeline frames, the full-resolution ending/action/C4 views and a complete
   MP4 decode. It is a direct H.264 transcode with no slideshow, substituted UI
   or time compression. Complete broader refusal/recovery and ordinary-use
   acceptance beyond this scoped demo; earlier clips retain their own revision.
   The accepted raw take and associated assertions/manifests were also copied to
   the chat's `outputs/raw/15-live-c4-v2/20261011T064943643243Z`; the original
   capture directory remains intact.
4. Complete the applicable SD01–SD12 and UX01–UX08 observations, including ordinary
   navigation, enlarged text/manual accessibility, consequential recovery and
   response-time findings. Targeted checks and an edited video do not close them.
5. Freeze the exact candidate and package runnable setup, source/template/checker
   manifests, raw outcomes and limitations. Report actual commit/push/remote-check
   outcomes separately when they occur.

Before calling the shared M1 subject complete, associate review and generated
build identities through an explicitly versioned, forward-compatible contract
and prove that an incompatible data/screen/payload build cannot borrow a workflow
review decision. Preserve earlier review history rather than relabelling it.

`SOURCE_REVIEW_REQUIRED` remains a legitimate owner checkpoint. No source stamp,
production owner approval, live-provider effectiveness, participant comprehension
study, external payment/delivery or production deployment is established by this
record. M0/M1 are progressing; they are not declared complete here.
