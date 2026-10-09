# Symbols of application.new_system

# Constants

* [application.new_system.FIELD](FIELD.md) - Constant `FIELD` in `application/new_system`.
* [application.new_system.KIND_LISTS](KIND_LISTS.md) - Constant `KIND_LISTS` in `application/new_system`.
* [application.new_system.LINE](LINE.md) - Constant `LINE` in `application/new_system`.
* [application.new_system.LIST](LIST.md) - Constant `LIST` in `application/new_system`.
* [application.new_system.MAX_LINES](MAX_LINES.md) - Constant `MAX_LINES` in `application/new_system`.
* [application.new_system.NAME](NAME.md) - Constant `NAME` in `application/new_system`.
* [application.new_system.RECORD](RECORD.md) - Constant `RECORD` in `application/new_system`.
* [application.new_system.SKETCH_HELP](SKETCH_HELP.md) - Constant `SKETCH_HELP` in `application/new_system`.
* [application.new_system.UNSUPPORTED](UNSUPPORTED.md) - Constant `UNSUPPORTED` in `application/new_system`.

# Functions

* [application.new_system.checked_documents](checked_documents.md) - The documents, if the kernel's checks accept them; `PackError` with every problem otherwise.
* [application.new_system.classes](classes.md) - A system's record class and each class's attribute names, for naming data-model steps (ADR-0202); None when the system has no class diagram.
* [application.new_system.declare](declare.md) - `pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declares them (ADR-0201): an action gets the base guards and one audit entry, a role one active, assigned f…
* [application.new_system.new_names](new_names.md) - The actions and roles `transactions` name that `pack` does not declare, in order of first use.
* [application.new_system.parse_sketch](parse_sketch.md) - The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line.
* [application.new_system.sketch_documents](sketch_documents.md) - `pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
* [application.new_system.summary](summary.md) - What the new system has, for the form to say before it is created.
* [application.new_system.system_id](system_id.md) - A pack id for a new system called `name`, unlike every id in `taken`.
* [application.new_system.template_documents](template_documents.md) - A copy of a template's documents as a new system: new id and name, the same model, rules, laws, screens and test cases (`scenarios.json`).
