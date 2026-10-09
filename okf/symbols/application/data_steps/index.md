# Symbols of application.data_steps

# Classes

* [application.data_steps.AddAttribute](AddAttribute.md) - `class AddAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.RemoveAttribute](RemoveAttribute.md) - `class RemoveAttribute(Contract)` in `application/data_steps`.
* [application.data_steps.SetRequired](SetRequired.md) - `class SetRequired(Contract)` in `application/data_steps`.

# Constants

* [application.data_steps.DATA_EDITS](DATA_EDITS.md) - Constant `DATA_EDITS` in `application/data_steps`.
* [application.data_steps.DATA_STEP_KINDS](DATA_STEP_KINDS.md) - Constant `DATA_STEP_KINDS` in `application/data_steps`.
* [application.data_steps.FIXED](FIXED.md) - Constant `FIXED` in `application/data_steps`.

# Functions

* [application.data_steps.apply_data](apply_data.md) - `data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
* [application.data_steps.data_changes](data_changes.md) - What changed on the class diagram, in words: attributes gained and lost, and required ones made optional or back.
* [application.data_steps.describe_data](describe_data.md) - One line a person can check against the class diagram.
* [application.data_steps.draft_pack](draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and the data model holds their data-model steps (ADR-0202).
* [application.data_steps.is_data](is_data.md) - `def is_data(step: Step) -> bool` in `application/data_steps`.
* [application.data_steps.parse_step](parse_step.md) - A plan step: a data-model step, or else a kernel transaction (`parse_transaction`).
* [application.data_steps.split](split.md) - The kernel transactions and the data-model steps, each in plan order.

# Type Aliases

* [application.data_steps.DataEdit](DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.DataStep](DataStep.md) - Type alias `DataStep` in `application/data_steps`.
* [application.data_steps.Step](Step.md) - Type alias `Step` in `application/data_steps`.
