# Symbols of application.history

# Classes

* [application.history.SemanticHistory](SemanticHistory.md) - Validated replay; models includes the selected meaning followed by each applied owner edit.

# Functions

* [application.history.command_event](command_event.md) - Append-only command provenance; decision and receipt payloads remain in their existing audit.
* [application.history.history_view](history_view.md) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
* [application.history.replay](replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
