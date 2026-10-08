# Mutation analysis

Mutation testing asks whether the kernel test suite would *notice* a fault. A tool makes one small change to the source (flip `==` to `!=`, swap a role name, drop a `not`), runs the tests, and records whether any test failed. A change no test notices is a **survivor**: a hole in the tests, not proof of a bug.

This measures **fault-detection power over a stated fault model**. It does not prove the kernel correct, and the tests that raised the score were written by the same author who read the survivors, so it is not an independent hidden-mutation evaluation. See [ADR-0033](../adr/0033-mutation-tool-selection.md) (engine choice) and [ADR-0034](../adr/0034-mutation-measurement-and-ratchet.md) (what is measured).

## Run it

```bash
pip install -e ".[dev,mutation]"           # cosmic-ray 8.7.0, pinned in the mutation extra

nox -s mutation_quick                       # full tier: protected policy only, two workers
nox -s mutation                             # release tier: every target module
python -m quality.mutation run --quick      # same as mutation_quick, without nox and without the gate
python -m quality.mutation run --module src/eija_studio/domain/evidence.py --check
```

| Session | Tier | Scope | Gate |
|---|---|---|---|
| `mutation_quick` | `full` | `domain/policy.py` | score not below the ratchet floor |
| `mutation` | `release` | `domain/{policy,models,impact,evidence}.py`, `application/{runtime,verifier}.py` | each module's score not below its floor |

A missing `cosmic-ray` reports `NOT_RUN` (nox "skipped"), never a pass. Exit status of `python -m quality.mutation`: `0` passed, `1` ratchet failed, `2` the measurement itself failed (red baseline, engine crash after retries, the scratch copy not being the code under test). A measurement failure produces no score.

Useful options: `--module PATH` (repeatable), `--sample N` (deterministic sample of N mutants per module: an estimate, never gated), `--workers 1|2` (2 is a hard ceiling on the shared PC), `--resume` (reuse a finished shard whose inputs are byte-identical; never used by the sessions), `--write-baseline` (raise or establish floors from a full run; `--allow-lower` to lower one, in review).

## Reports

Written to `reports/mutation/` (gitignored, deterministic, no timestamps):

* `summary.json`: per module and overall `total`, `killed`, `survived`, `timeout`, `incompetent`, `score`, the tests used, the operator list, engine version and platform.
* `survivors.md`: every survivor with its diff and a suggested test, plus every mutant that could not be exercised.

`score = (killed + timeout) / (killed + timeout + survived)`, rounded down to four places. `incompetent` mutants (import or collection failures, worker crashes) are excluded, and the gate fails if more than 20% of a module's mutants are incompetent.

## Baseline and ratchet

`quality/mutation/baseline.json` holds one floor per module, taken from a full run on the platform named in the file. The gate fails if a score drops below its floor, if a module has no floor, or if no mutants were generated. Floors go up with `--write-baseline`; lowering one needs `--allow-lower` and shows up as a diff of a committed file.

BASELINE_TABLE

## How it works (Windows notes)

* **Engine:** [cosmic-ray](https://github.com/sixty-north/cosmic-ray). mutmut 3 does not support native Windows (it forks); see ADR-0033 for the evaluation.
* **Isolation:** each shard mutates its own copy of the repository under `.tmp/mutation/<module>-<i>of<n>/` (inside the checkout, never the slow system temp). The real tree is never rewritten. Before any mutant runs the tooling proves the copy is what Python imports and that the selected tests pass unmutated.
* **Parallelism:** at most two workers; every target is split into two exact shards (`i mod 2`), so one module uses both.
* **Operators:** a curated set (comparison boundaries, `and`/`or`, `not`, booleans, numbers, arithmetic sign, `continue`/`break`, exception type, zero-iteration loops) plus three EIJA operators for names: identifier-like string constants, return values and membership tests (`quality/mutation/eija_operators.py`). Prose strings and `Literal[...]` type arguments are not mutated.
* **Timeouts:** each mutant gets `8 x baseline + 30` seconds. On Windows cosmic-ray can only kill the immediate test process, so selected tests avoid grandchildren where possible. A timeout counts as detected but is reported separately.
* **Crashes:** a process that dies with an NTSTATUS exit code (seen at start-up on a heavily loaded PC) is retried up to four times with backoff, and every attempt is logged in `.tmp/mutation/<shard>/.tmp/engine.log`. A test failure is never retried.
* **Selection caveat:** a mutant is tested only by its target's selected test files (`quality/mutation/targets.py`). A survivor may therefore be killed by an unselected test. Widen the selection when that is the case.

## Working through survivors

1. Read `reports/mutation/survivors.md`. Each entry shows the diff and what a killing test must assert.
2. If the change would alter behaviour, add a test that asserts the *specified* behaviour (from the docs or ADRs, not copied from the code) and fails on the mutant.
3. If the change cannot alter behaviour (an equivalent mutant), mark the line `# pragma: no mutate` with a one-line justification. Do not weaken production code or policy to make a mutant die.
4. Rerun the module, then `python -m quality.mutation run --module ... --write-baseline` to raise the floor, and commit `baseline.json`.

## Limits

* Six modules and a curated fault model: a high score here says nothing about code that is not mutated (adapters, HTTP, providers, compiler, service).
* Mutation score is not coverage and not correctness. A test can kill a mutant for an incidental reason.
* Strings that contain whitespace, and `Literal[...]` types, are not mutated; nor are mutants that need several simultaneous changes (higher-order mutants).
* The 88 pre-existing tests left survivors that an author reading the policy tables would not have missed; the added tests close them, but they share an author with the survivor list.
