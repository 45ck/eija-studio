"""Tests of the mutation-analysis glue (quality/mutation), not of the kernel.

The pure parts (classification, scoring, ratchet, reports) always run. Tests that need cosmic-ray itself
(`pip install -e ".[mutation]"`) skip when it is absent: a skip is a NOT_RUN, never a pass.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # quality/ is engineering tooling outside the shipped package

from quality.mutation import engine, report  # noqa: E402
from quality.mutation.model import INCOMPETENT, KILLED, SURVIVED, TIMEOUT, Mutant, classify, score, tally  # noqa: E402
from quality.mutation.targets import OPERATORS, QUICK_MODULES, TARGETS, by_module  # noqa: E402

needs_cosmic_ray = pytest.mark.skipif(importlib.util.find_spec("cosmic_ray") is None,
                                      reason="NOT_RUN: pip install -e '.[mutation]'")


def result(worker="normal", test="killed", output="", diff="") -> dict:
    return {"result": {"worker_outcome": worker, "test_outcome": test, "output": output, "diff": diff}}


def mutant(status=SURVIVED, module="src/eija_studio/domain/policy.py", line=5, operator="core/ReplaceTrueWithFalse", function="f") -> Mutant:
    return Mutant(module, operator, 0, (line, 4), (line, 8), function, status, "--- a\n+++ b\n@@ -1 +1 @@\n-x = True\n+x = False", "")


# ---- classification and score ----------------------------------------------------------------------

@pytest.mark.parametrize("record,expected", [
    (result(test="survived"), SURVIVED),
    (result(test="killed", output="1 failed"), KILLED),
    (result(test="killed", output="timeout"), TIMEOUT),
    (result(test="killed", output="Interrupted: 1 error during collection"), INCOMPETENT),
    (result(test="incompetent"), INCOMPETENT),
    (result(worker="exception", test=None), INCOMPETENT),
    (result(worker="abnormal", test=None), INCOMPETENT),
    (result(worker="skipped", test=None), "skipped"),
])
def test_classification(record, expected):
    assert classify(record) == expected


def test_classification_refuses_unfinished_or_unknown_results():
    with pytest.raises(ValueError):
        classify({"result": None})
    with pytest.raises(ValueError):
        classify(result(test="mystery"))


def test_score_counts_timeouts_as_detected_and_ignores_incompetent_and_rounds_down():
    assert score({KILLED: 1, TIMEOUT: 1, SURVIVED: 1, INCOMPETENT: 50}) == 0.6666
    assert score({KILLED: 3, SURVIVED: 0}) == 1.0
    assert score({SURVIVED: 2}) == 0.0
    assert score({INCOMPETENT: 3}) is None  # nothing assessed is not a perfect score


def test_tally_counts_every_status():
    counts = tally([mutant(KILLED), mutant(KILLED), mutant(SURVIVED), mutant(TIMEOUT), mutant(INCOMPETENT)])
    assert counts == {"total": 5, "killed": 2, "survived": 1, "timeout": 1, "incompetent": 1, "equivalent": 0, "score": 0.75}


# ---- config, targets, operators --------------------------------------------------------------------

def test_targets_exist_and_have_existing_tests():
    for target in TARGETS:
        assert (ROOT / target.module).is_file(), target.module
        assert target.tests and all((ROOT / t).is_file() for t in target.tests), target
    assert len({t.slug for t in TARGETS}) == len(TARGETS)
    assert set(QUICK_MODULES) <= {t.module for t in TARGETS}


def test_unknown_module_is_an_error_not_a_silent_skip():
    with pytest.raises(SystemExit):
        by_module(["src/eija_studio/domain/nope.py"])


def test_config_is_deterministic_and_carries_the_selection():
    target = TARGETS[0]
    text = engine.render_config(target, timeout=42.0)
    assert text == engine.render_config(target, timeout=42.0)
    assert f'module-path = "{target.module}"' in text and "timeout = 42.0" in text
    assert all(t in text for t in target.tests)
    assert "\\" not in text.split("test-command")[1].split("\n")[0].replace("\\\"", ""), "backslashes break shlex on Windows"


def test_operator_filter_regex_excludes_exactly_the_operators_not_curated():
    """cosmic-ray joins patterns as `(:?p)` and uses `re.match`; reproduce that to prove the negative-lookahead form."""
    pattern = json.loads(engine.render_config(TARGETS[0], 1.0).split("exclude-operators = [")[1].split("]")[0])
    excluded = re.compile(f"(:?{pattern})")
    assert all(excluded.match(name) is None for name in OPERATORS)
    for name in ("core/ReplaceBinaryOperator_Add_Pow", "core/VariableReplacer", "core/ReplaceComparisonOperator_Eq_NotEqX",
                 "core/ReplaceComparisonOperator_Eq_Lt", "eija/ReplaceStringLiteralX"):
        assert excluded.match(name), name


def test_scratch_workspace_is_isolated_from_the_checkout(tmp_path):
    fake = tmp_path / "repo"
    (fake / "src" / "eija_studio").mkdir(parents=True)
    (fake / "src" / "eija_studio" / "a.py").write_text("x = 1\n")
    (fake / ".venv").mkdir()
    (fake / ".venv" / "big").write_text("excluded")
    scratch = engine.prepare_workspace(fake, TARGETS[0])
    assert scratch.is_relative_to(fake / ".tmp" / "mutation")
    assert (scratch / "src" / "eija_studio" / "a.py").read_text() == "x = 1\n"
    assert not (scratch / ".venv").exists()
    (scratch / "src" / "eija_studio" / "a.py").write_text("x = 2\n")
    assert (fake / "src" / "eija_studio" / "a.py").read_text() == "x = 1\n"
    assert str(scratch / "src") in engine.environment(scratch)["PYTHONPATH"].split(";" if sys.platform == "win32" else ":")


# ---- ratchet and reports ---------------------------------------------------------------------------

def summary(score_value=0.9, *, total=100, incompetent=0, sample=None, module="src/eija_studio/domain/policy.py") -> dict:
    row = {"total": total, "killed": 0, "survived": 0, "timeout": 0, "incompetent": incompetent, "score": score_value, "tests": []}
    return {"schema": report.SUMMARY_SCHEMA, "engine": "cosmic-ray test", "platform": "test", "workers": 2, "sample": sample,
            "operators": [], "modules": {module: row}, "overall": row}


FLOOR = {"schema": report.BASELINE_SCHEMA, "modules": {"src/eija_studio/domain/policy.py": {"score": 0.9, "total": 100, "survived": 10}}}


def test_ratchet_passes_at_or_above_the_floor_and_fails_below():
    assert report.check(summary(0.9), FLOOR) == []
    assert report.check(summary(0.95), FLOOR) == []
    failures = report.check(summary(0.8999), FLOOR)
    assert len(failures) == 1 and "below the ratchet floor" in failures[0]


@pytest.mark.parametrize("bad,fragment", [
    (summary(0.99, sample=10), "sampled runs"),
    (summary(0.99, total=0), "no mutants"),
    (summary(0.99, incompetent=30), "not exercisable"),
    (summary(0.99, module="src/eija_studio/domain/unlisted.py"), "no baseline floor"),
    (summary(None), "below the ratchet floor"),
])
def test_ratchet_fails_closed(bad, fragment):
    assert any(fragment in f for f in report.check(bad, FLOOR)), report.check(bad, FLOOR)


def test_baseline_only_ratchets_up_unless_explicitly_overridden():
    raised = report.update_baseline(summary(0.95), FLOOR)
    assert raised["modules"]["src/eija_studio/domain/policy.py"]["score"] == 0.95
    with pytest.raises(ValueError, match="lower"):
        report.update_baseline(summary(0.5), FLOOR)
    assert report.update_baseline(summary(0.5), FLOOR, allow_lower=True)["modules"]["src/eija_studio/domain/policy.py"]["score"] == 0.5
    with pytest.raises(ValueError, match="full run"):
        report.update_baseline(summary(0.99, sample=5), FLOOR)


def test_summary_is_deterministic_and_sorted():
    ms = [mutant(SURVIVED, line=9), mutant(KILLED, line=2), mutant(KILLED, line=5)]
    first = report.summarise(TARGETS[:1], ms, engine="e", workers=2, sample=None)
    second = report.summarise(TARGETS[:1], list(reversed(ms)), engine="e", workers=2, sample=None)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["modules"][TARGETS[0].module]["score"] == 0.6666


def test_survivor_report_lists_diff_and_a_suggested_test(tmp_path):
    (tmp_path / "src" / "eija_studio" / "domain").mkdir(parents=True)
    (tmp_path / TARGETS[0].module).write_text("\n\n\n\nRole = 'Teacher'\n")
    m = mutant(SURVIVED, line=5, operator="eija/ReplaceStringLiteral", function=None)
    m = Mutant(m.module, m.operator, 0, (5, 7), (5, 16), None, SURVIVED, m.diff, "")
    text = report.survivors_markdown([m], tmp_path, report.summarise(TARGETS[:1], [m], engine="e", workers=2, sample=None))
    assert "### survived: line 5, col 7" in text and "```diff" in text and "+x = False" in text
    assert "`'Teacher'`" in text and "Suggested test:" in text


def test_every_curated_operator_family_has_advice():
    source = ["x = 1"]
    for operator in OPERATORS:
        advice = report.suggest_test(Mutant("m.py", operator, 0, (1, 0), (1, 5), "fn", SURVIVED, "", ""), source)
        assert advice and "Add a test that fails when" not in advice, operator  # the generic fallback means a family was missed


def test_parse_dump_normalises_paths_and_drops_filtered_mutants():
    def line(job, outcome, test, output="", diff=""):
        item = {"job_id": job, "mutations": [{"module_path": "src\\m.py", "operator_name": "core/AddNot", "occurrence": 0,
                                                "start_pos": [3, 1], "end_pos": [3, 4], "operator_args": {}, "definition_name": "fn"}]}
        return json.dumps([item, {"worker_outcome": outcome, "test_outcome": test, "output": output, "diff": diff}])
    dump = "\n".join([line("a", "normal", "survived", diff="--- a\\x\n+++ b\\x"), line("b", "skipped", None), line("c", "normal", "killed", "boom")])
    parsed = engine.parse_dump(dump, "src/m.py")
    assert [m.status for m in parsed] == [SURVIVED, KILLED]
    assert parsed[0].diff == "--- a/x\n+++ b/x" and parsed[0].function == "fn" and parsed[1].output == ""


# ---- cosmic-ray integration (NOT_RUN when the extra is absent) -------------------------------------

def mutate(code: str, operator: str, occurrence: int = 0):
    from cosmic_ray.mutating import mutate_code
    from quality.mutation import eija_operators
    return mutate_code(code, eija_operators.OperatorProvider()[operator](), occurrence)


@needs_cosmic_ray
def test_string_operator_mutates_identifiers_and_leaves_prose_docstrings_literals_alone():
    assert mutate("role = 'Teacher'\n", "ReplaceStringLiteral") == "role = 'XXTeacherXX'\n"
    assert mutate('role = r"a|b"\n', "ReplaceStringLiteral") == 'role = r"XXa|bXX"\n'
    for untouched in ("msg = 'not an identifier'\n", "empty = ''\n", "raw = b'Teacher'\n", 'f = f"Teacher"\n',
                      "from typing import Literal\nGuard = Literal['a', 'b']\n", 'def f():\n    """Docstring."""\n'):
        assert mutate(untouched, "ReplaceStringLiteral") is None, untouched


@needs_cosmic_ray
def test_membership_operator_negates_in_and_not_in_but_not_loops():
    assert mutate("x = a in b\n", "ReplaceMembership") == "x = a not in b\n"
    assert mutate("x = a not in b\n", "ReplaceMembership") == "x = a in b\n"
    assert mutate("for a in b:\n    pass\n", "ReplaceMembership") is None
    assert mutate("x = [a for a in b]\n", "ReplaceMembership") is None


@needs_cosmic_ray
def test_return_operator_replaces_value_with_none_but_not_bare_or_none_returns():
    assert mutate("def f():\n    return 1 + 2\n", "ReplaceReturnValue") == "def f():\n    return None\n"
    assert mutate("def f():\n    return\n", "ReplaceReturnValue") is None
    assert mutate("def f():\n    return None\n", "ReplaceReturnValue") is None


@needs_cosmic_ray
def test_curated_operators_all_exist_in_the_engine():
    from cosmic_ray.plugins import operator_names
    from quality.mutation import eija_operators
    known = set(operator_names()) | {f"eija/{n}" for n in eija_operators.OperatorProvider()}
    assert set(OPERATORS) <= known, sorted(set(OPERATORS) - known)


@needs_cosmic_ray
def test_plugin_is_discoverable_from_the_scratch_workspace_without_installing(tmp_path):
    engine.install_operator_plugin(tmp_path)
    proc = subprocess.run([sys.executable, "-m", "cosmic_ray.cli", "operators"], capture_output=True, text=True,
                          env={**engine.environment(tmp_path)}, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "eija/ReplaceStringLiteral" in proc.stdout and "eija/ReplaceReturnValue" in proc.stdout


@needs_cosmic_ray
def test_sampling_and_sharding_partition_work_deterministically(tmp_path):
    from cosmic_ray.work_db import use_db
    from cosmic_ray.work_item import MutationSpec, WorkItem

    def build(path: Path) -> None:
        with use_db(str(path)) as db:
            db.add_work_items([WorkItem.single(f"job{i}", MutationSpec("m.py", "core/AddNot", 0, (i + 1, 0), (i + 1, 3))) for i in range(20)])

    def pending(path: Path) -> set[str]:
        with use_db(str(path)) as db:
            return {w.job_id for w in db.pending_work_items}

    shards = []
    for index in range(2):
        path = tmp_path / f"s{index}.sqlite"
        build(path)
        engine.select_mutants(path, sample=None, shard=(index, 2))
        shards.append(pending(path))
    assert shards[0] | shards[1] == {f"job{i}" for i in range(20)} and not shards[0] & shards[1]
    samples = []
    for name in ("a", "b"):
        path = tmp_path / f"{name}.sqlite"
        build(path)
        engine.select_mutants(path, sample=5, shard=(0, 1))
        samples.append(pending(path))
    assert samples[0] == samples[1] and len(samples[0]) == 5


# ---- equivalent mutants ----------------------------------------------------------------------------

def _at(source: str, snippet: str, *, line: int | None = None, function: str | None = "f", module: str = "m.py", diff: str = "",
        operator: str = "core/ReplaceBinaryOperator_Mul_Div", status: str = SURVIVED) -> Mutant:
    lines = source.splitlines()
    row = line if line is not None else next(i for i, text in enumerate(lines, 1) if snippet in text)
    col = lines[row - 1].index(snippet)
    return Mutant(module, operator, 0, (row, col), (row, col + len(snippet)), function, status, diff, "")


def test_annotations_and_the_keyword_only_star_are_equivalent_but_real_arithmetic_is_not():
    from quality.mutation import equivalents
    source = "from __future__ import annotations\n\ndef f(a: int | None, *, b: str = 'x') -> dict | None:\n    return a * b\n"
    assert "annotation" in equivalents.reason(_at(source, "|", line=3), source)
    assert "annotation" in equivalents.reason(_at(source, "|", line=3, operator="core/ReplaceBinaryOperator_BitOr_BitAnd"), source)
    assert "keyword-only" in equivalents.reason(_at(source, "*", line=3), source)
    assert equivalents.reason(_at(source, "*", line=4), source) is None  # multiplication in the body
    assert equivalents.reason(_at(source, "'x'", line=3), source) is None  # a default value is behaviour


def test_annotations_count_only_when_future_annotations_defers_them():
    from quality.mutation import equivalents
    source = "def f(a: int | None):\n    return a\n"
    assert equivalents.reason(_at(source, "|"), source) is None  # evaluated at definition time: a real mutation


def test_accepted_equivalent_matches_only_the_exact_text_replacement_and_function():
    from quality.mutation import equivalents
    module = "src/eija_studio/application/runtime.py"
    source = "def execute():\n    binding = fingerprint({\"case\": case_id})\n"
    diff = "@@ -1 +1 @@\n-    binding = fingerprint({\"case\": case_id})\n+    binding = fingerprint({\"XXcaseXX\": case_id})"
    mutant = _at(source, '"case"', function="execute", module=module, diff=diff)
    assert equivalents.reason(mutant, source)
    other_function = _at(source, '"case"', function="other", module=module, diff=diff)
    other_text = _at(source, '"case"', function="execute", module=module, diff=diff.replace("XXcaseXX", "other"))
    other_module = _at(source, '"case"', function="execute", module="src/eija_studio/domain/policy.py", diff=diff)
    assert [equivalents.reason(m, source) for m in (other_function, other_text, other_module)] == [None, None, None]


def test_a_killed_mutant_is_never_reclassified_as_equivalent():
    def line(outcome: str) -> str:
        item = {"job_id": "a", "mutations": [{"module_path": "m.py", "operator_name": "core/ReplaceBinaryOperator_Mul_Div", "occurrence": 0,
                                                "start_pos": [1, 9], "end_pos": [1, 10], "operator_args": {}, "definition_name": "f"}]}
        return json.dumps([item, {"worker_outcome": "normal", "test_outcome": outcome, "output": "F", "diff": ""}])
    source = "def f(a, *, b): pass\n"
    assert [m.status for m in engine.parse_dump(line("survived"), "m.py", source)] == ["equivalent"]
    assert [m.status for m in engine.parse_dump(line("killed"), "m.py", source)] == ["killed"]
    assert [m.status for m in engine.parse_dump(line("survived"), "m.py", None)] == ["survived"]


def test_equivalents_are_excluded_from_the_score_and_listed_with_their_reason(tmp_path):
    (tmp_path / "src" / "eija_studio" / "domain").mkdir(parents=True)
    (tmp_path / TARGETS[0].module).write_text("x = 1\n")
    from dataclasses import replace
    eq = replace(mutant(SURVIVED, line=1), status="equivalent", equivalent_reason="label only")
    ms = [mutant(KILLED, line=1), eq]
    summary_ = report.summarise(TARGETS[:1], ms, engine="e", workers=2, sample=None)
    assert summary_["modules"][TARGETS[0].module]["score"] == 1.0 and summary_["modules"][TARGETS[0].module]["equivalent"] == 1
    assert "Accepted as equivalent, excluded from the score: label only" in report.survivors_markdown(ms, tmp_path, summary_)
