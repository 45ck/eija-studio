# Symbols of domain.policy

# Constants

* [domain.policy.CANONICAL_OPTIONS](CANONICAL_OPTIONS.md) - The four canonical interpretations a provider may propose; only recommend_only is supported.
* [domain.policy.EFFECTS](EFFECTS.md) - The exact audit and notification effects each action must produce at commit time.
* [domain.policy.FORBIDDEN](FORBIDDEN.md) - Effects no transition may ever perform: PaymentCaptured and ParentDataExported.

# Functions

* [domain.policy.apply_transaction](apply_transaction.md) - Applies one typed SemanticTransaction to a policy-valid workflow and returns a candidate that is itself re-checked against the policy.
* [domain.policy.baseline](baseline.md) - The trusted four-state excursion workflow (Draft, Submitted, Approved, Rejected) that every Change Case starts from.
* [domain.policy.check_policy](check_policy.md) - Returns the sorted policy error codes of a workflow; an empty list means the model stays inside the protected excursion policy.
* [domain.policy.ensure_policy](ensure_policy.md) - Raises DomainError POLICY_BLOCKED when check_policy reports any finding; called before every model is executed or transformed.
* [domain.policy.meaning_questions](meaning_questions.md) - The three critical questions a local owner must answer correctly before a decision is sealed.
* [domain.policy.projections](projections.md) - Derives rules, state views and journey sentences from the executable transitions, so no view is a second source of truth.
* [domain.policy.transition](transition.md) - Builds a Transition whose guards and effects come from the protected tables, never from caller input.
