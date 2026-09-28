# EIJA Studio 0.2.0
## See Meaning. Prove Change.

**A runnable local proof of concept, not a production assurance platform.**

Change one rule, inspect consequences, verify evidence, approve with authority.

EIJA means **Executable Intent and Journey Assurance**. One package contains a browser Studio, a command-line semantic compiler, the same deterministic kernel, persistent storage, and three interchangeable proposal providers. OpenRouter and Codex are implementation adapters, not separate products or approval engines.

The first supported domain is a **synthetic excursion workflow**. An ambiguous request—“Let teachers sign off excursions”—does not silently grant teacher approval. A local owner chooses recommendation-only, inspects the explicit registrar prerequisites, exercises the candidate, verifies its bounded behaviour, acknowledges unknowns, then separately applies the exact revision to the **local demo baseline**.

**AI proposes. The kernel checks. The local owner decides.**

## Start here

| Purpose | Entry point |
|---|---|
| Run it | Instructions below; `start.sh` or `start.ps1` |
| Understand engineering decisions and readiness | `docs/TECHNICAL_LEAD_REVIEW.md` |
| Inspect domain boundaries and contracts | `docs/architecture/ARCHITECTURE.md`, `contracts/` |
| Review risks and trust assumptions | `docs/SECURITY_AND_TRUST.md` |
| Reproduce measured results | `docs/verification/VERIFICATION.md`, `evidence/` |
| Audit source continuity | `provenance/PROVENANCE.md`, `provenance/source-inputs.json` |
| Hand off to an agent | `AGENTS.md`, `.agents/skills/eija-studio/SKILL.md` |

## Install

Requires Python **3.11 or later**. This release was exercised on **Linux/Python 3.13.5**; the other supported-intent platforms are not yet validated. No Node/frontend build is required. Runtime dependencies install from Python package indexes; dependencies are **not vendored**, so first installation is not air-gapped.

From this directory, on macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
eija doctor
eija serve --open
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
eija doctor
eija serve --open
```

An already-created virtual environment may also install the supplied wheel instead of editable source:

```bash
python -m pip install dist/eija_studio-0.2.0-py3-none-any.whl
```

The launchers create a virtual environment on first run. They do not install Codex or provide provider credentials. To update an existing environment, rerun the installation command explicitly. `--open` may launch the browser just before the listener is ready; refresh the private launch URL if needed.

The server listens on **127.0.0.1 only**. Open the complete private URL printed in the terminal, including its fragment. Do not share that URL. A new session token is generated on restart; use the new launch link. No login credential is needed for the offline fixture.

## OpenRouter

Choose a model identifier supported by your account that supports strict structured outputs. No model, price or availability is hard-coded. In your local terminal:

```bash
eija serve --provider openrouter --model 'provider/model-id' --allow-network --ask-key --open
```

Replace `provider/model-id` with a real identifier. `--ask-key` uses a non-echoing terminal prompt; the application does not persist the key. Alternatively supply `OPENROUTER_API_KEY` through your own secret-management environment. Do not paste keys into ChatGPT, a Change Case, a checked-in `.env`, or a browser field.

Before pressing **Ask for interpretations**, select the explicit egress-consent checkbox. Both the startup network flag and per-request consent are required. The provider receives the request and bounded synthetic baseline, not the workspace database, receipts, account directory or repository. User text itself may contain sensitive information: keep this demo synthetic.

The adapter requests schema-constrained JSON and required-parameter support, then validates locally. Unsupported schema/model combinations, tool calls, malformed output, authentication errors and timeouts fail visibly. There is no automatic provider fallback or retry. A timed-out call may still incur provider usage. Output limits are not a hard dollar budget. See official references in `provenance/PROVENANCE.md`.

## ChatGPT sign-in through Codex

Install the official Codex CLI separately, sign in using its **ChatGPT** option, then run:

```bash
codex login
codex login status
eija doctor --provider codex
eija serve --provider codex --allow-network --open
```

EIJA calls `codex exec`, reusing the saved CLI authentication. It does not implement an unofficial OAuth flow, extract `auth.json`, or treat your subscription as a generic OpenAI API key. Availability, limits and billing remain governed by your account and current Codex support.

`doctor` checks for the required CLI features and a recognisable ChatGPT login. It intentionally refuses unknown/API-key authentication for this adapter. It does **not** execute a paid model probe. The proposal subprocess gets an empty temporary working directory, schema-constrained final output, read-only execution policy, explicit disabled shell/app/search features, ignored user configuration, and an environment allowlist. Live compatibility/effective-policy validation is still required on your machine.

Both live adapters have mock-boundary tests. **Neither performed a real authenticated model call in this release environment.**

## First demonstration

Create a case with the default excursion request. Generate the three interpretations using the offline fixture, or a configured live provider. Select **recommendation only**. Final teacher approval is deliberately blocked, not downgraded to a supported meaning behind your back.

Under **Try**, reset to Draft. As `teacher-assigned`, Submit then Recommend. As `registrar`, Approve. Switch to `teacher-unassigned` or `teacher-revoked` to observe denied actions. These names represent synthetic fixture actors, not real staff authentication.

Under **Evidence & Decision**, run verification. The candidate has 125 one-step actor/state/action observations. Human understanding remains **UNKNOWN**. Acknowledge the critical consequences and the local-only boundary. Approve the exact revision, then separately apply it to the local baseline.

Before applying, changing the registrar rejection prerequisite through either the rule table or state view demonstrates semantic invalidation. Re-verification is required; the original receipt is retained. Layout controls currently save coordinate metadata rather than provide a drag-and-drop canvas.

## Compiler and agent use

```bash
# Compile/verify an explicit supported workflow without the browser.
eija compile examples/excursion-candidate.json --out output/compiled --verify

# Produce a synthetic demonstration case with no approval or apply.
eija demo --out output/demo-case.json

# Explicit external inference, only when the owner authorises the spend/egress.
eija propose 'Let teachers sign off excursions.' \
  --provider codex --allow-network --consent

eija list
eija verify CASE_ID --expected-version CURRENT_REVISION
eija export CASE_ID --out output/change-case.json
eija check-export output/change-case.json
```

`compile` outputs the normalized model, projections, mapped impacts and optional runtime receipt. It is a **bounded semantic compiler**, not an arbitrary Python/TypeScript/repository compiler, theorem prover or automatic application generator. Unsupported semantics are rejected. There is no MCP server or installed Codex desktop extension in this version. The CLI, Python ports and included repository skill are the integration surfaces.

## Verify and operate

```bash
python scripts/verify_release.py
python scripts/http_smoke.py
# Optional: install Playwright separately and provide a Chromium executable.
python scripts/browser_component_smoke.py --chromium /path/to/chromium
python scripts/browser_smoke.py --chromium /path/to/chromium

eija backup --out backups/studio-backup.sqlite3
```

The last browser command requires ordinary local browser navigation. It was blocked by this environment's browser policy; no policy was changed. Chromium DOM integration and actual TCP/server tests were run separately, with their narrower meanings recorded.

Do not publish workspace databases or `receipt.key`. Read the backup, recovery and upgrade boundaries in `docs/OPERATIONS.md`. Source modifications invalidate the shipped implementation fixture; ordinary approval cannot repair that. The maintainer stamping command is not an end-user “make green” button.

Package byte integrity can be checked with `python scripts/check_manifest.py`. This checks shipped file hashes, not authorship, truth or approval.
