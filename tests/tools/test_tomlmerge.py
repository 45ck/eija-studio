"""The TOML merge driver: independent keys merge cleanly, real conflicts are refused."""
from pathlib import Path

import tomlkit
from quality.tools.tomlmerge import merge_files

BASE = """[project.optional-dependencies]
# comment kept
dev = ["pytest==9.0.2"]
lint = []
hci = []
demos = []

[tool.pytest.ini_options]
pythonpath = ["src"]
"""


def run(tmp_path: Path, ours: str, theirs: str, base: str = BASE):
    paths = {}
    for name, text in (("base", base), ("ours", ours), ("theirs", theirs)):
        paths[name] = tmp_path / f"{name}.toml"
        paths[name].write_bytes(text.encode())
    conflicts = merge_files(paths["base"], paths["ours"], paths["theirs"])
    return conflicts, tomlkit.parse(paths["ours"].read_text(encoding="utf-8")).unwrap(), paths["ours"].read_text(encoding="utf-8")


def test_neighbouring_extras_from_two_lanes_merge_without_conflict(tmp_path):
    ours = BASE.replace("hci = []", 'hci = ["playwright==1.63.0"]')
    theirs = BASE.replace("demos = []", 'demos = ["playwright==1.63.0"]')
    conflicts, merged, text = run(tmp_path, ours, theirs)
    assert conflicts == []
    extras = merged["project"]["optional-dependencies"]
    assert extras["hci"] == ["playwright==1.63.0"] and extras["demos"] == ["playwright==1.63.0"]
    assert "# comment kept" in text  # formatting and comments survive


def test_same_key_changed_differently_is_a_real_conflict(tmp_path):
    ours = BASE.replace("lint = []", 'lint = ["ruff==0.9.0"]')
    theirs = BASE.replace("lint = []", 'lint = ["ruff==0.8.0"]')
    conflicts, _, text = run(tmp_path, ours, theirs)
    assert conflicts == ["project.optional-dependencies.lint"]
    assert 'ruff==0.9.0' in text  # ours untouched on conflict


def test_different_packages_added_to_the_same_extra_are_unioned(tmp_path):
    ours = BASE.replace("lint = []", 'lint = ["ruff==0.9.0"]')
    theirs = BASE.replace("lint = []", 'lint = ["mypy==1.13.0"]')
    conflicts, merged, _ = run(tmp_path, ours, theirs)
    assert conflicts == []
    assert merged["project"]["optional-dependencies"]["lint"] == ["ruff==0.9.0", "mypy==1.13.0"]


def test_arrays_both_sides_only_extended_are_unioned_in_order(tmp_path):
    ours = BASE.replace('pythonpath = ["src"]', 'pythonpath = ["src", "."]')
    theirs = BASE.replace('pythonpath = ["src"]', 'pythonpath = ["src", "tools"]')
    conflicts, merged, _ = run(tmp_path, ours, theirs)
    assert conflicts == []
    assert merged["tool"]["pytest"]["ini_options"]["pythonpath"] == ["src", ".", "tools"]


def test_array_element_removed_on_one_side_and_added_on_other_is_a_conflict(tmp_path):
    ours = BASE.replace('pythonpath = ["src"]', 'pythonpath = ["."]')
    theirs = BASE.replace('pythonpath = ["src"]', 'pythonpath = ["src", "tools"]')
    conflicts, _, _ = run(tmp_path, ours, theirs)
    assert conflicts == ["tool.pytest.ini_options.pythonpath"]


def test_new_table_added_only_by_theirs_is_taken(tmp_path):
    theirs = BASE + '\n[tool.ruff]\nline-length = 110\n'
    conflicts, merged, _ = run(tmp_path, BASE, theirs)
    assert conflicts == [] and merged["tool"]["ruff"]["line-length"] == 110


def test_identical_change_on_both_sides_is_not_a_conflict(tmp_path):
    both = BASE.replace("lint = []", 'lint = ["ruff==0.9.0"]')
    conflicts, merged, _ = run(tmp_path, both, both)
    assert conflicts == [] and merged["project"]["optional-dependencies"]["lint"] == ["ruff==0.9.0"]


def test_key_deleted_by_theirs_and_untouched_by_ours_is_deleted(tmp_path):
    theirs = BASE.replace("demos = []\n", "")
    conflicts, merged, _ = run(tmp_path, BASE, theirs)
    assert conflicts == [] and "demos" not in merged["project"]["optional-dependencies"]


def test_delete_versus_modify_is_a_conflict(tmp_path):
    ours = BASE.replace("demos = []", 'demos = ["x==1"]')
    theirs = BASE.replace("demos = []\n", "")
    conflicts, _, _ = run(tmp_path, ours, theirs)
    assert conflicts == ["project.optional-dependencies.demos"]


def test_arrays_of_tables_extended_on_both_sides_are_a_conflict_not_flattened(tmp_path):
    base = "[[tool.mypy.overrides]]\nmodule = ['a']\n"
    ours = base + "\n[[tool.mypy.overrides]]\nmodule = ['b']\n"
    theirs = base + "\n[[tool.mypy.overrides]]\nmodule = ['c']\n"
    conflicts, _, text = run(tmp_path, ours, theirs, base=base)
    assert conflicts == ["tool.mypy.overrides"]
    assert "[[tool.mypy.overrides]]" in text  # ours untouched, still real tables
