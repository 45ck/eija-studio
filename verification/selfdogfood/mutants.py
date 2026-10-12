"""Disposable callable faults, evaluated by behavioral expectations rather than hashes.

The clone is compiled from our known, trusted checkout's own function, with one named
guard removed. No production class/global/file is patched. Each variant is bound only
to the newly constructed synthetic Studio or Session. This is a same-author, visible
mutation set, not an independent hidden assessment.
"""
from __future__ import annotations

import ast
import inspect
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any

from eija_studio.adapters.sqlite_store import Session, SQLiteStore
from eija_studio.application.compiler import compile_case
from eija_studio.application.service import Studio
from eija_studio.domain.models import fingerprint

from .checks import StudioFactory, ensure, synthetic_studio


class _RemoveGuard(ast.NodeTransformer):
    def __init__(self, predicate: str | None):
        self.predicate, self.removed = predicate, 0

    def visit_If(self, node: ast.If) -> ast.If | None:
        if self.predicate is not None and ast.unparse(node.test) == self.predicate:
            self.removed += 1
            return None
        return self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> ast.Expr | None:
        call = node.value
        if (self.predicate is None and isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name) and call.func.value.id == "principal"
                and call.func.attr == "require"):
            self.removed += 1
            return None
        return self.generic_visit(node)


class _RemoveCaseCAS(ast.NodeTransformer):
    def __init__(self):
        self.removed = 0

    def visit_Call(self, node: ast.Call) -> ast.Call:
        if (len(node.args) == 2 and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value.startswith("UPDATE cases SET")
                and isinstance(node.args[1], ast.Tuple)):
            ensure(" AND version=?" in node.args[0].value, "Case CAS query is not the expected mutation subject")
            node.args[0].value = node.args[0].value.replace(" AND version=?", "")
            node.args[1].elts = node.args[1].elts[:-1]
            self.removed += 1
        return self.generic_visit(node)


def _clone(function: Callable[..., Any], transform: ast.NodeTransformer | None = None,
           *, globals_override: dict[str, Any] | None = None) -> tuple[Callable[..., Any], str]:
    """Only fixed local callable objects are accepted by our callers; no user source is executed."""
    tree = ast.parse(dedent(inspect.getsource(function)))
    if transform is not None:
        tree = transform.visit(tree)
        ensure(transform.removed == 1, "Mutation did not remove exactly one declared check")
    ast.fix_missing_locations(tree)
    namespace = function.__globals__.copy() | (globals_override or {})
    # This executes only a modified function definition from this checkout, never target
    # repository inputs or proposed code. The result is retained in a private namespace.
    exec(compile(tree, "<activation-negative-control>", "exec"), namespace)  # noqa: S102
    return namespace[function.__name__], fingerprint(ast.unparse(tree))


@dataclass(frozen=True)
class Mutation:
    id: str
    check: str
    description: str
    specimen_hash: str
    factory: StudioFactory


def _studio_mutation(method: str, check: str, predicate: str | None = None) -> Mutation:
    variant, digest = _clone(getattr(Studio, method), _RemoveGuard(predicate))
    cls = type("SyntheticMissingGuardStudio", (Studio,), {method: variant})

    def factory(directory: Path) -> Studio:
        return synthetic_studio(directory, cls=cls)

    description = "Remove principal.require" if predicate is None else f"Remove guard: {predicate}"
    name = "missing_" + method + "_guard" if predicate is None else "stale_review_subject_accepted"
    return Mutation(name, check, description, digest, factory)


def _stale_evidence_mutation() -> Mutation:
    compiler, compiler_hash = _clone(compile_case, _RemoveGuard("evidence != 'PASS'"))
    view, view_hash = _clone(Studio._compile, globals_override={"compile_case": compiler})
    cls = type("SyntheticStaleEvidenceStudio", (Studio,), {"_compile": view})

    def factory(directory: Path) -> Studio:
        return synthetic_studio(directory, cls=cls)

    return Mutation("stale_runtime_evidence_eligible", "stale_evidence_denied",
                    "Remove the runtime evidence eligibility blocker from the actual compiler callable",
                    fingerprint([compiler_hash, view_hash]), factory)


def _case_cas_mutation() -> Mutation:
    save_case, digest = _clone(Session.save_case, _RemoveCaseCAS())
    session_cls = type("SyntheticNoCaseCASSession", (Session,), {"save_case": save_case})

    class SyntheticNoCaseCASStore(SQLiteStore):
        @contextmanager
        def transaction(self) -> Iterator[Session]:
            with super().transaction() as session:
                session.__class__ = session_cls
                yield session

    def factory(directory: Path) -> Studio:
        studio = synthetic_studio(directory)
        studio.store.__class__ = SyntheticNoCaseCASStore
        return studio

    return Mutation("case_cas_removed", "stale_case_adapter_cas", "Remove the SQL expected-version predicate",
                    digest, factory)


def activation_mutations() -> tuple[Mutation, ...]:
    """Named mutants whose selected behavioral oracle must fail for a concrete bad outcome."""
    return (
        _studio_mutation("from_plan", "agent_plan_denied"),
        _studio_mutation("select", "agent_select_denied"),
        _studio_mutation("approve", "agent_approve_denied"),
        _studio_mutation("apply", "agent_apply_denied"),
        _studio_mutation("approve", "stale_review_subject_denied", "packet['subject_hash'] != subject_hash"),
        _stale_evidence_mutation(),
        _case_cas_mutation(),
    )
