---
type: Method
title: application.service.Studio.apply
description: Applies an approved candidate to the local baseline only if an eligible, authentic, exact-subject decision exists.
resource: repo://src/eija_studio/application/service.py#Studio.apply
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.apply
  title: application/service.py
  hash_method: ast-v2
  sha256: bd9ccfb7a076073bd570cf4cfbdb79f19bfef9810dd633cc76b4719b850c3d9b
description_override: Applies an approved candidate to the local baseline only if an eligible, authentic, exact-subject decision exists.
notes_baseline: 7ae6c02526966d00e39783925315431f20d6984fd32aa2776f60c48430a8c479
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 54d1699727ddc6215c45a311cfd5ca0d7b2baec089d1da3d52e339a74175fd64
  sources_sha256: 227e5a988200c87eff573195eafe8d2a5f3ff1712b64f8326495d8950a1911a3
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 54d1699727ddc6215c45a311cfd5ca0d7b2baec089d1da3d52e339a74175fd64
  sources_sha256: ca2a11fdbb4c4f097688f5edebe043fbdb79a703f796a996e98eda67fb3f7a0c
- by: process:codex-ide-integration
  at: '2026-10-02T05:15:30Z'
  notes_sha256: 54d1699727ddc6215c45a311cfd5ca0d7b2baec089d1da3d52e339a74175fd64
  sources_sha256: f3fe728d004fdf9381dbdb0a3820463ff787d783299933a1d9f3a36bcb10f0a7
- by: process:playide-activation
  at: '2026-10-10T14:05:00+11:00'
  notes_sha256: 58c8f2e42e4727bf16cac09f3ca0244846d97fedc8e82e80d843d8b6f8f5565e
  sources_sha256: cf1bc858dd1b62bbf890e9d76492d3d823507a2860b227a34ed146d1da86cc75
- by: process:playide-activation
  at: '2026-10-10T02:55:29+00:00'
  notes_sha256: 58c8f2e42e4727bf16cac09f3ca0244846d97fedc8e82e80d843d8b6f8f5565e
  sources_sha256: cf1bc858dd1b62bbf890e9d76492d3d823507a2860b227a34ed146d1da86cc75
- by: process:playide-exact-app
  at: '2026-10-11T09:17:31Z'
  notes_sha256: 24b63458dce1f701d8696ea3455173a1c2daf0a90e22da3754dbe0ac5a9a05da
  sources_sha256: 9de0e87f529ab7ee40b3bad9eeee61feca0aec6c942364b2a9e6473174ac684f
- by: process:playide-service-cohesion
  at: '2026-10-12T05:30:41Z'
  notes_sha256: 98adaa0ade426746570ac7e62fc9672cd0b0423f1937450968384ec6d2822962
  sources_sha256: 7ae6c02526966d00e39783925315431f20d6984fd32aa2776f60c48430a8c479
---

# application.service.Studio.apply

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.apply` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Requires `apply` and re-computes the packet at commit time. A changed active baseline adds the `STALE_BASELINE` blocker and the gate refuses; there is no automatic rebase (acceptance [AC06](/requirements/ac06.md)).

Protected selection and history replay are validated inside the same unit of work
before the decision and baseline writes. Corrupted persisted selection provenance
or commands refuse with `HISTORY_INCONSISTENT` and leave the active model unchanged.

A signed decision must belong to this case, baseline, scope, kind and complete subject. Exact-app cases remeasure their frozen payload, then commit the active model and generated association within the same transaction as the applied case and audit event.

`activation_association` only constructs the optional provenance value; Studio still performs the authority and current-subject checks, baseline compare-and-swap, case write and audit write. An unbound historical case continues to use the workflow-only activation path. The inherited activation views report these outcomes; they do not authorize the command.

<!-- okf:generated:begin links -->
## Depends on

* [application.generated_app.activation_association](/symbols/application/generated_app/activation_association.md) - Exact-app provenance to be committed atomically with the active model by Studio.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
