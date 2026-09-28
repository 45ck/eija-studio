"""Run the Bend proof gate in a pinned container and write ``reports/formal/bend.json``.

Bend 2 supports Linux, macOS and WSL, not native Windows, so the checker runs in the image built from
``verification/bend/Dockerfile`` (Bend and Lean pinned by version and archive checksum, base image by
digest). The container has no network, a read-only root filesystem, no capabilities, and sees the
staged files read-only. Several ``bend`` invocations share one container start (the start costs more
than the checks), one container at a time.

A gate run does four things, and reports each separately:

1. **Proof**: ``bend PROOF.bend --verdict`` on the committed ``main.bend`` / ``LAWS.bend`` /
   ``PROOF.bend``. ``--verdict`` rechecks every definition with BendTT, the small kernel proved sound in
   Lean. PASS means ``ALL PROOFS CHECK`` and exit 0, nothing weaker.
2. **Negative controls**: the unchanged proofs against deliberately unsafe models. Each must FAIL, and
   exactly the laws it was seeded to break must fail (per-law attribution).
3. **Counterexamples**: for each seeded fault, a concrete trace evaluated by Bend that shows the law is
   actually false in the unsafe model, so "the proof fails" is backed by "the property is violated".
4. **Conformance**: the Bend model evaluated against the real Python runtime on the runtime matrix and
   on witness traces (a differential test, see ``bend_conformance``).

Missing prerequisites (Docker, the daemon, the image, network for the first build) give ``NOT_RUN``,
never PASS. What this proves and does not prove is stated in ``docs/formal/bend.md``.
"""
# ruff: noqa: T201  (command-line tool: printing the verdict and the drift message is its output)
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))  # the repo root, so `verification.bend.*` resolves when run as a script

import verification.bend.bend_conformance as conformance  # noqa: E402
import verification.bend.bend_slicing as slicing  # noqa: E402
from verification.bend.bend_controls import CONTROLS, Control  # noqa: E402
from verification.bend.bend_generate import GENERATED_PATH, SLOTS, default_models, render_main  # noqa: E402

IMAGE = "eija-bend-checker:2.0.32"
DOCKERFILE = HERE / "Dockerfile"
REPORT_PATH = ROOT / "reports" / "formal" / "bend.json"
SNAPSHOT_PATH = HERE / "evidence" / "bend.json"
STAGE_ROOT = ROOT / ".tmp" / "bend-stage"
SCHEMA_VERSION = 1
LIMITS = (
    "Laws are proved about the generated Bend model, not about the Python runtime or its SQLite adapter.",
    "The model abstracts version (CAS), operation replay, audit persistence, crash durability and the HTTP layer.",
    "Effect emission is modelled as 'a successful step emits exactly its rule's declared effects'; the "
    "runtime's additional EFFECT_DENIED rejection of unknown effect kinds is not modelled (the model is more permissive).",
    "Conformance to the runtime is a bounded differential test (matrix cells and traces), not a proof.",
    "The unsafe models are a fixed set of seeded faults; failing them shows sensitivity to those faults only.",
    "The laws are authored by the same team as the model; they are not an independently blinded specification.",
)


class NotRun(Exception):
    """A prerequisite is missing: the gate reports NOT_RUN (never PASS)."""


@dataclass(frozen=True)
class Result:
    code: int
    out: str
    err: str = ""


class Job(NamedTuple):
    """One ``bend`` invocation: run in staged directory ``dir`` with ``args``."""
    dir: str
    args: tuple[str, ...]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Checker:
    """The pinned Bend container. Heavy work happens in ``docker run``; one container at a time."""

    def __init__(self, image: str = IMAGE):
        self.image = image

    @staticmethod
    def _docker(*args: str, timeout: int) -> Result:
        try:
            p = subprocess.run(["docker", *args],  # noqa: S603, S607  (fixed argv, no shell; docker resolved from PATH by design)
                                capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace", check=False)
        except FileNotFoundError as e:
            raise NotRun("docker CLI not found on PATH") from e
        except subprocess.TimeoutExpired as e:
            raise NotRun(f"docker {args[0]} timed out after {timeout}s") from e
        return Result(p.returncode, p.stdout, p.stderr)

    def prerequisites(self) -> dict:
        """Check the daemon and build the image if it is missing or was not built from the current Dockerfile."""
        info = self._docker("version", "--format", "{{.Server.Version}}", timeout=30)
        if info.code != 0 or not info.out.strip():
            raise NotRun("docker daemon is not running (docker version failed): " + info.err.strip()[:200])
        want = sha256_file(DOCKERFILE)
        inspect = self._docker("image", "inspect", self.image, "--format", "{{json .Config.Labels}}", timeout=30)
        labels = json.loads(inspect.out) if inspect.code == 0 and inspect.out.strip() not in ("", "null") else {}
        if labels.get("dev.eija.dockerfile.sha256") != want:
            build = self._docker("build", "--label", f"dev.eija.dockerfile.sha256={want}", "-t", self.image, str(HERE), timeout=900)
            if build.code != 0:
                raise NotRun("could not build the pinned Bend image (network needed for the first build): " + build.err.strip()[-300:])
        return {"docker_server_version": info.out.strip(), "dockerfile_sha256": want}

    def image_facts(self) -> dict:
        fmt = ("{{.Id}}|{{index .Config.Labels \"dev.eija.bend.version\"}}|{{index .Config.Labels \"dev.eija.bend.commit\"}}"
               "|{{index .Config.Labels \"dev.eija.lean.version\"}}")
        r = self._docker("image", "inspect", self.image, "--format", fmt, timeout=30)
        image_id, bend, commit, lean = [*r.out.strip().split("|"), "", "", "", ""][:4]
        version = self._docker("run", "--rm", "--network", "none", self.image, "version", timeout=60).out.strip()
        return {"image_tag": self.image, "image_id": image_id, "bend_version_output": version, "bend_version": bend,
                "bend_commit": commit, "lean_version": lean, "base_image": _base_image()}

    def run_jobs(self, root: Path, jobs: list[Job]) -> list[Result]:
        """Run every job in one container with ``root`` mounted read-only at /work; stdout and stderr merged."""
        script = "".join(
            f'echo "@@@BEGIN {i}"; (cd /work/{shlex.quote(j.dir)} && bend {" ".join(shlex.quote(a) for a in j.args)}) 2>&1; '
            f'echo "@@@END {i} $?"; ' for i, j in enumerate(jobs))
        run = self._docker(
            "run", "--rm", "--network", "none", "--read-only", "--tmpfs", "/tmp",  # noqa: S108  (a path inside the container, not a host temp file)
             "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges", "--pids-limit", "256", "--memory", "2g", "--cpus", "2",
            "-v", f"{root}:/work:ro", "--entrypoint", "sh", self.image, "-c", script, timeout=120 + 30 * len(jobs))
        if "@@@END" not in run.out:
            raise NotRun("the Bend container did not run: " + (run.err.strip() or run.out.strip())[-300:])
        return parse_jobs(run.out, len(jobs))


def parse_jobs(text: str, count: int) -> list[Result]:
    """Split the marker-delimited output of ``run_jobs`` (a missing marker is exit 255, never success)."""
    results = []
    for i in range(count):
        m = re.search(rf"@@@BEGIN {i}\r?\n(.*?)@@@END {i} (\d+)", text, re.DOTALL)
        results.append(Result(int(m.group(2)), m.group(1)) if m else Result(255, ""))
    return results


def _base_image() -> str:
    first = next(ln for ln in DOCKERFILE.read_text(encoding="utf-8").splitlines() if ln.startswith("FROM ubuntu"))
    return first.split()[1]


def stage(name: str, dirs: dict[str, dict[str, str]]) -> Path:
    """A clean tree ``STAGE_ROOT/name/<dir>/<file>`` (LF endings) holding exactly ``dirs``."""
    root = STAGE_ROOT / name
    if root.exists():
        shutil.rmtree(root)
    for directory, files in dirs.items():
        (root / directory).mkdir(parents=True)
        for filename, text in files.items():
            (root / directory / filename).write_bytes(text.encode("utf-8"))
    return root


def classify(result: Result) -> dict:
    """Bend's own verdict. Anything but ALL PROOFS CHECK with exit 0 is not a proof."""
    text = result.out + result.err
    if result.code == 0 and "ALL PROOFS CHECK" in result.out and "SOME PROOFS FAIL" not in text:
        return {"result": "PROVEN", "exit_code": result.code}
    error = text.split("SOME PROOFS FAIL", 1)[1].strip() if "SOME PROOFS FAIL" in text else ""
    location = re.search(r"^Location: (.+)$", error, re.MULTILINE)
    return {"result": "FAILED", "exit_code": result.code, "location": location.group(1) if location else None,
            "first_error": (error or text.strip())[:600]}


def prove_directory(checker: Checker, name: str, main: str, laws: str, proof: str, extra: dict[str, str],
                    jobs_extra: list[Job] | None = None, *, attribute: bool = True) -> tuple[dict, list[Result]]:
    """Check a model with the given laws/proofs: model check, full verdict, and (unless quick) each law alone.

    Per-law runs are Bend's ordinary check (attribution); the ``--verdict`` kernel recheck is the full run.
    Returns the verdicts and the raw results of ``jobs_extra`` (run in the ``full`` directory)."""
    law_list = slicing.law_names(laws) if attribute else []
    dirs = {"full": {"main.bend": main, "LAWS.bend": laws, "PROOF.bend": proof, **extra}}
    for law in law_list:
        sliced_laws, sliced_proof = slicing.slice_for_law(laws, proof, law)
        dirs[f"law-{law}"] = {"main.bend": main, "LAWS.bend": sliced_laws, "PROOF.bend": sliced_proof}
    jobs = [Job("full", ("main.bend", "--check-only")), Job("full", ("PROOF.bend", "--verdict"))]
    jobs += [Job(f"law-{law}", ("PROOF.bend",)) for law in law_list]
    jobs += jobs_extra or []
    results = checker.run_jobs(stage(name, dirs), jobs)
    verdicts = {"model_check": classify(results[0]), "full_run": classify(results[1]),
                "laws": {law: classify(results[2 + i]) for i, law in enumerate(law_list)}}
    return verdicts, results[2 + len(law_list):]


def run_proof(checker: Checker, *, attribute: bool = True) -> dict:
    """The gate proper: the committed files, full ``--verdict`` run, then (unless quick) each law alone."""
    main, laws, proof = (p.read_text(encoding="utf-8") for p in (GENERATED_PATH, HERE / "LAWS.bend", HERE / "PROOF.bend"))
    if main != render_main(default_models()):
        raise RuntimeError("main.bend is stale: run python verification/bend/bend_generate.py")
    unproved = sorted(set(slicing.law_names(laws)) - slicing.proof_names(proof))
    verdicts, _ = prove_directory(checker, "committed", main, laws, proof, {}, attribute=attribute)
    comments = slicing.law_comments(laws)
    if attribute:
        per_law = [{"name": n, "statement": comments.get(n, ""), "basis": "law checked alone (bend, sliced)", **v}
                   for n, v in verdicts["laws"].items()]
    else:  # quick: the full run proves every law in the file or none of them
        full_result = verdicts["full_run"]["result"]
        per_law = [{"name": n, "statement": comments.get(n, ""), "basis": "full --verdict run (all laws in one file)",
                    "result": full_result} for n in slicing.law_names(laws)]
    passed = (verdicts["full_run"]["result"] == "PROVEN" and verdicts["model_check"]["result"] == "PROVEN" and not unproved
              and all(item["result"] == "PROVEN" for item in per_law))
    return {"status": "PASS" if passed else "FAIL", "command": "bend PROOF.bend --verdict", "model_check": verdicts["model_check"],
            "full_run": verdicts["full_run"], "laws_without_proof": unproved, "laws": per_law}


def run_control(checker: Checker, control: Control, *, attribute: bool = True) -> dict:
    """One negative control: the unchanged laws and proofs against a seeded-unsafe model."""
    main = control.build()
    laws, proof = (HERE / "LAWS.bend").read_text(encoding="utf-8"), (HERE / "PROOF.bend").read_text(encoding="utf-8")
    extra, probes = {}, []
    if control.witness_steps:
        extra["witness.bend"] = conformance.witness_program("Candidate", control.witness_steps)
        probes.append(Job("full", ("witness.bend",)))
    if control.probe:
        extra["probe.bend"] = conformance.effects_program("Candidate", *control.probe)
        probes.append(Job("full", ("probe.bend",)))
    verdicts, probe_results = prove_directory(checker, f"control-{control.name}", main, laws, proof, extra, probes,
                                              attribute=attribute)
    failing = [n for n, v in verdicts["laws"].items() if v["result"] != "PROVEN"]
    passing = [n for n, v in verdicts["laws"].items() if v["result"] == "PROVEN"]
    entry = {"name": control.name, "description": control.description,
             "model_well_formed": verdicts["model_check"]["result"] == "PROVEN",
             "full_run": verdicts["full_run"], "expected_failing_laws": list(control.expected_failing_laws),
             "failing_laws": failing, "passing_laws": passing,
             "attribution": "per law (each law checked alone)" if attribute else "skipped (quick mode)",
             "kernel_policy_findings": control.kernel_policy_findings()}
    # Exact attribution: the seeded fault breaks the laws it was designed to break and no others.
    as_expected = (verdicts["model_check"]["result"] == "PROVEN" and verdicts["full_run"]["result"] == "FAILED"
                   and (set(failing) == set(control.expected_failing_laws) if attribute else True))
    outputs = iter(probe_results)
    confirmed = True
    if control.witness_steps:
        state = conformance.parse_state(next(outputs).out)
        entry["counterexample"] = {"steps": [list(s) for s in control.witness_steps], "final_state_in_unsafe_model": state,
                                   "final_state_expected_by_fault": control.witness_state, "confirmed": state == control.witness_state}
        confirmed &= state == control.witness_state
    if control.probe:
        emitted = [e for e in next(outputs).out.strip().strip('"').split(",") if e]
        entry["effect_probe"] = {"step": list(control.probe), "emitted": emitted, "confirmed": control.probe_effect in emitted}
        confirmed &= control.probe_effect in emitted
    entry["result"] = "PROOF_FAILS_AS_EXPECTED" if as_expected and confirmed else "UNEXPECTED"
    return entry


def run_conformance(checker: Checker) -> dict:
    """Bend model vs. the real runtime: the runtime matrix and the witness traces (shipped models)."""
    models = default_models()
    main = GENERATED_PATH.read_text(encoding="utf-8")
    programs = conformance.matrix_programs(models)
    witnesses = {f"witness_{i}.bend": conformance.witness_program(w.slot, w.steps) for i, w in enumerate(conformance.GOOD_WITNESSES)}
    names = [*programs, *witnesses]
    root = stage("conformance", {"work": {"main.bend": main, **programs, **witnesses}})
    results = checker.run_jobs(root, [Job("work", (n,)) for n in names])
    by_name = dict(zip(names, results, strict=True))
    scratch = conformance.scratch_workspace(ROOT / ".tmp" / "bend-conformance")
    try:
        bend_cells: dict = {}
        for name in programs:
            bend_cells.update(conformance.parse_matrix(by_name[name].out))
        report = conformance.compare_matrices(bend_cells, conformance.python_matrix(models, scratch))
        traces = []
        for i, w in enumerate(conformance.GOOD_WITNESSES):
            bend_state = conformance.parse_state(by_name[f"witness_{i}.bend"].out)
            python_state = conformance.python_witness(models[w.slot], w.steps, scratch)
            traces.append({"name": w.name, "model": w.slot, "why": w.why, "steps": [list(s) for s in w.steps],
                           "expected_final_state": w.final_state, "bend_final_state": bend_state, "python_final_state": python_state,
                           "agree": bend_state == python_state == w.final_state})
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    ok = not report["mismatches"] and not report["unmatched_cells"] and all(t["agree"] for t in traces)
    return {"status": "PASS" if ok else "FAIL", "method": "differential test (not a proof)", "matrix": report, "witnesses": traces}


def model_facts() -> dict:
    models = default_models()
    return {"semantic_hash": {slot: models[slot].semantic_hash for slot in SLOTS},
            "slots": {"Baseline": "policy.baseline()", "Candidate": "recommend_only candidate (apply_transaction enable_recommendation)"},
            "files": {name: sha256_file(HERE / name) for name in ("main.bend", "LAWS.bend", "PROOF.bend", "bend_generate.py")}}


def build_report(*, controls: bool = True, conformance_check: bool = True, quick: bool = False) -> dict:
    report: dict = {"kind": "bend_proof", "schema_version": SCHEMA_VERSION, "producer": "verification/bend/bend_runner.py",
                    "platform": platform.platform(), "python": platform.python_version(), "model": model_facts(),
                    "limits": list(LIMITS)}
    checker = Checker()
    try:
        report["tool"] = {**checker.prerequisites(), **checker.image_facts()}
        report["mode"] = "quick" if quick else "complete"
        report["proof"] = run_proof(checker, attribute=not quick)
        if controls:
            report["negative_controls"] = [run_control(checker, c, attribute=not quick) for c in CONTROLS]
        if conformance_check:
            report["conformance"] = run_conformance(checker)
    except NotRun as e:
        return {**report, "status": "NOT_RUN", "reason": str(e)}
    parts = [report["proof"]["status"]]
    if controls:
        parts.append("PASS" if all(c["result"] == "PROOF_FAILS_AS_EXPECTED" for c in report["negative_controls"]) else "FAIL")
    if conformance_check:
        parts.append(report["conformance"]["status"])
    report["status"] = "PASS" if set(parts) == {"PASS"} else "FAIL"
    report["summary"] = {"proof": report["proof"]["status"],
                         "negative_controls": parts[1] if controls else "NOT_RUN",
                         "conformance": report["conformance"]["status"] if conformance_check else "NOT_RUN"}
    return report


def write_report(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run the Bend proof gate (Docker) and write the evidence report")
    ap.add_argument("--report", type=Path, default=REPORT_PATH)
    ap.add_argument("--snapshot", action="store_true", help=f"also write the committed snapshot {SNAPSHOT_PATH.relative_to(ROOT)}")
    ap.add_argument("--quick", action="store_true", help="skip the per-law attribution runs (partial evidence; never snapshotted)")
    ap.add_argument("--no-controls", action="store_true", help="skip the negative controls (partial evidence; never snapshotted)")
    ap.add_argument("--no-conformance", action="store_true", help="skip the runtime conformance test (partial evidence; never snapshotted)")
    args = ap.parse_args(argv)
    report = build_report(controls=not args.no_controls, conformance_check=not args.no_conformance, quick=args.quick)
    write_report(report, args.report)
    complete = not (args.no_controls or args.no_conformance or args.quick)
    if args.snapshot and report["status"] == "PASS" and complete:
        write_report(report, SNAPSHOT_PATH)
    print(f"bend_proof: {report['status']}" + (f" ({report['reason']})" if report.get("reason") else "") + f" -> {args.report}")
    return {"PASS": 0, "FAIL": 1, "NOT_RUN": 3}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
