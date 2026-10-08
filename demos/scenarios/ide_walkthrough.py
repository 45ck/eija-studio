"""The IDE walkthrough: EIJA reviews a change to its own review journey, connected read-only to its own source.

Drives the real self-dogfood configuration (`--pack packs/eija-review-slice --repo <this checkout>`, offline
provider). Every step asserts text the Studio really renders, so the recording doubles as an e2e check.

Verification needs the owner-stamped release fixture (`SOURCE_REVIEW_REQUIRED` otherwise). Agents never stamp:
on an unstamped checkout the last act clicks Verify, shows the real refusal, and is reported as skipped.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene

TITLE = "The IDE walkthrough: EIJA reviews a change to itself"
CONNECT_REPOSITORY = True
PACK = "packs/eija-review-slice"
REQUEST = "Show the optional saved candidate path in EIJA's review journey."


def run(scene: Scene, server: RunningServer) -> None:
    scene.goto(server.launch_url)
    scene.expect_text("#connection", "offline", timeout_ms=60_000)
    scene.wait_for("body:not([aria-busy])")
    scene.title_card("EIJA Studio", "Review the meaning of a change, not every generated line.")

    _model_and_source(scene)
    _intent(scene)
    _changes(scene)
    _checked_edit(scene)
    _run_rules(scene)
    _evidence(scene, server)


def _model_and_source(scene: Scene) -> None:
    scene.caption("EIJA is connected to its own repository, read-only. This is the model of its review workflow.")
    scene.highlight("#model-canvas", duration_ms=1400)
    scene.caption("Every concept in the domain language is linked to the code that implements it.")
    _expand(scene, "term")
    scene.click('#domain-tree [data-eija-id="eija-review-slice.term.verify"]')
    scene.expect_text("#selection-detail", "Studio.verify")
    scene.highlight("#selection-detail", duration_ms=1400)
    scene.caption("Follow the concept into its source: captured bytes, exact lines, never executed.")
    scene.click('#selection-detail button:has-text("Studio.verify")')
    scene.expect_text("#code", "def verify", timeout_ms=60_000)
    scene.wait_for("body:not([aria-busy])")
    scene.highlight("#code .source-editor", duration_ms=1800)


def _intent(scene: Scene) -> None:
    scene.click('[data-tab="model"]')
    scene.caption("Now ask for a change in plain language.")
    scene.click("#start-intent")
    scene.type_text("#request", REQUEST, clear=True)
    scene.click("#create")
    scene.expect_text("#case-stage", "DRAFT")
    scene.click('[data-tab="change"]')
    scene.caption("Ask for interpretations. Offline here: a deterministic fixture stands in for the AI.")
    scene.click("#propose")
    scene.expect_text("#case-stage", "PROPOSED", timeout_ms=30_000)
    scene.wait_for("body:not([aria-busy])")
    scene.highlight("#options", duration_ms=1600)
    scene.caption("The AI proposes. Only the owner selects the meaning.")
    scene.click('#options button:text-is("Select this meaning")')
    scene.expect_text("#case-stage", "PREVIEW", timeout_ms=30_000)
    scene.wait_for("body:not([aria-busy])")


def _changes(scene: Scene) -> None:
    scene.click('[data-tab="review"]')
    scene.caption("Review the change by meaning: what was added, removed or modified in the model.")
    scene.click('#explorer button:has-text("Added · Save · TR-SAVE")')
    scene.wait_for("body:not([aria-busy])")
    scene.highlight("#explorer", duration_ms=1200)
    scene.caption("Before and after, side by side: a new Save path out of PREVIEW.")
    scene.wait(2600)


def _checked_edit(scene: Scene) -> None:
    scene.click('[data-tab="model"]')
    scene.caption("Edit the model directly. Each edit is a typed transaction the kernel checks first.")
    _expand(scene, "transition")
    scene.click('#domain-tree [data-eija-id="eija-review-slice.transition.TR-SAVE"]')
    scene.expect_text("#selection-detail", "Save")
    scene.highlight("#model-canvas .model-edge.selected", duration_ms=1400)
    scene.caption("Targets that would break the reference sequence are refused before anything is sent.")
    scene.highlight("#target-state", duration_ms=1600)
    scene.select_option("#target-state", "DRAFT")
    scene.click("#edit-target")
    scene.wait_for("#edit-preview[open]")
    scene.caption("A server-checked preview of the exact change. Nothing is written until you apply it.")
    scene.highlight("#edit-preview-comparison", duration_ms=2200)
    scene.click("#edit-preview-cancel")
    scene.wait_for("body:not([aria-busy])")
    scene.caption("Closed: the working model is unchanged.")


def _run_rules(scene: Scene) -> None:
    scene.click('[data-tab="try"]')
    scene.caption("Exercise the rules for real in an isolated preview, as different synthetic actors.")
    scene.click("#reset")
    scene.expect_text("#runtime-state", "DRAFT")
    scene.wait_for("body:not([aria-busy])")
    scene.select_option("#actor", "agent-active")
    _act(scene, "Propose")
    scene.caption("An agent may propose, but it cannot select the meaning. The runtime refuses, and records why.")
    scene.click('#runtime-actions button:text-is("SelectMeaning")')
    scene.wait_for('#runtime-result[data-status="refused"]')
    scene.highlight("#runtime-result", duration_ms=1800)
    scene.select_option("#actor", "owner-active")
    _act(scene, "SelectMeaning")
    scene.caption("The owner can.")
    scene.wait(1200)


def _evidence(scene: Scene, server: RunningServer) -> None:
    scene.click('[data-tab="evidence"]')
    scene.caption("Evidence is computed for an exact subject. Human understanding stays UNKNOWN until measured.")
    scene.highlight("#evidence", duration_ms=1600)
    if not server.release_fixture_matches:
        scene.skip("Verify, approve, apply: the owner has not restamped the release fixture, so verification returns "
                   "SOURCE_REVIEW_REQUIRED. Agents never stamp; not exercised.")
        scene.click("#verify")
        scene.expect_text("#notice", "SOURCE_REVIEW_REQUIRED")
        scene.caption("Verification stays blocked until the owner reviews the changed source. By design.")
        scene.highlight("#notice", duration_ms=1800)
    scene.clear_caption()
    scene.title_card("AI proposes. The kernel checks. You decide.", "EIJA Studio - open source, Apache-2.0")


def _expand(scene: Scene, kind: str) -> None:
    group = f'#domain-tree .tree-group[data-kind="{kind}"]'
    if scene.page.locator(group).get_attribute("aria-expanded") != "true":
        scene.click(group + " > span")


def _act(scene: Scene, action: str) -> None:
    scene.wait_for("body:not([aria-busy])")
    scene.click(f'#runtime-actions button:text-is("{action}")')
    scene.expect_text("#runtime-result", f"Committed: {action}")
    scene.wait_for("body:not([aria-busy])")
