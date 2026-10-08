# Symbols of domain.screens

# Classes

* [domain.screens.Screen](Screen.md) - `class Screen(Contract)` in `domain/screens`.
* [domain.screens.ScreenField](ScreenField.md) - `class ScreenField(Contract)` in `domain/screens`.
* [domain.screens.Screens](Screens.md) - `class Screens(Contract)` in `domain/screens`.

# Constants

* [domain.screens.CREATE](CREATE.md) - Constant `CREATE` in `domain/screens`.
* [domain.screens.SCREENS_FILE](SCREENS_FILE.md) - Constant `SCREENS_FILE` in `domain/screens`.

# Functions

* [domain.screens.check_screens](check_screens.md) - Design problems, each with a stable code and the use case it is about.
* [domain.screens.default_screens](default_screens.md) - One screen per use case: `create` asks for every record attribute; an action shows the required ones.
* [domain.screens.load_screens](load_screens.md) - The pack's screens, or None when the pack has no `screens.json`.
* [domain.screens.parse_screens](parse_screens.md) - `def parse_screens(document: Any, pack_id: str) -> Screens` in `domain/screens`.
* [domain.screens.require_buildable](require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.
* [domain.screens.screens_for](screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
* [domain.screens.use_cases](use_cases.md) - Creating a record (None), then each distinct action in transition-id order: the ellipses of the use case diagram.

# Methods

* [domain.screens.Screen.unique](Screen.unique.md) - `def unique(self) -> Screen` in `domain/screens`.
* [domain.screens.Screens.digest](Screens.digest.md) - `def digest(self) -> str` in `domain/screens`.
* [domain.screens.Screens.screen](Screens.screen.md) - `def screen(self, use_case: str | None) -> Screen | None` in `domain/screens`.
