# ADR-0222: Exact owner-plan selection and activation

* Status: accepted (workflow-only drafts under an unchanged pack identity)
* Date: 2026-10-10
* Lane: PlayIDE exact-plan activation

## Context

PlayIDE can preview accepted diagram and proposer edits, but its previous handoff created a Change Case from request text alone. Reinterpreting that request loses the exact reviewed batch. A runnable preview and the synthetic EIJA review reference pack do not establish that the actual application implements the represented lifecycle.

## Decision

Introduce an owner-selected plan origin alongside the existing named pack meaning. The immutable selection prefix contains the accepted typed workflow transactions and their provenance. A single application operation recomputes the candidate using the existing policy interpreter, checks the exact pack, baseline version and semantic identities, and atomically inserts the selected case and its audit event. Client candidate bytes, proposer wording and preview results grant no authority.

Replay, undo and redo retain that immutable prefix. Existing named-meaning cases remain readable and replayable. Verification, owner approval, application, subject freshness and the SQLite baseline compare-and-swap keep their existing enforcement responsibilities.

The first promotion contract accepts workflow transactions only. Data schemas, role/action vocabulary, laws, screens and scenarios remain explicit drafts. Changing these requires a separate system-revision and migration contract. No pack files or connected repository source are overwritten by activation.

## Evidence and interaction

PlayIDE presents exact model differences, source-review state, computed per-kind checks and owner-entered review answers in one workbench. Only the owner's explicit UI action requests approval or activation. Positive lifecycle mechanics run in disposable, clearly labelled engineering fixtures; they never stamp a production source identity or constitute owner approval.

Requirements retain their existing acceptance IDs. Explicit requirement/law/model/test links use the existing traceability vocabulary; unresolved links remain visible. Requirement prose changes are content changes and cannot silently become executable policy. The capability map distinguishes executable behaviour, checked design and unsupported constructs.

## Consequences

The reviewed draft can become active without a second provider interpretation. Material edits and competing baselines still invalidate applicability. New builds and reopened workspaces must use the active baseline; an old running preview is visibly stale.

Actual application methods, transactional storage and negative mutations provide behavioral evidence distinct from model simulation and syntax extraction. Source-review mismatch remains a separate release boundary. This milestone does not provide real authentication, general source rewriting, multi-record execution or production operations.
