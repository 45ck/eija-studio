"""Pure-Python checks of the scenario catalogue: no browser, no server."""
from manifest_helpers import put_manifest

from demos.__main__ import REGISTRY_MD
from demos.scenarios.registry import (
    KNOWN_LANES, SCENARIOS, WAVE1_LANES, WAVE2_LANES, Scenario, check_consistency, render_markdown,
)


def test_shipped_catalogue_is_consistent():
    assert check_consistency() == []


def test_generated_registry_matches_committed_file():
    assert REGISTRY_MD.read_bytes().decode("utf-8") == render_markdown()


def test_every_dependency_is_a_known_lane():
    assert {d for s in SCENARIOS for d in s.depends_on} <= KNOWN_LANES


def test_wave2_gaps_are_reachable_from_the_owner_asks():
    # The owner asked to demo drag-and-drop UML, DDD tree, image generation and personas/ICP.
    needed = {d for s in SCENARIOS for d in s.depends_on}
    assert needed >= WAVE2_LANES, "every wave-2 lane must be waited on by at least one scenario"
    assert WAVE1_LANES & needed


def test_blocked_scenario_with_a_module_is_rejected():
    fake = Scenario("assurance_loop", "x", "blocked", (), "story")  # module exists in this repo
    assert any("must not have a module" in p for p in check_consistency((fake,)))


def test_unblocked_scenario_without_a_module_is_rejected():
    fake = Scenario("no_such_scenario", "x", "scripted-not-recorded", (), "story")
    assert any("requires module" in p for p in check_consistency((fake,)))


def test_recorded_states_require_a_manifest(tmp_path):
    for status in ("recorded", "recorded-partial"):
        fake = Scenario("assurance_loop", "x", status, (), "story")
        assert any("manifest" in p and "missing" in p for p in check_consistency((fake,), tmp_path))


def test_recorded_means_no_skipped_acts_and_partial_means_some(tmp_path):
    put_manifest(tmp_path, "assurance_loop", ["Act 4 skipped"])
    complete = Scenario("assurance_loop", "x", "recorded", (), "story")
    partial = Scenario("assurance_loop", "x", "recorded-partial", (), "story")
    assert any("use 'recorded-partial'" in p for p in check_consistency((complete,), tmp_path))
    assert check_consistency((partial,), tmp_path) == []


def test_partial_without_skipped_acts_is_rejected(tmp_path):
    put_manifest(tmp_path, "assurance_loop")
    partial = Scenario("assurance_loop", "x", "recorded-partial", (), "story")
    assert any("use 'recorded'" in p for p in check_consistency((partial,), tmp_path))


def test_manifest_without_recorded_status_is_rejected(tmp_path):
    put_manifest(tmp_path, "assurance_loop")
    scripted = Scenario("assurance_loop", "x", "scripted-not-recorded", (), "story")
    assert any("manifest exists but status" in p for p in check_consistency((scripted,), tmp_path))


def test_unknown_lane_and_duplicates_are_rejected():
    a = Scenario("wave_x", "x", "blocked", ("nonexistent-lane",), "s")
    problems = check_consistency((a, a))
    assert any("unknown lane" in p for p in problems) and any("duplicate key" in p for p in problems)


def test_rendering_is_deterministic():
    assert render_markdown() == render_markdown()
