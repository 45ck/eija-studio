# Symbols of application.ports

# Class

* [application.ports.ProposalProvider](ProposalProvider.md) - The only door for AI: a provider returns an untrusted Proposal and cannot select meaning, approve or apply.
* [application.ports.ProviderResult](ProviderResult.md) - `class ProviderResult` in `application/ports` (the source has no docstring).
* [application.ports.ReceiptAuthenticator](ReceiptAuthenticator.md) - `class ReceiptAuthenticator(Protocol)` in `application/ports` (the source has no docstring).
* [application.ports.Repository](Repository.md) - `class Repository(Protocol)` in `application/ports` (the source has no docstring).
* [application.ports.UnitOfWork](UnitOfWork.md) - The application-owned persistence port: all mutations on it commit together or roll back together.

# Type Alias

* [application.ports.IdentityProvider](IdentityProvider.md) - `IdentityProvider = Callable[[], dict]` in `application/ports` (the source has no docstring).
* [application.ports.SandboxFactory](SandboxFactory.md) - Opens a disposable verification store that keeps unit-of-work atomicity and is deleted on exit.
