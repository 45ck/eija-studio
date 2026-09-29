"""Adapter around cosmic-ray (https://github.com/sixty-north/cosmic-ray), the OSS mutation engine.

cosmic-ray rewrites the module under test on disk for the duration of each test run. To keep that away
from the real checkout, and to let two targets run side by side, every target is mutated inside its own
scratch copy of the repository under `<repo>/.tmp/mutation/<slug>` (never the system temp dir: D: is a
slow HDD on the reference PC). The scratch copy is proven to be the code under test before any mutant runs.

Nothing here decides pass/fail: it produces `Mutant` records; `model` classifies and `report` gates.
"""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path

from . import equivalents
from .model import EQUIVALENT, INCOMPETENT, SKIPPED, SURVIVED, Mutant, classify
from .targets import OPERATORS, Target

_IGNORED = shutil.ignore_patterns(".git", ".venv", ".tmp", ".nox", "reports", ".pytest-tmp", ".pytest_cache",
                                  "__pycache__", ".eija", "output", "*.egg-info", "build", "dist")
PLUGIN_DIR = ".plugins"
_CR = (sys.executable, "-m", "cosmic_ray.cli")
_OPERATOR_FILTER = (sys.executable, "-m", "cosmic_ray.tools.filters.operators_filter")
_PRAGMA_FILTER = (sys.executable, "-m", "cosmic_ray.tools.filters.pragma_no_mutate")


class MutationError(RuntimeError):
    """The analysis could not be carried out (red baseline, wrong code under test, engine failure).

    Distinct from a survivor: a survivor is a finding; this is the measurement itself failing, and the
    gate reports it as a failure rather than as a score.
    """


def scratch_dir(root: Path, target: Target, shard: tuple[int, int] = (0, 1)) -> Path:
    return root / ".tmp" / "mutation" / f"{target.slug}-{shard[0]}of{shard[1]}"


def prepare_workspace(root: Path, target: Target, shard: tuple[int, int] = (0, 1)) -> Path:
    """Fresh copy of the repository (sources, tests, pyproject) that the engine may freely rewrite."""
    scratch = scratch_dir(root, target, shard)
    if scratch.exists():
        shutil.rmtree(scratch)
    shutil.copytree(root, scratch, ignore=_IGNORED)
    (scratch / ".tmp").mkdir()
    install_operator_plugin(scratch)
    return scratch


def install_operator_plugin(scratch: Path) -> None:
    """Make `eija_operators` discoverable by cosmic-ray's plugin loader without installing anything.

    stevedore reads entry points from any dist-info directory on `sys.path`, so a dist-info next to a copy
    of the module inside the scratch workspace is enough; the real environment is never modified.
    """
    plugins = scratch / PLUGIN_DIR
    dist = plugins / "eija_operators-0.dist-info"
    dist.mkdir(parents=True)
    (dist / "METADATA").write_bytes(b"Metadata-Version: 2.1\nName: eija-operators\nVersion: 0\n")
    (dist / "entry_points.txt").write_bytes(b"[cosmic_ray.operator_providers]\neija = eija_operators:OperatorProvider\n")
    shutil.copyfile(Path(__file__).with_name("eija_operators.py"), plugins / "eija_operators.py")


def environment(scratch: Path) -> dict[str, str]:
    env = dict(os.environ)
    env.update(PYTHONPATH=os.pathsep.join([str(scratch / "src"), str(scratch / PLUGIN_DIR)]), PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
               TMP=str(scratch / ".tmp"), TEMP=str(scratch / ".tmp"), TMPDIR=str(scratch / ".tmp"))
    return env


def pytest_command(target: Target) -> list[str]:
    return [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", "-o", "addopts=", *target.tests]


def render_config(target: Target, timeout: float) -> str:
    """Deterministic cosmic-ray TOML: same inputs, same bytes."""
    # cosmic-ray splits the command with shlex (POSIX rules): forward slashes survive, backslashes do not.
    command = " ".join(shlex.quote(Path(a).as_posix() if a == sys.executable else a) for a in pytest_command(target))
    operators = "|".join(OPERATORS)
    # cosmic-ray can only exclude by regex, so exclude everything that is not a curated operator.
    exclude = json.dumps(f"(?!(?:{operators})$).*")
    return "\n".join([
        "[cosmic-ray]",
        f'module-path = "{target.module}"',
        f"timeout = {timeout:.1f}",
        "excluded-modules = []",
        f"test-command = {json.dumps(command)}",
        "",
        "[cosmic-ray.distributor]",
        'name = "local"',
        "",
        "[cosmic-ray.filters.operators-filter]",
        f"exclude-operators = [{exclude}]",
        "",
    ])


_WINDOWS_CRASH = 0xC0000000  # NTSTATUS error range: the process died (seen at start-up on a heavily loaded PC), it did not fail
_ATTEMPTS = 4
_BACKOFF_SECONDS = 20  # a crash seen at start-up went away when the PC was less loaded; do not retry in a tight loop


def _run(args: list[str], scratch: Path, log: Path, *, capture: bool = False, check: bool = True,
         reset: Path | None = None) -> subprocess.CompletedProcess:
    """Run one engine step, retrying only when the process itself crashed (an NTSTATUS exit code).

    A test failure, a red baseline or an engine error exits with a small code and is never retried. Every
    step is safe to repeat: `init` starts from a deleted session (`reset`), `exec` resumes pending work only,
    the filters and `dump` are idempotent, and a crashed process produced no result. Every attempt is logged.
    """
    for attempt in range(1, _ATTEMPTS + 1):
        if reset is not None:
            reset.unlink(missing_ok=True)
        proc = subprocess.run(args, cwd=scratch, env=environment(scratch), capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        with log.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(f"$ {' '.join(args)}  [attempt {attempt}, exit {proc.returncode:#x}]\n"
                         f"{'<captured>' if capture else proc.stdout}\n{proc.stderr}\n")
        if proc.returncode < _WINDOWS_CRASH or attempt == _ATTEMPTS:
            break
        time.sleep(_BACKOFF_SECONDS * attempt)
    if check and proc.returncode != 0:
        raise MutationError(f"{' '.join(args[:4])} failed with exit code {proc.returncode:#x}; see {log}\n{proc.stderr[-800:]}")
    return proc


def baseline_seconds(target: Target, scratch: Path, log: Path) -> float:
    """The selected tests must pass unmutated, against the scratch copy, before any mutant is meaningful."""
    probe = _run([sys.executable, "-c", "import eija_studio;print(eija_studio.__file__)"], scratch, log, capture=True)
    located = Path(probe.stdout.strip()).resolve()
    if scratch.resolve() not in located.parents:
        raise MutationError(f"code under test resolves to {located}, not the scratch copy {scratch}: mutants would not be observed")
    started = time.monotonic()
    proc = _run(pytest_command(target), scratch, log, check=False)
    elapsed = time.monotonic() - started
    if proc.returncode != 0:
        raise MutationError(f"baseline is red for {target.module} with {target.tests}; mutation results would be meaningless\n{proc.stdout[-1500:]}")
    return elapsed


def _sample_key(module_path: str, start: list[int], end: list[int], operator: str, occurrence: int) -> str:
    return hashlib.sha256(f"{Path(module_path).as_posix()}|{start}|{end}|{operator}|{occurrence}".encode()).hexdigest()


def select_mutants(session: Path, *, sample: int | None, shard: tuple[int, int]) -> None:
    """Skip pending mutants outside the requested sample and shard.

    Mutants are ordered by a stable hash of position and operator, so a sample of `size` is reproducible
    (same source, same sample) and independent of test outcome; a sampled score is an estimate over that
    sample. Shard `i` of `n` takes every n-th mutant of the (sampled) order: shards partition the work
    exactly, which is how one target uses both workers.
    """
    from cosmic_ray.work_db import use_db
    from cosmic_ray.work_item import WorkResult, WorkerOutcome

    def key(item) -> str:
        m = item.mutations[0]
        return _sample_key(str(m.module_path), list(m.start_pos), list(m.end_pos), m.operator_name, m.occurrence)

    index, count = shard
    with use_db(str(session)) as db:
        ordered = sorted(db.pending_work_items, key=key)
        kept = ordered if sample is None else ordered[:sample]
        keep = {item.job_id for position, item in enumerate(kept) if position % count == index}
        for item in ordered:
            if item.job_id not in keep:
                db.set_result(item.job_id, WorkResult(output="Not selected", worker_outcome=WorkerOutcome.SKIPPED))


def parse_dump(dump: str, module: str, source: str | None = None) -> list[Mutant]:
    """Turn `cosmic-ray dump` JSON lines into sorted `Mutant` records; skipped ones are dropped.

    With `source` (the unmutated module text) a survivor that provably cannot change behaviour is reclassified
    as `equivalent` (see `equivalents`); a killed mutant is never reclassified."""
    mutants = []
    for line in dump.splitlines():
        item, result = json.loads(line)
        mutation = item["mutations"][0]
        status = classify({"result": result})
        if status == SKIPPED:
            continue  # filtered operator, pragma, or outside the sample: not part of the measurement
        found = Mutant(
            module=module, operator=mutation["operator_name"], occurrence=mutation["occurrence"],
            start=tuple(mutation["start_pos"]), end=tuple(mutation["end_pos"]), function=mutation.get("definition_name"),
            status=status, diff=(result.get("diff") or "").replace("\\", "/"),
            output=(result.get("output") or "") if status in {SURVIVED, INCOMPETENT} else "")
        why = equivalents.reason(found, source) if source is not None and status == SURVIVED else None
        mutants.append(replace(found, status=EQUIVALENT, equivalent_reason=why) if why else found)
    return sorted(mutants, key=lambda m: m.sort_key)


def run_target(root: Path, target: Target, *, sample: int | None = None, shard: tuple[int, int] = (0, 1)) -> list[Mutant]:
    """Mutate one shard of one module and return its measured mutants. Raises `MutationError`."""
    scratch = prepare_workspace(root, target, shard)
    log = scratch / ".tmp" / "engine.log"
    seconds = baseline_seconds(target, scratch, log)
    (scratch / "cr.toml").write_bytes(render_config(target, timeout=round(8 * seconds + 30, 1)).encode())
    session = scratch / "session.sqlite"
    _run([*_CR, "init", "cr.toml", str(session)], scratch, log, reset=session)
    _run([*_OPERATOR_FILTER, str(session), "cr.toml"], scratch, log)
    _run([*_PRAGMA_FILTER, str(session)], scratch, log)
    select_mutants(session, sample=sample, shard=shard)
    _run([*_CR, "exec", "cr.toml", str(session)], scratch, log)
    mutants = parse_dump(_run([*_CR, "dump", str(session)], scratch, log, capture=True).stdout, target.module,
                          (root / target.module).read_text(encoding="utf-8"))
    unloadable = [m for m in mutants if m.status == INCOMPETENT and "plugins.py" in m.output]
    if unloadable:
        raise MutationError(f"{len(unloadable)} mutants failed to load their operator plugin (see {log}); the score would be meaningless")
    return mutants


def engine_version() -> str:
    from importlib.metadata import version
    return version("cosmic-ray")
