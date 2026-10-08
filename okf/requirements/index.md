# Acceptance matrix criteria and their evidence

# Acceptance Criteria

* [AC01: Contract](ac01.md) - PASS_LOCAL: Unknown fields/operators and malformed transactions are rejected before preview.
* [AC02: Projection](ac02.md) - PASS_LOCAL: Rule-table and state-view edits of the same meaning yield the same semantic transaction and domain hash.
* [AC03: Projection](ac03.md) - PARTIAL: Layout-only edits preserve domain hash and domain receipts; presentation hash changes and affected UI evidence is reconsidered.
* [AC04: Isolation](ac04.md) - PASS_LOCAL: Preview and save do not change baseline files, aggregate state or external effects.
* [AC05: Isolation](ac05.md) - PARTIAL: Discard restores the prior baseline without candidate data leakage.
* [AC06: Concurrency](ac06.md) - PASS_LOCAL: A stale baseline or aggregate version rejects apply; no silent overwrite or implicit rebase.
* [AC07: Intent](ac07.md) - PASS_LOCAL: Ambiguous sign-off request remains proposed until an explicit authority chooses an interpretation.
* [AC08: Authority](ac08.md) - PARTIAL: The proposing agent cannot approve its own change; missing reviewer capability blocks apply.
* [AC09: Authority](ac09.md) - PASS_LOCAL: Teacher final approval is denied under every candidate path and direct API call.
* [AC10: Guards](ac10.md) - PASS_LOCAL: Recommend requires active and assigned actor from trusted fixture state; missing/unknown resolver blocks rather than ignores.
* [AC11: Authority](ac11.md) - PASS_LOCAL: Role or assignment revocation after preview is checked at commit and blocks stale authority.
* [AC12: Workflow](ac12.md) - PARTIAL: Recommend requires Submitted; registrar Approve/Reject requires Recommended; Submit and Revise remain valid.
* [AC13: Effects](ac13.md) - PASS_LOCAL: One accepted Recommend produces one audit append and at-most-once local notification enqueue; payments/export never occur.
* [AC14: Replay](ac14.md) - PASS_LOCAL: Duplicate operation replay binds actor, target and payload; mismatched reuse is denied and replay does not bypass current authority.
* [AC15: Truthful UI](ac15.md) - PARTIAL: Success appears only after commit; failure/stale version never renders Recommended/Approved as achieved.
* [AC16: Impact](ac16.md) - PASS_LOCAL: Typed traversal reaches beyond depth five and terminates on cycles; capped traversal returns complete=false and a frontier.
* [AC17: Evidence](ac17.md) - PASS_LOCAL: Affected evidence and approvals become inapplicable after material edits; original receipt payloads remain unchanged.
* [AC18: Evidence](ac18.md) - PASS_LOCAL: Wrong model/core/build/policy/environment/harness identities cannot satisfy a required claim.
* [AC19: Admissibility](ac19.md) - PASS_LOCAL: Browser/synthetic evidence cannot satisfy a claim about real teacher comprehension.
* [AC20: Admissibility](ac20.md) - PASS_LOCAL: Caller-supplied PASS/current/admissible/approved flags cannot override independently computed policy.
* [AC21: Meaning](ac21.md) - PARTIAL: All projected labels distinguish recommendation from final approval; changed registrar prerequisites are explicit.
* [AC22: Decision](ac22.md) - PARTIAL: Approval is bound to reviewer, scope and exact subject; a material edit during review invalidates it before local apply.
* [AC23: Trust boundary](ac23.md) - PARTIAL: Core change or unsupported semantics requires source-level review; ordinary approval cannot silently bless it.
* [AC24: Scope](ac24.md) - PASS_LOCAL: Technical eligibility may coexist with visible human UNKNOWN; field-use scope requiring that claim cannot pass.
* [AC25: Export](ac25.md) - PARTIAL: Export includes original intent, transaction, before/after subject, completeness, receipts, traces, decision and unknowns with verified hashes.
* [AC26: Independent evaluation](ac26.md) - NOT_RUN: An independent hidden mutation set tests authority, assignment, omissions, evidence, labels, effects and approval; no compensating aggregate score.
* [AC27: Local durability](ac27.md) - PASS_LOCAL: If SQLite persistence is implemented, workflow/operation/audit/outbox commit atomically and crash tests expose no partial accepted operation.
* [AC28: Human validation](ac28.md) - NOT_RUN: Reviewer benefit is not labelled measured until an actual counterbalanced task study records correctness, errors, time and full effort.
