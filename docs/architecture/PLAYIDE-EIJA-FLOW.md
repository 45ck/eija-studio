# How PlayIDE, executable UML and EIJA fit together

**11 October 2026 — implementation guide, not milestone acceptance.** PlayIDE is the browser workbench shipped by the `eija-studio` Python package. EIJA supplies its typed model contracts, compiler, policy checks, application generator, runtime and review services. They are parts of one project, not competing products or separate sources of business meaning.

## One model, several different jobs

| Part | Its job | What it does not establish |
|---|---|---|
| Supported UML model | States, transitions, roles, supported guards/effects and the record contract describe executable behaviour | Arbitrary UML, drawings and imported source do not automatically become executable |
| EIJA policy and typed edits | Validate a candidate and refuse unsupported or prohibited changes | A valid edit is not owner approval |
| EIJA compiler | Derive projections, mapped impact, obligations, evidence applicability and the review packet | It is a bounded semantic/report compiler, not an arbitrary-source compiler |
| App generator | Produce model/configuration files, HTTP/storage adapters, a frontend and conformance cases from one snapshot | Generation is not activation, deployment or a data migration |
| EIJA runtime kernel | Decide each supported action using current actor, state, version, operation binding and effects | It does not supply real authentication or external delivery |
| PlayIDE frontend | Edit, compare, navigate, try the app and inspect results | The browser does not grant authority or create trusted evidence |
| C4, source links and other projections | Explain generated structure or explicitly extracted/bound relationships | They do not execute rules or prove arbitrary source behaviour |

`eija compile` emits model/report artifacts and optionally applicable verification evidence. `eija build` generates a runnable bundle and its conformance check. The Studio uses the corresponding services directly; it does not have to invoke the CLI. The generator and review compiler consume the supported model through different paths, rather than one compiler output automatically becoming an approved application.

Executable support is deliberately bounded. Flat workflow states/transitions, declared roles/guards/effects and one validated record class have runtime meaning. Other classes, relationships, screen designs, C4 and domain-language links have their own design/projection standing. Value conditions, general updates/migrations, external timers and connected-workflow delivery need further semantics. See the [capability roadmap](../ROADMAP.md) and [executable UML profile](executable-uml.md).

## Two frontends and two databases

**The workbench frontend** is hand-written HTML, CSS and JavaScript, served by the local Studio. Feature scripts share the current model/view context. maxGraph supplies diagram interactions and rendering; Dagre supplies layout. There is no Node build step required to run it. Browser state holds presentation preferences and recoverable drafts; authoritative checks and model operations go through the Studio API. A rendered green result is only useful when it belongs to the current subject.

**The generated frontend** uses React and Mantine components, rendered from the build's screens, record fields, fixture actors, actions, outcomes and history. Maintainer tooling bundles JavaScript and external CSS; ordinary Python users need neither Node nor a CDN. The emitted app retains authored source, the exact dependency lock, licences and a build manifest. In Design + Play it lives inside an iframe beside the model, and can also open separately. It calls the generated application's HTTP API, not the Studio review API. See [ADR-0225](../adr/0225-react-for-generated-application-frontends.md).

| Store | Owns | Must remain separate |
|---|---|---|
| Studio workspace SQLite | Active baseline, change cases, review history, receipts, decisions and Studio preview instances | Generated app actions cannot approve or activate a change case |
| Generated app SQLite | App records, operation replay, audit and local outbox entries | This is not the Studio workspace database or an owner-review receipt store |

Both use the relevant application/storage adapters. The generated app runs a separate local server and requires the matching installed EIJA package. Its stored records survive an unchanged rebuild; incompatible model/data identities are refused rather than silently migrated. The actor picker is a fixture directory, not login.

## Follow one edit

1. A diagram gesture or proposal produces typed plan steps. PlayIDE chat currently uses an offline phrase reader; a general live model is not established by that interface.
2. The Studio resolves the active baseline or selected case, checks the expected model identity and applies accepted steps through the typed interpreter and policy. Browser-provided candidate state is not silently trusted.
3. Diff, ripple, screen checks, scenarios and architecture views derive their own scoped results. Draft previews can be inspected and built without changing the active baseline. Layout preferences do not become semantic edits.
4. **Build & run** generates one snapshot, checks its payload/implementation identity, runs the declared conformance cases and starts the local app. Those cases compare the generated adapters with the kernel's answers; this is bounded conformance, not independent proof of the kernel.
5. **Build exact app for review**, then **Transfer exact accepted steps**, sends workflow commands, provenance, expected model identities and the expected generated build digest to the owner-only `/api/cases/from-plan`. The server independently assembles the candidate and freezes the matching bundle. A retained case then uses the existing evidence, explicit owner decision and atomic-application services.
6. Activation changes the Studio's active workflow revision and atomically records its exact generated-app association. It does not rewrite connected repository source, migrate generated-app records or automatically replace an already running app. Subsequent builds use the active revision and claim `ACTIVE_APPROVED` only when they match the valid applied case and stored binding. Unsupported mixed policy/schema/screen changes remain drafts.

## Follow one app action

1. The generated frontend sends an action, fixture actor, expected record version and operation identity to its own HTTP API.
2. Its storage service opens a transaction and calls `runtime.execute`. The kernel checks current authority before replay, then state/version and operation binding; the adapter persists the state, audit, outbox and operation together or rolls back.
3. Only after the transaction completes does the API return a committed result or refusal. The frontend renders the server outcome.
4. The embedded frontend sends a minimal observation back to PlayIDE. The receiver checks the actual frame/window, origin, recording nonce, model/build subject and declared action vocabulary. Duplicate, stale or mismatched observations do not become new diagram actions.
5. PlayIDE animates and records that observation. Pause/step/replay inspect the recorded events without resubmitting actions. The bridge is a scoped UI observation channel, not a cryptographic proof or an owner approval channel. Model simulation remains separate.

For RefundDesk, `FailPayout` is a successful local commit reporting the business state `PayoutFailed`. It is not an HTTP transport failure or evidence that a payment provider was contacted.

## Identity and evidence boundaries

The generated **build subject** binds the workflow, pack, data, screens, templates, installed implementation and generated payload. The generated server checks its installed implementation against that subject; C4 projects the same generated snapshot and the trace handshake names its build digest.

The **review subject** retains workflow meaning, presentation and the existing implementation/policy/environment/harness dimensions. Newly bound exact-app cases additionally identify the generated envelope and the checker/configuration used to execute conformance. Changed templates, React assets, data, screens, payload or implementation invalidate that match. Historical workflow-only cases stay historical and cannot claim exact-app approval. See [ADR-0224](../adr/0224-approve-the-exact-generated-application.md).

The generated conformance receipt records observed execution; kernel verification cannot substitute for it. Captured bundle bytes are remeasured before consequential operations. Approval belongs to a case, baseline and complete subject. A failed check followed by a pass remains conflicting evidence; repair and start a fresh review case rather than erase the failure.

`SOURCE_REVIEW_REQUIRED` remains visible until legitimate review of changed implementation. Structural source links, model-law checks, service observations, generated-app conformance, browser interactions and human comprehension are distinct claims. A hash identifies the subject; it does not prove correctness. Unknown and stale results remain visible.

## Where the connections live

These are navigation pointers to the current implementation, not a second specification:

| Follow this concern | Source |
|---|---|
| Workbench page and diagram/editor coordination | [play.html](../../src/eija_studio/resources/web/play.html), [play.js](../../src/eija_studio/resources/web/play.js) |
| Studio routes, model resolution and exact plan transfer | [http.py](../../src/eija_studio/interfaces/http.py), [play.py](../../src/eija_studio/interfaces/play.py) |
| Semantic review compiler and CLI compilation | [compiler.py](../../src/eija_studio/application/compiler.py), [cli.py](../../src/eija_studio/interfaces/cli.py) |
| Generated contracts, templates and bounded conformance | [appgen.py](../../src/eija_studio/application/appgen.py), [app_build.py](../../src/eija_studio/interfaces/app_build.py) |
| Shared decisions and generated storage/API | [runtime.py](../../src/eija_studio/application/runtime.py), [service template](../../src/eija_studio/resources/appgen/service.py.tmpl), [server template](../../src/eija_studio/resources/appgen/server.py.tmpl) |
| Generated frontend and observed-action bridge | [React source](../../src/eija_studio/resources/appgen/react-source/main.jsx), [app template](../../src/eija_studio/resources/appgen/web/app.js.tmpl), [play-live.js](../../src/eija_studio/resources/web/play-live.js) |
| Exact-app evidence and atomic association | [generated-app contracts](../../src/eija_studio/domain/generated_app.py), [generation adapter](../../src/eija_studio/adapters/generated_apps.py), [Studio service](../../src/eija_studio/application/service.py) |
| Exact generated identity and C4 projection | [build_subject.py](../../src/eija_studio/application/build_subject.py), [c4.py](../../src/eija_studio/application/c4.py) |

For current proof obligations use [self-dogfood acceptance](../engineering/SELF-DOGFOOD-ACCEPTANCE.md). The [11 October demo manifest](../demos/assets/playide-live-20261011/manifest.json) records one actual bounded run; it does not close the whole milestone.
