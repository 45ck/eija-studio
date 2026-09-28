# Source modules grouped by layer

# Sections

* [adapters](adapters/) - Adapters: SQLite, providers, receipts and identity behind application ports
* [application](application/) - Application layer: runtime, verifier, compiler, ports and the Studio use cases
* [domain](domain/) - Domain layer: contracts, protected policy, impact closure and evidence assessment
* [interfaces](interfaces/) - Interfaces: the eija CLI and the FastAPI HTTP app

# Modules

* [bootstrap](bootstrap.md) - The only composition root: wires application ports to concrete adapters.
