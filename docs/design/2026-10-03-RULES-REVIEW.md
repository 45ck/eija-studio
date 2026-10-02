# Rules and impact review: current subject, explicit destinations

**Eight scoped browser checks and a separate two-check 320-width reflow probe passed on 3 October 2026.** Fast gates passed; the HCI budget run still failed and release verification retains **SOURCE_REVIEW_REQUIRED**. The original defect and unsuccessful attempts remain recorded below. Implementation: [integration checkpoint](https://github.com/45ck/eija-studio/tree/dbdf1dfb1569911e14016be13a6e519785d41c23). This docs-only publication does not deliver the implementation to main or complete the IDE/POC/POF goals.

The reproduced defect was concrete: after previewing the original baseline, activating the candidate-only Save rule opened that earlier Model view. The repair enters the current working model with the exact transition selected. Rules now shows its current candidate identity, revision, change markers and mapped-impact scope. When Model is previewing an older subject, a visible warning explains that difference before a rule is opened. With no case, Rules shows the actual loaded baseline without creating a case. State flow, journeys, editing, layout and raw closure details remain available through labeled disclosures.

Impact links use declared model projections. Rule/state-view references open the unambiguous transition comparison; runtime references open Run controls without starting a preview; journeys open current case-wide journeys; obligation, receipt and review-packet references open case-wide Evidence. Local-decision opens the existing review location without deciding anything. These destinations do not infer repository-source bindings, verify individual receipts or establish complete behavioral impact. Missing/ambiguous handling is implemented separately but was not exercised by this browser fixture.

## Observed scope

The normal-CSP, offline disposable run used Chromium `153.0.8010.12`. Independent server GETs supplied expected rule fields, identities and model topology; the oracle also checked painted labels, selected transitions and path endpoints. Navigation preserved the authoritative case/history/packet. Fixture creation and one intentional Save-role edit were allowed; navigation did not execute runtime actions or perform verification, approval, apply or export.

| Check | Actual result |
| --- | --- |
| Empty baseline inventory | PASS: five actual baseline rules; no case created. |
| Baseline → current candidate | PASS: candidate-only `TR-SAVE` opens in the current dropdown, tree, inspector and painted model. |
| History → current candidate | PASS: historical Owner rule opens its current Agent version; navigation does not mutate history/case. |
| Changes → Model | PASS: Inspect in model opens the current candidate. |
| Case roundtrip | PASS: two cases sharing `TR-SAVE` retain distinct Agent/Owner models. |
| Rules → Evidence | PASS: the exact current case-wide packet and its statuses/blockers are shown. |
| Impact references | PASS: all 14 fixture references reach the declared destination with visible focus; no execution or owner mutation. |
| Keyboard/viewports | PASS: native disclosures, named table region and rule activation at 1440×900 and 1280×800; no page-wide horizontal overflow. |

The separate narrow probe created its case on desktop, then reflowed to **320×800**. Both checks passed: expanded disclosures and the table stayed keyboard-operable; pinning Domain and returning preserved context without navigation writes. The table had **704 px of content within a 266 px region** and responded to arrow scrolling with focus retained. Body and document widths stayed 320 px. An independent DOM Range observation found all 24 measured Actor/From/To header and cell tokens on single lines. This covers populated reflow, not mobile-first entry or physical touch use.

Both final runs report the same captured source identity, unchanged during each run; the main capture contains **115 source/pack/replay files**. Each recorded zero JavaScript errors, HTTP errors and forbidden attempts, and closed its browser/server. This is a summary of retained receipts, not a new run or a raw signed receipt. The [pinned replay guide](https://github.com/45ck/eija-studio/blob/dbdf1dfb1569911e14016be13a6e519785d41c23/tests/hci/rules_ripple_review.md) describes the main fixture and independent oracles; the narrow probe has a separate script identity below.

![Current candidate Rules while Model is previewing the original baseline](https://raw.githubusercontent.com/45ck/eija-studio/dbdf1dfb1569911e14016be13a6e519785d41c23/docs/demos/assets/rules-review-20261003/rules-subject.png)

The warning explains that Rules shows the current candidate while Model still previews the original baseline. Opening Save switches Model to the current candidate and selects that transition:

![Save selected in the current candidate Model](https://raw.githubusercontent.com/45ck/eija-studio/dbdf1dfb1569911e14016be13a6e519785d41c23/docs/demos/assets/rules-review-20261003/current-model.png)

![Desktop-created candidate reflowed to 320 pixels with a horizontally scrollable table](https://raw.githubusercontent.com/45ck/eija-studio/dbdf1dfb1569911e14016be13a6e519785d41c23/docs/demos/assets/rules-review-20261003/rules-reflow.png)

These are unchanged screenshots from the final runs. The [image and observation manifest](https://github.com/45ck/eija-studio/blob/dbdf1dfb1569911e14016be13a6e519785d41c23/docs/demos/assets/rules-review-20261003/manifest.json) binds their exact bytes and recorded result/script/subject identities. They do not illustrate an unscrolled first-use session or a new observation.

## HCI and story coverage

| Criterion / stories | Supported subset and remaining boundary |
| --- | --- |
| **H04 recognition/disclosure; US02/05/07** | Current Rules subject, exact selected rule, coverage label and case-wide Evidence destination observed. Complete source-witness and counterexample navigation remain outside this check. |
| **H07 control/recovery; US02/09/11** | Baseline/history return, cross-case identity and navigation nonmutation observed. This does not cover the full interrupted-request, stale-write or restore matrix. |
| **H08 consistent meaning/status; US05/07/08** | All generated fixture references reached their explicitly scoped destinations. Unknown/ambiguous impact and removed-rule browser fixtures remain NOT_RUN. A destination is not execution or a verdict. |
| **H09 accessibility; US10** | Scoped keyboard/focus at two desktop sizes and populated 320-width reflow observed, including readable atomic table tokens. These Rules probes perform no axe or manual accessibility checks. Full WCAG, screen-reader, forced-color and mobile-first acceptance remain unproved. |

No complete story or HCI criterion is accepted by these runs. Human comprehension, satisfaction, live-provider usefulness and superior V&V remain unmeasured. This synthetic reference-model flow does not establish arbitrary application conformance.

## Gate results and remaining work

The final fast tier passed **22/22 sessions**, exit 0. The separate three-repeat [HCI report](https://github.com/45ck/eija-studio/blob/dbdf1dfb1569911e14016be13a6e519785d41c23/docs/hci/REPORT.md) completed its journey but exited 1: **15 PASS, one GAP, two FAIL**. Density remains **52 > 27** at `try-denied` (34 controls + 18 text groups); Evidence verified records 50. Rules/impact records **41** (25 controls + 16 groups), compared with 56 (31 + 25) in the [earlier checkpoint](2026-10-03-CODE-REVIEW-VALIDATION.md), and still exceeds the unchanged limit. These are visibility-proxy counts, not measured comprehension. KLM remains **65.31 > 65 seconds**. Settled-DOM p95 is **733.1 ms**, a GAP against the 400 ms target and below the 4000 ms ratchet; its difference from the earlier 747.6 ms is not established speed improvement. No threshold was relaxed and the whole application is not accepted.

That HCI run used its separate pytest-harness identity, synthetic excursion journey and Chrome `154.0.8037.58`; it is not the normal-identity Rules proof or a release approval. Its automated accessibility observations do not establish manual accessibility or human benefit. Earlier reports remain historical observations rather than being relabeled. Main's canonical HCI files and gates are unchanged by this docs-only update. HCI report SHA-256: `dd6028087cb4b1916be061896288ef6b89e6b7b79b1053e780801a7673b8477a`.

Release verification completed with **2,380 passed, 206 skipped, 26 deselected and two expected failures** in 483.54 seconds; its test exit code was 0. The overall command exited **2**, with `SOURCE_REVIEW_REQUIRED`, `trusted_fixture: false` and live providers not tested. This is not release approval. The wrapper took 487.063 seconds. No fixture was restamped; the three pre-existing evidence files were restored byte for byte after retaining the new run output. Test, browser, HCI and release outcomes remain separate.

## Retained attempts and identities

| Attempt | Outcome | Original result SHA-256 |
| --- | --- | --- |
| Before 1 | FAIL at the current-model assertion; no completed check entry. | `c4456258ba9ddebed17b9ac031f3680f3b25b13aa526588d64d60d5dfab6852a` |
| After 1 | FAIL after empty-baseline PASS: the entry helper expected Model despite the correctly retained Rules tab. It stopped before candidate creation, not at the repaired assertion. | `f0b787099e9db6ec3a1500fc89fb4eb19c2e09b5196fa0bdd4c7d4cb9b16272e` |
| After 2 | PASS, eight checks after explicitly entering Model; original current-model assertion retained. | `b59571d1b7015abed1047fc2b890e7c75cf18c4bfef65a3283797dbdeb2f6617` |
| Narrow 1 | FAIL in a desktop-assuming creation helper before the intended reflow check; not a mobile-first success. | `b2c01a3aabdda655ccfbf871c6cdca36bcf4759f2816801fbfe3289e2384b72a` |
| Narrow 2 | FAIL: the table shrank instead of providing real horizontal scrolling; the retained image exposed unreadable character wrapping. | `245f1d338e46933b6267ca14be78c6b81a34c475874d3f4ae7bcd14c617e14bb` |
| After 3 / narrow 3 | PASS within their earlier checks after a table-width repair; later token-readability assertions were not part of narrow 3. | `e3115ee443f05f3e992035c8d9cccfb4b5a866cd0719b0608bdd0791f3ed0f96` / `a1f9b6e6b55160ce94bade4d601aa4933ed5ef71add529fc19ae8110d410de4e` |
| **After 4** | **PASS, eight checks** after the final table-column repair. | `9e8ef8493586358d37103f28fd0d3895e72fd5e190c8666b923e93f01ce2bea3` |
| **Narrow 4** | **PASS, two checks**, including the strengthened independent single-line token oracle. | `7c18232ec09788e0880468c28cd5dab59ed445407d56e1c9ab0f24c00c243afb` |

Before 1 captured subject: `02385afa2d6333880d3046ed74823fe379e36b5df59721ac6fb6bf2a50794ff7`; runner: `f1d0f77c6d4f155134c46b77c310f01dcd8e40708ac4bc740cfc746e8bd3d1b8`.

After 1 captured subject: `2a8a186659f621d69e5712099798e5a08f9fbde6b20e7d3a80565b850a6d7678`; runner: `513af6486b5005af0f024215ec512e0f32867d3aea313e901f65a0b44d905f77`.

After 2 captured subject: `e8a7007fd3c757405f684d14f1926a6e52aaf1ddb9300cb0a3785664bd4205da`. After 3/narrow 3 captured subject: `d54be3c91dcc5375709c8779617c079b6a984b7520ba5946eb6c47f6f750eb4d`.

Final after 4/narrow 4 captured subject: `a8025b31d5d07a18a1065e208b6df18f7158c88f3dcad5fc41a7c221e54483cd`. Main runner: `847326a788b982f3f707549602a6f587a1e66fb69a8e044e742c4e38ce2d4556`; narrow runner: `22284f4766bbdf49ccd0ccab5a2533dfcaa42364a2985680a172ce1a7e893015`.

Every listed attempt preserved its captured source and closed browser/server. The before and after runners differ because coverage and entry sequencing changed; the narrow oracle was strengthened for the final run. This is not a byte-identical harness or immutable Git-pair proof. Captured subject identities remain distinct from the pinned committed implementation identity. Raw reports contain local/disposable details and are not copied into this note.
