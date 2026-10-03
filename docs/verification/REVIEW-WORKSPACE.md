# Review workspace verification

This increment connects the paired semantic comparison, focused evidence review
and source snapshot navigation. It remains part of the full IDE acceptance work;
the prior density FAIL, latency GAP and `SOURCE_REVIEW_REQUIRED` are not cleared
by unit tests or a generated design image.

## Observable behavior

| Story / HCI criterion | Required observation | Failure control |
|---|---|---|
| US04–05 / H03–04 | Baseline and candidate share a viewport, retain their own exact graph membership and expose every actual change. An absent item says Not present. | Wrong painted endpoint, missing/duplicated item, false label and omitted initial marker fail an independent oracle. |
| US06–07 / H04, H08 | Selected-change links use declared references. Case-wide impact and evidence are labelled separately. All raw statuses, blockers and limits remain accessible. | Removed claims or upgraded NOT_RUN fail the same content oracle. No inferred source binding from an action name. |
| US09–11 / H07, H09–10 | Focus evidence is optional; Restore restores ordinary preferences. Problems, keyboard destinations and deliberately reopened panes remain usable. | Corrupted preferences, recollapsed panes and focus returned into hidden content are detected. |
| US05, US10 / H06–08 | Source/impact reads bind the displayed repository snapshot. Refresh cancels obsolete responses and preserves unsent model input, current case, history and runtime. | External tracked-file edit causes a stale refusal; reverse response order, wrong response hash and changed selection cannot overwrite newer context. |
| US10 / H07 | Failed source navigation preserves explicitly labelled prior source. Back advances only when its requested read succeeds. | Refused Back and failed refresh keep their error and do not manufacture a successful navigation. |

The reference workflow and external repository bytes are different subjects.
Source freshness only compares captured bytes at read time. It does not bind
external source into a model receipt, establish conformance or measure human
understanding. Repository intake and syntax/declared links remain partial.

## Reproduction

Run the normal installation and browser prerequisites from the repository setup
guide, then the local gates. The Python wrapper includes all review suites; direct
Node invocation is useful while working on the UI:

```powershell
node --test tests/web/shell.test.cjs tests/web/focus-layout.test.cjs tests/web/evidence-overview.test.cjs tests/web/compare.test.cjs tests/web/source-freshness.test.cjs
python -m pytest -q tests/test_repository_freshness.py tests/test_repository_source.py tests/test_repository_connection.py tests/test_workbench_interfaces.py tests/test_ide_shell.py
python -m nox -t fast
python -m nox -t full
python scripts/verify_release.py
```

The release fixture must not be restamped to clear a changed-source result. Keep
its actual exit/status separate from application/test defects.

Browser evidence must use the ordinary CSP, disposable application data and the
actual authenticated browser-to-server APIs. Record the exact implementation
manifest, environment, screenshots, raw observations and failures. Check normal,
focused, opened-detail and error states; preserve the HCI thresholds. The separate
external-edit fixture may mutate its own disposable tracked file only, never the
connected EIJA checkout. Label that fixture distinctly from the main EIJA journey.

## Initial implementation checks

On 2 October 2026 the focused backend/API run passed 56 tests before two additional
comparison-removal mutation controls were added. The three comparison/focus/evidence
Node suites passed 41 tests. These are intermediate implementation checks, not the
final combined gate run. Browser, full-tier and final-byte release results for this
increment are still pending at this checkpoint.

Existing historical proof remains linked from the [implementation ledger](../design/IMPLEMENTATION-STATUS.md).
