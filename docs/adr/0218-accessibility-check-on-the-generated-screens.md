# ADR-0218: An accessibility check on the generated screens

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE (owner direction, 9 October 2026: refine how humans and software are designed; thread "Humans, roles and screens")

## Context and problem statement

PlayIDE designs the screens of the app it builds ([ADR-0154](0154-use-cases-and-screens-designed-against-the-model.md)) and the role lens shows them as each role ([ADR-0215](0215-see-and-run-the-app-as-each-role.md)). Nothing said whether those screens were usable by everyone. When we measured the built app's theme, the dark theme drew the field names (`.values dt`) and the action panel (`.action-screen`) with fixed light colours: secondary text on the action panel came out at 1.15:1, far below the 4.5:1 that WCAG 2.2 SC 1.4.3 asks for. The design check passed anyway, because it only asked whether a screen could be built.

## Decision drivers

* A real check, with a verdict per WCAG success criterion and the measured value where there is one, not a badge.
* It runs as you design (every screen edit already re-checks), so it must be fast, pure and need no browser.
* Every check must be able to fail: a negative oracle per check.
* Honest limits: a pass is not a full audit.

## Considered options

* A pure check in the application layer over the screens, the record class and the page templates, with axe-core on the built app in the browser tests (chosen).
* axe-core in the designer itself: needs the app built and a browser page per edit, so it cannot run on every keystroke.
* pa11y or Lighthouse in a nox session: a whole headless browser per run, and the result would arrive long after the edit.

## Decision outcome

`application/screen_access.check_accessibility` judges two things, and `/api/play/screens` returns its report beside the design problems.

* **What the design changes:** a screen that repeats a label (SC 1.3.1, 2.4.6); actions offered from one state with the same title (2.4.6); fields that show an attribute's code name as their label (advice, WARN, since the name may read well enough).
* **What the page templates fix:** text contrast for every pair of theme tokens the page draws, in the light and the dark theme (1.4.3, with each ratio); colours written outside the theme (1.4.3); no positive tabindex, so the keyboard follows the screen (2.4.3); labels tied to every input and the actor picker (1.3.1, 4.1.2); required fields marked `required` for assistive technology, not only with `*` (3.3.2).

The Screens tab shows the report under the design check: each check with PASS, WARN or FAIL, its success criteria, and a swatch and ratio per contrast pair. A FAIL also keeps the "Screens pass the design check" item of the checks ring open. The dark theme's two fixed colours now use theme tokens.

### Consequences

* Good: the defect above is caught and fixed, and any later template change that breaks contrast, labels or keyboard order fails the check and its tests.
* Good: the browser test runs axe-core (axe-playwright-python, already the HCI lane's tool) on the built app in both themes and finds no WCAG 2.0 to 2.2 A/AA violation, so the pure check and the browser agree.
* Bad: the template checks read the template text for known patterns (`input.required = true`, `el("label"`); a rewrite of the page that keeps the behaviour but changes the code fails them until the patterns move with it. They are tests of our own templates, not of arbitrary HTML.
* Limits: no check of focus visibility, reflow, target size or screen reader output. The report says it is not a full audit.
