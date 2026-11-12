# Symbols of application.runtime

# Functions

* [application.runtime.check_actor](check_actor.md) - Denies a command unless the trusted actor is active, holds the transition's role and, where guarded, is assigned.
* [application.runtime.check_due](check_due.md) - Refuse a transition with a time event, ``after(14 days)``, before the record has been in its source state that long (ADR-0237).
* [application.runtime.check_guards](check_guards.md) - Refuse a transition whose guards over the record's values do not hold (ADR-0234).
* [application.runtime.check_linked](check_linked.md) - The moves a transition makes on the objects the record links to, given each object's state (ADR-0241).
* [application.runtime.check_separation](check_separation.md) - Refuse an actor who already took another action of a separation law on this record.
* [application.runtime.execute](execute.md) - Executes one command against a preview instance: authority is checked before replay, versions are compare-and-swap, and audit and outbox commit with the state change.
* [application.runtime.initialise](initialise.md) - Creates an isolated preview instance bound to a model hash at version 0, after the policy check.
* [application.runtime.receive](receive.md) - Start a record because another workflow of the system sent `signal` (issue #93 item 5, ADR-0242).
* [application.runtime.separations](separations.md) - The pack's separation-of-duties laws in force on ``model`` that name ``action`` (issue #149, ADR-0233).
