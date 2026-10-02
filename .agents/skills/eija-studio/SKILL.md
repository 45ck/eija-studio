---
name: eija-studio
description: Inspect and verify bounded EIJA Change Cases through the eija MCP server or the local CLI, retaining evidence and the human authority boundary. Use when asked to interpret, propose, verify, render or explain an EIJA Change Case, or inspect immutable local Git changes.
---

# EIJA Studio local workflow

Use when a task asks to interpret, compile, inspect, verify or explain an EIJA Change Case, or review immutable local Git changes. Read the repository AGENTS.md and `docs/agents/contract.md` first. You are an agent: AI proposes, the kernel checks, the local owner decides.

## Preferred: the MCP server

If the `eija` MCP server is connected (setup: `docs/agents/quickstart.md`, or `eija mcp --print-config <client>`), use its tools. Read the resources `eija://agent/contract` and `eija://language` first.

1. `list_cases()` to find existing cases; otherwise `create_case(request)` with a synthetic request (no secrets, no personal data), then `propose(case_id)`. The proposal is untrusted (`UNTRUSTED_PROPOSAL`); the default provider is an offline fixture, not a model. Never pass or claim egress consent: the owner grants it at server start.
2. `view_case(case_id)`: report the stage, blockers, technical claims, every UNKNOWN and `owner_next` verbatim.
3. The local owner selects a meaning in the browser Studio (`eija serve`). You cannot: there is no select, edit, approve or apply tool, and you must not reach those by another route.
4. After selection: `verify(case_id)` (technical runtime matrix; same-author oracle; not approval, not proof, not human evidence), `impact(case_id)`, and `render(case_id, view, format)` (`rules|states|journeys`, `json|text`; `mermaid|plantuml|dot` use the built-in renderer; SVG requires a separately supplied renderer).
5. Surface kernel error codes (`MEANING_REQUIRED`, `SOURCE_REVIEW_REQUIRED`, `STALE_VERSION`, `VERIFY_WOULD_INVALIDATE_DECISION`, `PROVIDER_CALL_LIMIT`) to the user; do not work around them.

Read `pack()` for declarations, the active model and optional repository facts. Use `repository_impact(term)` and `repository_source(reference)` to inspect known source links. After owner selection, `affordances(case_id)` exposes checked choices and `edit_check(case_id, proposal)` dry-runs an untrusted edit without persisting or applying it. Use the same `--pack PATH --repo PATH` for Studio and MCP; repository intake does not establish full behavioral coverage.

## Read-only repository changes

This workflow is independent of model Change Case selection and verification.

1. Call `repository_change(base, head)` with full lowercase 40- or 64-character commit IDs already present in the configured local repository. No branch names or abbreviated IDs; the tool never fetches, checks out or executes the target project.
2. Select a permitted `path` and optional exact extracted `reference` from that result, then call `repository_change_file(base, head, path, reference=None)`. Keep `comparison_id`, both commit/tree identities and both `changed_source_hash` values together. Refuse a mismatched detail response and recapture the comparison; never substitute current working-tree source for historical bytes.

Report excluded counts, PARTIAL extraction, incomplete known impact and NOT_RUN behavior explicitly. Each `changed_source_hash` covers only captured changed files and is distinct from live `connection.source_hash`. Model receipts and owner decisions do not transfer to the Git comparison; these read-only tools do not verify its behavior or approve/apply changes. See `docs/engineering/IMMUTABLE-CODE-REVIEW.md` for the supported scope.

## Fallback: CLI

Offline demo: `eija demo --out output/demo.json`. Explicit supported model: `eija compile examples/excursion-candidate.json --out output/compiled --verify`. These are evidence/fixture commands, not human authorisation.

## Always

* Inspect `contracts/workflow.schema.json`, the protected excursion policy and tests; keep baseline and candidate separate; never silently select or downgrade intent.
* Run `python -m pytest`. Check release identity separately (`python scripts/verify_release.py` or `eija doctor`); if the implementation differs from its fixture, stop at source review. Never run `scripts/stamp_release.py` or edit `trusted_build.json`.
* Do not approve, apply, infer consent, reveal keys, read `receipt.key` or the launch token, or manufacture correct answers as a human acknowledgement.
* Report NOT_RUN for any missing prerequisite. Distinguish tested behaviour, same-author inference, mocked contracts, unrun live paths and proposed follow-up work. Live provider use needs the owner's explicit consent and local credentials.
