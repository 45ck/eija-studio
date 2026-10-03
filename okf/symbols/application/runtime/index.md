# Symbols of application.runtime

# Functions

* [application.runtime.check_actor](check_actor.md) - Denies a command unless the trusted actor is active, holds the transition's role and, where guarded, is assigned.
* [application.runtime.execute](execute.md) - Executes one command against a preview instance: authority is checked before replay, versions are compare-and-swap, and audit and outbox commit with the state change.
* [application.runtime.initialise](initialise.md) - Creates an isolated preview instance bound to a model hash at version 0, after the policy check.
