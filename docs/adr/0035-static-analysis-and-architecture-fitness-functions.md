# ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets

* Status: accepted
* Date: 2026-09-28
* Lane: quality

## Context and problem statement

The kernel's central claims (a vendor-free domain, authority checked before replay, computed evidence) hold only while the code keeps its shape. Many parallel lanes are about to edit it. Review alone will not notice a `sqlite3` import in `domain/`, a function growing from 16 to 40 branches, or a dependency used but undeclared. The gates must be tool-enforced, runnable offline, and honest about the debt the code already carries.

## Decision drivers

* ADR-0016: adopt mature OSS, write only EIJA-specific glue.
* Other lanes edit `src/` and `tests/` concurrently, so a mass reformat would cause conflicts on every branch.
* Gates must be reproducible locally on Windows and POSIX because hosted CI is unavailable (ADR-0017).
* A gate that cannot fail is worse than no gate, so each needs a negative control.

## Considered options

* Ruff, mypy, import-linter, radon/xenon, coverage.py, deptry and pip-audit as separate nox sessions with thresholds in `pyproject.toml` (chosen)
* pylint plus flake8 plugins (rejected: slower, and several tools to do what Ruff does; only the pylint rule subset that Ruff implements is used)
* pyright (rejected: mypy has the pydantic plugin the contracts need)
* A custom AST architecture test only (kept as an extra, insufficient alone: it does not follow transitive imports)
* Blanket adoption of every rule at once, or `ruff format` over the kernel (rejected: breaks parallel lanes and hides real debt)

## Decision outcome

Chosen option: separate, tiered nox sessions in `quality/sessions/quality.py`, each tool configured in `pyproject.toml`, all pinned in the `lint` extra.

* **Ratchet, not cliff.** The current code passes every gate except the release-tier audit. Existing violations are named debt: per-file ruff ignores, per-module mypy overrides, a complexity baseline. Thresholds tighten, never loosen; debt is deleted in the commit that fixes it.
* **Architecture as fitness functions** with import-linter: layers `interfaces > bootstrap > adapters > application > domain`, a vendor-free domain and application, and adapters wired only by bootstrap. `tests/test_quality_gates.py` seeds violations into a copy of the kernel and requires the contracts to break.
* **mypy strict where invariants live** (`domain`, `application`), default profile elsewhere with a written module-by-module plan. No `ignore_errors`.
* **Complexity**: xenon enforces average and module rank; a small custom ratchet (`quality/gates/complexity_ratchet.py`) adds the per-function debt list xenon cannot express. `--update` can only lower debt.
* **Coverage** is branch coverage with `fail_under` at the floor of the measured value.
* **Dependency hygiene**: deptry in the fast tier; pip-audit in the release tier because it needs network, reporting `NOT_RUN` when offline.
* **Kernel edits** were limited to type annotations with no behaviour change (`dict[str, Any]`, callable types, one narrowing `assert`).

### Consequences

* Good: architectural drift and complexity growth fail locally within seconds; the debt is visible, small and pinned.
* Good: pip-audit surfaced real advisories against `requirements-tested.txt` on its first run (recorded in `docs/quality/gates.md`); the gate reports them instead of hiding them.
* Bad: pinned linters need deliberate upgrades, and the `lint` extra adds install time to a venv.
* Bad: the coverage floor (78 %) is low, `cli.py` is 0 % covered, and formatting-class findings remain ignored in the legacy trees.
* Revisit when: the legacy trees stop being edited in parallel (then format them and delete the style ignores), or a gate's false-positive rate makes people bypass it.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| xenon, radon `cc`, Ruff `C901` | None can hold a named list of legacy functions at their current value while enforcing a budget on everything else | `quality/gates/complexity_ratchet.py` is about 130 lines on radon's API; replace it with Ruff `C901` and per-function `noqa` once the debt list is empty |
