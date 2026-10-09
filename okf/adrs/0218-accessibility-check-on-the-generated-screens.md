---
type: Architecture Decision Record
title: 'ADR-0218: An accessibility check on the generated screens'
description: PlayIDE designs the screens of the app it builds (ADR-0154) and the role lens shows them as each role (ADR-0215).
resource: repo://docs/adr/0218-accessibility-check-on-the-generated-screens.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0218-accessibility-check-on-the-generated-screens.md
  title: 0218-accessibility-check-on-the-generated-screens.md
  hash_method: lf-sha256-v1
  sha256: 841eb8cd2fcf6f402b0380bdc7659d14710e32077d7e5d27154e114cfb8a5af2
notes_baseline: 187d35a9f0d0cdeeb0e9d3eb93a6e7edb0cd2217f9212044c3e72f77e575c610
---

# ADR-0218: An accessibility check on the generated screens

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE (owner direction, 9 October 2026: refine how humans and software are designed; thread "Humans, roles and screens") |
| Source | `repo://docs/adr/0218-accessibility-check-on-the-generated-screens.md` |

## Decision outcome (verbatim)

> `application/screen_access.check_accessibility` judges two things, and `/api/play/screens` returns its report beside the design problems.
>
> * **What the design changes:** a screen that repeats a label (SC 1.3.1, 2.4.6); actions offered from one state with the same title (2.4.6); fields that show an attribute's code name as their label (advice, WARN, since the name may read well enough).
> * **What the page templates fix:** text contrast for every pair of theme tokens the page draws, in the light and the dark theme (1.4.3, with each ratio); colours written outside the theme (1.4.3); no positive tabindex, so the keyboard follows the screen (2.4.3); labels tied to every input and the actor picker (1.3.1, 4.1.2); required fields marked `required` for assistive technology, not only with `*` (3.3.2).
>
> The Screens tab shows the report under the design check: each check with PASS, WARN or FAIL, its success criteria, and a swatch and ratio per contrast pair. A FAIL also keeps the "Screens pass the design check" item of the checks ring open. The dark theme's two fixed colours now use theme tokens.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0154: Use case diagrams, and screens designed against the model](/adrs/0154-use-cases-and-screens-designed-against-the-model.md) - PlayIDE shows the workflow as a state machine (ADR-0151) and the data as a class diagram (ADR-0153).
* [ADR-0215: See and run the app as each role](/adrs/0215-see-and-run-the-app-as-each-role.md) - PlayIDE already models the human side of a system: roles and fixture actors in the pack, a use case diagram (ADR-0154), one screen per use case, and a Permissi…
<!-- okf:generated:end links -->
