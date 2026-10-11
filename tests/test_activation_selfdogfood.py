"""Observed service behavior and meaningful faults, separate from release source approval."""
import pytest

from eija_studio.adapters.identity import identity, implementation_files
from verification.selfdogfood.checks import CHECKS, HARNESS_MARK, synthetic_studio
from verification.selfdogfood.mutants import activation_mutations
from verification.selfdogfood.run import run_activation_checks


@pytest.mark.parametrize("check_id", CHECKS)
def test_actual_activation_service_behavior(check_id, tmp_path):
    studio = synthetic_studio(tmp_path / "synthetic-workspace")
    assert studio.identity_provider()["identity_source"] == HARNESS_MARK
    assert CHECKS[check_id](studio)


@pytest.mark.parametrize("index", range(7))
def test_broken_callable_is_detected_by_behavior(index, tmp_path):
    mutant = activation_mutations()[index]
    studio = mutant.factory(tmp_path / "synthetic-mutant")
    # The mutated callable must reach an actual bad outcome. A hash mismatch, unrelated
    # exception, unavailable tool or failed import cannot satisfy this expectation.
    with pytest.raises(AssertionError, match=r"unexpectedly accepted|remained eligible"):
        CHECKS[mutant.check](studio)


def test_report_separates_source_model_behavior_and_owner_authority():
    before = implementation_files()
    measured = identity()
    report = run_activation_checks()
    # Parallel integration edits may invalidate a single checked subject. Functional
    # results still remain inspectable; concurrent edits must be labelled STALE.
    after = implementation_files()
    assert report["status"] in {"PASS", "STALE"}
    if report["status"] == "PASS":
        assert report["source"]["unchanged_during_run"]
    else:
        assert not report["source"]["unchanged_during_run"]
    assert report["source"]["identity"]["trusted_fixture"] == measured["trusted_fixture"]
    assert report["observed_behavior"]["passed"] == report["observed_behavior"]["total"] == 15
    assert report["negative_controls"]["detected"] == report["negative_controls"]["total"] == 7
    assert report["structural_source"]["claim"].startswith("Declared syntax")
    assert report["model_reference"]["status"] == "NOT_RUN"
    assert report["checker"]["identity_source"] == HARNESS_MARK
    assert report["bounds"]["network_calls"] == 0
    assert report["bounds"]["existing_user_workspaces_opened"] == 0
    assert all(item["status"] == "NOT_RUN" for item in report["skipped"])
    assert report["bounds"]["temporary_workspaces_cleaned"]
    # The checker itself stays immutable; implementation edits by other lanes are
    # captured above, rather than silently rounded into fresh evidence.
    assert before["adapters/identity.py"] == after["adapters/identity.py"]
