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
* [application.appgen.data_cases](data_cases.md) - Record values to create with, and `check_values`' answer for each: a valid record, then each required value missing, each value of the wrong type, each text one character too long, an undeclared choice and an unknown fi…
* [application.appgen.generate](generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.oracle_cases](oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
