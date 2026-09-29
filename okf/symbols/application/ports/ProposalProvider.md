---
type: Class
title: application.ports.ProposalProvider
description: 'The only door for AI: a provider returns an untrusted Proposal and cannot select meaning, approve or apply.'
resource: repo://src/eija_studio/application/ports.py#ProposalProvider
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#ProposalProvider
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: e729e5f4017c0f25ad40c1fdebf2e894ffc2dc24d665e4b063836c10c9e215e9
description_override: 'The only door for AI: a provider returns an untrusted Proposal and cannot select meaning, approve or apply.'
notes_baseline: 36b11ff444e878bc972d7433aed15158e16577e0a9a981098b004b464f236a4d
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 26c06fa8143628e68479b67d4d740bdde46473133f5dd061bae5a4743b830168
  sources_sha256: 36b11ff444e878bc972d7433aed15158e16577e0a9a981098b004b464f236a4d
---

# application.ports.ProposalProvider

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class ProposalProvider(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#ProposalProvider` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` |  |
| `networked` | `bool` |  |

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def propose(self, request: str, model: Workflow) -> ProviderResult`
* `def doctor(self) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

Implemented by the adapters in the `src/eija_studio/adapters/providers/` package: offline, OpenRouter, Anthropic API, and the CLI providers Claude Code, Codex, Gemini and OpenCode. Networked providers additionally need `--allow-network` and per-request consent.

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.ProviderResult](/symbols/application/ports/ProviderResult.md) - `class ProviderResult` in `application/ports`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [Provider integration](/contexts/provider-integration.md) - Owns Vendor transport, authentication delegation, limits and response normalization
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
