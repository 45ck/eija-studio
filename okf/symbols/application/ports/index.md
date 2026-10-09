# Symbols of application.ports

# Classes

* [application.ports.EditProposer](EditProposer.md) - Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
* [application.ports.FormalEvidenceSource](FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [application.ports.PlanProposer](PlanProposer.md) - Turns a chat request into {summary, meaning, steps: [{transaction, why}]}.
* [application.ports.ProposalProvider](ProposalProvider.md) - The only door for AI: a provider returns an untrusted Proposal and cannot select meaning, approve or apply.
* [application.ports.ProviderResult](ProviderResult.md) - `class ProviderResult` in `application/ports`.
* [application.ports.ReceiptAuthenticator](ReceiptAuthenticator.md) - `class ReceiptAuthenticator(Protocol)` in `application/ports`.
* [application.ports.Repository](Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.ports.SystemDescriber](SystemDescriber.md) - Turns a description of an app into {name, record, sketch, fields, reading} for "Describe your app" (ADR-0203).
* [application.ports.UnitOfWork](UnitOfWork.md) - The application-owned persistence port: all mutations on it commit together or roll back together.

# Type Aliases

* [application.ports.IdentityProvider](IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [application.ports.SandboxFactory](SandboxFactory.md) - Opens a disposable verification store that keeps unit-of-work atomicity and is deleted on exit.
