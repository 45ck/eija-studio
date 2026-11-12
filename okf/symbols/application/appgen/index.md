# Symbols of application.appgen

# Constants

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
* [application.appgen.data_cases](data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown f…
* [application.appgen.generate](generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.may_start](may_start.md) - Whether the model lets this role start a record (ADR-0231): any role when it names no initiators.
* [application.appgen.oracle_cases](oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
* [application.appgen.separation_cases](separation_cases.md) - One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same record; the kernel's answer to the second (ADR-0233).
* [application.appgen.start_cases](start_cases.md) - Each active fixture actor starting a record, and the kernel's answer.
* [application.appgen.stock](stock.md) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [application.appgen.timer_cases](timer_cases.md) - For each transition with a time event, an actor who may take it tries it on a record that has been in the source state half the time and the whole time, and the kernel's answer (ADR-0236).
* [application.appgen.value_cases](value_cases.md) - For each transition with guards over record values, an actor who may take it tries it on records holding every combination of values its guards can tell apart (`value_guards.combinations`), and the kernel's answer (ADR-…
