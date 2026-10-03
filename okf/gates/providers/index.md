# Gates defined in quality/sessions/providers.py

# Quality Gates

* [nox -s providers_contract](providers-contract.md) - Shared contract for codex/claude/opencode/gemini (mocked runner), tree-kill on real processes, HTTP providers (mock transport).
* [nox -s providers_doctor](providers-doctor.md) - Local, offline diagnostic of every CLI provider (version, flags, official login status).
