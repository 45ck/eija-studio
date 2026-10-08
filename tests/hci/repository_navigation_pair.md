# Reproduce the real navigation change

This proof runs the same failed-read and busy-navigation scenarios against two
actual EIJA revisions. The earlier revision must show the designated dropdown
and current-case mismatch; the later revision must retain the current identity
and pass the successful retry controls. A timeout or missing prerequisite cannot
stand in for the required earlier counterexample.

The fixed local commits are:

- Before: `9c22d425ee33e52980a95b33330babec43c6aa59`.
- After: `c666b6bb76905c0c9bd03e81cac0922136c4cf3e`.

## Prerequisites

Use a source checkout containing these scripts and the `quality/` tooling;
engineering tooling is not distributed in the installed application wheel.
Both complete commit objects and their trees/blobs must already exist locally.
A shallow clone missing either revision cannot run this proof. Neither command
fetches objects, changes a checkout, resets an index or registers a worktree.
Replacement-object and promisor repositories are refused by the shared adapter.

Install the current checkout's dependencies in a virtual environment using
Python 3.11 or newer. The dependency installation is explicit; it does not
install a browser:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[hci,source-analysis]"
```

An installed Chromium compatible with the pinned Playwright version is required
for the second command. The proof launches a separate headless browser and fresh
contexts. It does not attach to a personal browser profile. If browser routing
is required on the current endpoint, complete its configured preflight first;
on Calvin personal endpoints the browser-account-router device status must be
`ready`. Keep browser/heavy validation serial.

## Export, then run

Run from the tooling checkout root. Put that root on `PYTHONPATH` so Python can
import the unshipped `quality/` package. The examples use sibling output
directories; **both must be new**. The export bundle must be outside the source
repository, and the proof output must be outside both exported source roots.

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe -B tests/hci/repository_navigation_exports.py --repository . --out ../eija-navigation-exports-1
```

Continue only when the export command exits zero and its `validation.json`
reports `PASS`:

```powershell
.\.venv\Scripts\python.exe -B tests/hci/repository_navigation_pair.py --exports ../eija-navigation-exports-1/exports-manifest.json --intake ../eija-navigation-exports-1/comparison.json --out ../eija-navigation-proof-1
```

`--repository` defaults to the checkout containing the export script. It can
instead name another local clone that contains the fixed objects. The export
command creates the complete `exports-manifest.json`, exact `base/` and `head/`
source copies, retained Git archives, a fresh read-only `comparison.json`, and
its integrity validation report. No pre-existing private intake artifact is
needed. Current ignore policy must allow the historical app.js comparison;
policy exclusions are reported, not bypassed.

Playwright uses its installed Chromium location by default. If that browser is
already installed in a custom cache, set `PLAYWRIGHT_BROWSERS_PATH` to that cache
before the proof command. Alternatively append
`--browser-executable "<path-to-an-installed-chromium-executable>"` to the proof
command. No command in this guide downloads Chromium. A missing executable
leaves the behavioral result `NOT_PROVEN`; the export command itself does not
need a browser executable. Use the same Python environment for both commands.
Do not enable Python optimization: the pair runner refuses it because assertion
oracles would otherwise be disabled. `-B` suppresses bytecode generation and
does not disable assertions.

## What the commands check

The export command adapts Git's archive output and reuses the pair runner's
constants and exact-source validators. Scope is only `src`, `packs` and
`pyproject.toml`, including the bundled OSS assets needed to run these revisions.
It admits at most 3,000 files, 8 MiB per file and 64 MiB per revision. It checks
archive paths, regular-file modes, sizes, case collisions, complete inventories,
SHA-256 values and Git blob identities before accepting the exports. Private or
generated paths, links, unexpected files and altered archive substitutions are
rejected. It records Git observations before and after. It executes no exported
code and starts no server or browser.

The pair runner then deliberately executes each verified EIJA export through
the existing real CLI/server harness, with an offline provider, normal CSP,
normal `SOURCE_REVIEW_REQUIRED` identity and disposable local storage. Each side
creates two unselected `DRAFT` cases. Those create operations are the only
permitted writes: their packets remain blocked by `MEANING_REQUIRED`, with no
candidate or review subject. Other application requests are GETs. No meaning
selection, model edit, preview, verification, owner approval/apply or provider
inference is performed. The source-review condition is preserved, not stamped
away.

The runner checks served app.js bytes against the export and independently reads
the case state. Controlled transport failures and held responses test whether
the dropdown, title, case label and selected list entry still identify the same
current case. It does not replace successful application data or mutate browser
application globals. Fresh browser contexts and disposable servers are closed,
and both source exports and the shared harness are rechecked after the run.

## Read and retain the evidence

The authoritative behavioral result is the new proof directory's `result.json`.
It retains the exact pair, source and helper identities, browser executable
hash/version, declared conditions, expected and observed identities, request and
fault records, independent GET observations, screenshots, cleanup results and
artifact hashes. `base/result.json` and `head/result.json` contain the respective
observations. The export manifest contains local absolute paths needed for
validation; keep that original manifest with its run.

Keep failed and partial attempts. A later retry uses a new output directory;
never overwrite a failure, edit an expected outcome to produce green evidence,
or relabel infrastructure failure as the required before-fail observation.
Source/cleanup failures prevent `PASS`. Export `PASS` establishes source
integrity only; it does not establish the later browser result.

This proof covers two displayed-navigation identity properties under controlled
conditions. It does not prove preview retention/clearing, every changed function,
arbitrary repositories, complete source/model conformance, owner authorization,
live-provider usefulness or reduced human comprehension burden. The source
comparison retains its own behavior `NOT_RUN`; the browser observations are
separate, scoped evidence. Git author metadata and the declared Codex-assisted
label do not authenticate AI authorship.
