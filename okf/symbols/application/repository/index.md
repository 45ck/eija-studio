# Symbols of application.repository

# Classes

* [application.repository.RepositoryChangeSource](RepositoryChangeSource.md) - Immutable, read-only facts for an explicit pair in one configured repository.
* [application.repository.RepositorySource](RepositorySource.md) - Evidence about one explicitly configured checkout and its declared domain bindings.

# Constants

* [application.repository.COMMIT_OID_PATTERN](COMMIT_OID_PATTERN.md) - Constant `COMMIT_OID_PATTERN` in `application/repository`.

# Functions

* [application.repository.compare_repository_changes](compare_repository_changes.md) - Validate an immutable comparison request before dispatch to its read-only port.
* [application.repository.read_repository_change_file](read_repository_change_file.md) - Bound the historical selection before dispatch; absence never bypasses validation.
* [application.repository.unconfigured_repository](unconfigured_repository.md) - An absent connection is visible, never an empty successful extraction.
* [application.repository.unconfigured_repository_changes](unconfigured_repository_changes.md) - No comparison connection is not a successful empty code change.
* [application.repository.validate_change_revisions](validate_change_revisions.md) - Validate full object IDs before calling any configured repository port.
