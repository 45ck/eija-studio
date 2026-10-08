"""Pure-Python checks of the scenario catalogue: no browser, no server."""
from manifest_helpers import put_manifest

from demos.__main__ import REGISTRY_MD
from demos.scenarios.registry import (
    KNOWN_LANES, LANDED_LANES, SCENARIOS, WAVE1_LANES, WAVE2_LANES, Scenario, check_consistency, render_markdown,
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


# ---- "waits for" reflects reality (WBS 0.6): a scenario waits only for lanes that have not landed ----------------

def test_no_scenario_waits_for_a_lane_that_has_landed():
    assert LANDED_LANES == WAVE1_LANES and not LANDED_LANES & WAVE2_LANES
    for s in SCENARIOS:
        assert not set(s.waits_for) & LANDED_LANES, s.key


def test_a_scenario_is_blocked_exactly_when_it_waits_for_an_unlanded_lane():
    for s in SCENARIOS:
        assert (s.status == "blocked") == bool(s.waits_for), s.key
    blocked = {s.key: s.waits_for for s in SCENARIOS if s.status == "blocked"}
    assert blocked == {"uml_drag_and_drop": ("uml-editor",), "ubiquitous_language_ddd_tree": ("ddd-language",),
                       "image_generation_in_studio": ("imagegen",), "e2e_tests_personas_icp": ("personas-e2e",)}


def test_a_blocked_status_that_waits_for_only_landed_lanes_is_rejected():
    stale = Scenario("no_module_yet", "x", "blocked", ("agents", "providers", "visual"), "story")
    assert any("every lane it needs has landed" in p for p in check_consistency((stale,)))


def test_a_ready_status_that_still_waits_for_a_lane_is_rejected():
    early = Scenario("no_module_yet", "x", "unscripted", ("visual", "uml-editor"), "story")
    assert any("still waits for lane(s) ['uml-editor']" in p for p in check_consistency((early,)))


def test_an_unscripted_scenario_has_no_module_and_no_manifest(tmp_path):
    scripted = Scenario("assurance_loop", "x", "unscripted", (), "story")  # the module exists in this repo
    assert any("unscripted scenario must not have a module" in p for p in check_consistency((scripted,), tmp_path))
    put_manifest(tmp_path, "assurance_loop")
    assert any("manifest exists but status" in p for p in check_consistency((scripted,), tmp_path))


def test_the_registry_table_lists_only_unlanded_lanes_and_never_claims_a_recording():
    text = render_markdown()
    row = {s.key: next(line for line in text.splitlines() if line.startswith(f"| `{s.key}`")) for s in SCENARIOS}
    assert "| nothing |" in row["formal_vv_tour"] and "`bend`" not in row["formal_vv_tour"]
    assert "`uml-editor` (wave 2)" in row["uml_drag_and_drop"] and "`visual`" not in row["uml_drag_and_drop"]
    recorded = [s for s in SCENARIOS if s.status.startswith("recorded")]
    assert [s.key for s in recorded] == ["assurance_loop", "ide_walkthrough", "playide_tour", "playide_ripple", "playide_showcase"]
    assert all(s.manifest().is_file() for s in recorded)  # recorded only where a manifest says so
