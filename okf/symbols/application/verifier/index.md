# Symbols of application.verifier

# Constants

* [application.verifier.ACTORS](ACTORS.md) - `ACTORS = [('teacher-assigned', 'Teacher', True, True), ('teacher-unassigned', 'Teacher', True, False), ('teacher-revoked', 'Teacher', False, True), (…` in `application/verifier` (the source has no docstring).
* [application.verifier.ORACLE](ORACLE.md) - Hand-authored expected role, source and target state per action, separate from the runtime's guard evaluator.

# Functions

* [application.verifier.verify_runtime](verify_runtime.md) - Runs the declared actor x state x action matrix against the real runtime in a disposable sandbox and returns the artifact a receipt is built from.
