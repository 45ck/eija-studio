"""Source-bound, bounded self-dogfood checks of actual activation services.

The report is engineering evidence, never an admissible release receipt or an owner
decision. Running it is read-only for source and existing data. It creates and deletes
only disposable synthetic workspaces beneath the checkout's .tmp directory.
"""
from __future__ import annotations

import platform
import shutil
import subprocess
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from eija_studio.adapters.identity import PACKAGE, identity, implementation_files
from eija_studio.adapters.self_facts import SOURCE_SYMBOLS, analyze_eija_source_files
from eija_studio.domain.models import DomainError, fingerprint

from .checks import CHECKS, HARNESS_MARK, ORACLE_PATH, fixture_pack, synthetic_studio
from .mutants import activation_mutations

ROOT = PACKAGE.parents[1]
SCHEMA = "eija.activation-selfdogfood.v1"


def _revision() -> dict[str, Any]:
    git = shutil.which("git")
    if git is None:
        return {"status": "NOT_RUN", "reason": "Git is unavailable"}
    result: dict[str, Any] = {"status": "OBSERVED"}
    for field, args in (("commit", ["rev-parse", "HEAD"]),
                        ("dirty_paths", ["status", "--porcelain", "--untracked-files=normal"])):
        try:
            command = subprocess.run(  # noqa: S603 - fixed read-only argv, resolved git
                [git, "-C", str(ROOT), *args], check=False, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            result[field] = None
            result["status"] = "PARTIAL"
            continue
        result[field] = command.stdout.strip() if command.returncode == 0 else None
        if field == "dirty_paths" and result[field] is not None:
            result[field] = result[field].splitlines()
        if command.returncode != 0:
            result["status"] = "PARTIAL"
    return result


def _checker_manifest() -> dict[str, str]:
    paths = [*Path(__file__).parent.glob("*.py"), ROOT / "tests/test_activation_selfdogfood.py", ORACLE_PATH]
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths) if path.is_file()}


def _observed_checks(root: Path) -> list[dict[str, Any]]:
    observations = []
    for name, check in CHECKS.items():
        studio = synthetic_studio(root / name)
        try:
            result = check(studio)
        except AssertionError as error:
            observations.append({"id": name, "status": "FAIL", "reason": str(error)})
        except DomainError as error:
            observations.append({"id": name, "status": "FAIL", "reason": "Unexpected refusal", "code": error.code})
        except Exception as error:  # isolated checker failure must be visible; never infer PASS
            observations.append({"id": name, "status": "ERROR", "error_type": type(error).__name__})
        else:
            observations.append({"id": name, "status": "PASS", "observations": result})
    return observations


def _negative_controls(root: Path) -> list[dict[str, Any]]:
    controls = []
    for index, mutant in enumerate(activation_mutations()):
        studio = mutant.factory(root / f"mutant-{index}")
        result = {"id": mutant.id, "check": mutant.check, "description": mutant.description,
                  "specimen_hash": mutant.specimen_hash}
        try:
            CHECKS[mutant.check](studio)
        except AssertionError as error:
            result |= {"status": "DETECTED", "counterexample": str(error)}
        except Exception as error:
            result |= {"status": "ERROR", "error_type": type(error).__name__,
                       "reason": "An unrelated crash is not successful mutation detection"}
        else:
            result |= {"status": "UNDETECTED", "reason": "Broken callable passed its behavioral oracle"}
        controls.append(result)
    return controls


def run_activation_checks(*, negative_controls: bool = True) -> dict[str, Any]:
    """Observe this checkout without mutating source, active user models or owner release state."""
    pack = fixture_pack()
    measured_before = identity(pack)
    manifest_before = implementation_files()
    checker = _checker_manifest()
    syntax = analyze_eija_source_files({name: (ROOT / name).read_bytes() for name in SOURCE_SYMBOLS
                                       if (ROOT / name).is_file()})
    temporary_root = ROOT / ".tmp"
    temporary_root.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="activation-behavior-", dir=temporary_root,
                            ignore_cleanup_errors=True) as directory:
        root = Path(directory)
        checks = _observed_checks(root)
        controls = _negative_controls(root) if negative_controls else []
    workspaces_cleaned = not root.exists()
    current_manifest = implementation_files()
    source_stable = (manifest_before == current_manifest
                     and measured_before["implementation"] == fingerprint(manifest_before)
                     and checker == _checker_manifest())
    observed_pass = all(check["status"] == "PASS" for check in checks)
    controls_pass = all(control["status"] == "DETECTED" for control in controls)
    # A concurrently edited checkout cannot claim a single fresh checked subject.
    status = "STALE" if not source_stable else "PASS" if observed_pass and controls_pass else "FAIL"
    return {
        "schema": SCHEMA, "status": status, "created_at": datetime.now(UTC).isoformat(),
        "claim": "Bounded direct-call behavior of actual PlayIDE activation services under a synthetic local owner",
        "source": {"revision": _revision(), "identity": measured_before,
                   "manifest": manifest_before, "manifest_hash": fingerprint(manifest_before),
                   "unchanged_during_run": source_stable,
                   "identity_matches_manifest": measured_before["implementation"] == fingerprint(manifest_before),
                   "review_status": "RELEASE_FIXTURE_MATCH" if measured_before["trusted_fixture"] else "SOURCE_REVIEW_REQUIRED"},
        "checker": {"name": "activation-selfdogfood", "version": 1, "manifest": checker,
                    "manifest_hash": fingerprint(checker), "python": platform.python_version(),
                    "platform": platform.platform(), "identity_source": HARNESS_MARK,
                    "oracle_provenance": "Hand-declared expectations; same author as this integration work, not hidden holdout"},
        "pack": {"id": pack.id, "digest": pack.digest, "baseline_semantic_hash": pack.model.semantic_hash},
        "observed_behavior": {"status": "PASS" if observed_pass else "FAIL", "checks": checks,
                              "passed": sum(check["status"] == "PASS" for check in checks), "total": len(checks)},
        "negative_controls": {"status": "NOT_RUN" if not negative_controls else "PASS" if controls_pass else "FAIL",
                              "controls": controls, "detected": sum(item["status"] == "DETECTED" for item in controls),
                              "total": len(controls)},
        "structural_source": {"status": syntax["extraction"]["status"], "method": "python_ast",
                              "source_digest": syntax["source_digest"], "gaps": syntax["gaps"],
                              "claim": "Declared syntax occurrences only; these do not prove runtime behavior"},
        "model_reference": {"status": "NOT_RUN", "claim": "The declared review pack is a separate bounded reference journey",
                            "reason": "These checks call actual Studio services; they do not prove complete model-to-code equivalence"},
        "skipped": [
            {"id": "normal_owner_release_activation", "status": "NOT_RUN",
             "reason": "Synthetic harness decisions do not perform legitimate owner source review or approve this implementation"},
            {"id": "browser_end_to_end", "status": "NOT_RUN", "reason": "This runner calls services; ordinary browser journeys are separate evidence"},
            {"id": "hardware_crash", "status": "NOT_RUN", "reason": "Rollback injection and fresh SQLite connections do not simulate power loss"},
            {"id": "human_comprehension", "status": "NOT_RUN", "reason": "No participant study or independent hidden oracle"},
        ],
        "bounds": {"fixture": "One excursion pack, one five-command owner-plan candidate",
                   "concurrency": "Two approved candidates interleaved; adapter CAS and rollback injection",
                   "restart": "Fresh SQLiteStore/Studio connections in one process",
                   "mutation_scope": "Named principal guards, exact review-subject guard, evidence blocker and case SQL CAS",
                   "network_calls": 0, "existing_user_workspaces_opened": 0,
                   "temporary_workspaces_cleaned": workspaces_cleaned},
        "limitations": [
            "No same-OS-user adversarial boundary; a synthetic principal is not authenticated human authority.",
            "No real owner approval, source stamping, provider inference, deployment or user-data migration is performed.",
            "A hash identifies bytes and a detected mutation demonstrates only the named failure class.",
            "PASS is a local bounded engineering observation; freshness and source-review status are separate.",
        ],
    }
