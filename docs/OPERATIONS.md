# Operations and developer runbook

## Configuration and startup

The command-line options are the source of truth: run `eija --help` and `eija serve --help`. The default workspace is `.eija` relative to the launch directory. Set `--workspace` explicitly for repeatable operations. `EIJA_PROVIDER` and `EIJA_MODEL` set defaults; `OPENROUTER_API_KEY` supplies an optional server-side key. `--ask-key` is an ephemeral local prompt. No `.env` auto-loader is provided.

Use one server per workspace. SQLite protects concurrent transactions, but the provider single-flight lock and session boundary are single-process. A second server could initiate a second paid call. There is no background worker, automatic delivery or recurring model job.

`eija doctor` checks release identity and provider configuration/readiness without inference. “Ready” does not mean the configured live model completed a request. Codex must report a ChatGPT login and the required flags. OpenRouter requires a model ID/key; schema compatibility is only known when a request is executed.

## Local data

`studio.sqlite3` plus its WAL/SHM files contain cases, active baseline, synthetic actors, preview instances, operations, audit and outbox. `receipt.key` supplies local HMAC integrity. POSIX directory/file modes are set best-effort; Windows ACLs are not certified. Do not sync the workspace into shared folders by default.

All preview instances represent copies of one synthetic excursion fixture. The fixture assignment flag is deliberately simple, not a per-student/per-excursion assignment directory. Denied executions are returned as errors; accepted effects and governance/provider events are recorded. A complete denied-attempt security log is not implemented.

## Backup and restore

Run `eija backup --workspace PATH --out NEW_BACKUP.sqlite3`. This uses SQLite's online backup API rather than copying a live file without its WAL. Preserve `receipt.key` separately in appropriately protected storage. The application rejects an existing CLI backup destination to avoid accidental overwrite.

To restore, stop EIJA, create a new private workspace directory, restore the database as `studio.sqlite3`, restore the matching `receipt.key`, then restart against that directory. Keep the original untouched. If the receipt key is lost, older signatures cannot be authenticated; do not pretend a new key repairs them. Use a fresh workspace and regenerate observations under an explicit new review.

The tested backup check reopened database contents. The test suite also restarts a workspace and verifies its seals. This does not replace a full disaster-recovery exercise on the target OS/storage system.

## Schema and upgrades

Database schema version is 1. Unsupported versions fail with `SCHEMA_MIGRATION_REQUIRED`; there is no automatic migration or backward-compatible importer for the historical six packs. They are source/research lineage, not databases to open directly. Export cases and back up before upgrading. A future migration must be transactional, reversible/tested on a copy, and preserve evidence subjects rather than rewriting them to the new version.

Source changes require source review and a fresh release identity. `scripts/stamp_release.py --acknowledge-self-authored-fixture` is for a maintainer deliberately creating a new reviewed fixture. It must never be run automatically by `doctor`, installation, ordinary model changes or an agent trying to remove a blocker. A stamped fixture remains self-authored, not external certification.

## Failure diagnosis

| Code / symptom | Meaning | Action |
|---|---|---|
| SESSION_REQUIRED | Missing/stale local capability | Use the new private URL printed by the running server |
| ORIGIN_DENIED / HOST_DENIED | Request outside the local browser origin boundary | Use the direct loopback launch URL, not a proxy |
| EGRESS_CONSENT_REQUIRED | Network startup or per-request consent missing | Review the payload; explicitly opt in only for an authorised synthetic test |
| PROVIDER_BUSY | One proposal is already running | Wait for that call; no retry has been made |
| PROVIDER_AUTH / RATE_LIMIT / provider configuration errors | Adapter rejected credential/availability conditions | Inspect local account and model configuration; never paste the key into case text |
| STALE_VERSION / STALE_BASELINE | Case, instance or baseline changed | Reload or create an explicitly rebased new case; do not force overwrite |
| STALE_INSTANCE | Candidate semantics changed | Reset the isolated preview |
| SOURCE_REVIEW_REQUIRED | Package no longer matches the fixture | Inspect the exact source change before creating a new release |
| GATE_BLOCKED | Missing/stale/conflicting evidence or authority | Inspect the raw packet; do not edit receipt status |
| ASSIGNMENT_DENIED / ACTOR_REVOKED / ROLE_DENIED | Current fixture actor cannot perform that transition | Fix the intended request/actor, not the evidence record |

## Build and reproduce

```bash
python -m pip install -e '.[dev]'
python scripts/verify_release.py
python scripts/http_smoke.py
python scripts/browser_component_smoke.py --chromium /path/to/chromium
python -m pip wheel . --no-deps --no-build-isolation -w dist
```

Runtime requirements are pinned in `pyproject.toml`; the measured environment closure is recorded in `evidence/environment.json` and `requirements-tested.txt`. The latter is a measured version constraint set, not a complete hash-locked supply-chain manifest or guarantee on another platform. Build tools, optional browsers and Codex are separate prerequisites. CI configuration is included but was not run on a remote CI service.

Changing Python/package versions changes the environment evidence dimension and requires re-verification. UUIDs/timestamps, local HMAC keys and platform dimensions mean exported experiment bytes will differ across runs. Reproducibility means the declared behaviours/check outcomes and trace structure, not identical random IDs or a byte-identical ZIP.
