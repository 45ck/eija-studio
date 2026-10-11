# Design and Play: shared product craft

11 October 2026. This pass refines the working PlayIDE shell and shared web-app templates. The existing identity, typed model contracts, source review and owner authority remain the implementation boundary. The wider [HCI design system](../hci/design/design-system-architecture.md) is a proposal; this pass does not claim its entire migration, gallery or human study is implemented.

## Product and task

The workbench serves UML-literate engineers designing, checking and inspecting supported software. The primary path is **model → check/build → try the local app → inspect the outcome**. A useful failure preserves the last valid model or record and names the reason and next action. Requirements prose, executable policy, model simulation and observed implementation behaviour remain different things.

Generated apps serve people performing that model's domain tasks. The current shared generator produces local stateful record applications. Their role pickers use fixtures; event actors are manually selected; an outbox is local enqueueing. Names such as PaymentGateway do not establish a real payment integration. Typed action values, record updates, relationships, connected workflows and deployment need separately versioned semantics.

## Design direction

Treat both surfaces as Operate interfaces. Preserve the established system sans, neutral surfaces and blue action/selection accent. Use precise grouping, consistent controls and explicit current state rather than decorative animation or another layer of cards. The diagram is the playful object; the application is where a consequence becomes tangible. A layout preference must not edit the model or restart an embedded app.

The opt-in **Design + Play** layout keeps the existing single app frame beside the model, with a stacked alternative when the space is narrow. The separate model simulation remains labelled. The runtime bridge accepts scoped observations of committed actions and refusals from that generated app. A versioned build subject, frame/origin checks and a recording nonce prevent another build's messages from appearing as this run. Pause and replay inspect recorded observations without submitting actions. Browser acceptance is recorded separately from this implementation contract.

The generated template is the shared design boundary. Improvements apply to every newly generated web app without pack-specific CSS. Existing generated bundles must be rebuilt to receive them. This is a common presentation system, not a new model theme or screen schema.

## Token and component contract

| Intent | Runtime source | Rule |
|---|---|---|
| Canvas/background, panel, ink, secondary text, border | Existing `--bg`, `--panel`, `--ink`, `--muted`, `--line` | Preserve light/dark contrast; secondary does not mean unreadable. |
| Primary action and selection | `--accent`, `--accent-ink`, current/selected surface | Accent signals an action or selected state. |
| Committed outcome, refusal, warning | Existing success/refusal/warning tokens and words | Colour supplements an explicit outcome; it never supplies authority. |
| Spacing | Shared template/shell roles on the existing proposed 4 px scale | Tight control groups, more space between task groups; avoid ad hoc pack overrides. |
| Typography | System family; fixed rem sizes; tabular record/version numerals | Body and fields remain readable; long role/action/state/value text wraps. |
| Keyboard focus | Accent outline, visible focus and native controls | Cancel restores the opener; a committed/refused action gives a persistent focusable outcome. |
| Layout and table containment | `min-width:0`, structural breakpoints, full rule wrapping | No truncation of authority, rules or failure reasons. |

The workbench and generated apps have separate CSS bundles and existing palette aliases. They share semantic roles and craft rules; this pass does not introduce a second token compiler or a universal component framework.

## State and recovery rules

- Current role, current record state and available actions are visible together. Actions remain server-derived; another role's unavailable command explains its constraint.
- Create/action inputs survive a server refusal. Errors sit by the task and name the observed problem. Do not infer field authority from free-text error prose.
- Reads can expose an explicit reload/retry. Mutations must never retry automatically: the user should inspect the outcome before deciding again.
- Controls have coherent default, hover, focus, disabled and busy presentation. Reduced motion and forced-colour environments retain meaningful state cues.
- Forms, table headings, status announcements and keyboard traversal use native semantics. An automated accessibility pass is bounded evidence, not a WCAG conformance certification.
- In tall app panes the measured opaque header keeps the fixture actor visible. Short panes retain normal document flow. Rule tables adapt to their own panel width: narrow panels show labelled full-width values while retaining accessible table headers and server order.

## Guidance and provenance

Applied [Impeccable](https://github.com/pbakaus/impeccable) 4.5.2 at source revision `d631a8827f99414d2b6daba4ef08b7f8701751d7`, Apache-2.0, downloaded outside the repository into this chat's task-local skills directory. Its context check permits scoped refinement of the incumbent system. Relevant playbooks: Operate, Layout, Harden and Craft floor. No provider hooks or runtime dependency are added to PlayIDE.

The local design-token-alignment, accessibility-precheck and cognitive-friction-detector skills complement that guidance. They supply questions and practices; actual application checks and visual inspection supply observations.

## Acceptance and evidence

Run the real application under normal CSP. Inspect the paired shell at desktop and narrow supported workbench sizes, persistence, keyboard resizing and the unchanged default dock. Test generated apps with long labels at 320, 768, 1024 and 1600 CSS pixels, both colour schemes, keyboard action cancellation, commit/refusal and explicit read recovery. Preserve meaningful negative tests, records and history. Record an actual 30–90-second interaction after checking the source identity; retain raw media and inspect the final MP4.

Mechanical skill findings, observed layout, service behaviour and human comprehension are separate records. No claim of effortless use, superior builder performance or viral distribution follows from this pass. `SOURCE_REVIEW_REQUIRED` remains visible until legitimate owner review. Earlier clips and review bundles retain their old revision identities.

The trusted implementation fixture and generated build subject have different scopes. The build subject explicitly binds template bytes, generated files, workflow, pack, data, screens and measured implementation. The core implementation manifest now also includes generator templates, making previous review evidence stale after a template change. Generated servers refuse to start against a different installed implementation. Captures retain the template manifest and source revision as well. No build digest grants owner approval or restamps the trusted-source fixture.
