# Symbols of application.memo

# Classes

* [application.memo.IdentityMemo](IdentityMemo.md) - A small, bounded memo for pure functions of frozen contracts, keyed by the identity of the arguments.

# Functions

* [application.memo.ensure_conforms](ensure_conforms.md) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check's own.
* [application.memo.model_hash](model_hash.md) - `model.semantic_hash`, computed once per model object.

# Methods

* [application.memo.IdentityMemo.get](IdentityMemo.get.md) - `def get(self, args: tuple[Any, ...], compute: Callable[[], _T]) -> _T` in `application/memo`.
