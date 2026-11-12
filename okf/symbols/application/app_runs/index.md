# Symbols of application.app_runs

# Functions

* [application.app_runs.create_cases](create_cases.md) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.
* [application.app_runs.journeys](journeys.md) - For each transition, a record started through the app and walked to it: the shortest run from the initial state whose last step is that transition, each step taken by the first fixture actor the kernel allows, and the k…
* [application.app_runs.options_cases](options_cases.md) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether the kernel would take it from there at version 0, with its r…
* [application.app_runs.rules](rules.md) - The rule table the app shows: each action once, every state it leaves, where it leads and who takes it.
