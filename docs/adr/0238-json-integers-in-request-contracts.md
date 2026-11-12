# ADR-0238: Integers in request contracts are JSON integers

* Status: accepted
* Date: 2026-11-12
* Lane: kernel / contracts (issue #235)

## Context and problem statement

`contracts/*.schema.json` declare integer fields as `"type": "integer"`. Under JSON Schema 2020-12 that accepts `5` and
`5.0` and refuses `"5"` and `true`. The Pydantic models disagreed in both directions, and three strict xfails in
`tests/property/test_contract_schemas.py` recorded the drift:

* Lax ints (`LayoutChange.x`/`y`, the integer fields of `ChangeCase`) accepted `"5"` and `true`. That is fail-open on type.
* `ExecuteCommand.expected_version` was `strict=True`, so it refused `1.0`, which `json.dumps(1.0)` writes. That is fail-closed.

## Decision drivers

* The published contract and the model must give the same verdict on every input.
* Untrusted requests must not get a looser reading than the contract states.

## Considered options

* `StrictInt` everywhere. Rejected: it refuses `1.0`, which the contracts allow.
* Narrow the schemas to refuse integral floats. Rejected: the schemas follow JSON's single number type, and other
  clients would have to know a Python-specific rule.
* A `JsonInt` type: an int, or a finite float with no fractional part, read as an int. A string, a boolean, a
  fractional float, NaN or infinity is refused (chosen).

## Decision outcome

`domain.models.JsonInt` is used for `LayoutChange.x`/`y`, `ExecuteCommand.expected_version`, and `ChangeCase.version`,
`baseline_version` and `layout`. The owner-plan request's `round` and `expected_baseline_version` use it too, since
they had the same strict-int refusal of `1.0`. The three xfails are removed, so the property test now checks the
contracts and the models agree on every integer coercion. A fast regression test in `tests/test_hostile_input.py`
pins the cases.

### Consequences

* Good: the schema and the model agree, and a request can no longer send `"5"` or `true` for a number.
* Neutral: a stored case is read back with real ints, so nothing stored changes.
* Bad: `GeneratedAppBinding`'s strict ints (`timeout_seconds`, `baseline_version`) still refuse `1.0`. They are
  evidence bindings the kernel writes itself, not request input, so they stay as they are.
