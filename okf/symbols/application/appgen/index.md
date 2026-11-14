# Symbols of application.appgen

# Constants

* [application.appgen.CASE_KINDS](CASE_KINDS.md) - Constant `CASE_KINDS` in `application/appgen`.
* [application.appgen.FORMAT](FORMAT.md) - Constant `FORMAT` in `application/appgen`.
* [application.appgen.LIMITS](LIMITS.md) - Constant `LIMITS` in `application/appgen`.
* [application.appgen.NO_DATA](NO_DATA.md) - Constant `NO_DATA` in `application/appgen`.
* [application.appgen.SAMPLES](SAMPLES.md) - Constant `SAMPLES` in `application/appgen`.
* [application.appgen.UNDECLARED_ACTION](UNDECLARED_ACTION.md) - Constant `UNDECLARED_ACTION` in `application/appgen`.
* [application.appgen.UNKNOWN_ACTOR](UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/appgen`.
* [application.appgen.WITH_DATA](WITH_DATA.md) - Constant `WITH_DATA` in `application/appgen`.
* [application.appgen.WRONG](WRONG.md) - Constant `WRONG` in `application/appgen`.

# Functions

* [application.appgen.absent](absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.appgen.app_limits](app_limits.md) - `def app_limits(data: DataModel | None) -> list[str]` in `application/appgen`.
* [application.appgen.create_cases](create_cases.md) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.
* [application.appgen.data_cases](data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown f…
* [application.appgen.generate](generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.journeys](journeys.md) - For each transition, a record started through the app and walked to it: the shortest run from the initial state whose last step is that transition, each step taken by the first fixture actor the kernel allows, and the k…
* [application.appgen.linked_cases](linked_cases.md) - For each transition that moves linked objects, an actor who may take it tries it with the objects in every state of their lifecycles, and the kernel's answer, with the objects' states after a commit (ADR-0241).
* [application.appgen.may_start](may_start.md) - Whether the model lets this role start a record (ADR-0231): any role when it names no initiators.
* [application.appgen.object_cases](object_cases.md) - Objects of each class a record refers to, created through the app (ADR-0235): a valid one, which starts in its lifecycle's initial state when the model gives it one (ADR-0241), then each value missing, of the wrong type…
* [application.appgen.options_cases](options_cases.md) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether the kernel would take it from there at version 0, with its r…
* [application.appgen.oracle_cases](oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
* [application.appgen.rules](rules.md) - The rule table the app shows: each action once, every state it leaves, where it leads and who takes it.
* [application.appgen.separation_cases](separation_cases.md) - One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same record; the kernel's answer to the second (ADR-0233).
* [application.appgen.signal_cases](signal_cases.md) - Each signal the model receives, delivered with valid record values, and the kernel's answer (a record started in the initial state), then the first one under a name it does not receive and from a sender it does not hear…
* [application.appgen.start_cases](start_cases.md) - Each active fixture actor starting a record, and the kernel's answer.
* [application.appgen.stock](stock.md) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [application.appgen.timer_cases](timer_cases.md) - For each transition with a time event, an actor who may take it tries it on a record that has been in the source state half the time and the whole time, and the kernel's answer (ADR-0237).
* [application.appgen.valid_values](valid_values.md) - A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class.
* [application.appgen.value_cases](value_cases.md) - For each transition with guards over record values, an actor who may take it tries it on records holding every combination of values its guards can tell apart (`value_guards.combinations`), and the kernel's answer (ADR-…
