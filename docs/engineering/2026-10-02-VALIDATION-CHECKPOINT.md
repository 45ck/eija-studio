# Integration validation record — 2 October 2026

This record preserves the original full run and subsequent affected reruns.
Read it with the [browser run report](2026-10-02-IDE-SELF-DOGFOOD.md). It does **not**
claim a clean full-suite pass or final release readiness. Counts from overlapping
test selections are not added together.

## Completed full-suite run

`.tmp/codex-e2e/final-ide-full.log` records **35 nox sessions in 18 minutes:
28 reported successful, six failed, one skipped**. “Reported successful” needs
the TLA qualification below. The six reported failures were:

| Session | Actual cause in this run | Subsequent state at this checkpoint |
| --- | --- | --- |
| `hci` | Visibility/chunk proxy 68 exceeded limit 27. Selection: 34 passed, one failed, one expected failure, 96 deselected. Settled-DOM p95 961.3ms exceeded the 400ms target but stayed within the 4000ms ratchet. | Actual unresolved HCI budget failure; newer measurement below. |
| `metrics` | `LANE-01` aggregated the failed lane report; 19 budgets passed, one failed, one was NOT_RUN. | Derived lane failure, not a second independent product defect. |
| `demos_dry` | Legacy assurance-loop script tried the hidden Rules & ripple tab without opening Reference views. | Ordinary menu-opening fix applied; affected rerun pending. |
| `vocabulary` | New UI strings contained the pack tokens `Draft` and `Cancel`. | Wording replaced with `Reset unsent fields` and the corresponding unsent-fields message; focused scan has zero findings. Affected gate rerun pending. |
| `adr_index` | Its tools selection failed the same two vocabulary tests. | Same wording repair; affected rerun pending. |
| `coverage` | The same two vocabulary tests failed, despite measured coverage 92.84% exceeding the unchanged 78% floor. | Raw selection: 1,926 passed, two failed, 201 skipped, two expected failures. Session remains failed until rerun. |

The four non-HCI/metrics failures have concrete repairs applied; they are not
retroactively marked passed. `.tmp/codex-e2e/final-full-subject.json` compares the
preceding browser subject with the end of the suite: **102 captured files,
UNCHANGED, zero changed paths**, content SHA-256
`868d892f9489aa436c3c618b41f6a7fa5e29bd9717914fd918c6fcd7273e4ce5` both times.
Base HEAD was `40c30fcf044093032f421ee551cd38af3a2cd93a`, dirty checkout. The
manifest file SHA-256 is
`8c8a3ff4902ea32801a8a5eb2902683fc807f5d0865bd5495f2650e053a79aec`.
Its scope is public source, packs and the named browser scripts; it is not a
complete identity manifest of every test, tool or documentation file.

## Concrete V&V established, with limits

- **Agent boundary:** `agents` ran 83 tests successfully, including the narrowed
  MCP port and owner-operation exclusion. No live provider usefulness claim follows.
- **Properties and faults:** 98 property tests passed with six named existing
  expected failures below. The quick policy mutation run killed 107 mutations,
  with zero survivors/timeouts/incompetent mutants and 22 classified equivalents.
  Its 1.0 score is for that policy scope, not the whole application.
- **Bounded SMT:** 15/15 excursion invariants were UNSAT; non-vacuity and the exact
  three-model accepted set were checked. There were 2,572 differential candidates,
  zero disagreements, and 8/8 negative controls. Generated law checks also ran,
  but the self-review pack still reported four laws NOT_RUN; library-loan reported
  two. Hand/generated equivalence existed for excursion only (23/23 codes and
  27/27 planted defects detected).
- **Bounded runtime exploration:** BMC at depth six completed baseline 224 states/
  13,992 transitions and candidate 140/9,496, with 6/6 seeded runtime faults caught.
  It is bounded exploration of the named models, not arbitrary-code verification.
- **Graph/reference checks:** 49 impact-math tests passed; graph formal tests
  reported 140 passed, eight skipped and one expected failure. Reference selfchecks
  and Alloy's 11/11 expected commands passed. The skipped implementation bindings
  below prevent treating all reference laws as implemented-product conformance.
- Lint, Linux/default and Windows typechecks, architecture, complexity, dependency,
  source/diagram drift, documentation links and OKF sessions reported success.
  OKF's 561 pages included **526 unverified** pages; zero stale pages is not proof
  of their correctness. `hci_docs` validated an older snapshot's internal
  derivation while explicitly warning about different UI bytes.

### TLA false-success finding — repair/rerun required

The full log's `formal_tla` result is **not valid evidence of complete current
conformance**. Three TLC model checks and four intended counterexamples ran, and
baseline conformance reported agreement. Candidate conformance then crashed at
`verification/tla/abstraction.py:124`: `Session.enqueue()` required `recipient`.
The session wrapper accepted exit code 1 and trusted an existing PASS JSON.
That file was dated **29 September**, before this 2 October run, so nox incorrectly
reported success. The adapter and wrapper regression repair are assigned; retain
the traceback and require a fresh successful run before promoting TLA status.

A read-only audit found no further such mismatch in the other successful log
sections or SMT/BMC, graph-formal and Bend wrappers: SMT/BMC required exit 0 and
wrote fresh reports; graph-formal checked fresh stdout; Bend preserved its fresh
NOT_RUN result. The demo registry's success also explicitly warned that the
assurance-loop video retained an older scenario hash; registry consistency does
not make that footage current.

## Final UI wording: separate seven-journey run

`reports/ide-journey-edges-3/observations.json` records **7/7 PASS**, exit 0,
Chromium 153.0.8010.12: source-first, intent → Changes, two-case history/source
isolation, **Reset unsent fields**, stale second-page edit, transport failure/retry,
and keyboard edit/refusal. Actual GET responses check source text/ranges/hashes,
case/subject/history preservation, exact accepted transactions and refused writes.
There were zero JavaScript errors, unexpected HTTP errors or approval/apply attempts.
Browser/server closed; offline provider and normal source-review identity remained.

All **102** captured files were unchanged during this later run. Dirty base HEAD
remained `40c30fc`; its changed UI/script bytes have the distinct content SHA-256
`bfe7011d4919fc727c0f8d25552e596548beec9819cedc5222d667f9991ea113`.
The subject-manifest file SHA-256 is
`cf9b3fb01d0e86dd07235c877a242926ab77a8dda905354c033f9d1c61c96419`;
script SHA-256 is
`56361ca1fb124dfccd27de5006383169399c6e4588a18db1f0df85281fcefa44`.
The 37 artifacts were archived and SHA-checked under
`work/ide-browser-qa/ide-journey-edges-3` and copied by the integrator into the
preview output bundle.

The unchanged SD05 painted-endpoint oracle separately passed LR/TB **2/2**, detected
the deliberately wrong target in each, restored geometry exactly, and preserved
the server model. Keep its original LR rounded-corner failure and scoped pack
limits. The older **20-check video is a different run on earlier bytes**; do not
present these as “27/27 on the final build” or imply the video shows the later fixes.

## Expected failures and unavailable evidence remain explicit

- Property expected failures: duplicate `forbidden_effects` cause spuriously
  different semantic hashes; four ChangeCase/LayoutChange string/boolean coercion
  cases disagree with JSON Schema; ExecuteCommand's integral-float restriction
  disagrees in the opposite direction. These are unresolved findings, not passes.
- Graph/coverage expected failure: a lone-surrogate string literal crashes the
  codelink hash instead of returning an unresolved result. Bend's old snapshot also
  remains an expected failure pending regeneration by the current toolchain.
- Bend proof was **NOT_RUN** because Docker was unavailable. Other explicitly
  unavailable checks include POSIX-shell hooks on this environment, CPython 3.11/
  3.13 cross-version hashing, the offline SARIF schema, `pyshacl`, a sibling OKF
  worktree, and eight not-yet-present `eijagraph` implementation symbols. Coverage's
  opt-in property/HCI skips must be read alongside their separate executed lanes;
  they are not all missing tooling. Release-only diagram syntax checks were not
  established by this full run.
- Human comprehension, comparative engineering benefit, live-provider usefulness,
  representative-user/owner acceptance and held-out external-codebase validation
  remain **NOT_RUN**. Source review is outstanding; no stamp or owner decision was
  manufactured to turn a status green.

## Subsequent integration results

The integrator's archived `work/ide-browser-qa/hci-final-1` already gives a newer
HCI measurement on the final UI: **16 PASS, one GAP, one FAIL**, still **68 versus
27** chunks, settled-DOM p95 **838.2ms** versus target 400ms. Its report JSON SHA-256
is `70f3bea4366e8986612c098b39c71a6c8666ab2210a6b08e62ebb608d379bc19`.
The current-UI derivation check passed. Keep it distinct from full-suite 961.3ms
and historical refresh3's 70 chunks/836.8ms.

The subsequent fast tier (`final-fast.log`) passed **22/22 sessions**, including
ADR/tools and vocabulary checks. The affected full selections
(`final-affected-full.log`) passed `coverage` with **1,928 passed, 201 skipped,
two existing expected failures**, **92.84%** against the unchanged 78% floor.
`demos_dry` now executes successfully but reports **PARTIAL**: Act 4 verification,
approval and apply remain unavailable under normal SOURCE_REVIEW_REQUIRED identity.
`metrics` still fails the inherited HCI lane status (19 PASS, one FAIL, one NOT_RUN);
its separate `reports/coverage/coverage.json` is absent (the reason recorded by
the collector). The successful coverage gate is separate evidence, not an
inferred metrics result.

The UI and recovery checkpoint was committed and pushed as
`0ef082d56d19a5c649f37f8d693b2df3e4a00218` on `integrate/all`. Local HEAD,
origin branch and GitHub's advertised branch matched, with 0/0 divergence.

The repaired `formal_tla` gate then passed in **465.6 seconds**, with a fresh
report dated `2026-10-02T07:28:23+00:00`. The three supported configurations passed
TLC and agreed with the real runtime: baseline **208 states / 37,440 state-command
cells / 283 traces**; candidate **688 / 247,680 / 312**; candidate with rejection
from Submitted **208 / 37,440 / 283**. All four expected negative-control models
produced their intended violations. The replay-before-authority runtime fault
was detected by both the state graph and trace validation. These are bounded
excursion models, not conformance of every connected repository or the self-review
pack. The old falsely successful report is retained separately.

The fix supplies the pack's declared notification recipient when reconstructing
runtime state. The gate archives prior reports, rejects unsuccessful child
execution, requires a fresh valid report, and fixes the required configuration
scope. Its **23 focused regression tests passed**; the two original fault
controls failed against the original code as intended. The required full gate
was rerun, rather than treating those regression tests as formal evidence.

The final post-repair fast tier (`final-post-tla-fast.log`) passed **22/22
sessions**, including **1,951 tests, 201 skips and two existing expected
failures**. OKF reports 561 pages, zero stale pages and zero stale curated Notes;
526 pages remain unverified. `scripts/verify_release.py` then ran the ordinary
suite: **1,951 passed, 201 skipped, 26 deselected, two expected failures**, with
`tests_exit_code: 0`. Its overall command remained nonzero because the structured
result is **SOURCE_REVIEW_REQUIRED**, `trusted_fixture: false`. No stamping or
owner approval/apply occurred. The resulting identity record is
[`evidence/last-verification.json`](../../evidence/last-verification.json).

There is **no green full-tier or release claim**: the HCI density failure remains,
metrics inherits it, and source review is outstanding. Fresh public-GitHub
clone/install feasibility is a separate next execution, not inferred from these
local gates.
