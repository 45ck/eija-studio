# Symbols of domain.policy

# Constants

* [domain.policy.CANONICAL_OPTIONS](CANONICAL_OPTIONS.md) - The four canonical interpretations a provider may propose; only recommend_only is supported.
* [domain.policy.EFFECTS](EFFECTS.md) - The exact audit and notification effects each action must produce at commit time.
* [domain.policy.FORBIDDEN](FORBIDDEN.md) - Effects no transition may ever perform: PaymentCaptured and ParentDataExported.

# Functions

* [domain.policy.apply_meaning](apply_meaning.md) - The candidate a supported pack meaning produces from ``model`` (policy-checked).
* [domain.policy.apply_structural_all](apply_structural_all.md) - ``model`` with every transaction applied in order; structure only, no policy (what-if and meaning previews).
* [domain.policy.apply_transaction](apply_transaction.md) - Applies one typed SemanticTransaction to a policy-valid workflow and returns a candidate that is itself re-checked against the policy.
* [domain.policy.apply_transactions](apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
* [domain.policy.baseline](baseline.md) - The trusted four-state excursion workflow (Draft, Submitted, Approved, Rejected) that every Change Case starts from.
* [domain.policy.check_policy](check_policy.md) - Returns the sorted policy error codes of a workflow; an empty list means the model stays inside the protected excursion policy.
* [domain.policy.declared_codes](declared_codes.md) - Every transition must perform a declared action, with exactly its declared guards and required effects, and must declare every pack-forbidden effect forbidden.
* [domain.policy.demo_candidate](demo_candidate.md) - The pack's baseline with its first supported meaning applied.
* [domain.policy.effects_table](effects_table.md) - Declared required effects per action.
* [domain.policy.ensure_policy](ensure_policy.md) - Raises DomainError POLICY_BLOCKED when check_policy reports any finding; called before every model is executed or transformed.
* [domain.policy.first_supported_meaning](first_supported_meaning.md) - The id of the pack's first supported meaning (the demo candidate's meaning).
* [domain.policy.forbidden_effects](forbidden_effects.md) - `def forbidden_effects(pack: Pack | None=None) -> tuple[str, ...]` in `domain/policy`.
* [domain.policy.law_violations](law_violations.md) - `def law_violations(model: Workflow, pack: Pack | None=None) -> list[Violation]` in `domain/policy`.
* [domain.policy.meaning_options](meaning_options.md) - The pack's meanings as the review surface shows them: label, whether supported, consequences.
* [domain.policy.meaning_questions](meaning_questions.md) - The three critical questions a local owner must answer correctly before a decision is sealed.
* [domain.policy.meaning_transactions](meaning_transactions.md) - `def meaning_transactions(meaning_id: str, pack: Pack | None=None) -> tuple[Transaction, ...]` in `domain/policy`.
* [domain.policy.policy_refs](policy_refs.md) - The laws and model elements a refusal points at (``law:<id>``, ``transition:<id>``, ``state:<id>``), sorted.
* [domain.policy.projections](projections.md) - Derives rules, state views and journey sentences from the executable transitions, so no view is a second source of truth.
* [domain.policy.transition](transition.md) - Builds a Transition whose guards and effects come from the protected tables, never from caller input.
* [domain.policy.what_if](what_if.md) - What an UNSUPPORTED meaning would do to ``model`` (structure only, never a candidate), or None when it declares no transactions or they do not even apply structurally.
