# ADR-0022: Live provider evidence is consent-gated, one call, and NOT_RUN when unproven

* Status: accepted
* Date: 2026-09-28
* Lane: providers

## Context and problem statement

Mocked contract tests prove an adapter's handling of faked output. They do not prove that the real vendor CLI accepts the flags, honours tool lockdown or emits the assumed envelope. Live calls cost subscription usage and send data out, so they need consent, and their absence must not read as success.

## Decision drivers

* "A mocked result is never live" and "a missing prerequisite is NOT_RUN, never PASS" (lane rules).
* Login status may only come from official commands; token files are never read.
* Evidence must name the platform and the tool versions, and must be re-runnable one provider at a time.

## Considered options

* Opt-in script that makes exactly one synthetic call per provider and merges its result into a committed evidence file (chosen).
* A nox session that runs live calls.
* No live evidence, mocks only.

## Decision outcome

Chosen option: "opt-in script", because it keeps live calls out of every automatic gate. `scripts/live_provider_smoke.py --provider X --consent` sends only the fixed synthetic request and baseline, refuses without `--consent`, caps the timeout at 180 s, and records status, CLI version, model when reported, latency, `schema_valid` and error class in `evidence/live-providers/<date>-<platform>.json`.

* `PASS` means a live call returned a schema-valid Proposal. It does not measure interpretation quality.
* `NOT_RUN` means a prerequisite is missing: the CLI is absent, `doctor()` reports not signed in, a key is absent, or the CLI itself reported an authentication error.
* `FAIL` means a call was made and failed.
* Gemini CLI has no official status command, so its login is `UNKNOWN`; the single call may return an auth error, which is recorded as `NOT_RUN`, not `FAIL`.
* OpenCode with zero stored credentials is `NOT_RUN` even though it can reach free anonymous models: those are not an owner account and were not authorised.

### Consequences

* Good: the evidence file says exactly what was and was not exercised on the reference machine.
* Bad: PASS is per CLI version and per date; a CLI upgrade needs a re-run.
* Revisit when: hosted CI returns and a vendor offers a no-cost test endpoint.
