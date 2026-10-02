"""The assurance loop: intent -> explicit meaning -> exercised rule -> computed evidence -> decision.

This is the shipped v0.2 flow (README "First demonstration"); it needs no other lane. Every
assertion below is against text the Studio really renders, so the recording doubles as an e2e check.

Prerequisite for the last act: verification refuses to run when the source differs from the
owner-stamped release fixture (`SOURCE_REVIEW_REQUIRED`). Agents never stamp. When the fixture does not
match, this scenario records the first three acts and reports the rest as skipped - it does not
bypass the gate.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene

TITLE = "The assurance loop: intent to applied baseline"


def run(scene: Scene, server: RunningServer) -> None:
    scene.goto(server.launch_url)
    # The Studio ignores clicks while its startup request is still running (`aria-busy` on <body>); an instant
    # dry run would click Create into that window and lose it. Wait for the page to go idle first.
    scene.wait_for("body:not([aria-busy])")
    scene.title_card("EIJA Studio", "See meaning. Prove change. An AI proposes, a kernel checks, you decide.")

    # Act 1 - intent, then explicit meanings ------------------------------------------------------
    scene.caption("Start with intent: a plain-language request, not code.")
    # The workbench opens on Model; reveal the new-intent form through its public control.
    scene.click("#start-intent")
    scene.type_text("#request", "Let teachers sign off excursions.", clear=True)
    scene.click("#create")
    scene.expect_text("#notice", "Case created")

    scene.caption("No model call yet. Ask for interpretations - the offline fixture stands in for an LLM.")
    scene.click("#propose")
    scene.expect_text("#notice", "Interpretations received")
    scene.expect_text("#options", "Teacher recommends")

    scene.caption("Final approval is blocked by policy - not quietly downgraded to something else.")
    scene.highlight('#options article:has-text("Teacher grants final approval")', duration_ms=1600)

    scene.caption("The owner - not the AI - selects the meaning.")
    scene.click('#options article:has-text("Teacher recommends") button')
    scene.expect_text("#notice", "Meaning selected")

    # Act 2 - one model, synchronised views --------------------------------------------------------
    scene.click("#open-workspace")
    scene.click('[data-workspace-view="impact"]')
    scene.caption("One substrate, synchronised views: the rule table and state flow derive from one model.")
    scene.click("#rules-state-flow > summary")
    scene.highlight("#state-flow")
    scene.highlight("#rule-table")

    # Act 3 - exercise the rule as different synthetic actors ---------------------------------------
    scene.click('[data-tab="try"]')
    scene.caption("Try the rule for real: an isolated executable preview, not a mocked response.")
    scene.click("#reset")
    scene.expect_text("#runtime-state", "Draft")
    scene.wait_for("body:not([aria-busy])")

    scene.select_option("#actor", "teacher-assigned")
    _act(scene, "Submit")
    _act(scene, "Recommend")

    scene.caption("An unassigned teacher cannot approve. The runtime denies it - and records why.")
    scene.select_option("#actor", "teacher-unassigned")
    scene.click('#runtime-actions button:text-is("Approve")')
    scene.expect_text("#notice", "required role")
    scene.highlight("#notice", duration_ms=1600)

    scene.caption("Only the registrar holds final approval.")
    scene.select_option("#actor", "registrar")
    _act(scene, "Approve")
    scene.expect_text("#runtime-state", "Approved")

    # Act 4 - computed evidence and a separate human decision ---------------------------------------
    scene.click('[data-tab="evidence"]')
    if not server.release_fixture_matches:
        scene.skip("Act 4 (verify, approve, apply): the owner has not restamped the release fixture, so "
                   "verification returns SOURCE_REVIEW_REQUIRED. Agents never stamp; not exercised.")
        # Exercise the gate rather than describe it: clicking Verify must be refused with the real error.
        # Only after the Studio has shown that refusal do we narrate it, so the caption matches the screen.
        scene.click("#verify")
        scene.expect_text("#notice", "SOURCE_REVIEW_REQUIRED")
        scene.caption("Verification is blocked until the owner reviews changed source - by design.")
        scene.highlight("#notice", duration_ms=1600)
        scene.clear_caption()
        scene.title_card("Intent, meaning, consequence",
                         "Evidence and the human decision come next - once the owner stamps the release.")
        return

    scene.caption("Evidence is computed from 125 executed observations - a green label is never trusted.")
    scene.click("#verify")
    scene.expect_text("#notice", "Bounded runtime verification finished")
    scene.highlight("#formal")

    scene.caption("Human understanding stays UNKNOWN. The owner answers, then approves the exact revision.")
    scene.highlight(".unknown")
    scene.type_text("#q-authority", "Registrar")
    scene.type_text("#q-assignment", "No")
    scene.type_text("#q-reject_entry", "Recommended")
    scene.check("#acknowledge")
    scene.click("#approve")
    scene.expect_text("#notice", "Exact local revision acknowledged")

    scene.caption("Apply is a separate action, and only touches the local demo baseline.")
    scene.click("#apply")
    scene.expect_text("#notice", "Applied to the local demo baseline only")
    scene.expect_text("#case-stage", "APPLIED")
    scene.clear_caption()
    scene.title_card("Meaning reviewed. Evidence computed. Decision yours.",
                     "EIJA Studio - open source, Apache-2.0")


def _act(scene: Scene, action: str) -> None:
    scene.wait_for("body:not([aria-busy])")
    scene.click(f'#runtime-actions button:text-is("{action}")')
    scene.expect_text("#runtime-result", f"Committed: {action}")
    scene.wait_for("body:not([aria-busy])")
