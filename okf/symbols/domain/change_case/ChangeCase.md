---
type: Class
title: domain.change_case.ChangeCase
description: Aggregate linking one request to its interpretations, chosen meaning, baseline, candidate, transactions, receipts and decision.
resource: repo://src/eija_studio/domain/change_case.py#ChangeCase
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/change_case.py#ChangeCase
  title: domain/change_case.py
  hash_method: ast-sig-v1
  sha256: f2a77561dd11e8237231fe315488ca5864a8c6dbd8fd3dcd496b3917523b3bd1
description_override: Aggregate linking one request to its interpretations, chosen meaning, baseline, candidate, transactions, receipts and decision.
notes_baseline: 81db29f6cb82731361fd3be68c10f944f76974a178e8a1ed12ea3dc3aca2b3a7
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 7cfa996320ebcd8dc82a47a1193aae8a98578009b6f86c73f2a102ee4d7770ab
  sources_sha256: 96d50b233b1935efee7ad78cd377dd0bf8e854185472d6e0780c79975a30be80
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 7cfa996320ebcd8dc82a47a1193aae8a98578009b6f86c73f2a102ee4d7770ab
  sources_sha256: 7acf1d15dd42ae056bd469cf40243203e1959eb0b4ade3f01b89e8c9933e7479
- by: process:codex-ide-integration
  at: '2026-10-02T05:15:30Z'
  notes_sha256: 51dd8c27ccd9424ae7ecefd3ea3e37160645e438b23c1c095d1f596e84695f5a
  sources_sha256: 643098bf4edb2a84d27fd5245c569da35c4b0038a03a119ea4c6f159d74da191
- by: process:playide-activation
  at: '2026-10-10T13:50:00+11:00'
  notes_sha256: 7d023d2aab2f2322e6dd1280ceb09df4ec3d8b25a37018081c6dc32b757e156d
  sources_sha256: 270ed9b56dc0e41518b6f0427eaf9275b0606fd7c0ba899978db118ef56a40a7
- by: process:playide-activation
  at: '2026-10-10T02:55:29+00:00'
  notes_sha256: 7d023d2aab2f2322e6dd1280ceb09df4ec3d8b25a37018081c6dc32b757e156d
  sources_sha256: 270ed9b56dc0e41518b6f0427eaf9275b0606fd7c0ba899978db118ef56a40a7
- by: process:playide-exact-app
  at: '2026-10-11T09:17:31Z'
  notes_sha256: c7c985ce593921bffba33e813dee30e3943440c64b0eac2bf2575f1e33e3a6cb
  sources_sha256: 81db29f6cb82731361fd3be68c10f944f76974a178e8a1ed12ea3dc3aca2b3a7
---

# domain.change_case.ChangeCase

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/change_case`](/modules/domain/change_case.md) |
| Signature | `class ChangeCase(Contract)` |
| Code | `repo://src/eija_studio/domain/change_case.py#ChangeCase` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Aggregate boundary: transitions are mediated by the application and CAS store.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` |  |
| `version` | `int` |  |
| `stage` | `Literal['DRAFT', 'PROPOSED', 'PREVIEW', 'SAVED', 'VERIFIED', 'APPROVED', 'APPLIED', 'DISCARDED']` |  |
| `request` | `str` |  |
| `baseline_version` | `int` |  |
| `baseline` | `Workflow` |  |
| `candidate` | `Workflow \| None` |  |
| `proposal` | `Proposal \| None` |  |
| `provider_run` | `dict[str, Any] \| None` |  |
| `selected_meaning` | `str \| None` |  |
| `selected_by` | `str \| None` |  |
| `selection` | `Selection \| None` | `None` |
| `transactions` | `tuple[Transaction, ...]` |  |
| `redo_transactions` | `tuple[Transaction, ...]` | `()` |
| `layout` | `dict[str, dict[str, int]]` |  |
| `receipts` | `tuple[dict[str, Any], ...]` |  |
| `decision` | `dict[str, Any] \| None` |  |
| `app_build` | `GeneratedAppBinding \| None` | `None` |
| `created_at` | `str` |  |

## Methods

* [`at_version`](/symbols/domain/change_case/ChangeCase.at_version.md) - `def at_version(self, expected: int) -> None`
* [`executable`](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow`
* [`require_editable`](/symbols/domain/change_case/ChangeCase.require_editable.md) - `def require_editable(self) -> None`
<!-- okf:generated:end facts -->

## Notes

`redo_transactions` is a persisted command stack, empty by default for older compatible
cases. The selected meaning or exact owner plan stays an atomic prefix outside undo. Restoring a model
does not restore its old version or decision; fresh edits discard the redo branch.

The optional tagged `selection` distinguishes `pack_meaning` from `owner_plan`.
Legacy cases retain their existing `selected_meaning` and history. Owner plans
retain pack/baseline/candidate identities and reported step provenance, with
owner authority recorded separately as `selected_by`.

The aggregate behind [Change Case](/language/change-case.md). Its `version` is a compare-and-swap counter distinct from an instance version. Stage never grants eligibility on its own: [compile_case](/symbols/application/compiler/compile_case.md) computes it. `APPLIED` and `DISCARDED` cases are closed ([require_editable](/symbols/domain/change_case/ChangeCase.require_editable.md)).

Optional app_build carries a typed exact generated subject plus checker/configuration binding. It defaults to None for historical case JSON. Existing receipt bytes and workflow-only subject meaning remain unchanged for those cases.

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.Selection](/symbols/domain/change_case/Selection.md) - Type alias `Selection` in `domain/change_case`.
* [domain.generated_app.GeneratedAppBinding](/symbols/domain/generated_app/GeneratedAppBinding.md) - `class GeneratedAppBinding(Contract)` in `domain/generated_app`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [Change Case](/language/change-case.md) - Aggregate linking one original request to interpretations, chosen meaning, baseline, candidate, transactions, receipts and decision.
* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
* [application.generated_app.activation_association](/symbols/application/generated_app/activation_association.md) - Exact-app provenance to be committed atomically with the active model by Studio.
* [application.generated_app.app_build_blockers](/symbols/application/generated_app/app_build_blockers.md) - `def app_build_blockers(case: ChangeCase, view: dict[str, Any]) -> list[str]` in `application/generated_app`.
* [application.generated_app.app_build_view](/symbols/application/generated_app/app_build_view.md) - Keep workflow evidence separate from generated application execution evidence.
* [application.generated_app.app_current](/symbols/application/generated_app/app_current.md) - Remeasure a selected application's current bytes through the existing port.
* [application.generated_app.capture_app](/symbols/application/generated_app/capture_app.md) - Bind the checked payload to this exact selected case; persistence stays in Studio.
* [application.generated_app.require_app_current](/symbols/application/generated_app/require_app_current.md) - A workflow-only historical case remains unbound; a bound app must still be current.
* [application.generated_app.verify_app](/symbols/application/generated_app/verify_app.md) - Seal the observed checker artifact, without approving or writing the case.
* [application.history.command_event](/symbols/application/history/command_event.md) - Append-only command provenance; decision and receipt payloads remain in their existing audit.
* [application.history.history_view](/symbols/application/history/history_view.md) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [domain.change_case.ChangeCase.at_version](/symbols/domain/change_case/ChangeCase.at_version.md) - `def at_version(self, expected: int) -> None` in `domain/change_case`.
* [domain.change_case.ChangeCase.executable](/symbols/domain/change_case/ChangeCase.executable.md) - `def executable(self) -> Workflow` in `domain/change_case`.
* [domain.change_case.ChangeCase.require_editable](/symbols/domain/change_case/ChangeCase.require_editable.md) - `def require_editable(self) -> None` in `domain/change_case`.
<!-- okf:generated:end links -->
