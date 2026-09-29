# ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows

* Status: accepted
* Date: 2026-09-29
* Lane: mutation

## Context and problem statement

The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role or a weakened evidence check. [ADR-0018](0018-formal-vv-portfolio.md) lists mutation analysis as its own evidence kind: it measures **fault-detection power of the tests over a stated fault model**. It does not prove the kernel correct. The reference platform is Windows 11 with Git Bash, CPython 3.12 and a shared 16 GB PC, and [ADR-0016](0016-oss-first-adapters-not-engines.md) requires adopting an existing tool before writing any engine.

## Decision drivers

* Must run on native Windows: contributors and the reference PC are Windows; a gate that needs a second OS layer is a gate people skip.
* Maintained, and correct about what it reports (killed, survived, timed out, could not run).
* Must not mutate the working tree in place in a way that a crash could leave behind.
* Bounded resources: at most two workers, temp data inside the checkout.
* Extensible enough to cover the fault classes that matter for authority code (names, roles, states, error codes).

## Considered options

Each option below was tried on the reference platform (Windows 11 10.0.26200, CPython 3.12.10, 2026-09-29), not judged from its README.

* **mutmut 3.8.0**: installed in a scratch venv; `mutmut --help` (and importing `mutmut.__main__`) prints "To run mutmut on Windows, please use the WSL. Native windows support is tracked in issue https://github.com/boxed/mutmut/issues/397". mutmut 3 forks worker processes, which native Windows does not have. **Rejected for native use.** The WSL route needs an installed Linux distribution: `wsl -l` on the reference PC lists only `docker-desktop`, which is Docker's internal utility distribution, not a user environment.
* **mutmut 3.8.0 inside Docker**: see "Docker probe" below. It works in principle but adds an image pull, a bind mount over a slow filesystem and a running Docker Desktop to what should be a one-command gate, and it would occupy the one container this lane may run.
* **cosmic-ray 8.7.0** (sixty-north): installed natively; `init`, `exec` and `dump` all run on Windows. It parses with parso, rewrites the module under test on disk for the duration of each test run, restores it afterwards, and runs tests through `subprocess` with a timeout. Operators are plugins (entry point group `cosmic_ray.operator_providers`), and results live in a SQLite session that `exec` can resume. **Chosen.**
* **mutatest 3.1.0**: last released in 2020; not maintained. Not evaluated further.
* **A custom mutation engine**: not needed, because cosmic-ray works. Not written.

### Docker probe

DOCKER_PROBE_RESULT

## Decision outcome

Chosen option: "cosmic-ray, natively", because it is the only maintained OSS mutation tool that runs on the reference platform without a second operating-system layer, and its plugin interface lets EIJA add the fault classes it lacks without forking it.

EIJA-specific glue, in `quality/mutation/` (outside the shipped package):

* `engine.py`: runs cosmic-ray inside a **scratch copy** of the repository under `<checkout>/.tmp/mutation/` so the real tree is never rewritten, proves the copy is the code under test before any mutant runs (import path probe and a green baseline), and turns `cosmic-ray dump` into typed records.
* `eija_operators.py`: three operators that cosmic-ray lacks (identifier-like string constants, return values, membership tests). They are loaded through a dist-info written into the scratch copy, so nothing is installed.
* `model.py`, `report.py`: classification, score, the ratchet and the survivor report.
* `runner.py`: two workers maximum, each target split into two exact shards.

### Consequences

* Good: native, resumable, no second OS layer; the engine carries its own history; the real checkout is never mutated.
* Good: a survivor report with diffs and suggested tests turns the score into work items.
* Bad: cosmic-ray's `local` distributor is serial, so parallelism comes from our own shards, each with its own scratch copy (copying ~6 MB per shard).
* Bad: cosmic-ray kills only the immediate test process on a timeout on Windows (no process groups). Selected tests therefore avoid grandchild processes where possible, and a timeout is reported separately so an unusual number of them is visible.
* Revisit when: mutmut ships native Windows support (issue 397), or cosmic-ray drops Windows.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| cosmic-ray 8.7.0 (engine, adopted) | It has no string-constant, return-value or membership operator, no way to shard one module across workers with isolated working trees, and no ratchet or survivor report. All of that is glue around it. | Operators can be upstreamed to cosmic-ray as a provider; the rest is a thin adapter. |
| mutmut 3.8.0 | Not runnable natively on Windows (above). | Swap `engine.py` for a mutmut-in-container adapter; `model.py`/`report.py` are engine-neutral. |
| mutatest 3.1.0 | Unmaintained. | None. |
