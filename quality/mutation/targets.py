"""What is mutated, by which tests, and with which mutation operators.

Per-module test selection is a deliberate cost decision (ADR-0033): a mutant that survives the
selected tests is reported as a survivor even if some other, unselected test would kill it. The
selection therefore lists the fast oracle tests that exercise the module directly. The slow Studio-level
tests (a `verified` case costs about a second of setup each) are left out: a survivor they alone would
kill is a missing direct test, which is the finding the analysis exists to surface.
"""
from __future__ import annotations

from dataclasses import dataclass

SRC = "src/eija_studio"


@dataclass(frozen=True)
class Target:
    """One mutated module and the tests allowed to kill its mutants (fastest file first)."""

    module: str  # POSIX path relative to the repository root
    tests: tuple[str, ...]
    keyword: str = ""  # a pytest -k expression that leaves out slow tests of a selected file (a built app, a chart)

    @property
    def pytest_args(self) -> tuple[str, ...]:
        return (*self.tests, *(("-k", self.keyword) if self.keyword else ()))

    @property
    def slug(self) -> str:
        return self.module.removeprefix(SRC + "/").removesuffix(".py").replace("/", "-")


TARGETS: tuple[Target, ...] = (
    Target(f"{SRC}/domain/policy.py", ("tests/test_policy_authority.py", "tests/test_domain.py", "tests/test_kernel_inspection.py",
                                       "tests/test_merged_pr_inspection.py")),
    Target(f"{SRC}/domain/models.py", ("tests/test_contract_limits.py", "tests/test_domain.py", "tests/test_policy_authority.py", "tests/test_runtime_oracle.py",
                                       "tests/test_kernel_inspection.py", "tests/test_merged_pr_inspection.py")),
    Target(f"{SRC}/domain/impact.py", ("tests/test_impact_oracle.py", "tests/test_domain.py")),
    Target(f"{SRC}/domain/evidence.py", ("tests/test_evidence_oracle.py",)),
    # The refusals of the kernel features of 11-12 November (ADR-0231 to ADR-0242) are asserted in their own files; their
    # built-app, chart and differential tests take seconds each and are left out (integration review I2).
    Target(f"{SRC}/application/runtime.py", ("tests/test_runtime_oracle.py", "tests/test_runtime.py", "tests/test_initiators.py",
                                             "tests/test_separation_of_duties.py", "tests/test_signals.py", "tests/test_time_events.py",
                                             "tests/test_value_guards.py", "tests/test_linked_objects.py"),
           keyword="not built_app and not scxml and not differential and not running_app"),
    Target(f"{SRC}/application/verifier.py", ("tests/test_verifier_oracle.py",)),
    # ADR-0239: the representatives the law proof, Simulate and the generated app's oracle try for value guards.
    Target(f"{SRC}/domain/value_guards.py", ("tests/test_value_guard_edges.py", "tests/test_value_guards.py",
                                             "tests/property/test_value_guards.py", "tests/test_kernel_inspection.py")),
    Target(f"{SRC}/domain/laws.py", ("tests/test_reach_end_law.py", "tests/test_law_proof.py", "tests/test_library_loan.py",
                                     "tests/test_actor_kinds.py", "tests/test_separation_of_duties.py",
                                     "tests/property/test_value_guards.py", "tests/test_kernel_inspection.py")),
)
QUICK_MODULES: tuple[str, ...] = (f"{SRC}/domain/policy.py",)

# cosmic-ray ships ~210 operators; most only re-spell the same fault (`+` to `**`, `<<`, `^` ... on
# strings or ints) and are killed by any TypeError, which inflates a score without measuring
# fault-detection power. This curated set keeps one operator per fault class relevant to guards.
_COMPARISONS = ("Eq_NotEq", "NotEq_Eq", "Lt_LtE", "LtE_Lt", "Gt_GtE", "GtE_Gt", "Lt_GtE", "GtE_Lt",
                "Gt_LtE", "LtE_Gt", "Is_IsNot", "IsNot_Is")
_ARITHMETIC = ("Add_Sub", "Sub_Add", "Mul_Div", "BitOr_BitAnd", "BitAnd_BitOr")
_LOGIC = ("AddNot", "ReplaceTrueWithFalse", "ReplaceFalseWithTrue", "ReplaceAndWithOr", "ReplaceOrWithAnd",
          "ReplaceBreakWithContinue", "ReplaceContinueWithBreak", "ExceptionReplacer", "NumberReplacer",
          "ZeroIterationForLoop", "RemoveDecorator", "ReplaceUnaryOperator_Delete_Not")
OPERATORS: tuple[str, ...] = tuple(sorted(
    [f"core/ReplaceComparisonOperator_{c}" for c in _COMPARISONS]
    + [f"core/ReplaceBinaryOperator_{a}" for a in _ARITHMETIC]
    + [f"core/{x}" for x in _LOGIC]
    + ["eija/ReplaceStringLiteral", "eija/ReplaceReturnValue", "eija/ReplaceMembership"]))  # quality/mutation/eija_operators.py


def by_module(paths: list[str] | None) -> tuple[Target, ...]:
    """Resolve requested module paths; `None` means all. Unknown paths are an error, not a skip."""
    if not paths:
        return TARGETS
    known = {t.module: t for t in TARGETS}
    unknown = sorted(set(paths) - set(known))
    if unknown:
        raise SystemExit(f"unknown mutation target(s): {', '.join(unknown)}; known: {', '.join(sorted(known))}")
    return tuple(known[p] for p in sorted(set(paths)))
