---
type: Class
title: domain.screens.Screens
description: '`class Screens(Contract)` in `domain/screens`.'
resource: repo://src/eija_studio/domain/screens.py#Screens
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#Screens
  title: domain/screens.py
  hash_method: ast-sig-v1
  sha256: 098d3c2b5eb39fdafb563f13d0af8a4329c355e662ca99557e975ab2209009e2
notes_baseline: f020de258c2515063210ef65eb0396506ebe5eccba3ee756ddc3cb079300b5fe
---

# domain.screens.Screens

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `class Screens(Contract)` |
| Code | `repo://src/eija_studio/domain/screens.py#Screens` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.screens.v1']` | `'eija.screens.v1'` |
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
| `screens` | `tuple[Screen, ...]` | `Field(min_length=1, max_length=80)` |

## Methods

* [`digest`](/symbols/domain/screens/Screens.digest.md) - `def digest(self) -> str`
* [`screen`](/symbols/domain/screens/Screens.screen.md) - `def screen(self, use_case: str \| None) -> Screen \| None`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.screens.Screen](/symbols/domain/screens/Screen.md) - `class Screen(Contract)` in `domain/screens`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.ripple.check_follow_ons](/symbols/application/ripple/check_follow_ons.md) - The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy (`base` with `plan` and the step), a scr…
* [application.ripple.ripple](/symbols/application/ripple/ripple.md) - Every diagram's effects of going from `base` to `candidate`.
* [application.screen_access.check_accessibility](/symbols/application/screen_access/check_accessibility.md) - Each check with its WCAG success criteria and PASS, WARN (advice) or FAIL, the design's first.
* [domain.screens.Screens.digest](/symbols/domain/screens/Screens.digest.md) - `def digest(self) -> str` in `domain/screens`.
* [domain.screens.Screens.screen](/symbols/domain/screens/Screens.screen.md) - `def screen(self, use_case: str | None) -> Screen | None` in `domain/screens`.
* [domain.screens.check_screens](/symbols/domain/screens/check_screens.md) - Design problems, each with a stable code and the use case it is about.
* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One default screen per use case.
* [domain.screens.load_screens](/symbols/domain/screens/load_screens.md) - The pack's screens, or None when the pack has no `screens.json`.
* [domain.screens.parse_screens](/symbols/domain/screens/parse_screens.md) - `def parse_screens(document: Any, pack_id: str) -> Screens` in `domain/screens`.
* [domain.screens.require_buildable](/symbols/domain/screens/require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.
* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
<!-- okf:generated:end links -->
