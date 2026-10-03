# Rules subject and impact navigation browser proof

From an EIJA checkout with the HCI extra and cached Chromium installed:

```powershell
$env:PYTHONPATH = "$PWD/tests/hci;$PWD/src;$PWD"
.\.venv\Scripts\python.exe tests/hci/rules_ripple_review.py --out reports/rules-ripple-review-1
```

Use the checkout root as the current directory. The replay imports the repository's
quality and shared browser helpers. If Playwright browsers live in a custom cache,
set `PLAYWRIGHT_BROWSERS_PATH` to that existing cache first. The retained Windows
run used `E:\.dev-cache\ms-playwright`; this is a host-specific prerequisite, not
a portable default. No browser installation is performed by the replay.

Use a new output directory. On Calvin personal endpoints, first obtain a ready
browser-account-router device preflight. Python optimization is refused because
it disables assertion oracles; missing browser prerequisites cannot produce PASS.

The script reuses the existing normal-identity disposable EIJA review server,
isolated Chromium, server GET oracle and subject manifest helpers. The real
checkout is connected read-only. Creating candidates and the one permitted Save
role edit use ordinary UI controls in temporary workspace data. Verification,
approval, apply and export endpoints are blocked; no personal browser, live
provider, private owner token or live source mutation is used.

The complete run has eight checks:

1. A no-case Rules view contains the actual workbench baseline transitions.
2. From an original-baseline preview, a candidate-only Save rule opens the current
   candidate in the dropdown, tree, inspector and actual painted model.
3. An earlier historical Owner preview opens the current Agent version of that
   same rule; navigation does not change case/history.
4. Changes' Inspect in model also opens its current candidate subject.
5. Two cases sharing rule IDs retain their distinct models during return trips.
6. Rules opens the exact current case-wide Evidence subject and blocker/statuses.
7. Every real generated impact reference has the declared destination: paired
   transition, runtime controls, case-wide journeys/evidence, or review location.
   Navigation cannot execute a runtime step, fill owner answers, acknowledge,
   mutate the case, or guess a repository source binding.
8. At 1440x900 and 1280x800, ordinary keyboard disclosures and a named table scroll
   region preserve full rule/journey facts, focus, and reachable model controls.

Expected fields, change markers and topology come from independent server GETs,
not renderer helpers. Painted path endpoints are checked against the corresponding
state borders, together with actual labels and selection. Complete recorded GETs,
observations, screenshots, script bytes and source-before/after hashes remain in
the output, including on failure. The script checks browser/server cleanup.

For the original context defect only, use `--scenario candidate-context`. This
is a single scoped check, not the full eight-check result. The earlier reproduced
failure is retained separately and must not be relabeled after repair.

Unknown/ambiguous impact identities, removed-rule fixtures, human usability and
comprehension, manual accessibility, live models and owner authorization are not
measured. Opening a review location confers no decision or evidence. A passing
run applies only to its exact captured subject; no threshold or HCI journey is
changed by this script.
