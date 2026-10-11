# Exact model changes in PlayIDE

PlayIDE can transfer the exact accepted workflow draft into a review case. No second proposal or interpretation is needed. The server recomputes the candidate through the existing interpreter and checks the pack digest, active baseline version/hash and candidate hash before storing anything.

## Ordinary local journey

1. Start the normal offline application with a pack and a disposable local workspace. Connect this checkout read-only with `--repo` when inspecting PlayIDE itself.
2. Draw or request a workflow edit. Inspect the UML difference and the accepted steps, including reported authorship.
3. Open **Review & activate** and **Transfer exact accepted steps**. The candidate is now a retained case; the active model is unchanged.
   **Effects across system** compares the candidate to its retained baseline, using
   the existing ripple checks for states, data classes, use cases, screens,
   generated components, scenarios and the declared system landscape. An explicit
   round comparison remains scoped to that round. Unbound impact is not a safety claim.
   Choose the connected overview or grouped details and customise which views are
   emphasised. These browser preferences preserve every view and unknown; they do
   not change the model or evidence. Connectors group views of the comparison,
   rather than claiming causal or runtime edges.
4. Inspect the checks, source-review status, questions and evidence scope. Verification reports a source-review refusal until the source gate permits fresh evidence.
5. The local owner enters answers for the exact reviewed subject and acknowledges the unknowns. Approval records that decision. **Activate approved revision** is a separate action.
6. After commit the active revision is loaded across views. Build & run uses it. Reopening the same workspace preserves it. Earlier drafts remain recoverable but do not automatically replace the active model.

Changed implementation reports **SOURCE_REVIEW_REQUIRED**. An agent cannot restamp source, fabricate the owner's answers or approve this change autonomously. Engineering fixtures test the mechanics separately and never satisfy that release boundary.

## What can become active

The first contract promotes existing typed workflow transactions under an unchanged pack identity. It refuses mixed data-schema, action/role vocabulary, actor-kind, law, screen and scenario edits. Those edits remain drafts until their revision and migration contracts exist. Activation writes the existing SQLite baseline; it does not rewrite pack files, connected source or an already running generated application's records.

`POST /api/cases/from-plan` carries the accepted commands, their reported provenance and expected identities. The response is a selected `PREVIEW` case with a tagged `owner_plan` origin. Named pack meanings retain their `pack_meaning` origin, and old cases remain replayable. Both origins protect their initial command batch from undo; subsequent owner edits keep the existing history and evidence invalidation rules.

## Requirements, rules and capability coverage

**Capabilities & requirements** shows executable, checked-design and unsupported parts of the software lifecycle. The acceptance CSV snapshot names its original revision, byte identity and historical statuses; those statuses are not fresh test results. Pack-owned explicit links use `formalises`, `satisfies` and `verifies`; a missing link or unexecuted check remains visible.

Requirement wording is a prose draft. Law descriptions and executable law fields are compared separately using the existing law contracts. Draft comparisons cannot silently change active policy. Follow links to a model or law and inspect actual simulation traces; selecting a trace step never reruns or changes that record.

## Verification and retained evidence

Run the normal applicable gates and `python scripts/verify_release.py`. Preserve source-review mismatch as a separate expected release limitation. Direct-call implementation observations and their seven behavioral fault controls are documented in [the checker contract](PLAYIDE-ACTIVATION-EVIDENCE.md). Browser transport, generated-app conformance, finite model-law search, source facts and those service observations are different evidence kinds.

The user-facing recordings are real local application interactions with ordinary CSP enforcement. A fixture showing approval/activation must be identified as an isolated engineering test, not a real owner's approval. No live inference, institutional authentication, external delivery, deployment or PR publication is established by this milestone.

## Coverage references and the next executable slice

The capability map is a bounded account of this kernel, not a claim of standards
conformance. [OMG fUML 1.5](https://www.omg.org/spec/FUML/1.5) supplies an established
syntax and execution-semantics reference for future action inputs, object updates,
values and activities. Each supported construct needs a typed meaning, runtime
observation and useful refusal before it is labelled executable here.

[OWASP ASVS](https://github.com/OWASP/ASVS) is the application-security coverage
reference. This slice exercises local capability enforcement, exact review subjects,
stale evidence and concurrency; it does not establish institutional authentication
or a complete ASVS assessment. [WCAG 2.2](https://www.w3.org/TR/WCAG22/) is the
accessibility coverage reference, including keyboard operation, visible focus,
focus not obscured and programmatically available status messages. Browser focus
and dialog checks are evidence for selected interactions, not whole-product
accessibility conformance.

After legitimate source review and the ordinary activation checkpoint, the next
useful application is a record action with typed input, a validated update and a
value condition. Show a refused value, its rule and the retained record values;
then change the model, check and retry. Relationships and connected workflows
follow once their persistence, multiplicity, delivery and recovery semantics exist.
