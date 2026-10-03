"""Schema/model drift detection for ``contracts/*.schema.json`` against the Pydantic contracts.

The published JSON Schemas are what clients and agents read; the Pydantic models are what the kernel
enforces. Drift between them is a silent contract bug. ``hypothesis-jsonschema`` generates instances
from each committed schema and this module checks both directions:

1. *Schema-valid => model accepts.* The model may still reject an instance for a cross-field rule that
   JSON Schema cannot express, but only with a model-level ``value_error`` (see ``CROSS_FIELD``).
   Any other rejection (pattern, length, enum, extra key, type) is drift.
2. *Model accepts => schema-valid.* Applied to schema-generated instances after one random mutation
   (added/removed key, retyped, longer/shorter string, +/-1 numbers, array grown/shrunk): anything the
   model still accepts must validate against the schema, otherwise the published schema is stricter
   than the enforced contract.

What this establishes: the committed schemas and the models agree on structure, bounds, enums and
required keys over the generated and near-miss instances. What it does NOT establish: agreement on
cross-field rules (listed in ``CROSS_FIELD`` and covered by domain tests), or behaviour of an
implementation of JSON Schema in another language (regular expressions differ; see ``pattern_safe``).
"""
from __future__ import annotations

import copy
import functools
import json
import re
from typing import Any

import pytest
from hypothesis import assume, given, settings, strategies as st
from hypothesis_jsonschema import from_schema
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.models import BASE_GUARDS, OWNER, Alternative, ExecuteCommand, LayoutChange, Proposal, Workflow
from eija_studio.domain.transactions import RetargetTransition, SetRole, TransactionDocument
from .property_strategies import workflows
from .property_support import REQUEST, ROOT, ephemeral_studio, examples, scratch_directory

CONTRACTS = {
    "change-case": ChangeCase, "execute-command": ExecuteCommand, "layout-change": LayoutChange,
    "proposal": Proposal, "semantic-transaction": TransactionDocument, "workflow": Workflow,
}

# Rules enforced by ``model_validator`` that JSON Schema (structural) cannot state. A schema-valid
# instance may be refused by the model with exactly these messages and no other.
CROSS_FIELD = (
    "Mandatory guards cannot be removed", "Duplicate guards", "Duplicate required effects",
    "Required/forbidden effect conflict", "Duplicate states or missing initial state", "Dangling transition state",
    "Duplicate or ambiguous transition/action", "Duplicate interpretation", "Unknown description too long",
)


# Nested schemas cost far more per generated instance (hypothesis-jsonschema fills every branch).
GENERATED_BUDGET = {"change-case": 15, "workflow": 40, "proposal": 40}
NEAR_MISS_BUDGET = {"change-case": 100, "workflow": 60, "proposal": 100}


def load(name: str) -> dict:
    return json.loads((ROOT / "contracts" / f"{name}.schema.json").read_text(encoding="utf-8"))


def pattern_safe(value: Any) -> bool:
    """Strings that end in a newline are the one place the two regex engines disagree: Python's ``re``
    lets ``$`` match before a trailing newline, ECMA-262 and Rust do not. Pydantic (Rust) is the
    enforcing side, so such instances are excluded from the comparison rather than reported as drift."""
    if isinstance(value, str):
        return not value.endswith("\n")
    if isinstance(value, list):
        return all(pattern_safe(v) for v in value)
    if isinstance(value, dict):
        return all(pattern_safe(k) and pattern_safe(v) for k, v in value.items())
    return True


def refused_only_by_cross_field_rule(error: ValidationError) -> bool:
    """True when every error is a listed cross-field ``value_error``, or the length error that follows
    from an element being dropped after failing one (the input's own length satisfied the schema)."""
    def legitimate(e: dict) -> bool:
        if e["type"] == "value_error":
            return any(rule in e["msg"] for rule in CROSS_FIELD)
        if e["type"] == "too_short":  # "0 items after validation" because an element was refused above
            return len(e["input"]) >= e["ctx"]["min_length"]
        return False
    return all(legitimate(e) for e in error.errors())


def repaired(instance: Any) -> Any:
    """Generation aid: turn a schema-generated instance into one the model is likely to accept, by
    satisfying the cross-field rules JSON Schema cannot state (mandatory guards, unique guards / effects /
    states / ids / actions / interpretations, effect sets disjoint, state references resolvable).
    The caller re-validates the result against the committed schema, so a repair cannot hide drift."""
    if isinstance(instance, list):
        return [repaired(v) for v in instance]
    if not isinstance(instance, dict):
        return instance
    out = {k: repaired(v) for k, v in instance.items()}
    if isinstance(out.get("guards"), list):
        out["guards"] = list(dict.fromkeys(list(BASE_GUARDS) + out["guards"]))
    for key in ("states", "required_effects"):
        if isinstance(out.get(key), list):
            out[key] = list(dict.fromkeys(out[key]))
    if isinstance(out.get("forbidden_effects"), list) and isinstance(out.get("required_effects"), list):
        out["forbidden_effects"] = [e for e in out["forbidden_effects"] if e not in out["required_effects"]]
    if isinstance(out.get("states"), list) and out["states"] and isinstance(out.get("transitions"), list):
        states = out["states"]
        out["initial_state"] = states[0]
        for i, t in enumerate(out["transitions"]):
            if isinstance(t, dict):
                t["id"] = f"T{i}"
                t["action"] = f"{str(t.get('action', 'a'))[:40]}#{i}"
                for key in ("from_state", "to_state"):
                    t[key] = states[sum(map(ord, str(t.get(key)))) % len(states)]
    if isinstance(out.get("alternatives"), list):
        seen: dict[Any, Any] = {}
        for alternative in out["alternatives"]:
            if isinstance(alternative, dict):
                seen.setdefault(alternative.get("interpretation"), alternative)
        out["alternatives"] = list(seen.values())
    return out


def instances(schema: dict, *, repair: bool) -> st.SearchStrategy:
    """Instances of the committed schema; with ``repair`` nudged toward acceptability and re-checked."""
    strategy = from_schema(schema)
    if not repair:
        return strategy
    return strategy.map(repaired).filter(Draft202012Validator(schema).is_valid)


def walk(value: Any, path: tuple = ()) -> list[tuple]:
    found: list[tuple] = [path]
    if isinstance(value, dict):
        for k, v in value.items():
            found.extend(walk(v, (*path, k)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            found.extend(walk(v, (*path, i)))
    return found


def mutate_once(instance: Any, path: tuple, kind: str, junk: str) -> Any:
    """Copy of ``instance`` with one change at ``path``; the instance itself when nothing applies."""
    document = copy.deepcopy(instance)
    if not path:
        return document
    parent = document
    for step in path[:-1]:
        parent = parent[step]
    key = path[-1]
    value = parent[key]
    if kind == "delete":
        if isinstance(parent, dict):
            del parent[key]
        else:
            parent.pop(key)
    elif kind == "retype":
        parent[key] = "~" + junk if not isinstance(value, str) else 0  # not coercible to a number or bool
    elif kind == "add_key" and isinstance(value, dict):
        value[junk or "extra"] = 1
    elif kind == "stretch" and isinstance(value, str):
        parent[key] = value + junk * (1700 // len(junk) + 1)  # longer than any maxLength in the contracts
    elif kind == "empty" and isinstance(value, str):
        parent[key] = ""
    elif kind == "bump" and isinstance(value, int) and not isinstance(value, bool):
        parent[key] = value + 1
    elif kind == "drop" and isinstance(value, int) and not isinstance(value, bool):
        parent[key] = value - 1
    elif kind == "grow" and isinstance(value, list):
        parent[key] = value + copy.deepcopy(value[-1:] or ["x"])
    elif kind == "shrink" and isinstance(value, list) and value:
        parent[key] = value[:-1]
    return document


def applicable_kinds(value: Any) -> list[str]:
    """Mutation kinds that change a value of this type (so generation does not waste draws on no-ops)."""
    kinds = ["delete", "retype"]
    if isinstance(value, dict):
        kinds.append("add_key")
    elif isinstance(value, str):
        kinds += ["stretch", "empty"]
    elif isinstance(value, int) and not isinstance(value, bool):
        kinds += ["bump", "drop"]
    elif isinstance(value, list):
        kinds += ["grow"] + (["shrink"] if value else [])
    return kinds


def value_at(document: Any, path: tuple) -> Any:
    for step in path:
        document = document[step]
    return document


@pytest.mark.parametrize("name", sorted(CONTRACTS))
def test_committed_schema_is_the_models_schema(name):
    """The committed file is exactly what the model publishes today (regeneration drift)."""
    assert load(name) == CONTRACTS[name].model_json_schema()


@pytest.mark.parametrize("name", sorted(CONTRACTS))
def test_schemas_are_valid_json_schema(name):
    Draft202012Validator.check_schema(load(name))


@pytest.mark.parametrize("name", sorted(CONTRACTS))
def test_schema_valid_instances_are_accepted_by_the_model(name):
    schema, model = load(name), CONTRACTS[name]

    @settings(max_examples=examples(GENERATED_BUDGET.get(name, 100)))
    @given(instances(schema, repair=False))
    def check(instance):
        assume(pattern_safe(instance))
        try:
            model.model_validate(instance)
        except ValidationError as error:
            assert refused_only_by_cross_field_rule(error), f"schema-valid instance refused: {error.errors()}"

    check()


@functools.lru_cache(maxsize=1)
def real_change_cases() -> tuple[str, ...]:
    """Change Cases as the kernel really produces them at four stages (with receipts at the last), as JSON."""
    with scratch_directory() as directory:
        studio = ephemeral_studio(directory)
        draft = studio.create(REQUEST)
        proposed = studio.propose(draft["id"], draft["version"])
        preview = studio.select(proposed["id"], proposed["version"], "recommend_only", OWNER)
        verified = studio.verify(preview["id"], preview["version"])
        return tuple(json.dumps(c) for c in (draft, proposed, preview, verified))


def seeds(name: str, schema: dict) -> st.SearchStrategy:
    """Instances the model is likely to accept. Change Cases are seeded from real kernel output because
    schema generation for the nested aggregate is slow and rarely reaches an acceptable one."""
    if name == "change-case":
        return st.integers(0, 3).map(lambda i: json.loads(real_change_cases()[i]))
    return instances(schema, repair=True)


def near_misses(name: str):
    """(schema validator, model, strategy of (seed, mutated)) for one contract."""
    schema = load(name)

    @st.composite
    def pairs(draw):
        seed = draw(seeds(name, schema))
        assume(pattern_safe(seed))
        path = draw(st.sampled_from([p for p in walk(seed) if p]))
        kind = draw(st.sampled_from(applicable_kinds(value_at(seed, path))))
        mutated = mutate_once(seed, path, kind, draw(st.text(min_size=1, max_size=3)))
        assume(mutated != seed and pattern_safe(mutated))
        return seed, mutated

    return Draft202012Validator(schema), CONTRACTS[name], pairs()


@pytest.mark.parametrize("name", sorted(CONTRACTS))
def test_model_accepted_instances_are_schema_valid_even_after_mutation(name):
    """Direction 2: whatever the model still accepts after one random mutation must satisfy the schema."""
    validator, model, pairs = near_misses(name)
    seen = {"seeds_accepted": 0, "mutants_accepted": 0}

    @settings(max_examples=examples(NEAR_MISS_BUDGET.get(name, 150)))
    @given(pairs)
    def check(pair):
        seed, mutated = pair
        try:
            model.model_validate(seed)
            seen["seeds_accepted"] += 1
            assert validator.is_valid(seed), "model accepts a seed the schema rejects"
        except ValidationError:
            pass
        try:
            model.model_validate(mutated)
        except ValidationError:
            return  # refused: the both-or-neither test judges whether that refusal is legitimate
        seen["mutants_accepted"] += 1
        errors = sorted(e.message for e in validator.iter_errors(mutated))
        assert not errors, f"model accepts an instance the schema rejects: {errors[:3]}"

    check()
    assert seen["seeds_accepted"] > 0, "vacuous: the model never accepted a generated seed"


@pytest.mark.parametrize("name", sorted(CONTRACTS))
def test_mutations_are_refused_by_both_or_neither(name):
    """Agreement in both directions on near-miss instances: schema and model may disagree only where the
    model applies a cross-field rule that JSON Schema cannot state."""
    validator, model, pairs = near_misses(name)
    seen = {"agree_valid": 0, "agree_invalid": 0, "cross_field_only": 0}

    @settings(max_examples=examples(NEAR_MISS_BUDGET.get(name, 150)))
    @given(pairs)
    def check(pair):
        _, mutated = pair
        schema_ok = validator.is_valid(mutated)
        try:
            model.model_validate(mutated)
            model_ok, cross_field = True, False
        except ValidationError as error:
            model_ok, cross_field = False, refused_only_by_cross_field_rule(error)
        assert schema_ok == model_ok or (schema_ok and cross_field), (
            f"schema says {'valid' if schema_ok else 'invalid'}, model says {'accepts' if model_ok else 'refuses'}")
        seen["agree_valid" if schema_ok and model_ok else "agree_invalid" if not schema_ok else "cross_field_only"] += 1

    check()
    assert seen["agree_valid"] > 0 and seen["agree_invalid"] > 0, f"the comparison never saw both outcomes: {seen}"


TEXT = st.text(alphabet=st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=60)
MODEL_INSTANCES = {
    "execute-command": st.builds(
        ExecuteCommand, operation_id=st.from_regex(r"[A-Za-z0-9_-]{1,100}", fullmatch=True),
        actor_id=st.text(min_size=1, max_size=80), instance_id=st.text(min_size=1, max_size=80),
        action=st.text(min_size=1, max_size=60), expected_version=st.integers(0, 2**40)),
    "layout-change": st.builds(LayoutChange, node=st.text(min_size=1, max_size=60), x=st.integers(0, 2000), y=st.integers(0, 2000)),
    "semantic-transaction": st.one_of(
        st.builds(RetargetTransition, kind=st.just("retarget_transition"), transition=st.from_regex(r"[A-Z][A-Z0-9_-]{0,20}", fullmatch=True),
                  end=st.sampled_from(["source", "target"]), state=st.text(min_size=1, max_size=60)),
        st.builds(SetRole, kind=st.just("set_role"), transition=st.from_regex(r"[A-Z][A-Z0-9_-]{0,20}", fullmatch=True),
                  role=st.text(min_size=1, max_size=60))).map(TransactionDocument),
    "proposal": st.builds(
        Proposal, summary=st.text(min_size=1, max_size=200),
        alternatives=st.lists(st.builds(Alternative, interpretation=st.sampled_from(["recommend_only", "final_approval", "confirm_only", "unsupported"]),
                                        explanation=st.text(min_size=1, max_size=200)),
                              min_size=1, max_size=4, unique_by=lambda a: a.interpretation).map(tuple),
        unknowns=st.lists(st.text(max_size=100), max_size=10).map(tuple)),
    "workflow": workflows(),
}


@pytest.mark.parametrize("name", sorted(MODEL_INSTANCES))
def test_instances_the_model_builds_are_schema_valid(name):
    """Direction 2 without any schema-side generator: what the model accepts and serialises is valid
    against the published schema, so a schema stricter than the model cannot hide."""
    validator = Draft202012Validator(load(name))

    @settings(max_examples=examples(150 if name != "workflow" else 60))
    @given(MODEL_INSTANCES[name])
    def check(instance):
        assume(pattern_safe(instance.model_dump(mode="json")))
        errors = sorted(e.message for e in validator.iter_errors(instance.model_dump(mode="json")))
        assert not errors, f"model output rejected by its own schema: {errors[:3]}"

    check()


@pytest.mark.parametrize("stage", range(4))
def test_real_change_cases_are_schema_valid(stage):
    """Change Cases exactly as the kernel produced them (draft, proposed, preview, verified)."""
    document = json.loads(real_change_cases()[stage])
    ChangeCase.model_validate(document)
    assert not sorted(e.message for e in Draft202012Validator(load("change-case")).iter_errors(document))


STRICTER = ("KERNEL FINDING (schema/model drift, fail-closed): ExecuteCommand.expected_version is `strict=True`, so an "
            "integer-valued float such as 1.0 is refused, while contracts/execute-command.schema.json declares "
            '`"type": "integer"` and JSON Schema 2020-12 treats 1.0 as an integer (Python json.dumps(1.0) emits 1.0). '
            "Fix in a separate kernel change: accept integral floats or publish the restriction.")
LAXER = ("KERNEL FINDING (schema/model drift, fail-open on type): this integer field is Pydantic-lax, so the model "
         "accepts a numeric string or a boolean where contracts/*.schema.json declares `\"type\": \"integer\"`. "
         "ExecuteCommand.expected_version is `strict=True` and refuses both, so the contracts are inconsistent. "
         "Fix in a separate kernel change: StrictInt (or strict=True) on integer fields of request models.")
COERCIONS = {"float": float, "string": str, "bool": lambda v: True}
DIVERGENCES = {("execute-command", "float"): STRICTER, ("layout-change", "string"): LAXER, ("layout-change", "bool"): LAXER,
               ("change-case", "string"): LAXER, ("change-case", "bool"): LAXER}
COERCION_CASES = [
    pytest.param(name, kind, marks=pytest.mark.xfail(strict=True, reason=DIVERGENCES[name, kind])) if (name, kind) in DIVERGENCES
    else pytest.param(name, kind)
    for name in ("change-case", "execute-command", "layout-change") for kind in COERCIONS]


@pytest.mark.parametrize(("name", "coercion"), COERCION_CASES)
def test_integer_coercions_are_treated_alike_by_schema_and_model(name, coercion):
    """JSON has one number type and Pydantic has strict and lax integers: for an integer field replaced by
    an integral float, a numeric string or a boolean, the schema and the model must agree."""
    validator, model, _ = near_misses(name)
    schema = load(name)

    @settings(max_examples=examples(60))
    @given(st.data())
    def check(data):
        seed = data.draw(seeds(name, schema))
        int_paths = [p for p in walk(seed) if p and isinstance(value_at(seed, p), int) and not isinstance(value_at(seed, p), bool)]
        assume(int_paths)
        path = data.draw(st.sampled_from(int_paths))
        mutated = copy.deepcopy(seed)
        value_at(mutated, path[:-1])[path[-1]] = COERCIONS[coercion](value_at(seed, path))
        schema_ok = validator.is_valid(mutated)
        try:
            model.model_validate(mutated)
            model_ok = True
        except ValidationError:
            model_ok = False
        assert schema_ok == model_ok, f"{path}: schema says {schema_ok}, model says {model_ok}"

    check()


def test_cross_field_rules_are_all_still_in_the_models():
    """Keeps ``CROSS_FIELD`` honest: every listed message is still raised by some model validator."""
    source = (ROOT / "src" / "eija_studio" / "domain" / "models.py").read_text(encoding="utf-8")
    assert all(re.search(re.escape(rule), source) for rule in CROSS_FIELD)

