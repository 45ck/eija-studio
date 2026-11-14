"""Every refusal code a mutated module writes is asserted by a test that may kill its mutants (integration review I2).

Mutation analysis lets only a module's selected tests kill its mutants (quality/mutation/targets.py, ADR-0033). On
2026-11-14 `LINKED_LIFECYCLE_CONFLICT` (added to policy.py by #257, tested in a new file) left two survivors, and
`mutation_quick` went red on `main`: the new test file never joined the selection. A code literal in a mutated module
must therefore appear in one of its selected test files, so a new rule and its test land in the selection together.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from quality.mutation.targets import TARGETS

ROOT = Path(__file__).resolve().parents[1]
CODE = re.compile(r'"([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+):?"')  # SNAKE_CASE codes such as "UNDECLARED_ROLE:" or "POLICY_BLOCKED"


@pytest.mark.parametrize("target", TARGETS, ids=lambda t: t.slug)
def test_each_code_a_mutated_module_writes_is_asserted_by_its_selected_tests(target):
    codes = set(CODE.findall((ROOT / target.module).read_text(encoding="utf-8")))
    selected = "\n".join((ROOT / test).read_text(encoding="utf-8") for test in target.tests)
    assert sorted(c for c in codes if c not in selected) == []


def test_the_check_reads_codes_with_and_without_a_colon():
    assert CODE.findall('x = "UNDECLARED_ROLE:" + t.id; raise refused("EDIT_INVALID", "Words")') == ["UNDECLARED_ROLE", "EDIT_INVALID"]
