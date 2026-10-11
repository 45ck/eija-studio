# PlayIDE delivery contract

Approved direction, **11 October 2026**. The [roadmap](../ROADMAP.md) holds milestones and current capability scope; the [mission](MISSION.md) and [self-dogfood acceptance](SELF-DOGFOOD-ACCEPTANCE.md) define product and evidence quality.

## Ship continuously

During this initial stage, make small coherent commits and push them promptly **directly to `main`**. A feature branch or pull request is not the default prerequisite for each improvement. Ship useful previews throughout a milestone, with stronger release claims only when their acceptance evidence exists. This supersedes older lane-branch/PR sequencing in the mission, lane map, WBS and contribution guidance for the current owner-authorised development effort.

1. Inspect the working tree and remote state. Preserve unrelated changes, other contributors' work and original evidence. Assign one integration owner; parallel contributors own disjoint files and report their checks.
2. Implement a reviewable increment with appropriate failure checks. Stage only that increment; do not sweep unrelated work into a commit. Check its diff for secrets, private paths and misleading claims.
3. Run targeted checks and `nox -t fast` before committing. Fix failures without lowering budgets or changing expected results merely to pass. Commit with a concrete description of the behaviour and verification.
4. Fetch and reconcile remote changes before pushing. Push the verified commits to `main` without force pushing. The supplied pre-push hook runs `nox -t full` when installed; respect active hooks. Batch small commits into the next passing full-tier push when needed rather than bypassing hooks.
5. Observe the actual remote result and any configured checks. Repair or revert regressions promptly; keep `main` usable. Report commit identifiers, verification, unresolved limitations and the next useful increment.

Run `python scripts/verify_release.py` for changed implementation and the broader integrated acceptance on a release candidate. Keep `SOURCE_REVIEW_REQUIRED` separate from functional failures. An expected source-review restriction can accompany an honestly labelled development preview; it is never permission to claim trusted activation or bypass a failing hook.

**CI baseline:** `.github/workflows/test.yml`, `quality.yml` and `guardrails.yml` are manual-dispatch definitions. Automatic checks on push are **NOT_CONFIGURED** in the inspected repository configuration. A supplied Linux workflow is not a completed Linux run. Report remote checks as NOT_RUN unless a real result is retained, and report local gates as local. Reassess hosted automation through a separate reviewed infrastructure change.

**Hook baseline:** the inspected integration checkout has no configured `core.hooksPath`. Committed `.githooks/` files do not establish automatic execution; [ADR-0036](../adr/0036-noslop-hooks-adapted-to-nox.md) makes installation explicit. Check each checkout's effective hook configuration and report manual gate runs separately. Do not claim a hook ran from the presence of its file, or change shared hook configuration silently.

Direct-main delivery grants no authority to restamp trusted source, approve a model as the owner, bypass protected-hook review, read credentials, spend on providers, migrate user data or deploy production services. Existing security controls remain in force. Reassess this initial policy when external contributions, shared environments or production obligations require a different process.

## One connected product

Keep domain concepts, requirements, UML, C4, generated screens, source links and evidence connected through versioned identities. There is one semantic kernel; diagrams and browser interactions do not invent parallel policy. AI output is an untrusted proposal. Source connections remain read-only until a separately supported transformation contract exists.

The core interaction is **build → predict → try → inspect → repair → see the improvement**. Reward observed outcomes, make refusals useful and preserve the last valid state. Apply shared design quality to both the workbench and generated apps. Theme, density, layout and motion preferences do not become executable policy.

The first release scope is the coherent local workflow in M1. M2–M5 add data-dependent behaviour and migrations, relationships and delivery, source transformations/parallel work, then shared operations. Work can be committed incrementally before an entire milestone is ready; unsupported capabilities remain visibly unsupported.

## Evidence and milestone ledger

For each increment, link the existing requirement/issue and record:

| Field | Required record |
|---|---|
| Outcome and owner | User-visible result, integration owner and contributing file/module owners |
| Subject | Commit plus dirty-content manifest where relevant; pack/model/configuration, generator and checker identities |
| Four delivery states | Implemented, integrated, exercised and release-ready separately; evidence status PASS, FAIL, PARTIAL, STALE or NOT_RUN with scope |
| Acceptance | Existing AC, SD01–SD12 and UX01–UX08 IDs that apply; new criteria only for genuinely new semantics |
| Observations | Exact command/journey, raw result location, meaningful negative controls, browser/platform/tool versions and skipped prerequisites |
| Next action | Remaining defect, dependency or legitimate owner/external checkpoint |

Link dated run records instead of duplicating their totals. Record each milestone's entry dependencies and exit observations from the roadmap; a merged change or completed assignment is not an observed pass. Keep original failures and distinguish structural source links, model checks, direct service observations, browser execution, live providers and human study results.

The repository's current trusted-user, loopback boundary remains explicit. Generated apps need versioned revision/migration contracts before retaining data across incompatible changes. Production identity, delivery and recovery require their own implementation and adversarial evidence.

## Releases and demonstrations

Prove installation outside the repository in a fresh environment, including a path containing spaces. Record the tested Windows/Linux matrix; do not infer a platform pass from a workflow file. Distribution must include required packs/resources or document and verify their installation.

Retain inspected 30–90-second clips of actual interactions with raw recordings, revision records, outcomes and skipped functionality. Use normal security settings and pinned recording dependencies. No slideshows standing in for execution, fabricated success, or fixture credentials presented as real identity. A longer walkthrough follows the complete supported flow. Keep local capture paths out of public documentation; publish a portable reproduction record and licensed, reviewed media.

The four product outcomes are reproducible installation, understandable supported changes, visible consequential failures and satisfying experimentation/recovery. The later engineer study tests whether PlayIDE improves decisions and maintenance effort. Viral reach and superiority to alternatives require observations; they do not follow from release frequency.
